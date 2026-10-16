"""Paired significance between two systems' per-item predictions on the
SAME items (dumps from eval_orgbench.py / eval_baseline.py / eval_laya.py
--dump-preds). Items are matched on (task, idx); each dump must come from the
same cached val split (data/jsonl/<task>_val.jsonl) — --limit N in one system
simply restricts the comparison to the first N items of every task.

Per task and pooled:
  * accuracy of A and B, paired difference with a 10k-bootstrap 95% CI
  * exact McNemar test (two-sided, on the discordant pairs b = A right/B wrong,
    c = A wrong/B right); Holm-Bonferroni across tasks
  * top-label ECE-10 of each system where confidences exist, with a paired
    bootstrap CI on ECE(A) - ECE(B)

Pure python (no scipy). Usage:
  python scripts/significance.py --a preds_verdict.jsonl --b preds_judge.jsonl \
      --name-a Verdict --name-b Qwen2.5-7B --out RESULTS_significance.md
"""
from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict


def load(path):
    rows = {}
    for line in open(path):
        if line.strip():
            r = json.loads(line)
            rows[(r["task"], r["idx"])] = r
    return rows


def cluster_key(row, field):
    """The resampling unit for the bootstrap: row[field] if given (e.g. "case", a shared passage/article/state hash
    added to dumps so all decisions about the same passage move together), else the row's own (task, idx) -- i.e.
    every decision is its own singleton cluster, the ORIGINAL (uncorrected) behavior."""
    if not field:
        return None
    if field not in row:
        raise SystemExit(f"cluster field {field!r} missing from a prediction row (keys: {sorted(row)})")
    return row[field]


def ece10(rows):
    b = [[0, 0, 0.0] for _ in range(10)]
    for c, h in rows:
        k = min(int(c * 10), 9)
        b[k][0] += 1; b[k][1] += h; b[k][2] += c
    n = len(rows)
    return sum(abs(h / c - cf / c) * c for c, h, cf in b if c) / n if n else float("nan")


