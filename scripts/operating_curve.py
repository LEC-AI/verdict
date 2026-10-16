"""Operating curve — Verdict's selective-prediction / autonomy analysis.

This is the paper's headline autonomy result: *auto-handle P% of the volume at
A% accuracy, escalate the rest*. It only works because Verdict's output is a
calibrated probability you can threshold. We treat the top class probability
(`Decision.confidence`; for a Noul that is max(P(yes), P(no))) as the selective
score: an item is COVERED (auto-handled) when confidence >= tau, and ESCALATED
(abstained) otherwise.

From per-example (confidence, correct) pairs it computes, over all tasks jointly
and per task:

  * the risk-coverage curve   — sort by confidence desc; risk(k)=error over the
                                top-k most confident, coverage(k)=k/N.
  * AURC                      — area under that curve (lower is better), plus the
                                random-selection baseline (= overall error, a flat
                                curve), the optimal-ordering AURC, and E-AURC
                                (the excess over optimal).
  * accuracy @ coverage       — accuracy on the covered set for coverage in
                                {0.5, 0.7, 0.9, 1.0}.
  * coverage @ target-accuracy — the max fraction you can auto-handle while
                                keeping accuracy-on-covered >= target, for targets
                                {0.90, 0.95, 0.99}, with the tau that achieves it.

Selection by a confidence threshold picks exactly a prefix of the
confidence-sorted list, so every (coverage, accuracy-on-covered) point on the
sweep is realizable by some tau — the coverage@target numbers are operational,
not hypothetical.

Run (no GPU training; a checkpoint forward pass only):

  python3 scripts/operating_curve.py \
      --ckpt out/verdict-base \
      --tasks route_topic,signal_positive,affect \
      --out out/operating_curve

Inputs: a trained checkpoint dir (--ckpt, e.g. out/verdict-base) and the cached
val splits data/jsonl/<task>_val.jsonl (written by scripts/train.py). If a cache
file is missing it is rebuilt from the public source via build_task.

Outputs (written under --out/):
  operating_curve.csv   tau,coverage,accuracy_on_covered,escalation_rate  (tau 0..1)
  operating_curve.json  machine-readable: overall + per-task AURC, acc@coverage,
                        coverage@target, and a (downsampled) risk-coverage curve.
  operating_curve.md    the paper table ("auto-handle P% at A% accuracy").
Also prints a short human summary to stdout.
"""

from __future__ import annotations

import argparse
import bisect
import csv
import json
import os
import sys

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict import Choice, Noul, Score, Verdict  # noqa: E402
from verdict.data import build_task, dump_jsonl, load_jsonl  # noqa: E402

COVERAGES = (0.5, 0.7, 0.9, 1.0)
TARGETS = (0.90, 0.95, 0.99)


def _q(rec):
    if rec.qtype == "noul":
        return Noul(rec.question)
    if rec.qtype == "score":
        return Score(rec.question, k=len(rec.options))
    return Choice(rec.question, rec.options)


def batches(x, n):
    for i in range(0, len(x), n):
        yield x[i:i + n]


def load_recs(task, cache_dir, limit):
    """Load a task's val split from cache; rebuild from the public source if absent."""
    path = os.path.join(cache_dir, f"{task}_val.jsonl")
    if os.path.isfile(path):
        recs = load_jsonl(path)
    else:
        try:
            recs = build_task(task, "validation", limit=limit or 2000)
        except Exception:
            recs = build_task(task, "test", limit=limit or 2000)
        os.makedirs(cache_dir, exist_ok=True)
        dump_jsonl(recs, path)
    return recs[:limit] if limit else recs


@torch.no_grad()
def collect(model, recs, bs):
    """Return per-example (confidence, correct) pairs for `recs`."""
    pairs = []
    for ch in batches(recs, bs):
        for d, r in zip(model.predict_batch([_q(x) for x in ch]), ch):
            pairs.append((float(d.confidence), int(d.top == r.answer)))
    return pairs


# --- selective-prediction metrics (pure python, exact) --------------------

def rc_curve(pairs):
    """Sort by confidence desc; return (sorted_pairs, coverage[], risk[], acc[])
    where index k-1 corresponds to auto-handling the top-k most confident."""
    s = sorted(pairs, key=lambda p: p[0], reverse=True)
    n = len(s)
    cum_err = 0
    cov, risk, acc = [], [], []
    for k in range(1, n + 1):
        cum_err += 1 - s[k - 1][1]
        cov.append(k / n)
        risk.append(cum_err / k)
        acc.append(1.0 - cum_err / k)
    return s, cov, risk, acc


