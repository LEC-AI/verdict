"""Measure Jev (TypeSafe AI) on standard, peer-reviewed benchmarks (RACE, BoolQ, MultiRC) via Vercel AI Gateway,
using the EXACT SAME records, instructions, option wording and case grouping as our own Verdict-MQ and the matched
baselines (verdict.mq_data.load_split + to_cases) -- a real, controlled comparison on established benchmarks, not
the niche typed-decisions benchmark Jev's own card is built around. Written 2026-09-25.

Jev batches all of one case's questions into a single call (same "encode once, decide many" case-level test as our
own model), so cost and latency are directly comparable to Verdict-MQ's packed numbers, not just accuracy.

  python3 scripts/eval_jev_std.py --task race --limit 20 --out /tmp/jev_race_pilot.md   # pilot
  python3 scripts/eval_jev_std.py --task race --out RESULTS_jev_race.md --dump-preds preds_jev_race.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict.mq_data import item_key, load_split, to_cases  # noqa: E402
sys.path.insert(0, os.path.dirname(__file__))
from _std_to_typed import build_questions  # noqa: E402

GATEWAY = "https://ai-gateway.vercel.sh/v1/evaluate"
KEY_FILE = os.path.expanduser("~/.config/verdict/vercel_ai_gateway.key")


def call_jev(key, state, questions, retries=6):
    for attempt in range(retries):
        r = requests.post(GATEWAY, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                          json={"model": "typesafe-ai/jev", "state": state, "questions": questions}, timeout=60)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429, 500, 502, 503, 504) and attempt < retries - 1:
            time.sleep(min(2 ** attempt * 2, 30)); continue
        raise RuntimeError(f"Jev call failed ({r.status_code}): {r.text[:300]}")
    raise RuntimeError("Jev call failed: retries exhausted")


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
    ap.add_argument("--limit", type=int, default=0, help="pilot mode: only this many cases")
    ap.add_argument("--sleep", type=float, default=0.3)
    ap.add_argument("--workers", type=int, default=1, help="concurrent requests (each still retries/backs off on 429/5xx)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--dump-preds", default=None)
    a = ap.parse_args()
    if not os.path.isfile(KEY_FILE):
        raise SystemExit(f"no Vercel AI Gateway key at {KEY_FILE}")
    key = open(KEY_FILE).read().strip()

    recs = load_split(a.task, "test", a.cache_dir)
    cases = to_cases(recs)
    if a.limit:
        cases = cases[:a.limit]

    y, pr, rows, dump, errors, t0 = [], [], [], [], [], time.time()
    lock = threading.Lock()
    done_n = [0]
    lat = []

    def process_one(i, case, crecs):
        payload = build_questions(case)
        t_call = time.perf_counter()
        try:
            resp = call_jev(key, case.state, payload)
        except Exception as e:
            return i, str(e), []
        with lock:  # per-call latency: excludes the inter-call --sleep; still includes call_jev's retry backoff
            lat.append(time.perf_counter() - t_call)
        ans = resp.get("answers", {})
        out = []
        for j, (q, r) in enumerate(zip(case.questions, crecs)):
            qname = f"q{j}"; a_ = ans.get(qname)
            if a_ is None:
                out.append(("err", f"case {i} missing {qname}")); continue
            n_opt = len(q.options)
            if q.qtype == "noul":
                p1 = float(a_.get("probability", 0.5)); probs = [1 - p1, p1]
            else:
                pd = a_.get("probabilities", {}); probs = [float(pd.get(str(k), 0.0)) for k in range(n_opt)]
            s = sum(probs) or 1.0; probs = [x / s for x in probs]
            top = max(range(n_opt), key=probs.__getitem__)
            hit = int(top == r.answer)
            out.append(("ok", {"task": a.task, "idx": item_key(r), "gold": r.answer, "pred": top, "conf": max(probs), "hit": hit, "probs": probs}))
        return i, None, out

    def consume(i, err, out):
        if err:
            errors.append(err)
        for kind, val in out:
            if kind == "err":
                errors.append(val); continue
            dump.append(val); y.append(val["gold"]); pr.append(val["pred"]); rows.append((val["conf"], val["hit"]))
        with lock:
            done_n[0] += 1
            if done_n[0] % 25 == 0:
                acc_so_far = sum(int(u == v) for u, v in zip(y, pr)) / max(len(y), 1)
                print(f"  {done_n[0]}/{len(cases)} cases, {len(y)} decisions, acc so far {acc_so_far:.3f}, {len(errors)} errors", flush=True)

    if a.workers <= 1:
        for i, (case, crecs) in enumerate(cases):
            consume(*process_one(i, case, crecs)); time.sleep(a.sleep)
    else:
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            futs = [ex.submit(process_one, i, case, crecs) for i, (case, crecs) in enumerate(cases)]
            for f in as_completed(futs):
                consume(*f.result())

    acc = sum(int(u == v) for u, v in zip(y, pr)) / max(len(y), 1)
    md = [f"# Jev (TypeSafe AI, typesafe-ai/jev) on {a.task.upper()} TEST -- measured via Vercel AI Gateway, "
          "same records/instructions/case-grouping as Verdict-MQ", "",
          f"accuracy **{acc*100:.2f}%** (n={len(y)} decisions, {len(cases)} cases attempted, {len(errors)} errors), "
          f"macro-F1 {macro_f1(y, pr)*100:.1f}, ECE-10 {ece10(rows):.4f}, {time.time()-t0:.0f}s wall-clock "
          f"(includes the --sleep between calls; per-call latency excluding it: median "
          f"{statistics.median(lat) if lat else float('nan'):.3f}s, mean {statistics.mean(lat) if lat else float('nan'):.3f}s)"]
    if errors:
        md += ["", f"**{len(errors)} errors** (first 5): " + "; ".join(errors[:5])]
    open(a.out, "w").write("\n".join(md) + "\n")
    json.dump({"acc": acc, "macro_f1": macro_f1(y, pr), "ece": ece10(rows), "n": len(y), "n_errors": len(errors),
               "latency_median_s": statistics.median(lat) if lat else None, "latency_mean_s": statistics.mean(lat) if lat else None},
              open(a.out.rsplit(".", 1)[0] + ".json", "w"), indent=2)
    if a.dump_preds:
        with open(a.dump_preds, "w") as f:
            for r in dump:
                f.write(json.dumps(r) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
