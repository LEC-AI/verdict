"""Pick a training recipe by mean DEV accuracy (typed_dev held-out TRAIN cases) — never by test.
Reads RESULTS_dev_<config>_s<seed>.json written by eval_mq.py --typed-split dev and writes the winning
config's train_mq arguments to --out. Usage: python3 scripts/pick_recipe.py --configs lr1e5e6,lr1e5e10,lr5e6e10"""
import argparse, glob, json, statistics as st

RECIPES = {
    "lr2e5e6": "--lr 2e-5 --epochs 6",
    "lr1e5e6": "--lr 1e-5 --epochs 6",
    "lr1e5e10": "--lr 1e-5 --epochs 10",
    "lr5e6e10": "--lr 5e-6 --epochs 10",
    "lin3e5e6": "--lr 3e-5 --epochs 6",
    "const2e5e6": "--lr 2e-5 --epochs 6 --schedule constant",
    "const1e5e6": "--lr 1e-5 --epochs 6 --schedule constant",
    "mix0": "",
    "mix1": "--option-mixer 1",
    "mix2": "--option-mixer 2",
    "lr2e5e6mix": "--lr 2e-5 --epochs 6 --option-mixer MIXER",
}
ap = argparse.ArgumentParser(); ap.add_argument("--configs", required=True); ap.add_argument("--out", default="out/chosen_large_recipe.txt")
ap.add_argument("--report", default="RESULTS_recipe_dev.md")
ap.add_argument("--prefix", default="RESULTS_dev_", help="result-file prefix, e.g. RESULTS_devb_ for the base model")
a = ap.parse_args()
rows, best = [], None
for c in a.configs.split(","):
    accs = [json.load(open(f))["typed"]["acc"] for f in sorted(glob.glob(f"{a.prefix}{c}_s*.json"))]
    if not accs:
        continue
    m, sd = st.mean(accs), (st.stdev(accs) if len(accs) > 1 else 0.0)
    rows.append((c, accs, m, sd))
    if best is None or m > best[2]:
        best = (c, accs, m, sd)
open(a.out, "w").write(RECIPES[best[0]] + "\n")
md = ["# Large-model recipe selection on the DEV split (15% of typed-decisions TRAIN cases, held out by case)", "",
      "| config | args | dev acc per seed | mean ± sd |", "|---|---|---|---|"]
md += [f"| {c}{' **(chosen)**' if c == best[0] else ''} | `{RECIPES[c]}` | {', '.join(f'{x:.3f}' for x in accs)} | {m:.3f} ± {sd:.3f} |" for c, accs, m, sd in rows]
open(a.report, "w").write("\n".join(md) + "\n"); print("\n".join(md)); print("chosen:", RECIPES[best[0]])