def aurc_stats(risk, n_err, n):
    """AURC = mean risk over the sorted prefixes. Also the optimal-ordering AURC
    (all correct ranked first), E-AURC = AURC - optimal, and the random baseline
    (a flat curve at the overall error rate)."""
    aurc = sum(risk) / n
    n_correct = n - n_err
    opt = sum(max(0, k - n_correct) / k for k in range(1, n + 1)) / n
    overall_err = n_err / n
    return {
        "aurc": aurc,
        "aurc_optimal": opt,
        "e_aurc": aurc - opt,
        "aurc_random_baseline": overall_err,
    }


def acc_at_coverage(sorted_pairs, acc, cov_target):
    """Accuracy on the most-confident `cov_target` fraction (the achievable
    accuracy if you auto-handle that share of volume, ranked by confidence)."""
    n = len(sorted_pairs)
    k = min(n, max(1, round(cov_target * n)))
    return {
        "coverage_requested": cov_target,
        "coverage_actual": k / n,
        "accuracy_on_covered": acc[k - 1],
        "escalation_rate": 1.0 - k / n,
        "tau": sorted_pairs[k - 1][0],
    }


def coverage_at_target(sorted_pairs, acc, target):
    """Max coverage whose accuracy-on-covered >= target, and the tau achieving it.
    Scans all prefixes so a lone confident error can't cap coverage early."""
    n = len(sorted_pairs)
    best_k = 0
    for k in range(1, n + 1):
        if acc[k - 1] >= target:
            best_k = k
    if best_k == 0:
        return {"target_accuracy": target, "coverage": 0.0, "escalation_rate": 1.0,
                "accuracy_on_covered": None, "tau": None,
                "note": "target unreachable at any coverage"}
    return {
        "target_accuracy": target,
        "coverage": best_k / n,
        "escalation_rate": 1.0 - best_k / n,
        "accuracy_on_covered": acc[best_k - 1],
        "tau": sorted_pairs[best_k - 1][0],
    }


def holdout_transfer(pairs, targets):
    """Leak-free operating point: choose tau for each target accuracy on the
    even-indexed half of `pairs` (fit), then report the REALIZED coverage and
    accuracy of that tau on the odd-indexed half (eval). This is what an
    operator gets when a threshold picked on past data is applied to new data."""
    fit, ev = pairs[0::2], pairs[1::2]
    s, _, _, acc = rc_curve(fit)
    out = {}
    for t in targets:
        r = coverage_at_target(s, acc, t)
        tau = r["tau"]
        if tau is None:
            out[f"{t:.2f}"] = {"target_accuracy": t, "tau_fit": None, "note": "unreachable on fit half"}
            continue
        covered = [h for c, h in ev if c >= tau]
        out[f"{t:.2f}"] = {
            "target_accuracy": t,
            "tau_fit": tau,
            "fit_coverage": r["coverage"],
            "fit_accuracy": r["accuracy_on_covered"],
            "eval_coverage": len(covered) / max(len(ev), 1),
            "eval_accuracy": (sum(covered) / len(covered)) if covered else None,
            "n_fit": len(fit), "n_eval": len(ev),
        }
    return out


def tau_sweep(pairs, steps):
    """(tau, coverage, accuracy_on_covered, escalation_rate) as tau sweeps 0..1.
    Coverage counts confidence >= tau (act at or above the cutoff)."""
    n = len(pairs)
    s = sorted(pairs, key=lambda p: p[0], reverse=True)          # confidence desc
    conf_asc = sorted(p[0] for p in pairs)                        # for coverage count
    cum_corr = [0]                                                # prefix correct over desc order
    for _, h in s:
        cum_corr.append(cum_corr[-1] + h)
    rows = []
    for i in range(steps + 1):
        tau = i / steps
        count = n - bisect.bisect_left(conf_asc, tau)            # #(confidence >= tau)
        coverage = count / n
        acc = (cum_corr[count] / count) if count else None       # top-`count` are the covered set
        rows.append((tau, coverage, acc, 1.0 - coverage))
    return rows


