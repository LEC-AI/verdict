"""Joint (marker, k) selection on DEV splits only (SPLIT_PLAN.md amendment, 2026-09-24).

  python3 scripts/pick_split2.py --tasks boolq,multirc,race --markers mask,cls --ks 0,4,22

Reads RESULTS_<task>_mq<marker>k<k>_s0_dev.json. Writes "<marker> <k>" to --out (default out/chosen_marker_k.txt).
Selection: highest mean dev accuracy averaged over the given tasks; ties within 0.5 points of the best broken toward
the smaller k, then toward "cls".
"""
import argparse, glob, json, statistics as st

ap = argparse.ArgumentParser()
ap.add_argument("--tasks", default="boolq,multirc,race")
ap.add_argument("--markers", default="mask,cls")
ap.add_argument("--ks", default="0,4,22")
ap.add_argument("--out", default="out/chosen_marker_k.txt")
ap.add_argument("--report", default="RESULTS_split2_pick.md")
a = ap.parse_args()

tasks, markers, ks = a.tasks.split(","), a.markers.split(","), [int(k) for k in a.ks.split(",")]
per = {}                                                        # (task, marker, k) -> dev acc (seed 0)
for t in tasks:
    for mk in markers:
        for k in ks:
            fs = sorted(glob.glob(f"RESULTS_{t}_mq{mk}k{k}_s*_dev.json"))
            accs = [json.load(open(f))[t]["acc"] for f in fs]
            if accs:
                per[(t, mk, k)] = st.mean(accs)

cells = [(mk, k) for mk in markers for k in ks if all((t, mk, k) in per for t in tasks)]
score = {c: st.mean(per[(t, c[0], c[1])] for t in tasks) for c in cells}
best = max(score.values())
tied = [c for c in cells if score[c] >= best - 0.005]
chosen = min(tied, key=lambda c: (c[1], 0 if c[0] == "cls" else 1))

md = ["# Joint (marker, k) selection on DEV splits (pre-registered rule, SPLIT_PLAN.md)", "",
      "| marker | k | " + " | ".join(tasks) + " | mean |", "|---|---|" + "---|" * (len(tasks) + 1)]
for mk, k in sorted(cells):
    star = " **(chosen)**" if (mk, k) == chosen else ""
    cells_txt = [f"{per[(t, mk, k)]*100:.2f}" for t in tasks]
    md.append(f"| {mk} | {k}{star} | " + " | ".join(cells_txt) + f" | {score[(mk, k)]*100:.2f} |")
md += ["", f"chosen: marker={chosen[0]} k={chosen[1]}"]
open(a.out, "w").write(f"{chosen[0]} {chosen[1]}\n")
open(a.report, "w").write("\n".join(md) + "\n")
print("\n".join(md))
