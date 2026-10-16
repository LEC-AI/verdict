"""Measure Laya (open, released by Convai Innovations) on standard, peer-reviewed benchmarks (RACE, BoolQ, MultiRC),
using the EXACT SAME records, instructions, option wording and case grouping as our own Verdict-MQ and the matched
baselines (verdict.mq_data.load_split + to_cases) -- a real, controlled comparison on established benchmarks, not
the niche typed-decisions benchmark Laya's own card is built around. Mirrors scripts/eval_jev_std.py. Written 2026-09-25.

  python3 scripts/eval_laya_std.py --task race --limit 20 --out /tmp/laya_race_pilot.md   # pilot
  python3 scripts/eval_laya_std.py --task race --out RESULTS_laya_race.md --dump-preds preds_laya_race.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict.mq_data import item_key, load_split, to_cases  # noqa: E402
sys.path.insert(0, os.path.dirname(__file__))
from _std_to_typed import build_questions  # noqa: E402


def macro_f1(y, p):
    labels = sorted(set(y) | set(p)); f1s = []
    for c in labels:
        tp = sum(1 for a, b in zip(y, p) if a == c and b == c); fp = sum(1 for a, b in zip(y, p) if a != c and b == c)
        fn = sum(1 for a, b in zip(y, p) if a == c and b != c)
        f1s.append(2 * tp / max(2 * tp + fp + fn, 1))
    return sum(f1s) / len(f1s)


def ece10(rows):
    b = [[0, 0, 0.0] for _ in range(10)]
    for c, h in rows:
        k = min(int(c * 10), 9); b[k][0] += 1; b[k][1] += h; b[k][2] += c
    n = len(rows)
    return sum(abs(h / c - cf / c) * c for c, h, cf in b if c) / n if n else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, choices=["race", "boolq", "multirc", "phishing"])
    ap.add_argument("--cache-dir", default="data/jsonl")
    ap.add_argument("--subfolder", default="default", help="Laya checkpoint subfolder: 'default' (general, not fitted on any of these tasks) is the fair comparison here, not the typed-decisions specialist")
    ap.add_argument("--device", default=None)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dump-preds", default=None)
    a = ap.parse_args()

    import laya
    agent = laya.load("convaiinnovations/laya", subfolder=None if a.subfolder in ("", "none", "default") else a.subfolder, device=a.device)

    recs = load_split(a.task, "test", a.cache_dir)
    cases = to_cases(recs)
    if a.limit:
        cases = cases[:a.limit]

    y, pr, rows, dump, errors, t0 = [], [], [], [], [], time.time()
    for i, (case, crecs) in enumerate(cases):
        payload = build_questions(case, bool_type="noul")
        try:
            ans = agent.predict(case.state, payload)["answers"]
        except Exception as e:
            errors.append(f"case {i}: {e}"); continue
        for j, (q, r) in enumerate(zip(case.questions, crecs)):
            qname = f"q{j}"; a_ = ans.get(qname)
            if a_ is None:
                errors.append(f"case {i} missing {qname}"); continue
            n_opt = len(q.options)
            if q.qtype == "noul":
                p1 = float(a_.get("noul", a_.get("probability", 0.5))); probs = [1 - p1, p1]
            else:
                pd = a_.get("probabilities", {}); probs = [float(pd.get(str(k), 0.0)) for k in range(n_opt)]
            s = sum(probs) or 1.0; probs = [x / s for x in probs]
            top = max(range(n_opt), key=probs.__getitem__)
            y.append(r.answer); pr.append(top)
            hit = int(top == r.answer)
            rows.append((max(probs), hit))
            dump.append({"task": a.task, "idx": item_key(r), "gold": r.answer, "pred": top, "conf": max(probs), "hit": hit, "probs": probs})
        if (i + 1) % 100 == 0:
            acc_so_far = sum(int(u == v) for u, v in zip(y, pr)) / max(len(y), 1)
            print(f"  {i+1}/{len(cases)} cases, {len(y)} decisions, acc so far {acc_so_far:.3f}, {len(errors)} errors", flush=True)

    acc = sum(int(u == v) for u, v in zip(y, pr)) / max(len(y), 1)
    md = [f"# Laya ({a.subfolder}) on {a.task.upper()} TEST -- measured by us, same records/instructions/case-grouping as Verdict-MQ", "",
          f"accuracy **{acc*100:.2f}%** (n={len(y)} decisions, {len(cases)} cases attempted, {len(errors)} errors), "
          f"macro-F1 {macro_f1(y, pr)*100:.1f}, ECE-10 {ece10(rows):.4f}, {time.time()-t0:.0f}s"]
    if errors:
        md += ["", f"**{len(errors)} errors** (first 5): " + "; ".join(str(e) for e in errors[:5])]
    open(a.out, "w").write("\n".join(md) + "\n")
    json.dump({"acc": acc, "macro_f1": macro_f1(y, pr), "ece": ece10(rows), "n": len(y), "n_errors": len(errors)},
              open(a.out.rsplit(".", 1)[0] + ".json", "w"), indent=2)
    if a.dump_preds:
        with open(a.dump_preds, "w") as f:
            for r in dump:
                f.write(json.dumps(r) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