def summarize(pairs):
    s, cov, risk, acc = rc_curve(pairs)
    n = len(pairs)
    n_err = sum(1 - h for _, h in pairs)
    return {
        "n": n,
        "accuracy": 1.0 - n_err / n,
        **aurc_stats(risk, n_err, n),
        "acc_at_coverage": {f"{c:.2f}": acc_at_coverage(s, acc, c) for c in COVERAGES},
        "coverage_at_target": {f"{t:.2f}": coverage_at_target(s, acc, t) for t in TARGETS},
        "_curve": (s, cov, risk, acc),   # stripped before JSON dump
    }


def downsample_curve(cov, risk, acc, max_pts=256):
    n = len(cov)
    if n <= max_pts:
        idx = range(n)
    else:
        step = n / max_pts
        idx = sorted({int(i * step) for i in range(max_pts)} | {n - 1})
    return [{"coverage": cov[i], "risk": risk[i], "accuracy_on_covered": acc[i]} for i in idx]


# --- rendering ------------------------------------------------------------

def _pct(x):
    return "n/a" if x is None else f"{x * 100:.1f}%"


def _tau(x):
    return "n/a" if x is None else f"{x:.3f}"


def render_md(tasks, overall, per_task):
    L = ["# Verdict operating curve — selective prediction / autonomy", ""]
    L += [
        "Confidence = top calibrated class probability. An item is auto-handled "
        "when confidence >= tau and escalated otherwise. Selection by a threshold "
        "picks a confidence-ranked prefix, so every point below is realizable by "
        "some tau.", "",
        f"**Tasks:** {', '.join(tasks)}  ·  **n = {overall['n']}**  ·  "
        f"**overall accuracy = {_pct(overall['accuracy'])}**", "",
        f"**AURC = {overall['aurc']:.4f}** (lower is better)  ·  "
        f"random-selection baseline = {overall['aurc_random_baseline']:.4f}  ·  "
        f"optimal ordering = {overall['aurc_optimal']:.4f}  ·  "
        f"E-AURC = {overall['e_aurc']:.4f}", "",
        "## Auto-handle P% at A% accuracy  (coverage @ target accuracy)", "",
        "| target accuracy | coverage auto-handled | escalated | accuracy on covered | tau |",
        "|---|---|---|---|---|",
    ]
    for t in TARGETS:
        r = overall["coverage_at_target"][f"{t:.2f}"]
        L.append(f"| {t * 100:.0f}% | {_pct(r['coverage'])} | {_pct(r['escalation_rate'])} "
                 f"| {_pct(r['accuracy_on_covered'])} | {_tau(r['tau'])} |")
    L += ["", "## Accuracy at fixed coverage", "",
          "| coverage auto-handled | accuracy on covered | escalated | tau |",
          "|---|---|---|---|"]
    for c in COVERAGES:
        r = overall["acc_at_coverage"][f"{c:.2f}"]
        L.append(f"| {_pct(r['coverage_actual'])} | {_pct(r['accuracy_on_covered'])} "
                 f"| {_pct(r['escalation_rate'])} | {_tau(r['tau'])} |")
    L += ["", "## Per task", "",
          "| task | n | acc | AURC | E-AURC | cov@95% acc | acc@90% cov |",
          "|---|---|---|---|---|---|---|"]
    for name, m in per_task.items():
        c95 = m["coverage_at_target"]["0.95"]
        a90 = m["acc_at_coverage"]["0.90"]
        L.append(f"| {name} | {m['n']} | {_pct(m['accuracy'])} | {m['aurc']:.4f} "
                 f"| {m['e_aurc']:.4f} | {_pct(c95['coverage'])} | {_pct(a90['accuracy_on_covered'])} |")
    L.append("")
    return "\n".join(L)


