"""Matched temperature-scaling calibration comparison (found missing by independent review, 2026-09-27): raw ECE
comparisons are not calibration-fair because each system's confidences may already be miscalibrated by different
amounts that a single scalar temperature would fix. This fits one temperature per system on a FIT half of the typed-
decisions test decisions (case-level split, same convention as autonomy_from_preds.py) and reports ECE on the other
(EVAL) half both raw and after each system's own best-fit temperature -- so the comparison is "does the accuracy/
calibration edge survive giving each system its own fair calibration knob", not just raw numbers.

Temperature scaling (T fit by grid search minimizing NLL on the FIT half) is monotonic, so it never changes which
option is predicted (argmax is invariant to positive T) -- only confidence values and thus ECE/Brier/KL change.

  python3 scripts/calibration_temp_scale.py --dumps Laya=preds_laya_td.jsonl "Verdict-MQ=preds_stable_cls_s42.jsonl"
"""
import argparse
import hashlib
import json
import math


def load(path):
    return [json.loads(l) for l in open(path) if l.strip()]


def fit_side(r):
    return int(hashlib.sha1(f"{r['idx']}".encode()).hexdigest()[:8], 16) % 2 == 0


def scaled_probs(probs, T):
    logp = [math.log(max(p, 1e-12)) / T for p in probs]
    m = max(logp)
    ex = [math.exp(x - m) for x in logp]
    s = sum(ex)
    return [x / s for x in ex]


def nll(rows, T):
    total = 0.0
    for r in rows:
        sp = scaled_probs(r["probs"], T)
        total -= math.log(max(sp[r["gold"]], 1e-12))
    return total / len(rows)


def fit_temperature(rows, lo=0.1, hi=5.0, steps=245):
    grid = [lo + i * (hi - lo) / steps for i in range(steps + 1)]
    best_T, best_nll = 1.0, float("inf")
    for T in grid:
        v = nll(rows, T)
        if v < best_nll:
            best_nll, best_T = v, T
    return best_T


def ece10(conf_hit):
    b = [[0, 0, 0.0] for _ in range(10)]
    for c, h in conf_hit:
        k = min(int(c * 10), 9)
        b[k][0] += 1; b[k][1] += h; b[k][2] += c
    n = len(conf_hit)
    return sum(abs(h / c - cf / c) * c for c, h, cf in b if c) / n if n else float("nan")


def calibrated(rows, T):
    """(idx, task) -> (calibrated top-conf, hit), restricted to the EVAL half, fitting T on the FIT half."""
    fit = [r for r in rows if fit_side(r)]
    ev = [r for r in rows if not fit_side(r)]
    Tf = fit_temperature(fit) if T is None else T
    out = {}
    for r in ev:
        out[(r["task"], r["idx"])] = (max(scaled_probs(r["probs"], Tf)), r["hit"])
    return out, Tf


def paired_ece_ci(a_cal, b_cal, rng, nboot=10000):
    """Case-cluster bootstrap CI on ECE(a) - ECE(b), matched by (task, idx), clustered by idx (case)."""
    keys = sorted(set(a_cal) & set(b_cal))
    groups = {}
    for k in keys:
        groups.setdefault(k[1], []).append(k)
    cl_ids = list(groups)
    diffs = []
    for _ in range(nboot):
        sample_keys = [k for cl in (cl_ids[rng.randrange(len(cl_ids))] for _ in range(len(cl_ids))) for k in groups[cl]]
        ea = ece10([a_cal[k] for k in sample_keys])
        eb = ece10([b_cal[k] for k in sample_keys])
        diffs.append(ea - eb)
    diffs.sort()
    point = ece10([a_cal[k] for k in keys]) - ece10([b_cal[k] for k in keys])
    lo, hi = diffs[int(0.025 * nboot)], diffs[int(0.975 * nboot) - 1]
    return point, lo, hi, len(keys), len(cl_ids)


def main():
    import random
    ap = argparse.ArgumentParser()
    ap.add_argument("--dumps", nargs="+", required=True, help="name=path, each row must have a 'probs' field")
    ap.add_argument("--pair-base", default=None, help="name=path: compute a paired case-cluster bootstrap CI on "
                    "calibrated ECE(each --dumps system) - ECE(this system), matched by (task, idx)")
    ap.add_argument("--out", default="RESULTS_calibration_temp.md")
    a = ap.parse_args()
    md = ["# Matched temperature-scaling calibration (T fit on one half of cases, applied to the other)", "",
          "| system | n (eval) | fitted T | raw ECE-10 (eval) | calibrated ECE-10 (eval) |", "|---|---|---|---|---|"]
    cal_by_name = {}
    for spec in a.dumps:
        name, path = spec.split("=", 1)
        rows = load(path)
        assert all("probs" in r for r in rows), f"{path}: missing 'probs' field, cannot temperature-scale"
        fit = [r for r in rows if fit_side(r)]
        ev = [r for r in rows if not fit_side(r)]
        T = fit_temperature(fit)
        raw_ece = ece10([(r["conf"], r["hit"]) for r in ev])
        cal_ece = ece10([(max(scaled_probs(r["probs"], T)), r["hit"]) for r in ev])
        md.append(f"| {name} | {len(ev)} | {T:.3f} | {raw_ece:.4f} | {cal_ece:.4f} |")
        cal_by_name[name] = (rows, T)
    md.append("")
    md.append("T fit by grid-search NLL minimization on the FIT half; argmax (and thus accuracy/hit) is unchanged by "
               "temperature scaling, only confidence. Fit/eval split is case-level (idx hash), matching the autonomy "
               "dial's convention.")
    if a.pair_base:
        base_name, base_path = a.pair_base.split("=", 1)
        base_rows = load(base_path)
        assert all("probs" in r for r in base_rows)
        base_cal, base_T = calibrated(base_rows, None)
        md += ["", f"## Paired case-cluster bootstrap CI on calibrated ECE difference vs {base_name} (T={base_T:.3f})", "",
               f"| system | n matched | n clusters | ECE diff (system - {base_name}) | 95% CI | excludes 0? |",
               "|---|---|---|---|---|---|"]
        rng = random.Random(0)
        for name, (rows, _) in cal_by_name.items():
            if name == base_name:
                continue
            sys_cal, _ = calibrated(rows, None)
            point, lo, hi, n, ncl = paired_ece_ci(sys_cal, base_cal, rng)
            excl = "yes" if (lo > 0 or hi < 0) else "no"
            md.append(f"| {name} | {n} | {ncl} | {point:+.4f} | [{lo:+.4f}, {hi:+.4f}] | {excl} |")
    text = "\n".join(md)
    open(a.out, "w").write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