def mcnemar_exact(b, c):
    """Two-sided exact McNemar p-value on discordant counts b, c."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def holm(pvals):
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adj = [0.0] * len(pvals)
    running = 0.0
    m = len(pvals)
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * pvals[i])
        adj[i] = min(1.0, running)
    return adj


def analyse(pairs, rng, nboot, clusters=None):
    """pairs: list of (hitA, hitB, confA, confB). clusters: parallel list of cluster ids (e.g. one per case/passage);
    if given, the bootstrap resamples CLUSTERS with replacement (all of a cluster's decisions move together) instead
    of individual pairs, and the p-value is a cluster-bootstrap two-sided test (the fraction of resamples on the far
    side of zero, doubled) rather than exact McNemar, which assumes independent items and is anti-conservative when
    several decisions share a case/passage (found by independent review, 2026-09-27). The exact McNemar p is still
    reported alongside for continuity, clearly labeled as item-level and not the primary claim under clustering."""
    n = len(pairs)
    ha = [p[0] for p in pairs]; hb = [p[1] for p in pairs]
    acc_a, acc_b = sum(ha) / n, sum(hb) / n
    b = sum(1 for x, y in zip(ha, hb) if x and not y)
    c = sum(1 for x, y in zip(ha, hb) if y and not x)
    p_mc_itemlevel = mcnemar_exact(b, c)
    has_conf = all(p[2] is not None for p in pairs) and all(p[3] is not None for p in pairs)
    diffs, ece_diffs = [], []
    if clusters is None:
        for _ in range(nboot):
            idx = [rng.randrange(n) for _ in range(n)]
            diffs.append(sum(ha[i] for i in idx) / n - sum(hb[i] for i in idx) / n)
            if has_conf:
                ece_diffs.append(ece10([(pairs[i][2], ha[i]) for i in idx]) - ece10([(pairs[i][3], hb[i]) for i in idx]))
        p_boot = None
    else:
        groups = defaultdict(list)
        for i, cl in enumerate(clusters):
            groups[cl].append(i)
        cl_ids = list(groups)
        for _ in range(nboot):
            idx = [i for cl in (cl_ids[rng.randrange(len(cl_ids))] for _ in range(len(cl_ids))) for i in groups[cl]]
            m = len(idx)
            diffs.append(sum(ha[i] for i in idx) / m - sum(hb[i] for i in idx) / m)
            if has_conf:
                ece_diffs.append(ece10([(pairs[i][2], ha[i]) for i in idx]) - ece10([(pairs[i][3], hb[i]) for i in idx]))
        d_sorted = sorted(diffs)
        # add-one continuity correction (Davison & Hinkley 1997 s4.2.3): a raw count/nboot ratio can be exactly 0
        # when no resample crosses zero, which claims infinite certainty from a finite Monte Carlo sample -- a
        # randomization p-value should never be reported as exactly 0 (found in review, 2026-09-28). With
        # nboot=10000 the floor is 2*1/10001 ~= 0.0002, not 0; we report the corrected value directly rather than
        # capping display at an arbitrary "<0.0001".
        count_le0 = sum(1 for d in d_sorted if d <= 0)
        count_ge0 = sum(1 for d in d_sorted if d >= 0)
        frac_le0 = (count_le0 + 1) / (nboot + 1)
        frac_ge0 = (count_ge0 + 1) / (nboot + 1)
        p_boot = min(1.0, 2 * min(frac_le0, frac_ge0))
    diffs.sort(); ece_diffs.sort()
    lo, hi = diffs[int(0.025 * nboot)], diffs[int(0.975 * nboot) - 1]
    out = {"n": n, "acc_a": acc_a, "acc_b": acc_b, "diff": acc_a - acc_b, "ci": (lo, hi),
           "b": b, "c": c, "p_mcnemar": p_mc_itemlevel, "p_cluster_boot": p_boot,
           "n_clusters": len(groups) if clusters is not None else None}
    if has_conf:
        out["ece_a"] = ece10([(p[2], h) for p, h in zip(pairs, ha)])
        out["ece_b"] = ece10([(p[3], h) for p, h in zip(pairs, hb)])
        out["ece_ci"] = (ece_diffs[int(0.025 * nboot)], ece_diffs[int(0.975 * nboot) - 1])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True); ap.add_argument("--b", required=True)
    ap.add_argument("--name-a", default="A"); ap.add_argument("--name-b", default="B")
    ap.add_argument("--boot", type=int, default=10000); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--cluster-field", default=None,
                    help="row field giving the resampling unit: 'case' (a shared passage/state hash in standard-benchmark "
                         "dumps), 'idx' (typed-decisions dumps, where idx is already a per-case state hash), or 'auto' "
                         "('case' if every row has it, else 'idx' for typed-decisions dumps, else an error). If unset, "
                         "each decision is its own cluster (item-level, anti-conservative under clustering).")
    ap.add_argument("--out", default="RESULTS_significance.md")
    args = ap.parse_args()
    A, B = load(args.a), load(args.b)
    keys = sorted(set(A) & set(B))
    if not keys:
        raise SystemExit("no matched (task, idx) items between the two dumps")
    if args.cluster_field == "auto":
        rows = [A[k] for k in keys]
        if all("case" in r for r in rows):
            args.cluster_field = "case"
        elif all(":" in str(r["task"]) for r in rows):
            args.cluster_field = "idx"
        else:
            raise SystemExit("--cluster-field auto: dumps have no 'case' field and are not typed-decisions; "
                             "re-run eval_mq.py to add 'case' or pass --cluster-field explicitly")
        print(f"clustering by {args.cluster_field!r}")
    by_task = defaultdict(list); cl_by_task = defaultdict(list)
    for k in keys:
        a, b = A[k], B[k]
        by_task[k[0]].append((a["hit"], b["hit"], a.get("conf"), b.get("conf")))
        cl_by_task[k[0]].append(cluster_key(a, args.cluster_field) if args.cluster_field else None)
    rng = random.Random(args.seed)
    tasks = sorted(by_task)
    use_cl = bool(args.cluster_field)
    res = {t: analyse(by_task[t], rng, args.boot, cl_by_task[t] if use_cl else None) for t in tasks}
    res["overall"] = analyse([p for t in tasks for p in by_task[t]], rng, args.boot,
                             [c for t in tasks for c in cl_by_task[t]] if use_cl else None)
    p_for_holm = [res[t]["p_cluster_boot"] if use_cl else res[t]["p_mcnemar"] for t in tasks]
    adj = holm(p_for_holm)
    for t, p in zip(tasks, adj):
        res[t]["p_holm"] = p

    p_col = "cluster-bootstrap p" if use_cl else "McNemar p"
    note = (f" Clustered by `{args.cluster_field}` ({res['overall']['n_clusters']} clusters overall): the primary "
            f"p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for "
            f"continuity only)." if use_cl else "")
    md = [f"# Paired significance: {args.name_a} vs {args.name_b}", "",
          f"Matched items: {len(keys)} across {len(tasks)} tasks; {args.boot} bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.{note}", "",
          f"| task | n | {args.name_a} acc | {args.name_b} acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | {p_col} | Holm p | item-level McNemar p |",
          "|---|---|---|---|---|---|---|---|---|"]
    for t in tasks + ["overall"]:
        r = res[t]
        p_primary = r["p_cluster_boot"] if use_cl else r["p_mcnemar"]
        md.append(f"| {t} | {r['n']} | {r['acc_a']*100:.1f}% | {r['acc_b']*100:.1f}% | "
                  f"{r['diff']*100:+.1f} [{r['ci'][0]*100:+.1f}, {r['ci'][1]*100:+.1f}] | {r['b']} / {r['c']} | "
                  f"{p_primary:.2g} | {r.get('p_holm', float('nan')):.2g} | {r['p_mcnemar']:.2g} |")
    if any("ece_a" in res[t] for t in tasks):
        md += ["", f"| task | ECE-10 {args.name_a} | ECE-10 {args.name_b} | Δ ECE [95% CI] |", "|---|---|---|---|"]
        for t in tasks + ["overall"]:
            r = res[t]
            if "ece_a" in r:
                md.append(f"| {t} | {r['ece_a']:.4f} | {r['ece_b']:.4f} | {r['ece_a']-r['ece_b']:+.4f} [{r['ece_ci'][0]:+.4f}, {r['ece_ci'][1]:+.4f}] |")
    text = "\n".join(md)
    open(args.out, "w").write(text + "\n")
    json.dump(res, open(args.out.rsplit(".", 1)[0] + ".json", "w"), indent=2)
    print(text)


if __name__ == "__main__":
    main()
