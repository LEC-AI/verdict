"""Matched-protocol training + eval on LocalLLaMA/typed-decisions — the
apples-to-apples comparison vs Laya (0.766) and Jev (0.727).

Fine-tune Verdict on the 1,200-case train split (5 decisions/case = 6,000
decisions), evaluate on the 400-case test split (2,000 decisions), reporting
overall accuracy plus breakdowns BY PRIMITIVE (noul/choice/score) and BY
WORKFLOW — the exact axes Laya reported (noul 0.857, choice 0.733, score 0.723).

  python3 scripts/train_typed.py --out out/verdict-typed --epochs 5 --batch-size 32

Prints a comparison table vs the published Laya/Jev numbers.
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import time
from collections import defaultdict

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict import Choice, Noul, Score, Verdict  # noqa: E402
from verdict.data_typed import load_typed  # noqa: E402

LAYA = {"overall": 0.766, "noul": 0.857, "choice": 0.733, "score": 0.723,
        "invoice_processing": 0.804, "security_incidents": 0.766,
        "customer_service": 0.764, "agent_trace_observability": 0.730}
JEV = {"overall": 0.727}
TEACHER = {"overall": 0.735}


def _q(r):
    if r.qtype == "noul":
        return Noul(r.question)
    if r.qtype == "score":
        return Score(r.question, k=len(r.options))
    return Choice(r.question, r.options)


def _ece(rows, nb=10):
    b = [[0, 0, 0.0] for _ in range(nb)]
    for c, h in rows:
        k = min(int(c * nb), nb - 1)
        b[k][0] += 1; b[k][1] += h; b[k][2] += c
    n = len(rows)
    return sum(abs(h / c - cf / c) * c for c, h, cf in b if c) / max(n, 1) if n else 0.0


def batches(x, n):
    for i in range(0, len(x), n):
        yield x[i:i + n]


def loss_of(model, recs, soft=False):
    logits = model.logits_batch([_q(r) for r in recs])
    dev = logits[0].device
    ls = []
    for lg, r in zip(logits, recs):
        n = lg.shape[0]
        if n < 2 or r.answer < 0 or r.answer >= n:
            continue  # marker/option mismatch — skip malformed
        sv = r.meta.get("soft")
        if soft and sv and len(sv) == n:
            target = torch.tensor(sv, device=dev, dtype=torch.float32)
            logp = torch.log_softmax(lg.float(), dim=-1)
            ls.append(-(target * logp).sum())          # soft cross-entropy (KL up to const)
        else:
            ls.append(torch.nn.functional.cross_entropy(
                lg.unsqueeze(0).float(), torch.tensor(r.answer, device=dev).unsqueeze(0)))
    if not ls:
        return None
    return torch.stack(ls).mean()


@torch.no_grad()
def evaluate(model, recs, bs):
    model.eval()
    correct = 0
    by_prim, by_wf, ece_rows = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0]), []
    skipped = 0
    for ch in batches(recs, bs):
        for d, r in zip(model.predict_batch([_q(x) for x in ch]), ch):
            if len(d.probs) < 2 or r.answer >= len(d.probs):
                skipped += 1; continue
            hit = int(d.top == r.answer); correct += hit
            by_prim[r.meta["primitive"]][0] += hit; by_prim[r.meta["primitive"]][1] += 1
            by_wf[r.meta["workflow"]][0] += hit; by_wf[r.meta["workflow"]][1] += 1
            ece_rows.append((d.confidence, hit))
    return {"overall": correct / max(len(recs), 1), "ece": _ece(ece_rows),
            "by_primitive": {k: v[0] / v[1] for k, v in by_prim.items()},
            "by_workflow": {k: v[0] / v[1] for k, v in by_wf.items()}, "n": len(recs)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out/verdict-typed")
    ap.add_argument("--backbone", default=None)
    ap.add_argument("--epochs", type=int, default=5)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--out-md", default="RESULTS_typed.md")
    ap.add_argument("--soft", action="store_true", help="train on soft annotator label distributions")
    ap.add_argument("--select", choices=["last", "val"], default="last",
                    help="epoch to report: 'last' = train on all 6,000 decisions, report the final epoch "
                         "(no selection); 'val' = hold out --val-pct of TRAIN cases, pick the epoch on them. "
                         "The test split is never used for selection.")
    ap.add_argument("--val-pct", type=int, default=15)
    ap.add_argument("--bf16", action="store_true", help="bf16 autocast (longer inputs with criterion descriptions)")
    ap.add_argument("--bare-options", action="store_true",
                    help="old protocol: option keys only, no criterion descriptions")
    args = ap.parse_args()

    random.seed(0); torch.manual_seed(0)
    from verdict.model import DEFAULT_BACKBONE
    train = load_typed("train", describe=not args.bare_options); test = load_typed("test", describe=not args.bare_options)
    val = []
    if args.select == "val":
        import hashlib as _h
        side = lambda r: int(_h.sha1(r.text.encode("utf-8")).hexdigest()[:8], 16) % 100 < args.val_pct  # by case
        val = [r for r in train if side(r)]; train = [r for r in train if not side(r)]
        print(f"selection: {len(val)} held-out TRAIN decisions for epoch selection", flush=True)
    print(f"typed-decisions: {len(train)} train / {len(test)} test decisions", flush=True)

    model = Verdict.from_pretrained(args.backbone or DEFAULT_BACKBONE)

    # preflight: verify [OPT] marker count == option count (catch truncation /
    # tokenization mismatches before they crash CUDA).
    import collections as _c
    bad, seen, by = 0, 0, _c.Counter()
    for r in train[:400]:
        q = _q(r)
        _, pos = model.collate([q])
        seen += 1
        if len(pos[0]) != len(q.options):
            bad += 1; by[r.qtype] += 1
            if bad <= 5:
                print(f"  MISMATCH {r.qtype}: {len(q.options)} opts vs {len(pos[0])} markers; opts={q.options}", flush=True)
    print(f"preflight marker/option mismatch: {bad}/{seen} (by type: {dict(by)})", flush=True)

    opt = torch.optim.AdamW(list(model.backbone.parameters()) + list(model.head.parameters()), lr=args.lr)
    _dev = next(model.backbone.parameters()).device
    amp = torch.autocast(device_type=_dev.type, dtype=torch.bfloat16, enabled=args.bf16 and _dev.type == "cuda")
    best, best_m = -1.0, None
    for ep in range(args.epochs):
        random.shuffle(train); model.train(); t0 = time.time(); run = 0.0; step = 0
        for ch in batches(train, args.batch_size):
            opt.zero_grad()
            with amp:
                loss = loss_of(model, ch, soft=args.soft)
            if loss is None:
                continue
            loss.backward()
            torch.nn.utils.clip_grad_norm_(list(model.backbone.parameters()) + list(model.head.parameters()), 1.0)
            opt.step(); step += 1; run += loss.item()
        with amp:
            m = evaluate(model, test, args.batch_size)
        print(f"== epoch {ep}: test overall={m['overall']:.4f} ece={m['ece']:.4f} "
              f"prim={ {k: round(v,3) for k,v in m['by_primitive'].items()} } "
              f"({(time.time()-t0):.0f}s) ==", flush=True)
        if args.select == "val":
            mv = evaluate(model, val, args.batch_size)
            print(f"   val overall={mv['overall']:.4f}", flush=True)
            if mv["overall"] >= best:
                best, best_m = mv["overall"], m
                model.save_pretrained(args.out)
        else:
            best, best_m = m["overall"], m      # last epoch wins, by construction
    if args.select == "last":
        model.save_pretrained(args.out)

    m = best_m
    best = m["overall"]
    lines = ["# Verdict on typed-decisions (matched protocol) vs Laya / Jev", "",
             f"Fine-tuned Verdict ({args.backbone or DEFAULT_BACKBONE}); {len(train)} train / {len(test)} test decisions.", "",
             "| metric | Verdict | Laya | Jev | teacher |", "|---|---|---|---|---|",
             f"| **overall** | **{m['overall']*100:.1f}%** | {LAYA['overall']*100:.1f}% | {JEV['overall']*100:.1f}% | {TEACHER['overall']*100:.1f}% |"]
    for p in ["noul", "choice", "score"]:
        if p in m["by_primitive"]:
            lines.append(f"| {p} | {m['by_primitive'][p]*100:.1f}% | {LAYA.get(p,0)*100:.1f}% | - | - |")
    lines += ["", "By workflow:", "", "| workflow | Verdict | Laya |", "|---|---|---|"]
    for wf in ["invoice_processing", "security_incidents", "customer_service", "agent_trace_observability"]:
        if wf in m["by_workflow"]:
            lines.append(f"| {wf} | {m['by_workflow'][wf]*100:.1f}% | {LAYA.get(wf,0)*100:.1f}% |")
    lines += ["", f"Verdict ECE: {m['ece']:.3f} (Laya reported 0.081 after temp scaling; Jev 0.144)."]
    open(args.out_md, "w").write("\n".join(lines))
    print("\n".join(lines), flush=True)
    print(f"DONE best_overall={best:.4f}", flush=True)


if __name__ == "__main__":
    main()
