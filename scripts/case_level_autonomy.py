"""Case-level (joint-acceptance) automation rate, as opposed to the per-decision coverage
autonomy_from_preds.py reports (found missing by independent review, 2026-09-28: per-decision coverage numbers
say nothing about how many whole CASES could be automated end-to-end if a real deployment requires every decision
about a case -- needs-reply, urgency, owner, etc. -- to individually clear the confidence bar before the case is
handled without a human). Uses the exact same FIT/EVAL split and threshold-fitting as autonomy_from_preds.py, then
additionally requires ALL of a case's decisions in the EVAL half to be >= tau for that case to count as auto-handled.

  python3 scripts/case_level_autonomy.py --dumps Laya=preds_laya_td.jsonl "Verdict-MQ s42=preds_stable_cls_s42.jsonl"
"""
import argparse
from collections import defaultdict

from autonomy_from_preds import fit_side, load, tau_for


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dumps", nargs="+", required=True, help="name=path")
    ap.add_argument("--target", type=float, default=0.90)
    ap.add_argument("--out", default="RESULTS_case_level_autonomy.md")
    a = ap.parse_args()
    md = ["# Case-level (joint-acceptance) vs per-decision automation, target "
          f"{a.target:.0%}", "",
          "| system | decision coverage | case coverage (all 5 decisions clear tau) | whole-case accuracy |",
          "|---|---|---|---|"]
    for spec in a.dumps:
        name, path = spec.split("=", 1)
        rows = load(path)
        fit = [r for r in rows if fit_side(r)]
        ev = [r for r in rows if not fit_side(r)]
        tau = tau_for(fit, a.target)
        dec_cov = sum(1 for r in ev if r["conf"] >= tau) / len(ev)
        by_case = defaultdict(list)
        for r in ev:
            by_case[r["idx"]].append(r)
        n_cases = len(by_case)
        auto_cases = [cr for cr in by_case.values() if all(r["conf"] >= tau for r in cr)]
        case_cov = len(auto_cases) / n_cases
        case_acc = (sum(1 for cr in auto_cases if all(r["hit"] for r in cr)) / len(auto_cases)
                    if auto_cases else float("nan"))
        md.append(f"| {name} | {dec_cov*100:.1f}% | {case_cov*100:.1f}% ({len(auto_cases)}/{n_cases}) | {case_acc*100:.1f}% |")
    md.append("")
    md.append("Decision coverage/tau match autonomy_from_preds.py exactly (same FIT/EVAL split, same threshold). "
               "Case coverage additionally requires every one of a case's decisions in the EVAL half to individually "
               "clear tau. Whole-case accuracy is over only the auto-handled cases, and only counts a case correct "
               "if every one of its decisions is correct.")
    open(a.out, "w").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
