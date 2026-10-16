"""Risk-coverage curve data for Figure 1 (paper/figures/rc_*.csv): pool the given dumps' (conf, hit) pairs, rank by
confidence descending, and report cumulative accuracy at each coverage level (matches autonomy_from_preds.py's
ranking convention).

  python3 scripts/make_rc_curve.py --dumps preds_a.jsonl preds_b.jsonl --out figures/rc_x.csv
"""
import argparse
import json


def load(path):
    return [json.loads(l) for l in open(path) if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dumps", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--step", type=float, default=0.005)
    a = ap.parse_args()
    rows = [r for p in a.dumps for r in load(p)]
    s = sorted(rows, key=lambda r: -r["conf"])
    n = len(s)
    out = ["coverage,accuracy"]
    hits = 0
    next_cov = a.step
    for k, r in enumerate(s, 1):
        hits += r["hit"]
        cov = k / n
        if cov >= next_cov or k == n:
            out.append(f"{cov:.4f},{hits / k:.4f}")
            next_cov += a.step
    open(a.out, "w").write("\n".join(out) + "\n")
    print(f"wrote {a.out}: {len(out) - 1} points from {n} pooled decisions")


if __name__ == "__main__":
    main()
