"""BoolQ stability search, round 2 (2026-09-25): judges candidates by DEV ACCURACY STABILITY directly across 4 seeds
(full 3-epoch training each), not by an early-epoch training-loss proxy. Round 1 (pick_stable2.py) used epoch-1 loss
with a 2-seed check and failed: a look at the actual loss curves afterwards showed epoch-1 loss overlaps between seeds
that go on to succeed and seeds that go on to stall (e.g. two seeds with IDENTICAL 0.665 epoch-1 loss, one finished at
78.6% and the other at 64.0%) -- the signal separates much better by epoch 2, and cleanest of all by final accuracy,
which this script uses directly. Also: 4 seeds/candidate instead of 2, since 2-seed checks proved too small a sample
to reliably tell a real fix from a lucky pair.

A candidate is STABLE if every one of its 4 seeds' dev accuracy is >= --min-acc (default 0.70, well above the ~0.63
majority-class stall level) and the spread across them is <= --max-spread (default 0.05). Among stable candidates,
the highest mean dev accuracy wins. If none pass, writes "NONE" and the report says so -- no candidate is silently
forced through."""
import argparse, glob, json, statistics as st

CFG = {
    "warm30": "--lr 3e-5 --warmup-frac 0.3",
    "lowlr": "--lr 1e-5 --warmup-frac 0.06",
    "lowlr_warm20": "--lr 1e-5 --warmup-frac 0.2",
    "verylow": "--lr 5e-6 --warmup-frac 0.1",
    # round 3 (2026-09-25): round 2 showed lower lr trades stall risk for a lower accuracy ceiling within 3 epochs --
    # test whether more epochs lets a low lr reach the good optimum slowly instead of stalling at it quickly.
    "lowlr_e6": "--lr 1e-5 --warmup-frac 0.06 --epochs 6",
    "verylow_e6": "--lr 5e-6 --warmup-frac 0.1 --epochs 6",
}
ap = argparse.ArgumentParser()
ap.add_argument("--task", default="boolq")
ap.add_argument("--configs", default="warm30,lowlr,lowlr_warm20,verylow")
ap.add_argument("--seeds", default="10,11,12,13")
ap.add_argument("--min-acc", type=float, default=0.70)
ap.add_argument("--max-spread", type=float, default=0.05)
ap.add_argument("--out", default="out/chosen_stable3_boolq.txt")
ap.add_argument("--report", default="RESULTS_stable3_pick.md")
a = ap.parse_args()
seeds = [int(s) for s in a.seeds.split(",")]

rows, best = [], None
for c in a.configs.split(","):
    accs = []
    for sd in seeds:
        f = f"RESULTS_{a.task}_stab3{c}_s{sd}_dev.json"
        try:
            accs.append(json.load(open(f))[a.task]["acc"])
        except FileNotFoundError:
            pass
    complete = len(accs) == len(seeds)
    spread = (max(accs) - min(accs)) if accs else float("inf")
    stable = complete and min(accs) >= a.min_acc and spread <= a.max_spread
    mean = st.mean(accs) if accs else float("nan")
    rows.append((c, accs, spread, stable, mean))
    if stable and (best is None or mean > best[4]):
        best = (c, accs, spread, stable, mean)

choice = best[0] if best else "NONE"
open(a.out, "w").write((CFG[choice] if choice != "NONE" else "") + "\n")
md = [f"# {a.task} stability search, round 2 (4 seeds/candidate, full training, judged by DEV ACCURACY not an early-loss proxy)", "",
      f"Stable = every seed's dev acc >= {a.min_acc:.2f} and spread (max-min) <= {a.max_spread:.2f}.", "",
      "| config | args | dev acc per seed | spread | stable | mean |", "|---|---|---|---|---|---|"]
md += [f"| {c}{' **(chosen)**' if c == choice else ''} | `{CFG[c]}` | {', '.join(f'{x:.3f}' for x in acc)} | {sp:.3f} | {'yes' if st_ else 'no'} | {m:.3f} |"
       for c, acc, sp, st_, m in rows]
md.append(f"\nChosen: `{CFG.get(choice, '(none stable)')}`" if choice != "NONE" else
          "\n**No candidate was stable.** BoolQ is reported as an unresolved instability rather than forcing a pick.")
open(a.report, "w").write("\n".join(md) + "\n"); print("\n".join(md))
