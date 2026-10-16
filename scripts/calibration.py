"""Calibration analysis for a trained Verdict checkpoint.

Computes the calibration metrics the paper reports (§6 "Calibration"): expected
calibration error (ECE) at 10 and 15 bins, maximum calibration error (MCE),
multiclass Brier score, and the per-bin reliability-diagram data. All are
reported per-task and pooled overall, and — with --ablation — both WITH the
learned calibration temperature (the deployed model) and WITHOUT it
(temperature forced to 1), which isolates how much of the calibration is due to
the learned temperature vs the head itself.

How the temperature ablation works: DecisionHead.forward already returns
raw_scores / temperature, so Verdict.logits_batch() yields temperature-scaled
logits. Multiplying those logits back by the learned temperature recovers the
raw (temperature=1) logits, whose softmax is the "no_temp" distribution.

Metric definitions (top-label calibration, matching scripts/train.py's _ece):
  confidence   = P(top) = max over options of the predicted probability
  bin b        = confidences in [b/nb, (b+1)/nb)  (last bin closes at 1.0)
  ECE(nb)      = sum_b (count_b / n) * |accuracy_b - mean_confidence_b|
  MCE(nb)      = max over non-empty bins of |accuracy_b - mean_confidence_b|
  Brier        = mean_i sum_k (p_ik - onehot_ik)^2   (multiclass, range [0, 2])

Run (does NOT train; needs a checkpoint from scripts/train.py and the cached
val splits it wrote to data/jsonl/, else it rebuilds them from the HF sources):

  python3 scripts/calibration.py --ckpt out/verdict-base \
      --tasks route_topic,signal_positive,affect --out out/calibration --bins 10,15 --ablation

Outputs (into the --out directory):
  calibration.json  — full nested metrics: per-task + "overall", each condition
                      (with_temp[, no_temp]) with acc, brier, ECE/MCE per bin
                      count, and the reliability bins; plus the learned temperature.
  metrics.csv       — one row per (task|overall) x condition: n, acc, brier, and
                      ece_<nb>/mce_<nb> columns for each requested bin count.
  reliability.csv   — reliability-diagram bin data: one row per
                      (task|overall) x condition x nbins x bin, with bin_lo,
                      bin_hi, mean_confidence, accuracy, count.
It also prints a 3-line human summary (temperature, overall ECE-10/MCE/Brier,
and — with --ablation — the with/without-temperature delta).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict import Choice, Noul, Score, Verdict  # noqa: E402
from verdict.data import build_task, dump_jsonl, load_jsonl  # noqa: E402

_DTYPES = {"float32": torch.float32, "float16": torch.float16, "bfloat16": torch.bfloat16}


def _q(rec):
    """Reconstruct the typed Question from a Record (mirrors scripts/train.py)."""
    if rec.qtype == "noul":
        return Noul(rec.question)
    if rec.qtype == "score":
        return Score(rec.question, k=len(rec.options))
    return Choice(rec.question, rec.options)


def _load_val(task, cache_dir, limit):
    """Load a task's cached val split; rebuild + cache it if absent."""
    path = os.path.join(cache_dir, f"{task}_val.jsonl")
    if not os.path.isfile(path):
        try:
            recs = build_task(task, "validation")
        except Exception:
            recs = build_task(task, "test")
        os.makedirs(cache_dir, exist_ok=True)
        dump_jsonl(recs, path)
    recs = load_jsonl(path)
    return recs[:limit] if limit else recs


def _bin_stats(rows, nb):
    """rows: list of (confidence, hit). -> (bins, ece, mce).

    bins is a list of dicts (one per bin) with bin index, edges, mean_confidence,
    accuracy, count. Empty bins are reported (count 0) but skipped in MCE.
    """
    agg = [[0, 0, 0.0] for _ in range(nb)]  # [count, hits, sum_conf]
    for c, h in rows:
        k = min(int(c * nb), nb - 1)
        agg[k][0] += 1
        agg[k][1] += h
        agg[k][2] += c
    n = max(len(rows), 1)
    bins, ece, mce = [], 0.0, 0.0
    for i, (cnt, hits, sconf) in enumerate(agg):
        acc = hits / cnt if cnt else 0.0
        mconf = sconf / cnt if cnt else 0.0
        gap = abs(acc - mconf)
        if cnt:
            ece += (cnt / n) * gap
            mce = max(mce, gap)
        bins.append({
            "bin": i,
            "bin_lo": i / nb,
            "bin_hi": (i + 1) / nb,
            "mean_confidence": mconf,
            "accuracy": acc,
            "count": cnt,
        })
    return bins, ece, mce


