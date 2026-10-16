"""Benchmark Laya (convaiinnovations/laya) on OrgBench — the direct same-family
comparator (Laya is the reference System-1 typed-decision model; ModernBERT-large
backbone). Zero-shot: Laya is a general typed-decision engine, so this answers
"does an off-the-shelf decision model handle org decisions, or must you
specialize?" (Verdict is specialized on OrgBench.)

  python3 scripts/eval_laya.py --tasks route_topic,signal_positive,affect \
      --subfolder typed-decisions --limit 200 --out RESULTS_laya.md

Maps each OrgBench Record to a Laya typed question:
  choice -> {type:choice, instructions, criteria={option:option}}
  noul   -> {type:noul,   instructions}
  score  -> {type:score,  instructions, criteria=[level,...]}
and compares Laya's answer to the gold label. Reports per-task + overall
accuracy, ECE where Laya exposes a probability, and latency.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict.data import load_jsonl  # noqa: E402


def _instr_and_state(rec):
    # rec.question is "<prompt>\n\n<text>"; give Laya the prompt as instructions
    # and the raw item as state.
    parts = rec.question.split("\n\n", 1)
    instr = parts[0]
    state = rec.text if rec.text else (parts[1] if len(parts) > 1 else rec.question)
    return instr, state


def _ece(rows, nb=10):
    b = [[0, 0, 0.0] for _ in range(nb)]
    for c, h in rows:
        k = min(int(c * nb), nb - 1)
        b[k][0] += 1; b[k][1] += h; b[k][2] += c
    n = len(rows)
    return sum(abs(h / c - cf / c) * c for c, h, cf in b if c) / max(n, 1) if n else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", required=True)
    ap.add_argument("--cache-dir", default="data/jsonl")
    ap.add_argument("--subfolder", default="typed-decisions")
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--out", default="RESULTS_laya.md")
    ap.add_argument("--dump-preds", default=None, help="per-item JSONL (task, idx, gold, pred, conf, hit) for significance.py")
    args = ap.parse_args()
    dump = open(args.dump_preds, "w") if args.dump_preds else None

    import laya
    try:
        agent = laya.load("convaiinnovations/laya", subfolder=args.subfolder)
    except Exception:
        agent = laya.load("convaiinnovations/laya")  # fall back to root ckpt

    lines = [f"# Laya baseline — convaiinnovations/laya ({args.subfolder}, zero-shot)", ""]
    overall_c = overall_n = 0
    lat_all, per_task = [], {}
    for task in args.tasks.split(","):
        recs = load_jsonl(os.path.join(args.cache_dir, f"{task}_val.jsonl"))[: args.limit]
        c, n, lat, ece_rows, err = 0, 0, [], [], 0
        for idx, r in enumerate(recs):
            instr, state = _instr_and_state(r)
            if r.qtype == "noul":
                q = {"q": {"type": "noul", "instructions": instr}}
            elif r.qtype == "score":
                q = {"q": {"type": "score", "instructions": instr, "criteria": list(r.options)}}
            else:
                q = {"q": {"type": "choice", "instructions": instr,
                           "criteria": {o: o for o in r.options}}}
            t0 = time.perf_counter()
            try:
                res = agent.predict(state, q)
                ans = res["answers"]["q"]
            except Exception as e:
                err += 1; n += 1
                if err <= 3:
                    print(f"  [{task}] predict error: {e}", flush=True)
                continue
            lat.append(time.perf_counter() - t0)
            pred, conf = -1, None
            if r.qtype == "noul":
                p = float(ans.get("noul", 0.0)); pred = 1 if p >= 0.5 else 0
                conf = p if pred == 1 else 1 - p
            elif r.qtype == "score":
                s = float(ans.get("score", 0.0)); pred = max(0, min(len(r.options) - 1, round(s)))
            else:
                chosen = ans.get("choice")
                pred = r.options.index(chosen) if chosen in r.options else -1
                conf = ans.get("confidence") or ans.get("prob")
            hit = int(pred == r.answer); c += hit; n += 1
            if dump:
                dump.write(json.dumps({"task": task, "idx": idx, "gold": r.answer, "pred": pred,
                                       "conf": (float(conf) if conf is not None else None), "hit": hit}) + "\n")
            if conf is not None:
                ece_rows.append((float(conf), hit))
        acc = c / max(n, 1)
        mlat = 1000 * sum(lat) / len(lat) if lat else 0
        per_task[task] = (acc, n, mlat, _ece(ece_rows) if ece_rows else None, err)
        overall_c += c; overall_n += n; lat_all += lat
        print(f"{task}: acc={acc:.4f} n={n} lat={mlat:.0f}ms err={err}", flush=True)

    lines += ["| task | acc | n | ECE | mean latency (ms) |", "|---|---|---|---|---|"]
    for t, (acc, n, mlat, ece, err) in per_task.items():
        lines.append(f"| {t} | {acc*100:.1f}% | {n} | {ece:.3f}" if ece is not None
                     else f"| {t} | {acc*100:.1f}% | {n} | n/a")
        lines[-1] += f" | {mlat:.0f} |"
    lat_all.sort()
    lines += ["", f"**Overall:** {overall_c/max(overall_n,1)*100:.1f}% (n={overall_n}), "
              f"mean latency {1000*sum(lat_all)/len(lat_all):.0f} ms/decision" if lat_all else "**Overall:** n/a"]
    open(args.out, "w").write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
