"""Fine-tune Laya (Apache-2.0) on OrgBench tasks with the SAME splits,
metrics, post-hoc calibration and prediction dumps as Verdict, as a fine-tuned
same-family reference.

The laya package ships inference only, so this drives its own pieces directly:
laya.common.build_sequence (question + options first, state truncated),
collate_items, and agent.model(...) -> per-marker logits; loss = cross-entropy
over the declared options. Evaluation uses raw marker logits (Laya's shipped
temperature is ignored; post-hoc T is fitted per task on the even half of val
and scored on the odd half, exactly as scripts/calibration.py does for Verdict).

It always reports ZERO-SHOT Laya on the same items first (epoch "0-shot"),
then each fine-tuning epoch; the reported fine-tuned number is the LAST epoch
(no selection on the reported split).

  python3 scripts/finetune_laya.py --tasks route_topic,signal_positive,affect \
      --epochs 3 --out RESULTS_laya_ft_public3.md --dump-preds preds_laya_ft_public3.jsonl
  python3 scripts/finetune_laya.py --tasks email_needs_reply,email_escalate,email_priority \
      --cache-dir data/jsonl_org --epochs 3 --out RESULTS_laya_ft_org.md
  python3 scripts/finetune_laya.py --tasks route_intent,signal_positive --epochs 0   # zero-shot only
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict.data import TASKS, build_task, dump_jsonl, load_jsonl  # noqa: E402


def load_split(task, split, cache_dir, limit):
    if task == "typed_decisions":
        from verdict.data_typed import load_typed
        recs = load_typed("train" if split == "train" else "test")
        recs = [r for r in recs if 0 <= r.answer < len(r.options)]
        return recs[:limit] if limit else recs
    path = os.path.join(cache_dir, f"{task}_{split}.jsonl")
    if os.path.isfile(path):
        recs = load_jsonl(path)
    elif task in TASKS:
        try:
            recs = build_task(task, "validation" if split == "val" else split)
        except Exception:
            recs = build_task(task, "test")
        os.makedirs(cache_dir, exist_ok=True); dump_jsonl(recs, path)
    else:
        raise SystemExit(f"no cached split {path}")
    return recs[:limit] if limit else recs


def to_internal(rec):
    """Record -> Laya's internal question. Typed-decisions options arrive as 'key: description'; hand them to
    Laya in its native form (choice: {key: description}; score: [description]; noul: {false/true: description})."""
    import re
    instr = rec.question.split("\n\n", 1)[0]
    def kv(o):
        k, sep, d = o.partition(": ")
        return (k, d) if sep else (o, None)
    if rec.qtype == "noul":
        c = dict(kv(o) for o in rec.options) if all(": " in o for o in rec.options) else None
        return {"t": "noul", "ins": instr, "crit": {k: v for k, v in c.items() if k in ("true", "false")} if c else None}
    if rec.qtype == "score":
        return {"t": "score", "ins": instr, "crit": [re.sub(r"^level \d+: ", "", o) for o in rec.options]}
    pairs = [kv(o) for o in rec.options]
    return {"t": "choice", "ins": instr, "crit": {k: v for k, v in pairs}}


def encode(agent, recs, C):
    max_len = agent.cfg.get("max_len", 512); head = agent.cfg.get("head_max_len", 192)
    items, keep = [], []
    for i, r in enumerate(recs):
        q = to_internal(r)
        seq, markers = C.build_sequence(agent.tok, r.text, q, max_len, head)
        if len(markers) != len(r.options):
            continue
        items.append({"ids": seq, "markers": markers, "qtype": C_QT[q["t"]], "label": r.answer})
        keep.append(i)
    return items, keep


def forward(agent, items, C, dev):
    b = C.collate_items([items], agent.tok.pad_token_id)
    logits, _ = agent.model(b["input_ids"].to(dev), b["attention_mask"].to(dev),
                            b["marker_pos"].to(dev), b["marker_mask"].to(dev), b["qtype"].to(dev))
    logits = logits.float().masked_fill(~b["marker_mask"].to(dev), -1e4)
    return logits, b["label"].to(dev), b["marker_mask"]


def ece10(rows):
    b = [[0, 0, 0.0] for _ in range(10)]
    for c, h in rows:
        k = min(int(c * 10), 9); b[k][0] += 1; b[k][1] += h; b[k][2] += c
    n = len(rows)
    return sum(abs(h / c - cf / c) * c for c, h, cf in b if c) / n if n else float("nan")


def macro_f1(y, p, k):
    f = []
    for c in range(k):
        tp = sum(1 for a, b in zip(y, p) if a == c and b == c)
        fp = sum(1 for a, b in zip(y, p) if a != c and b == c)
        fn = sum(1 for a, b in zip(y, p) if a == c and b != c)
        if tp + fp + fn == 0:
            continue
        pr = tp / (tp + fp) if tp + fp else 0.0; rc = tp / (tp + fn) if tp + fn else 0.0
        f.append(2 * pr * rc / (pr + rc) if pr + rc else 0.0)
    return sum(f) / len(f) if f else 0.0


def fit_T(logit_rows):
    """Scalar temperature by NLL (LBFGS on log T)."""
    logT = torch.zeros(1, requires_grad=True)
    opt = torch.optim.LBFGS([logT], lr=0.1, max_iter=200, line_search_fn="strong_wolfe")
    def nll():
        opt.zero_grad()
        loss = sum(-torch.log_softmax(z / logT.exp(), -1)[y] for z, y in logit_rows) / len(logit_rows)
        loss.backward(); return loss
    opt.step(nll)
    return float(logT.exp().detach())


@torch.no_grad()
def evaluate(agent, recs_by_task, C, dev, bs):
    agent.model.eval()
    out, dump = {}, []
    amp = torch.autocast(device_type=dev.type, dtype=torch.bfloat16, enabled=dev.type == "cuda")
    for task, recs in recs_by_task.items():
        items, keep = encode(agent, recs, C)
        rows = []  # (logits over k options, gold)
        for i in range(0, len(items), bs):
            ch = items[i:i + bs]
            with amp:
                lg, _, mm = forward(agent, ch, C, dev)
            for j, it in enumerate(ch):
                k = len(it["markers"]); rows.append((lg[j, :k].cpu(), it["label"]))
        preds = [int(z.argmax()) for z, _ in rows]; gold = [y for _, y in rows]
        conf = [float(torch.softmax(z, -1).max()) for z, _ in rows]
        hits = [int(p == g) for p, g in zip(preds, gold)]
        T = fit_T(rows[0::2]) if len(rows) > 20 else 1.0
        odd = rows[1::2]
        ph = [(float(torch.softmax(z / T, -1).max()), int(int(z.argmax()) == y)) for z, y in odd]
        ece_raw_odd = ece10([(float(torch.softmax(z, -1).max()), int(int(z.argmax()) == y)) for z, y in odd])
        if task == "typed_decisions":
            from verdict.typed_metrics import summarize
            card = summarize([{"q": torch.softmax(z, -1).tolist(), "p": recs[keep[i]].meta["soft"], "gold": y,
                               "qtype": recs[keep[i]].qtype, "key": (recs[keep[i]].meta["workflow"], recs[keep[i]].meta["question"])}
                              for i, (z, y) in enumerate(rows)])
        else:
            card = None
        out[task] = {"card": card, "n": len(rows), "skipped": len(recs) - len(rows), "acc": sum(hits) / max(len(hits), 1),
                     "macro_f1": macro_f1(gold, preds, len(recs[0].options)), "ece_raw": ece10(list(zip(conf, hits))),
                     "ece_raw_oddhalf": ece_raw_odd, "ece_posthoc_oddhalf": ece10(ph), "T_posthoc": T}
        dump += [{"task": task, "idx": keep[i], "gold": g, "pred": p, "conf": c, "hit": h}
                 for i, (g, p, c, h) in enumerate(zip(gold, preds, conf, hits))]
    n = sum(v["n"] for v in out.values())
    out["overall"] = {"n": n, "acc": sum(v["acc"] * v["n"] for v in out.values()) / max(n, 1),
                      "macro_f1": sum(v["macro_f1"] for k, v in out.items() if k != "overall") / max(len(out), 1)}
    return out, dump


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", required=True)
    ap.add_argument("--cache-dir", default="data/jsonl")
    ap.add_argument("--subfolder", default=None, help="Laya checkpoint subfolder (None = default English model)")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--eval-batch-size", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--limit", type=int, default=20000, help="max train records per task")
    ap.add_argument("--val-limit", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="RESULTS_laya_ft.md")
    ap.add_argument("--dump-preds", default=None)
    ap.add_argument("--save-dir", default=None)
    args = ap.parse_args()
    random.seed(args.seed); torch.manual_seed(args.seed)

    import laya
    import laya.common as C
    global C_QT
    C_QT = laya.QTYPES
    agent = laya.load("convaiinnovations/laya", subfolder=args.subfolder)
    dev = agent.device
    agent.model.float()
    tasks = args.tasks.split(",")
    val = {t: load_split(t, "val", args.cache_dir, args.val_limit) for t in tasks}
    print(f"Laya ckpt={args.subfolder or 'default'} device={dev} tasks={tasks}", flush=True)

    history = []
    res, dump = evaluate(agent, val, C, dev, args.eval_batch_size)
    history.append(("0-shot", res))
    print("0-shot: " + " ".join(f"{t}={res[t]['acc']:.4f}" for t in tasks) + f" overall={res['overall']['acc']:.4f}", flush=True)

    if args.epochs > 0:
        train = []
        for t in tasks:
            tr = load_split(t, "train", args.cache_dir, args.limit)
            items, _ = encode(agent, tr, C)
            train += items
            print(f"  {t}: {len(items)}/{len(tr)} train items encoded", flush=True)
        opt = torch.optim.AdamW(agent.model.parameters(), lr=args.lr, weight_decay=0.01)
        steps = math.ceil(len(train) / args.batch_size) * args.epochs
        sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / max(1, int(0.06 * steps))) * max(0.0, (steps - s) / steps))
        amp = torch.autocast(device_type=dev.type, dtype=torch.bfloat16, enabled=dev.type == "cuda")
        for ep in range(args.epochs):
            random.shuffle(train); agent.model.train(); t0 = time.time(); run = 0.0
            for i in range(0, len(train), args.batch_size):
                ch = train[i:i + args.batch_size]
                with amp:
                    lg, y, _ = forward(agent, ch, C, dev)
                loss = torch.nn.functional.cross_entropy(lg, y)
                opt.zero_grad(); loss.backward()
                torch.nn.utils.clip_grad_norm_(agent.model.parameters(), 1.0)
                opt.step(); sched.step(); run += loss.item()
                s = i // args.batch_size + 1
                if s % 200 == 0:
                    print(f"  e{ep} step{s} loss={run/s:.4f} {s*args.batch_size/(time.time()-t0):.0f} ex/s", flush=True)
            res, dump = evaluate(agent, val, C, dev, args.eval_batch_size)
            history.append((f"ft-epoch{ep}", res))
            print(f"epoch {ep}: " + " ".join(f"{t}={res[t]['acc']:.4f}" for t in tasks) + f" overall={res['overall']['acc']:.4f} ({time.time()-t0:.0f}s)", flush=True)
        if args.save_dir:
            os.makedirs(args.save_dir, exist_ok=True)
            torch.save(agent.model.state_dict(), os.path.join(args.save_dir, "laya_ft_state_dict.pt"))

    final_name, final = history[-1]
    md = [f"# Laya ({args.subfolder or 'default English'} checkpoint) on {', '.join(tasks)} — cache `{args.cache_dir}`", "",
          f"Reported row = **{final_name}** (last epoch, no selection). Raw marker logits; post-hoc T fit on even half of val, ECE on odd half.", "",
          "| stage | " + " | ".join(tasks) + " | overall |", "|---|" + "---|" * (len(tasks) + 1)]
    for name, r in history:
        md.append(f"| {name} | " + " | ".join(f"{r[t]['acc']*100:.1f}%" for t in tasks) + f" | {r['overall']['acc']*100:.1f}% |")
    md += ["", "| task | n | skipped | acc | macro-F1 | ECE raw | ECE raw (odd half) | ECE post-hoc (odd half) | T |", "|---|---|---|---|---|---|---|---|---|"]
    for t in tasks:
        v = final[t]
        md.append(f"| {t} | {v['n']} | {v['skipped']} | {v['acc']*100:.1f}% | {v['macro_f1']*100:.1f}% | {v['ece_raw']:.4f} | "
                  f"{v['ece_raw_oddhalf']:.4f} | {v['ece_posthoc_oddhalf']:.4f} | {v['T_posthoc']:.3f} |")
    if "typed_decisions" in tasks and final["typed_decisions"].get("card"):
        from verdict.typed_metrics import MD_HEADER, md_row
        md += ["", "typed-decisions card metrics (reported stage):", *MD_HEADER,
               md_row(f"Laya ({args.subfolder or 'default'}) {final_name}", "specialist", final["typed_decisions"]["card"])]
    open(args.out, "w").write("\n".join(md) + "\n")
    json.dump({"history": history}, open(args.out.rsplit(".", 1)[0] + ".json", "w"), indent=2)
    if args.dump_preds:
        with open(args.dump_preds, "w") as f:
            for row in dump:
                f.write(json.dumps(row) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
