"""Evaluate a trained Verdict checkpoint on one or more OrgBench tasks.

Reports, PER-TASK and OVERALL: accuracy, macro-F1, ECE (10-bin, top-label),
and decision latency (batched, warm) as mean + p50 milliseconds per decision.

  python3 scripts/eval_orgbench.py --ckpt out/verdict-base \
      --tasks route_topic,signal_positive,affect,route_intent \
      --batch-size 64 --limit 2000 --out RESULTS_orgbench.md

Data source: for each task it loads the cached data/jsonl/<task>_val.jsonl
written by scripts/train.py; if that file is missing it falls back to
build_task(task, "validation") and then build_task(task, "test").

Outputs (all three):
  * stdout: the markdown table AND the full JSON blob (plus a 1-line summary).
  * <out>            : the markdown table (default RESULTS_orgbench.md).
  * <out stem>.json  : the machine-readable results — a dict with a per-task
                       sub-dict {acc, macro_f1, ece, n, n_classes,
                       mean_latency_ms, p50_latency_ms} and an "overall" entry.

Metric definitions:
  * accuracy   — top==answer, micro (pooled) at the overall level.
  * macro-F1   — unweighted mean per-class F1 over the task's option space;
                 the OVERALL macro-F1 is the unweighted mean of the per-task
                 macro-F1 values (class spaces differ across tasks).
  * ECE        — 10-bin expected calibration error on the top-label confidence
                 (same estimator as scripts/train.py).
  * latency    — end-to-end .predict_batch cost (forward + softmax + Decision
                 build) per decision = batch_wall_time / batch_size, measured
                 after warmup with CUDA sync; mean and p50 over all decisions.

This script only READS a checkpoint and RUNS inference; it trains nothing.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict import Choice, Noul, Score, Verdict  # noqa: E402
from verdict.data import build_task, load_jsonl  # noqa: E402


def _q(rec):
    """Record -> typed Question (mirrors scripts/train.py)."""
    if rec.qtype == "noul":
        return Noul(rec.question)
    if rec.qtype == "score":
        return Score(rec.question, k=len(rec.options))
    return Choice(rec.question, rec.options)


def _ece(rows, nb=10):
    """10-bin top-label ECE. rows = list of (confidence, hit)."""
    b = [[0, 0, 0.0] for _ in range(nb)]
    for c, h in rows:
        k = min(int(c * nb), nb - 1)
        b[k][0] += 1; b[k][1] += h; b[k][2] += c
    n = len(rows)
    return sum(abs(h / c - cf / c) * c for c, h, cf in b if c) / max(n, 1)


def _macro_f1(y_true, y_pred, n_classes):
    """Unweighted mean per-class F1 over 0..n_classes-1."""
    f1s = []
    for c in range(n_classes):
        tp = sum(1 for t, p in zip(y_true, y_pred) if p == c and t == c)
        fp = sum(1 for t, p in zip(y_true, y_pred) if p == c and t != c)
        fn = sum(1 for t, p in zip(y_true, y_pred) if p != c and t == c)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        f1s.append(f1)
    return sum(f1s) / max(len(f1s), 1)


def batches(x, n):
    for i in range(0, len(x), n):
        yield x[i:i + n]


def _mean_p50(vals):
    if not vals:
        return 0.0, 0.0
    s = sorted(vals)
    return sum(s) / len(s), s[len(s) // 2]


def load_val(task, cache_dir, limit):
    """Cached <task>_val.jsonl, else build_task validation, else test."""
    path = os.path.join(cache_dir, f"{task}_val.jsonl")
    if os.path.isfile(path):
        recs = load_jsonl(path)
    else:
        try:
            recs = build_task(task, "validation", limit=limit)
        except Exception:
            recs = build_task(task, "test", limit=limit)
    if limit:
        recs = recs[:limit]
    return recs


@torch.no_grad()
def eval_task(model, recs, bs, dev):
    """Return per-task metrics dict for one task's records."""
    is_cuda = dev.type == "cuda"

    def sync():
        if is_cuda:
            torch.cuda.synchronize(dev)

    n_classes = len(recs[0].options)
    y_true, y_pred, conf_rows = [], [], []

    # --- accuracy / macro-F1 / ECE pass (also warms the model) ---
    for ch in batches(recs, bs):
        for d, r in zip(model.predict_batch([_q(x) for x in ch]), ch):
            y_true.append(r.answer)
            y_pred.append(d.top)
            conf_rows.append((d.confidence, int(d.top == r.answer)))

    acc = sum(int(t == p) for t, p in zip(y_true, y_pred)) / max(len(recs), 1)
    macro_f1 = _macro_f1(y_true, y_pred, n_classes)
    ece = _ece(conf_rows)

    # --- warm batched latency pass ---
    warm = list(batches(recs, bs))
    for ch in warm[:2]:  # explicit warmup, discarded
        model.predict_batch([_q(x) for x in ch])
    sync()
    lat_ms = []
    for ch in warm:
        qs = [_q(x) for x in ch]
        sync(); t0 = time.perf_counter()
        model.predict_batch(qs)
        sync(); dt = time.perf_counter() - t0
        per = 1000.0 * dt / len(qs)
        lat_ms.extend([per] * len(qs))
    mean_lat, p50_lat = _mean_p50(lat_ms)

    return {
        "acc": acc,
        "macro_f1": macro_f1,
        "ece": ece,
        "n": len(recs),
        "n_classes": n_classes,
        "mean_latency_ms": mean_lat,
        "p50_latency_ms": p50_lat,
    }, y_true, y_pred, conf_rows, lat_ms