def strip_curve(m):
    return {k: v for k, v in m.items() if k != "_curve"}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ckpt", required=True, help="trained checkpoint dir, e.g. out/verdict-base")
    ap.add_argument("--tasks", required=True, help="comma-separated task names")
    ap.add_argument("--out", default="out/operating_curve", help="output directory")
    ap.add_argument("--cache-dir", default="data/jsonl")
    ap.add_argument("--limit", type=int, default=0, help="cap val examples per task (0 = all)")
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--tau-steps", type=int, default=100, help="grid steps for the 0..1 tau sweep")
    ap.add_argument("--device", default=None)
    ap.add_argument("--holdout", action="store_true",
                    help="also pick tau on one half and report realized coverage/accuracy on the other half")
    args = ap.parse_args()

    tasks = args.tasks.split(",")
    model = Verdict.from_pretrained(args.ckpt, device=args.device)
    dev = next(model.backbone.parameters()).device
    print(f"loaded {args.ckpt} on {dev}; tasks={tasks}", flush=True)

    all_pairs, per_task = [], {}
    for t in tasks:
        recs = load_recs(t, args.cache_dir, args.limit)
        pairs = collect(model, recs, args.batch_size)
        all_pairs += pairs
        per_task[t] = summarize(pairs)
        m = per_task[t]
        print(f"  {t}: n={m['n']} acc={m['accuracy']:.4f} aurc={m['aurc']:.4f}", flush=True)

    overall = summarize(all_pairs)
    os.makedirs(args.out, exist_ok=True)

    # 1) tau-sweep CSV
    csv_path = os.path.join(args.out, "operating_curve.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tau", "coverage", "accuracy_on_covered", "escalation_rate"])
        for tau, cov, acc, esc in tau_sweep(all_pairs, args.tau_steps):
            w.writerow([f"{tau:.4f}", f"{cov:.6f}",
                        "" if acc is None else f"{acc:.6f}", f"{esc:.6f}"])

    # 2) JSON summary (with downsampled risk-coverage curves)
    def pack(m):
        s, cov, risk, acc = m["_curve"]
        d = strip_curve(m)
        d["risk_coverage_curve"] = downsample_curve(cov, risk, acc)
        return d

    summary = {
        "ckpt": args.ckpt,
        "tasks": tasks,
        "confidence": "top calibrated class probability (Decision.confidence)",
        "selection_rule": "auto-handle when confidence >= tau, else escalate",
        "coverages": list(COVERAGES),
        "targets": list(TARGETS),
        "overall": pack(overall),
        "per_task": {k: pack(v) for k, v in per_task.items()},
    }
    json_path = os.path.join(args.out, "operating_curve.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    # 3) markdown table
    md_path = os.path.join(args.out, "operating_curve.md")
    md_text = render_md(tasks, overall, per_task)
    if args.holdout:
        ho = {"overall": holdout_transfer(all_pairs, TARGETS)}
        summary["holdout_transfer"] = ho
        json.dump(summary, open(json_path, "w"), indent=2)
        lines = ["", "## Held-out threshold transfer (tau picked on even items, applied to odd items)", "",
                 "| target accuracy | tau (fit half) | fit coverage | fit accuracy | eval coverage | **eval accuracy** |",
                 "|---|---|---|---|---|---|"]
        for t in TARGETS:
            r = ho["overall"][f"{t:.2f}"]
            if r.get("tau_fit") is None:
                lines.append(f"| {t*100:.0f}% | unreachable | | | | |")
                continue
            lines.append(f"| {t*100:.0f}% | {_tau(r['tau_fit'])} | {_pct(r['fit_coverage'])} | {_pct(r['fit_accuracy'])} | "
                         f"{_pct(r['eval_coverage'])} | **{_pct(r['eval_accuracy'])}** |")
        md_text += "\n".join(lines) + "\n"
        for t in TARGETS:
            r = ho["overall"][f"{t:.2f}"]
            if r.get("tau_fit") is not None:
                print(f"  holdout: target {t*100:.0f}% -> tau {r['tau_fit']:.3f}: eval coverage {_pct(r['eval_coverage'])}, "
                      f"eval accuracy {_pct(r['eval_accuracy'])}", flush=True)
    open(md_path, "w").write(md_text)

    # human summary
    print(f"\nwrote {csv_path}\n      {json_path}\n      {md_path}")
    print(f"overall: n={overall['n']} acc={overall['accuracy']*100:.1f}% "
          f"AURC={overall['aurc']:.4f} (optimal {overall['aurc_optimal']:.4f})")
    for t in TARGETS:
        r = overall["coverage_at_target"][f"{t:.2f}"]
        print(f"  auto-handle {_pct(r['coverage'])} at >= {t*100:.0f}% accuracy "
              f"(escalate {_pct(r['escalation_rate'])}, tau={_tau(r['tau'])})")


if __name__ == "__main__":
    main()
