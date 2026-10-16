"""Train Verdict on one or more OrgBench tasks (multi-task if several).

  python3 scripts/train.py --tasks route_topic,signal_positive \
      --out out/verdict-base --epochs 3 --batch-size 32

Full backbone fine-tune by default (ModernBERT-base is small; trains in
minutes on a 4090). Reports val accuracy + ECE per epoch, saves best.
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import time

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict import Choice, Noul, Score, Verdict  # noqa: E402
from verdict.data import TASKS, build_task, dump_jsonl, load_jsonl  # noqa: E402


def _q(rec):
    if rec.qtype == "noul":
        return Noul(rec.question)
    if rec.qtype == "score":
        return Score(rec.question, k=len(rec.options))
    return Choice(rec.question, rec.options)


def _ece(rows, nb=10):
    b = [[0, 0, 0.0] for _ in range(nb)]
    for c, h in rows:
        k = min(int(c * nb), nb - 1)
        b[k][0] += 1; b[k][1] += h; b[k][2] += c
    n = len(rows)
    return sum(abs(h / c - cf / c) * c for c, h, cf in b if c) / max(n, 1)


def batches(x, n):
    for i in range(0, len(x), n):
        yield x[i:i + n]


def loss_of(model, recs, shuffle_options=False, rng=None, option_dropout=0.0, soft=False):
    """CE over per-option logits. With shuffle_options, each record's option list
    is randomly permuted (target remapped) so the head must read the option TEXT
    rather than memorize option POSITION (the robustness check showed the fixed-order model is
    position-locked: option-permutation accuracy falls to chance)."""
    qs, targets, softs = [], [], []
    for r in recs:
        sv = r.meta.get("soft") if soft and isinstance(r.meta, dict) else None
        if sv is not None and len(sv) != len(r.options):
            sv = None
        if shuffle_options:
            idx = list(range(len(r.options)))
            if option_dropout and len(idx) > 2 and rng.random() < option_dropout:
                # train on a random subset of the options (always keeping gold) so the
                # head sees varied option counts and cannot rely on a fixed label set
                k = rng.randint(2, len(idx) - 1)
                keep = [r.answer] + rng.sample([i for i in idx if i != r.answer], k - 1)
                idx = keep
            rng.shuffle(idx)                                               # idx[new] = old
            qs.append(Choice(r.question, [r.options[i] for i in idx]))
            targets.append(idx.index(r.answer))
            if sv is not None:
                sub = [sv[i] for i in idx]; z = sum(sub) or 1.0
                softs.append([x / z for x in sub])
            else:
                softs.append(None)
        else:
            qs.append(_q(r)); targets.append(r.answer); softs.append(sv)
    logits = model.logits_batch(qs)
    dev = logits[0].device
    losses = []
    for lg, t, sv in zip(logits, targets, softs):
        if sv is not None and len(sv) == lg.shape[0]:
            losses.append(-(torch.tensor(sv, device=dev) * torch.log_softmax(lg.float(), -1)).sum())
        else:
            losses.append(torch.nn.functional.cross_entropy(lg.unsqueeze(0).float(), torch.tensor(t, device=dev).unsqueeze(0)))
    return torch.stack(losses).mean()


@torch.no_grad()
def evaluate(model, recs, bs):
    model.eval()
    rows, correct = [], 0
    for ch in batches(recs, bs):
        for d, r in zip(model.predict_batch([_q(x) for x in ch]), ch):
            hit = int(d.top == r.answer); correct += hit
            rows.append((d.confidence, hit))
    return {"acc": correct / max(len(recs), 1), "ece": _ece(rows), "n": len(recs)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--backbone", default=None)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--val-limit", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--cache-dir", default="data/jsonl")
    ap.add_argument("--shuffle-options", action="store_true",
                    help="augmentation: random option order per example (breaks position shortcut)")
    ap.add_argument("--option-dropout", type=float, default=0.0,
                    help="with --shuffle-options: probability of training on a random option subset (choice tasks, >2 options)")
    ap.add_argument("--render", choices=["v1", "v2"], default="v2",
                    help="input layout; v2 puts options before the (truncatable) item text")
    ap.add_argument("--bf16", action="store_true", help="bf16 autocast for forward/backward (long inputs)")
    ap.add_argument("--soft", action="store_true", help="train on meta['soft'] label distributions where present")
    ap.add_argument("--select", choices=["best", "last"], default="best",
                    help="'best' = keep best val-acc epoch (val is also the reported split: mild selection bias); "
                         "'last' = keep the final epoch (no selection)")
    args = ap.parse_args()

    random.seed(args.seed); torch.manual_seed(args.seed)
    shuf_rng = random.Random(args.seed + 1)
    os.makedirs(args.cache_dir, exist_ok=True)

    tasks = args.tasks.split(",")
    train_recs, val_recs = [], []
    for t in tasks:
        tdir = args.cache_dir
        if "@" in t:                      # e.g. synth@data/synth -> data/synth/synth_{train,val}.jsonl
            t, tdir = t.split("@", 1)
        tr_path = os.path.join(tdir, f"{t}_train.jsonl")
        va_path = os.path.join(tdir, f"{t}_val.jsonl")
        if t == "typed_decisions":
            # Laya/Jev typed-decisions benchmark: many instructions + option sets per case
            from verdict.data_typed import load_typed
            tr = load_typed("train")
            va = load_typed("test")[:args.val_limit or None]
        elif t not in TASKS and os.path.isfile(tr_path):
            # distilled / org-authentic task (scripts/distill.py output): cache is the source
            tr = load_jsonl(tr_path)
            if args.limit:
                tr = tr[:args.limit]
            va = load_jsonl(va_path)[:args.val_limit or None]
        else:
            tr = build_task(t, "train", limit=args.limit, seed=args.seed)
            # some datasets use 'validation' vs 'test'
            try:
                va = build_task(t, "validation", limit=args.val_limit, seed=args.seed)
            except Exception:
                va = build_task(t, "test", limit=args.val_limit, seed=args.seed)
            dump_jsonl(tr, tr_path)
            dump_jsonl(va, va_path)
        bad = lambda r: not (0 <= r.answer < len(r.options)) or len(r.options) < 2
        nbt, nbv = sum(map(bad, tr)), sum(map(bad, va))
        if nbt or nbv:
            print(f"  {t}: dropping {nbt} train / {nbv} val records whose answer is outside their option list", flush=True)
            tr = [r for r in tr if not bad(r)]; va = [r for r in va if not bad(r)]
        train_recs += tr; val_recs += va
        print(f"task {t}: {len(tr)} train / {len(va)} val, {len(TASKS_opts(tr))} classes", flush=True)

    from verdict.model import DEFAULT_BACKBONE
    model = Verdict.from_pretrained(args.backbone or DEFAULT_BACKBONE, render_fmt=args.render)
    dev = next(model.backbone.parameters()).device
    amp = torch.autocast(device_type=dev.type, dtype=torch.bfloat16, enabled=args.bf16 and dev.type == "cuda")
    print(f"device={dev} tasks={tasks} train={len(train_recs)} val={len(val_recs)}", flush=True)

    opt = torch.optim.AdamW(list(model.backbone.parameters()) + list(model.head.parameters()), lr=args.lr)
    best = -1.0
    for ep in range(args.epochs):
        random.shuffle(train_recs)
        model.train(); t0 = time.time(); run = 0.0; step = 0
        for ch in batches(train_recs, args.batch_size):
            opt.zero_grad()
            with amp:
                loss = loss_of(model, ch, args.shuffle_options, shuf_rng, args.option_dropout, args.soft)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(list(model.backbone.parameters()) + list(model.head.parameters()), 1.0)
            opt.step(); step += 1; run += loss.item()
            if step % 50 == 0:
                print(f"e{ep} step{step} loss={run/step:.4f} {step*args.batch_size/(time.time()-t0):.0f} ex/s", flush=True)
        with amp:
            m = evaluate(model, val_recs, args.batch_size)
        print(f"== epoch {ep}: val acc={m['acc']:.4f} ece={m['ece']:.4f} (n={m['n']}) ==", flush=True)
        if args.select == "last" or m["acc"] >= best:
            best = m["acc"]; model.save_pretrained(args.out)
            print(f"   saved {'last' if args.select == 'last' else 'best'} acc={best:.4f} -> {args.out}", flush=True)
    print(f"DONE best_val_acc={best:.4f}", flush=True)


def TASKS_opts(recs):
    return set(tuple(r.options) for r in recs)


if __name__ == "__main__":
    main()
