"""Paired case-cluster bootstrap on the typed-decisions distribution metrics (KL, Brier, TV against the soft gold),
system A vs system B on identical decisions. significance.py tests accuracy and ECE only; the benchmark card
recommends reading KL and Brier rather than ECE, so this tests those directly.

  --temperature none : raw probabilities, all decisions
  --temperature soft : one temperature per system, fitted on the FIT half of the cases (same case-level hash split
                       as calibration_temp_scale.py) by minimising KL to the SOFT gold -- the metric's own target --
                       then scored on the held-out half only. (The hard-label temperature used for ECE sharpens
                       predictions and inflates KL against the soft gold, so it must not be reused here.)

  python3 scripts/distribution_significance.py --a preds_stable_cls_s40.jsonl --b preds_laya_td.jsonl \
      --name-a "Verdict-MQ s40" --name-b "Laya" --temperature soft --out RESULTS_distsig_s40_softT.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict.data_typed import load_typed  # noqa: E402

EPS = 1e-6


def fit_side(idx):
    return int(hashlib.sha1(f"{idx}".encode()).hexdigest()[:8], 16) % 2 == 0


def load(path):
    return {(o["task"], o["idx"]): o["probs"] for o in map(json.loads, open(path)) if o.get("probs")}


def scale(q, T):
    lp = [math.log(max(x, 1e-12)) / T for x in q]
    m = max(lp)
    e = [math.exp(x - m) for x in lp]
    s = sum(e)
    return [x / s for x in e]


def kl(p, q):
    return sum(pi * math.log((pi + EPS) / (qi + EPS)) for pi, qi in zip(p, q) if pi > 0)


def brier(p, q):
    return sum((qi - pi) ** 2 for pi, qi in zip(p, q))


def tv(p, q):
    return 0.5 * sum(abs(pi - qi) for pi, qi in zip(p, q))


def fit_T(preds, gold):
    keys = [k for k in preds if k in gold and fit_side(k[1])]
    grid = [round(0.30 + 0.02 * i, 2) for i in range(236)]  # 0.30 .. 5.00
    return min(grid, key=lambda T: sum(kl(gold[k], scale(preds[k], T)) for k in keys) / len(keys))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--name-a", default="A")
    ap.add_argument("--name-b", default="B")
    ap.add_argument("--temperature", choices=["none", "soft"], default="none")
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    gold = {(f"{r.meta['workflow']}:{r.meta['question']}", hashlib.sha1(r.text.encode()).hexdigest()[:16]): r.meta["soft"]
            for r in load_typed("test")}
    A, B = load(a.a), load(a.b)
    TA = TB = 1.0
    if a.temperature == "soft":
        TA, TB = fit_T(A, gold), fit_T(B, gold)
    keys = [k for k in A if k in B and k in gold and (a.temperature == "none" or not fit_side(k[1]))]
    cases = sorted({k[1] for k in keys})
    cix = {c: i for i, c in enumerate(cases)}
    agg = np.zeros((len(cases), 7))  # KL_A, KL_B, Brier_A, Brier_B, TV_A, TV_B, n
    for k in keys:
        p, qa, qb = gold[k], scale(A[k], TA), scale(B[k], TB)
        agg[cix[k[1]]] += [kl(p, qa), kl(p, qb), brier(p, qa), brier(p, qb), tv(p, qa), tv(p, qb), 1]
    n = agg[:, 6].sum()
    rng = np.random.default_rng(a.seed)
    idx = rng.integers(0, len(cases), size=(a.boot, len(cases)))
    tot = agg[idx].sum(1)                                  # (boot, 7)
    res = {"name_a": a.name_a, "name_b": a.name_b, "temperature": a.temperature, "T_a": TA, "T_b": TB,
           "n_decisions": int(n), "n_cases": len(cases), "boot": a.boot}
    for j, m in enumerate(("kl", "brier", "tv")):
        va, vb = agg[:, 2 * j].sum() / n, agg[:, 2 * j + 1].sum() / n
        d = (tot[:, 2 * j] - tot[:, 2 * j + 1]) / tot[:, 6]
        lo, hi = np.percentile(d, [2.5, 97.5])
        le, ge = ((d >= 0).sum() + 1) / (a.boot + 1), ((d <= 0).sum() + 1) / (a.boot + 1)  # add-one corrected
        res[m] = {"a": va, "b": vb, "diff": va - vb, "ci": [float(lo), float(hi)], "p_cluster_boot": min(1.0, 2 * min(le, ge))}
    json.dump(res, open(a.out, "w"), indent=1)
    print(f"{a.name_a} vs {a.name_b} [{a.temperature}] T=({TA},{TB}) n={int(n)} cases={len(cases)} | " + " | ".join(
        f"{m} {res[m]['a']:.4f} vs {res[m]['b']:.4f} d={res[m]['diff']:+.4f} [{res[m]['ci'][0]:+.4f},{res[m]['ci'][1]:+.4f}] "
        f"p={res[m]['p_cluster_boot']:.4f}" for m in ("kl", "brier", "tv")))


if __name__ == "__main__":
    main()
