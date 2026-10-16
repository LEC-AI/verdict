"""Evaluate any Verdict checkpoint on the typed-decisions TEST split (2,000
decisions), with the same metrics as scripts/train_typed.py. Optional
--permute-options re-scores every decision with a random option order.

  python3 scripts/eval_typed.py --ckpt out/verdict-mix --out RESULTS_typed_mix.md --permute-options
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict import Choice, Verdict  # noqa: E402
from verdict.data_typed import load_typed  # noqa: E402
from scripts.train_typed import _q, batches, evaluate  # noqa: E402
from verdict.typed_metrics import MD_HEADER, md_row, summarize  # noqa: E402


@torch.no_grad()
def card_metrics(model, recs, bs):
    rows = []
    for ch in batches(recs, bs):
        for d, r in zip(model.predict_batch([_q(x) for x in ch]), ch):
            if len(d.probs) != len(r.options) or not (0 <= r.answer < len(r.options)):
                continue
            rows.append({"q": list(d.probs), "p": list(r.meta["soft"]), "gold": r.answer, "qtype": r.qtype,
                         "key": (r.meta["workflow"], r.meta["question"])})
    return summarize(rows)


@torch.no_grad()
def permuted_acc(model, recs, bs, seed=0):
    rng = random.Random(seed); hits = 0
    for ch in batches(recs, bs):
        qs, perms = [], []
        for r in ch:
            p = list(range(len(r.options))); rng.shuffle(p)
            qs.append(Choice(r.question, [r.options[i] for i in p])); perms.append(p)
        for d, p, r in zip(model.predict_batch(qs), perms, ch):
            hits += int(p[d.top] == r.answer)
    return hits / max(len(recs), 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--permute-options", action="store_true")
    ap.add_argument("--out", default="RESULTS_typed_eval.md")
    ap.add_argument("--bare-options", action="store_true")
    ap.add_argument("--split", default="test", choices=["test", "train"],
                    help="'train' = development split for GENERALIST models (never trained on); keep 'test' for final numbers")
    a = ap.parse_args()
    model = Verdict.from_pretrained(a.ckpt)
    test = load_typed(a.split, describe=not a.bare_options)
    m = evaluate(model, test, a.batch_size)
    m["card"] = card_metrics(model, test, a.batch_size)
    if a.permute_options:
        m["permuted_overall"] = permuted_acc(model, test, a.batch_size)
    md = [f"# typed-decisions {a.split.upper()} — {a.ckpt}", "",
          f"overall **{m['overall']*100:.1f}%** (n={m['n']}), ECE {m['ece']:.3f}"
          + (f", option-permuted {m['permuted_overall']*100:.1f}%" if a.permute_options else ""), "",
          "by primitive: " + ", ".join(f"{k} {v*100:.1f}%" for k, v in m["by_primitive"].items()),
          "by workflow: " + ", ".join(f"{k} {v*100:.1f}%" for k, v in m["by_workflow"].items()),
          "", *MD_HEADER, md_row(os.path.basename(a.ckpt.rstrip("/")), "specialist (trained on these workflows)", m["card"]),
          "| ModernBERT-base (card) | specialist | 0.646 | 0.542 | 0.469 | 0.223 | 0.249 | 0.119 | 0.179 | 0.444 | 0.931 |",
          "| TypeSafe Jev 1.13.0 (card) | general | 0.727 | 0.580 | 0.613 | 1.442 | 0.251 | 0.148 | 0.144 | 0.391 | 0.952 |",
          "| meraGPT Decider 1 (card) | general | 0.768 | 0.608 | 0.641 | 0.096 | 0.149 | 0.052 | 0.180 | 0.219 | 0.984 |",
          "", "Card ceilings: perfect scenario understanding 0.704, teacher self-agreement 0.735. "
              "KL/TV/Brier definitions reproduce the card's Uniform row exactly; ECE/Prior use unstated card choices."]
    open(a.out, "w").write("\n".join(md) + "\n")
    json.dump(m, open(a.out.rsplit(".", 1)[0] + ".json", "w"), indent=2)
    print("\n".join(md))


if __name__ == "__main__":
    main()
