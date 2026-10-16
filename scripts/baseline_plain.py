"""Baseline: a PLAIN ModernBERT-base sequence-classification head on the
identical OrgBench tasks/splits — the ablation that tests whether Verdict's
option-marker head + joint normalization adds anything over a standard
fine-tuned ModernBERT classifier.

For each task we fine-tune a standard AutoModelForSequenceClassification (one
fixed-label head per task, num_labels = #options) on the SAME cached splits
Verdict used, same seed, and report accuracy / macro-F1 / ECE. Compare per-task
to Verdict (scripts/eval_orgbench.py). The criterion for Verdict: it matches or
exceeds this on accuracy AND is materially better calibrated / handles arbitrary
option sets in one shared model (which this per-task baseline cannot).

  python3 scripts/baseline_plain.py --tasks route_topic,signal_positive,affect \
      --epochs 3 --batch-size 32 --out RESULTS_plain.md
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict.data import load_jsonl  # noqa: E402

BACKBONE = "answerdotai/ModernBERT-base"


def _ece(confs, hits, nb=10):
    b = [[0, 0, 0.0] for _ in range(nb)]
    for c, h in zip(confs, hits):
        k = min(int(c * nb), nb - 1)
        b[k][0] += 1; b[k][1] += h; b[k][2] += c
    n = len(confs)
    return sum(abs(h / c - cf / c) * c for c, h, cf in b if c) / max(n, 1) if n else 0.0


def _macro_f1(preds, golds, k):
    f1s = []
    for c in range(k):
        tp = sum(1 for p, g in zip(preds, golds) if p == c and g == c)
        fp = sum(1 for p, g in zip(preds, golds) if p == c and g != c)
        fn = sum(1 for p, g in zip(preds, golds) if p != c and g == c)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1s.append(2 * prec * rec / (prec + rec) if prec + rec else 0.0)
    return sum(f1s) / len(f1s) if f1s else 0.0


def run_task(task, cache_dir, epochs, bs, lr, seed, device):
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    train = load_jsonl(os.path.join(cache_dir, f"{task}_train.jsonl"))
    val = load_jsonl(os.path.join(cache_dir, f"{task}_val.jsonl"))
    k = len(train[0].options)
    tok = AutoTokenizer.from_pretrained(BACKBONE)
    model = AutoModelForSequenceClassification.from_pretrained(BACKBONE, num_labels=k).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr)

    def enc(recs):
        return tok([r.question for r in recs], return_tensors="pt", padding=True,
                   truncation=True, max_length=512).to(device)

    random.Random(seed).shuffle(train)
    model.train()
    for ep in range(epochs):
        random.Random(seed + ep).shuffle(train)
        for i in range(0, len(train), bs):
            ch = train[i:i + bs]
            opt.zero_grad()
            out = model(**enc(ch), labels=torch.tensor([r.answer for r in ch], device=device))
            out.loss.backward(); opt.step()

    model.eval()
    preds, golds, confs, hits = [], [], [], []
    with torch.no_grad():
        for i in range(0, len(val), bs):
            ch = val[i:i + bs]
            probs = torch.softmax(model(**enc(ch)).logits.float(), dim=-1)
            conf, pred = probs.max(dim=-1)
            for j, r in enumerate(ch):
                p = int(pred[j]); preds.append(p); golds.append(r.answer)
                hits.append(int(p == r.answer)); confs.append(float(conf[j]))
    acc = sum(hits) / max(len(hits), 1)
    return {"acc": acc, "macro_f1": _macro_f1(preds, golds, k),
            "ece": _ece(confs, hits), "n": len(val), "k": k}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", required=True)
    ap.add_argument("--cache-dir", default="data/jsonl")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="RESULTS_plain.md")
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    lines = [f"# R1 plain-classifier baseline — {BACKBONE} (per-task seq-classification head)", "",
             "| task | plain acc | plain macro-F1 | plain ECE | n |", "|---|---|---|---|---|"]
    res = {}
    for task in args.tasks.split(","):
        t0 = time.time()
        r = run_task(task, args.cache_dir, args.epochs, args.batch_size, args.lr, args.seed, device)
        res[task] = r
        lines.append(f"| {task} | {r['acc']*100:.1f}% | {r['macro_f1']*100:.1f}% | {r['ece']:.3f} | {r['n']} |")
        print(f"{task}: acc={r['acc']:.4f} f1={r['macro_f1']:.4f} ece={r['ece']:.4f} ({time.time()-t0:.0f}s)", flush=True)
    ov = sum(res[t]["acc"] * res[t]["n"] for t in res) / sum(res[t]["n"] for t in res)
    lines += ["", f"**Plain-head overall (n-weighted): {ov*100:.1f}%.** Compare per-task to Verdict "
              "(eval_orgbench.py); criterion: Verdict matches or exceeds this AND is better "
              "calibrated with ONE shared model over arbitrary option sets."]
    open(args.out, "w").write("\n".join(lines))
    json.dump(res, open(args.out.replace(".md", ".json"), "w"), indent=2)
    print("\n".join(lines), flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