def _metrics(records, bin_counts):
    """records: list of (confidence, hit, brier_item). -> metrics dict."""
    n = len(records)
    rows = [(c, h) for c, h, _ in records]
    acc = sum(h for _, h in rows) / max(n, 1)
    brier = sum(b for _, _, b in records) / max(n, 1)
    ece, mce, reliability = {}, {}, {}
    for nb in bin_counts:
        bins, e, m = _bin_stats(rows, nb)
        ece[str(nb)] = e
        mce[str(nb)] = m
        reliability[str(nb)] = bins
    return {"n": n, "acc": acc, "brier": brier,
            "ece": ece, "mce": mce, "reliability": reliability}


def main():
    ap = argparse.ArgumentParser(description="Calibration analysis for a Verdict checkpoint.")
    ap.add_argument("--ckpt", required=True, help="checkpoint dir (e.g. out/verdict-base)")
    ap.add_argument("--tasks", required=True, help="comma-separated task names")
    ap.add_argument("--out", default="out/calibration", help="output directory")
    ap.add_argument("--bins", default="10,15", help="comma-separated bin counts for ECE/MCE")
    ap.add_argument("--ablation", action="store_true",
                    help="also report metrics WITHOUT the learned temperature (temperature=1)")
    ap.add_argument("--fit-temp", action="store_true",
                    help="post-hoc temperature scaling (Guo et al. 2017): fit one scalar T per task "
                         "by NLL on the even-indexed half of val, report ALL conditions on the odd half")
    ap.add_argument("--cache-dir", default="data/jsonl")
    ap.add_argument("--limit", type=int, default=0, help="cap val items per task (0 = all)")
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--device", default=None)
    ap.add_argument("--dtype", default="float32", choices=list(_DTYPES))
    args = ap.parse_args()

    tasks = [t for t in args.tasks.split(",") if t]
    bin_counts = [int(b) for b in args.bins.split(",") if b]
    conditions = ["with_temp"] + (["no_temp"] if args.ablation else [])
    if args.fit_temp:
        conditions.append("posthoc_temp")

    model = Verdict.from_pretrained(args.ckpt, device=args.device, dtype=_DTYPES[args.dtype])
    temp = float(model.head.temperature.detach().cpu())
    print(f"loaded {args.ckpt} | learned temperature = {temp:.4f} | "
          f"conditions = {conditions}", flush=True)

    # per_task[task][cond] -> list of (confidence, hit, brier_item)
    per_task = {t: {c: [] for c in conditions} for t in tasks}
    overall = {c: [] for c in conditions}
    fitted_T = {}

    for task in tasks:
        recs = _load_val(task, args.cache_dir, args.limit)
        # pass 1: collect raw (temperature=1) logits for every item
        raw, answers = [], []
        for i in range(0, len(recs), args.batch_size):
            chunk = recs[i:i + args.batch_size]
            qs = [_q(r) for r in chunk]
            with torch.no_grad():
                logits_list = model.logits_batch(qs)  # each (n_opt,), already /temperature
            for lg, r in zip(logits_list, chunk):
                raw.append(lg.float().cpu() * temp)  # undo learned T -> raw scores
                answers.append(r.answer)
        idx = list(range(len(recs)))
        T_post = 1.0
        if args.fit_temp:
            # fit scalar T on even-indexed half by NLL (Guo et al. 2017); evaluate on odd half
            fit_idx, idx = idx[0::2], idx[1::2]
            logT = torch.zeros(1, requires_grad=True)
            opt = torch.optim.LBFGS([logT], lr=0.1, max_iter=200, line_search_fn="strong_wolfe")

            def nll():
                opt.zero_grad()
                loss = sum(-torch.log_softmax(raw[j] / logT.exp(), -1)[answers[j]] for j in fit_idx) / len(fit_idx)
                loss.backward()
                return loss
            opt.step(nll)
            T_post = float(logT.exp().detach())
            fitted_T[task] = {"T": T_post, "n_fit": len(fit_idx), "n_eval": len(idx)}
            print(f"  {task}: post-hoc T = {T_post:.4f} (fit on {len(fit_idx)}, eval on {len(idx)})", flush=True)
        for j in idx:
            lg, ans = raw[j], answers[j]
            for cond in conditions:
                scaled = {"with_temp": lg / temp, "no_temp": lg, "posthoc_temp": lg / T_post}[cond]
                probs = torch.softmax(scaled, -1)
                top = int(torch.argmax(probs))
                conf = float(probs[top])
                hit = int(top == ans)
                onehot = torch.zeros_like(probs)
                onehot[ans] = 1.0
                brier_item = float(((probs - onehot) ** 2).sum())
                per_task[task][cond].append((conf, hit, brier_item))
                overall[cond].append((conf, hit, brier_item))
        with_n = len(per_task[task]["with_temp"])
        wm = _metrics(per_task[task]["with_temp"], bin_counts)
        print(f"  {task}: n={with_n} acc={wm['acc']:.4f} "
              f"ece10={wm['ece'][str(bin_counts[0])]:.4f} brier={wm['brier']:.4f}", flush=True)

    # assemble results
    results = {}
    for task in tasks:
        results[task] = {c: _metrics(per_task[task][c], bin_counts) for c in conditions}
    results["overall"] = {c: _metrics(overall[c], bin_counts) for c in conditions}

    payload = {
        "ckpt": args.ckpt,
        "tasks": tasks,
        "temperature": temp,
        "bins": bin_counts,
        "conditions": conditions,
        "posthoc_temperature": fitted_T,
        "results": results,
    }

    os.makedirs(args.out, exist_ok=True)
    json_path = os.path.join(args.out, "calibration.json")
    with open(json_path, "w") as f:
        json.dump(payload, f, indent=2)

    # metrics.csv
    metrics_path = os.path.join(args.out, "metrics.csv")
    header = ["task", "condition", "n", "acc", "brier"]
    header += [f"ece_{nb}" for nb in bin_counts] + [f"mce_{nb}" for nb in bin_counts]
    with open(metrics_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for task in tasks + ["overall"]:
            for cond in conditions:
                m = results[task][cond]
                row = [task, cond, m["n"], f"{m['acc']:.6f}", f"{m['brier']:.6f}"]
                row += [f"{m['ece'][str(nb)]:.6f}" for nb in bin_counts]
                row += [f"{m['mce'][str(nb)]:.6f}" for nb in bin_counts]
                w.writerow(row)

    # reliability.csv
    rel_path = os.path.join(args.out, "reliability.csv")
    with open(rel_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["task", "condition", "nbins", "bin", "bin_lo", "bin_hi",
                    "mean_confidence", "accuracy", "count"])
        for task in tasks + ["overall"]:
            for cond in conditions:
                for nb in bin_counts:
                    for b in results[task][cond]["reliability"][str(nb)]:
                        w.writerow([task, cond, nb, b["bin"],
                                    f"{b['bin_lo']:.4f}", f"{b['bin_hi']:.4f}",
                                    f"{b['mean_confidence']:.6f}", f"{b['accuracy']:.6f}",
                                    b["count"]])

    # 3-line human summary
    ov = results["overall"]["with_temp"]
    nb0 = str(bin_counts[0])
    print(f"temperature={temp:.4f} | wrote {json_path}, {metrics_path}, {rel_path}", flush=True)
    print(f"overall (with_temp): n={ov['n']} acc={ov['acc']:.4f} "
          f"ECE{nb0}={ov['ece'][nb0]:.4f} MCE{nb0}={ov['mce'][nb0]:.4f} "
          f"Brier={ov['brier']:.4f}", flush=True)
    if args.ablation:
        nt = results["overall"]["no_temp"]
        print(f"ablation temp=1: ECE{nb0}={nt['ece'][nb0]:.4f} (Δ {ov['ece'][nb0]-nt['ece'][nb0]:+.4f}) "
              f"MCE{nb0}={nt['mce'][nb0]:.4f} Brier={nt['brier']:.4f}", flush=True)
    else:
        print("ablation: not run (pass --ablation to compare temperature on/off)", flush=True)
    if args.fit_temp:
        pt = results["overall"]["posthoc_temp"]
        print(f"post-hoc T (held-out half): ECE{nb0}={pt['ece'][nb0]:.4f} (Δ {pt['ece'][nb0]-ov['ece'][nb0]:+.4f} vs with_temp) "
              f"MCE{nb0}={pt['mce'][nb0]:.4f} Brier={pt['brier']:.4f} | T per task: "
              + ", ".join(f"{t}={v['T']:.3f}" for t, v in fitted_T.items()), flush=True)


if __name__ == "__main__":
    main()
