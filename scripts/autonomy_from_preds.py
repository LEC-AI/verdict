"""Held-out autonomy dial from per-decision prediction dumps (conf, hit), comparable across systems.

Decisions are split into a FIT half and an EVAL half by a hash of (task, idx), identical for every system. For each
target accuracy, the confidence threshold tau is the one giving maximum coverage with accuracy >= target on the FIT
half; the table reports the coverage and accuracy that tau actually delivers on the EVAL half. Also AURC.

  python3 scripts/autonomy_from_preds.py --dumps Laya=preds_laya_td.jsonl "Verdict-MQ-large s3=preds_final_chosen_s3.jsonl"
"""
import argparse
import hashlib
import json


def load(path):
    return [json.loads(l) for l in open(path) if l.strip()]


def fit_side(r):
    # CASE-level split (idx alone), not decision-level: for typed-decisions, task = "workflow:question" differs
    # across the 5 questions of one case while idx = hash(state) is shared, so hashing on (task, idx) let different
    # questions of the SAME case land on different sides -- 374 of 400 cases contributed to both halves (found by
    # independent review, 2026-09-27). Hashing on idx alone keeps every decision of one case on the same side.
    return int(hashlib.sha1(f"{r['idx']}".encode()).hexdigest()[:8], 16) % 2 == 0


def tau_for(rows, target):
    """The deployed rule is `conf >= tau` (a VALUE threshold), not `keep the top-k rows` (a position threshold) --
    if several rows share the exact confidence value at the cutoff, `conf >= tau` pulls in the WHOLE tied group, not
    just however many of them happened to sort before position k. Must accumulate whole tied-value groups, not
    individual rows, or the threshold's assumed on-data accuracy doesn't match what `conf >= tau` actually selects
    (found by independent review, 2026-09-28: Laya's nominal 95% threshold only achieved 94.85% under the old,
    position-based selection)."""
    groups = {}
    for r in rows:
        g = groups.setdefault(r["conf"], [0, 0])
        g[0] += r["hit"]; g[1] += 1
    hits = 0; count = 0; best = None
    for c in sorted(groups, reverse=True):
        h, n = groups[c]
        hits += h; count += n
        if hits / count >= target:
            best = c
    return best


def aurc(rows):
    """rows must already be the EVAL-only subset -- computing this over FIT+EVAL combined leaks the threshold-
    fitting half into the reported risk-coverage curve (found by independent review, 2026-09-28)."""
    s = sorted(rows, key=lambda r: -r["conf"]); err = 0; tot = 0.0
    for k, r in enumerate(s, 1):
        err += 1 - r["hit"]; tot += err / k
    return tot / len(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dumps", nargs="+", required=True, help="name=path")
    ap.add_argument("--targets", default="0.90,0.95,0.98")
    ap.add_argument("--out", default="RESULTS_autonomy.md")
    a = ap.parse_args()
    targets = [float(t) for t in a.targets.split(",")]
    md = ["# Held-out autonomy dial (tau fit on one half of the decisions, applied to the other half)", "",
          "| system | acc | AURC | " + " | ".join(f"target {t:.0%}: coverage / realized acc" for t in targets) + " |",
          "|---|---|---|" + "---|" * len(targets)]
    for spec in a.dumps:
        name, path = spec.split("=", 1)
        rows = load(path)
        fit = [r for r in rows if fit_side(r)]; ev = [r for r in rows if not fit_side(r)]
        cells = []
        for t in targets:
            tau = tau_for(fit, t)
            if tau is None:
                cells.append("unreachable"); continue
            cov = [r for r in ev if r["conf"] >= tau]
            cells.append(f"{len(cov)/len(ev)*100:.1f}% / {sum(r['hit'] for r in cov)/max(len(cov),1)*100:.1f}%")
        acc = sum(r["hit"] for r in rows) / len(rows)
        md.append(f"| {name} | {acc*100:.1f}% | {aurc(ev):.4f} | " + " | ".join(cells) + " |")
    md += ["", "Coverage = share of decisions auto-handled on the EVAL half; realized acc = accuracy on those decisions. "
           "Acc is the full-dataset accuracy (both halves); AURC is computed on the EVAL half only, matching coverage/accuracy."]
    open(a.out, "w").write("\n".join(md) + "\n"); print("\n".join(md))


if __name__ == "__main__":
    main()
