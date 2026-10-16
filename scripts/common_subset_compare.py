"""Common-subset comparison (found missing by independent review, 2026-09-27): Jev's reported accuracy on RACE/BoolQ/
MultiRC excludes items where the API call failed (transient errors), while Verdict-MQ/baseline/Laya, run locally,
score every item. "Identical test items" was therefore not quite true -- Jev's denominator is smaller. This
recomputes every system's accuracy restricted to the exact common subset of items Jev succeeded on, so the
comparison is apples-to-apples, and reports the excluded item count/rate.

  python3 scripts/common_subset_compare.py --jev preds_jev_race.jsonl \
      --others "Verdict-MQ s0=preds_race_mqclsk22_s0.jsonl" "Baseline s0=preds_race_mc_lr3e-5_s0.jsonl" "Laya=preds_laya_race.jsonl"
"""
import argparse
import json


def load(path):
    return {(r["task"], r["idx"]): r for r in (json.loads(l) for l in open(path) if l.strip())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jev", required=True)
    ap.add_argument("--others", nargs="+", required=True, help="name=path")
    a = ap.parse_args()
    jev = load(a.jev)
    jev_keys = set(jev)
    jev_acc_full = sum(r["hit"] for r in jev.values()) / len(jev)
    print(f"Jev: {len(jev)} items succeeded, full-subset acc {jev_acc_full*100:.1f}%")
    for spec in a.others:
        name, path = spec.split("=", 1)
        rows = load(path)
        full_acc = sum(r["hit"] for r in rows.values()) / len(rows)
        common = jev_keys & set(rows)
        missing_from_jev = len(rows) - len(common)
        common_acc = sum(rows[k]["hit"] for k in common) / len(common)
        print(f"{name}: n={len(rows)} full acc {full_acc*100:.1f}% | common subset n={len(common)} "
              f"(excluded {missing_from_jev}, {missing_from_jev/len(rows)*100:.1f}%) acc {common_acc*100:.1f}%")


if __name__ == "__main__":
    main()