PROMPT_VARIANTS = {
    "route_topic": "Which team should this incoming item be routed to?",
    "signal_positive": "Does this message express a positive sentiment?",
    "affect": "Which emotion best describes the tone of this message?",
}


def _variant_question(rec):
    """Swap the task prompt (first line before the blank line) for a paraphrase."""
    head, _, body = rec.question.partition("\n\n")
    alt = PROMPT_VARIANTS.get(rec.task) or f"Decide the following. {head}"
    return f"{alt}\n\n{body}" if body else alt


@torch.no_grad()
def robustness(model, recs, base_pred, bs, mode, seed=0):
    """Re-score recs under a perturbation that must not change the answer.
    mode='permute': seeded random option-order permutation (all types rendered as
    Choice over the same option strings, which is exactly Noul/Score's rendering).
    mode='prompt': paraphrased task prompt, original option order.
    Returns (acc_perturbed, flip_rate vs base_pred)."""
    import random
    rng = random.Random(seed)
    preds = []
    for ch in batches(recs, bs):
        qs, inv = [], []
        for r in ch:
            n = len(r.options)
            if mode == "permute":
                perm = list(range(n)); rng.shuffle(perm)          # perm[new_pos] = old_idx
                qs.append(Choice(r.question, [r.options[i] for i in perm]))
                inv.append(perm)
            else:
                qs.append(Choice(_variant_question(r), list(r.options)))
                inv.append(list(range(n)))
        for d, perm in zip(model.predict_batch(qs), inv):
            preds.append(perm[d.top])                              # map back to original index
    acc = sum(int(p == r.answer) for p, r in zip(preds, recs)) / max(len(recs), 1)
    flips = sum(int(p != b) for p, b in zip(preds, base_pred)) / max(len(recs), 1)
    return acc, flips


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="out/verdict-base",
                    help="trained Verdict checkpoint dir (save_pretrained output)")
    ap.add_argument("--tasks", required=True, help="comma list of OrgBench task names")
    ap.add_argument("--limit", type=int, default=0, help="cap records per task (0=all)")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--cache-dir", default="data/jsonl")
    ap.add_argument("--out", default="RESULTS_orgbench.md")
    ap.add_argument("--dump-preds", default=None,
                    help="write per-item predictions (task, idx, gold, pred, conf, probs) as JSONL for scripts/significance.py")
    ap.add_argument("--permute-options", action="store_true",
                    help="re-score every item with a seeded random permutation of its option order; report acc delta + flip rate")
    ap.add_argument("--prompt-variant", action="store_true",
                    help="re-score every item with a paraphrased task prompt; report acc delta + flip rate")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    model = Verdict.from_pretrained(args.ckpt)
    dev = next(model.backbone.parameters()).device
    print(f"loaded {args.ckpt} on {dev}", flush=True)

    tasks = [t for t in args.tasks.split(",") if t]
    per_task = {}
    dump_rows = []
    all_true, all_pred, all_rows, all_lat = [], [], [], []
    task_f1s = []

    for task in tasks:
        recs = load_val(task, args.cache_dir, args.limit)
        if not recs:
            print(f"WARN: {task} has no records, skipping", flush=True)
            continue
        m, yt, yp, rows, lat = eval_task(model, recs, args.batch_size, dev)
        if args.permute_options:
            m["permute_acc"], m["permute_flip_rate"] = robustness(model, recs, yp, args.batch_size, "permute", args.seed)
            print(f"  [{task}] option-permutation: acc={m['permute_acc']:.4f} (Δ {m['permute_acc']-m['acc']:+.4f}) flip_rate={m['permute_flip_rate']:.4f}", flush=True)
        if args.prompt_variant:
            m["prompt_acc"], m["prompt_flip_rate"] = robustness(model, recs, yp, args.batch_size, "prompt", args.seed)
            print(f"  [{task}] prompt-paraphrase: acc={m['prompt_acc']:.4f} (Δ {m['prompt_acc']-m['acc']:+.4f}) flip_rate={m['prompt_flip_rate']:.4f}", flush=True)
        if args.dump_preds:
            dump_rows += [{"task": task, "idx": i, "gold": t, "pred": p_, "conf": c, "hit": h}
                          for i, (t, p_, (c, h)) in enumerate(zip(yt, yp, rows))]
        per_task[task] = m
        all_true += yt; all_pred += yp; all_rows += rows; all_lat += lat
        task_f1s.append(m["macro_f1"])
        print(f"{task}: acc={m['acc']:.4f} macroF1={m['macro_f1']:.4f} "
              f"ece={m['ece']:.4f} n={m['n']} "
              f"lat_mean={m['mean_latency_ms']:.2f}ms p50={m['p50_latency_ms']:.2f}ms",
              flush=True)

    # --- overall (micro acc / pooled ECE+latency / macro-over-tasks F1) ---
    o_mean_lat, o_p50_lat = _mean_p50(all_lat)
    overall = {
        "acc": sum(int(t == p) for t, p in zip(all_true, all_pred)) / max(len(all_true), 1),
        "macro_f1": sum(task_f1s) / max(len(task_f1s), 1),
        "ece": _ece(all_rows),
        "n": len(all_true),
        "mean_latency_ms": o_mean_lat,
        "p50_latency_ms": o_p50_lat,
    }

    results = {
        "ckpt": args.ckpt,
        "batch_size": args.batch_size,
        "limit": args.limit,
        "device": str(dev),
        "tasks": per_task,
        "overall": overall,
    }

    # --- markdown table ---
    md = [f"# Verdict on OrgBench — {args.ckpt}", "",
          "| task | acc | macro-F1 | ECE | n | mean lat (ms) | p50 lat (ms) |",
          "|---|---|---|---|---|---|---|"]
    for t, m in per_task.items():
        md.append(f"| {t} | {m['acc']*100:.1f}% | {m['macro_f1']*100:.1f}% | "
                  f"{m['ece']:.4f} | {m['n']} | {m['mean_latency_ms']:.2f} | "
                  f"{m['p50_latency_ms']:.2f} |")
    md.append(f"| **overall** | **{overall['acc']*100:.1f}%** | "
              f"**{overall['macro_f1']*100:.1f}%** | **{overall['ece']:.4f}** | "
              f"**{overall['n']}** | **{overall['mean_latency_ms']:.2f}** | "
              f"**{overall['p50_latency_ms']:.2f}** |")
    md.append("")
    md.append("_macro-F1 overall = mean of per-task macro-F1; acc/ECE/latency "
              "pooled across tasks; latency batched + warm._")
    md_text = "\n".join(md)

    # --- write outputs ---
    if args.dump_preds:
        with open(args.dump_preds, "w") as f:
            for row in dump_rows:
                f.write(json.dumps(row) + "\n")
        print(f"dumped {len(dump_rows)} per-item predictions -> {args.dump_preds}", flush=True)
    if args.permute_options or args.prompt_variant:
        md.append("")
        md.append("## Robustness: perturbations that must not change the answer")
        md.append("| task | acc | option-permutation acc | flip rate | prompt-paraphrase acc | flip rate |")
        md.append("|---|---|---|---|---|---|")
        for t, m in per_task.items():
            pa = f"{m['permute_acc']*100:.1f}%" if "permute_acc" in m else "-"
            pf = f"{m['permute_flip_rate']*100:.1f}%" if "permute_flip_rate" in m else "-"
            qa = f"{m['prompt_acc']*100:.1f}%" if "prompt_acc" in m else "-"
            qf = f"{m['prompt_flip_rate']*100:.1f}%" if "prompt_flip_rate" in m else "-"
            md.append(f"| {t} | {m['acc']*100:.1f}% | {pa} | {pf} | {qa} | {qf} |")
        md_text = "\n".join(md)
    json_path = os.path.splitext(args.out)[0] + ".json"
    with open(args.out, "w") as f:
        f.write(md_text + "\n")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + md_text)
    print("\n" + json.dumps(results, indent=2))
    print(f"\nwrote {args.out} and {json_path} | overall acc={overall['acc']*100:.1f}% "
          f"macroF1={overall['macro_f1']*100:.1f}% ece={overall['ece']:.4f} "
          f"mean_lat={overall['mean_latency_ms']:.2f}ms p50={overall['p50_latency_ms']:.2f}ms "
          f"(n={overall['n']})", flush=True)


if __name__ == "__main__":
    main()
