"""Per-task diagnostic: confusion matrix, per-class accuracy, confidence
histogram, and sample errors for one OrgBench task on a Verdict checkpoint.
Used to explain anomalies (e.g. signal_positive/sst2 at 77.8%).

    python scripts/diag_task.py --ckpt out/verdict-base --task signal_positive
"""
from __future__ import annotations

import argparse
import collections
import os
import sys

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict import Verdict  # noqa: E402
from verdict.model import render  # noqa: E402
from scripts.eval_orgbench import _q, batches, load_val  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="out/verdict-base")
    ap.add_argument("--task", required=True)
    ap.add_argument("--cache-dir", default="data/jsonl")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--errors", type=int, default=12)
    a = ap.parse_args()

    recs = load_val(a.task, a.cache_dir, a.limit)
    model = Verdict.from_pretrained(a.ckpt)
    opts = recs[0].options
    n = len(opts)
    print(f"task={a.task} n={len(recs)} options={opts}")
    print("--- rendered example ---")
    print(render(_q(recs[0])))
    print("------------------------")
    gold = collections.Counter(r.answer for r in recs)
    print("gold distribution:", {opts[k]: v for k, v in sorted(gold.items())})

    conf = [[0] * n for _ in range(n)]
    hist = collections.Counter()
    errs = []
    lens = []
    with torch.no_grad():
        for ch in batches(recs, a.batch_size):
            for d, r in zip(model.predict_batch([_q(x) for x in ch]), ch):
                conf[r.answer][d.top] += 1
                hist[int(d.confidence * 10) / 10] += 1
                lens.append(len(r.text.split()))
                if d.top != r.answer and len(errs) < a.errors:
                    errs.append((r.text[:160], opts[r.answer], opts[d.top], d.confidence))
    print("confusion (rows=gold, cols=pred):")
    print("        " + " ".join(f"{o[:8]:>8}" for o in opts))
    for i in range(n):
        print(f"{opts[i][:8]:>8}" + " ".join(f"{c:>8}" for c in conf[i]))
    print("per-class recall:", {opts[i]: round(conf[i][i] / max(sum(conf[i]), 1), 3) for i in range(n)})
    pred = collections.Counter()
    for i in range(n):
        for j in range(n):
            pred[opts[j]] += conf[i][j]
    print("pred distribution:", dict(pred))
    print("confidence histogram:", dict(sorted(hist.items())))
    print(f"mean text length (words): {sum(lens)/len(lens):.1f}")
    print("--- sample errors (text | gold -> pred @conf) ---")
    for t, g, p, c in errs:
        print(f"{t!r} | {g} -> {p} @{c:.2f}")


if __name__ == "__main__":
    main()
