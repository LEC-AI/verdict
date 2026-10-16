"""Typed-decisions metrics as reported on the benchmark card
(LocalLLaMA/typed-decisions): Acc, Soft acc, Macro F1, KL, TV, Brier, ECE,
Score MAE, Within-1-level. Pure python; validated by reproducing the card's
Uniform / Prior reference rows (scripts/typed_reference.py).

Each decision row = dict(q=[pred probs over option keys], p=[gold probs, same order],
                         gold=int gold index, qtype, key=(workflow, question)).
"""
from __future__ import annotations

import math
from collections import defaultdict

EPS = 1e-6


def _ece(rows, nb=10):
    b = [[0, 0, 0.0] for _ in range(nb)]
    for c, h in rows:
        k = min(int(c * nb), nb - 1); b[k][0] += 1; b[k][1] += h; b[k][2] += c
    n = len(rows)
    return sum(abs(h / c - cf / c) * c for c, h, cf in b if c) / n if n else float("nan")


def summarize(rows, brier_mode="sum"):
    n = len(rows)
    acc = soft = kl = tv = brier = 0.0
    conf_rows = []
    f1_by_key = defaultdict(lambda: ([], []))
    mae, w1, n_score = 0.0, 0, 0
    for r in rows:
        q, p, g = r["q"], r["p"], r["gold"]
        top = max(range(len(q)), key=q.__getitem__)
        hit = int(top == g)
        acc += hit
        soft += p[top]
        kl += sum(pi * math.log((pi + EPS) / (qi + EPS)) for pi, qi in zip(p, q) if pi > 0)
        tv += 0.5 * sum(abs(pi - qi) for pi, qi in zip(p, q))
        sq = sum((qi - pi) ** 2 for pi, qi in zip(p, q))
        brier += sq if brier_mode == "sum" else sq / len(q)
        conf_rows.append((q[top], hit))
        ys, ps = f1_by_key[r["key"]]; ys.append(g); ps.append(top)
        if r["qtype"] == "score":
            n_score += 1
            eq = sum(i * qi for i, qi in enumerate(q)); ep = sum(i * pi for i, pi in enumerate(p))
            mae += abs(eq - ep)
            w1 += int(abs(top - g) <= 1)
    f1s = []
    for (ys, ps) in f1_by_key.values():
        classes = sorted(set(ys) | set(ps)); fs = []
        for c in classes:
            tp = sum(1 for a, b in zip(ys, ps) if a == c and b == c)
            fp = sum(1 for a, b in zip(ys, ps) if a != c and b == c)
            fn = sum(1 for a, b in zip(ys, ps) if a == c and b != c)
            pr = tp / (tp + fp) if tp + fp else 0.0; rc = tp / (tp + fn) if tp + fn else 0.0
            fs.append(2 * pr * rc / (pr + rc) if pr + rc else 0.0)
        f1s.append(sum(fs) / len(fs) if fs else 0.0)
    return {"n": n, "acc": acc / n, "soft_acc": soft / n, "macro_f1": sum(f1s) / max(len(f1s), 1),
            "kl": kl / n, "tv": tv / n, "brier": brier / n, "ece": _ece(conf_rows),
            "score_mae": mae / n_score if n_score else None, "within1": w1 / n_score if n_score else None}


def md_row(name, kind, m):
    f = lambda x, d=3: "-" if x is None else f"{x:.{d}f}"
    return (f"| {name} | {kind} | {f(m['acc'])} | {f(m['soft_acc'])} | {f(m['macro_f1'])} | {f(m['kl'])} | {f(m['tv'])} | "
            f"{f(m['brier'])} | {f(m['ece'])} | {f(m['score_mae'])} | {f(m['within1'])} |")


MD_HEADER = ["| Model | Kind | Acc | Soft acc | Macro F1 | KL | TV | Brier | ECE | Score MAE | Within 1 level |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
