"""LLM-judge baseline on OrgBench: run the SAME typed-decision questions through
an instruct LLM (via an OpenAI-compatible endpoint, e.g. local ollama) and
measure accuracy + latency. This is the paper's parity comparison: Verdict
(150M, ms, calibrated) vs a mid-size LLM (billions of params, seconds,
uncalibrated).

  python3 scripts/eval_baseline.py --tasks route_topic,signal_positive,affect \
      --endpoint http://localhost:11434/v1 --model qwen2.5:7b-instruct --limit 400

Reports per-task + overall accuracy and mean/p50 latency per decision. The LLM
is asked to answer with ONLY the option index (greedy, temperature 0). Answers
that don't parse to a valid index count as wrong (and are logged), since an
unparseable decision is unusable downstream.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict.data import load_jsonl  # noqa: E402


def render_prompt(rec, shots=()) -> str:
    """Zero-shot by default; `shots` = labeled train Records prepended as worked examples
    (R5 few-shot judge). Same option list and answer format for every example."""
    opts = "\n".join(f"{i}: {o}" for i, o in enumerate(rec.options))
    head = rec.question.split("\n\n", 1)[0]
    demo = ""
    if shots:
        demo = "Here are labeled examples of this decision.\n\n" + "\n\n".join(
            f"Item: {s.text[:600]}\nAnswer: {s.answer}" for s in shots) + "\n\nNow decide the next item.\n\n"
    return (f"{head}\n\nOptions:\n{opts}\n\n{demo}Item: {rec.text}\n\n"
            f"Answer with ONLY the number of the single best option (0-{len(rec.options)-1}). "
            f"No words, just the number.")


def pick_shots(train_recs, k):
    """k examples per task, round-robin over classes (balanced), deterministic."""
    by_cls = {}
    for r in train_recs:
        by_cls.setdefault(r.answer, []).append(r)
    out, i = [], 0
    while len(out) < k and any(by_cls.values()):
        for c in sorted(by_cls):
            if by_cls[c] and len(out) < k:
                out.append(by_cls[c].pop(0))
        i += 1
    return out


def query(endpoint, model, prompt, timeout=60):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0, "max_tokens": 8,
    }).encode()
    req = urllib.request.Request(endpoint.rstrip("/") + "/chat/completions",
                                 data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        out = json.loads(r.read())
    return out["choices"][0]["message"]["content"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", required=True)
    ap.add_argument("--endpoint", default="http://localhost:11434/v1")
    ap.add_argument("--model", default="qwen2.5:7b-instruct")
    ap.add_argument("--cache-dir", default="data/jsonl")
    ap.add_argument("--limit", type=int, default=400)
    ap.add_argument("--out", default="RESULTS_baseline.md")
    ap.add_argument("--dump-preds", default=None, help="per-item JSONL (task, idx, gold, pred, hit) for significance.py")
    ap.add_argument("--few-shot", type=int, default=0, help="prepend K balanced labeled train examples per task (0 = zero-shot)")
    args = ap.parse_args()
    dump = open(args.dump_preds, "w") if args.dump_preds else None

    lines = [f"# LLM-judge baseline — {args.model}" + (f" ({args.few_shot}-shot)" if args.few_shot else " (zero-shot)"), ""]
    overall_correct = overall_n = 0
    lat_all = []
    per_task = {}
    for task in args.tasks.split(","):
        recs = load_jsonl(os.path.join(args.cache_dir, f"{task}_val.jsonl"))[: args.limit]
        shots = pick_shots(load_jsonl(os.path.join(args.cache_dir, f"{task}_train.jsonl")), args.few_shot) if args.few_shot else ()
        correct, n, lat, unparsed = 0, 0, [], 0
        for idx, r in enumerate(recs):
            t0 = time.perf_counter()
            try:
                text = query(args.endpoint, args.model, render_prompt(r, shots))
            except Exception as e:
                unparsed += 1; n += 1
                if n <= 3:
                    print(f"  [{task}] query error: {e}", flush=True)
                continue
            lat.append(time.perf_counter() - t0)
            m = re.search(r"\d+", text)
            pred = int(m.group()) if m else -1
            if pred < 0 or pred >= len(r.options):
                unparsed += 1
            correct += int(pred == r.answer)
            n += 1
            if dump:
                dump.write(json.dumps({"task": task, "idx": idx, "gold": r.answer, "pred": pred,
                                       "conf": None, "hit": int(pred == r.answer)}) + "\n")
        acc = correct / max(n, 1)
        mlat = 1000 * sum(lat) / len(lat) if lat else 0
        per_task[task] = (acc, n, mlat, unparsed)
        overall_correct += correct; overall_n += n; lat_all += lat
        print(f"{task}: acc={acc:.4f} n={n} mean_lat={mlat:.0f}ms unparsed={unparsed}", flush=True)

    lat_all.sort()
    lines += ["| task | acc | n | mean latency (ms) | unparsed |", "|---|---|---|---|---|"]
    for t, (acc, n, mlat, up) in per_task.items():
        lines.append(f"| {t} | {acc*100:.1f}% | {n} | {mlat:.0f} | {up} |")
    lines += ["",
              f"**Overall:** {overall_correct/max(overall_n,1)*100:.1f}% "
              f"(n={overall_n}), mean latency "
              f"{1000*sum(lat_all)/len(lat_all):.0f} ms/decision"
              + (f", p50 {1000*lat_all[len(lat_all)//2]:.0f} ms" if lat_all else ""), ""]
    open(args.out, "w").write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
