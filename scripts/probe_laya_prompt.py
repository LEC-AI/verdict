"""R5 debug: Laya zero-shot prompt sensitivity on signal_positive (sst2).
Laya returned P(yes) < 0.2 for nearly every item under the OrgBench prompt
(acc = 50% = share of negatives). This probe re-asks the same items under
several instruction paraphrases and reports acc / mean P(yes) / fraction "yes".

  python3 scripts/probe_laya_prompt.py --limit 100
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict.data import load_jsonl  # noqa: E402

VARIANTS = [
    "Is the sender's sentiment in this message positive?",
    "Is this movie review positive?",
    "Does the following text express a positive opinion?",
    "Is the sentiment of this sentence positive (yes) or negative (no)?",
    "Would the author recommend this film?",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="signal_positive")
    ap.add_argument("--cache-dir", default="data/jsonl")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--device", default=None)
    ap.add_argument("--out", default="RESULTS_laya_prompt_probe.md")
    args = ap.parse_args()
    import laya
    agent = laya.load("convaiinnovations/laya", subfolder="typed-decisions", device=args.device)
    recs = load_jsonl(os.path.join(args.cache_dir, f"{args.task}_val.jsonl"))[: args.limit]
    lines = [f"# Laya zero-shot prompt sensitivity — {args.task}, n={len(recs)}", "",
             "| instruction | acc | mean P(yes) | frac predicted yes |", "|---|---|---|---|"]
    for v in VARIANTS:
        ps = [float(agent.predict(r.text, {"q": {"type": "noul", "instructions": v}})["answers"]["q"]["noul"]) for r in recs]
        acc = sum(int((p >= 0.5) == (r.answer == 1)) for p, r in zip(ps, recs)) / len(recs)
        line = f"| {v} | {acc*100:.1f}% | {sum(ps)/len(ps):.3f} | {sum(p >= 0.5 for p in ps)/len(ps):.2f} |"
        lines.append(line); print(line, flush=True)
    gold_yes = sum(r.answer == 1 for r in recs) / len(recs)
    lines += ["", f"Gold fraction yes: {gold_yes:.2f}."]
    open(args.out, "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
