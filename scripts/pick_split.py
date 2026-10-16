"""Pre-registered selections for the split-depth study (SPLIT_PLAN.md), made on DEV (monitoring) splits only.

  k  : python3 scripts/pick_split.py k --tasks boolq,multirc,race --ks 0,2,4,8,22
       reads RESULTS_<task>_mqk<k>_s<seed>_dev.json; k* = the smallest k in {2,4,8} whose dev accuracy (mean over seeds,
       then over tasks) is within 0.5 points of the best of {2,4,8,22}; if none is, the best of {2,4,8}.
  lr : python3 scripts/pick_split.py lr --task boolq --kind pair --lrs 1e-5,2e-5,3e-5,5e-5
       reads RESULTS_<task>_<kind>_lr<lr>_s<seed>.json ("dev_acc"); picks the highest mean dev accuracy.
"""
import argparse, glob, json, statistics as st

ap = argparse.ArgumentParser()
ap.add_argument("mode", choices=["k", "lr"])
ap.add_argument("--tasks", default="boolq,multirc,race"); ap.add_argument("--ks", default="0,2,4,8,22")
ap.add_argument("--task"); ap.add_argument("--kind"); ap.add_argument("--lrs", default="1e-5,2e-5,3e-5,5e-5")
ap.add_argument("--out"); ap.add_argument("--report")
a = ap.parse_args()


def mean_sd(xs):
    return st.mean(xs), (st.stdev(xs) if len(xs) > 1 else 0.0)


if a.mode == "k":
    tasks, ks = a.tasks.split(","), [int(k) for k in a.ks.split(",")]
    per = {}                                                   # (task, k) -> [dev acc per seed]
    for t in tasks:
        for k in ks:
            fs = sorted(glob.glob(f"RESULTS_{t}_mqk{k}_s*_dev.json"))
            per[(t, k)] = [json.load(open(f))[t]["acc"] for f in fs]
    avail = [k for k in ks if all(per[(t, k)] for t in tasks)]
    score = {k: st.mean(st.mean(per[(t, k)]) for t in tasks) for k in avail}
    cand = [k for k in (2, 4, 8) if k in score]
    ref = max(score[k] for k in cand + ([22] if 22 in score else []))
    ok = [k for k in cand if score[k] >= ref - 0.005]
    chosen = min(ok) if ok else max(cand, key=score.get)
    md = ["# Split depth k* selection (DEV splits only; rule pre-registered in SPLIT_PLAN.md)", "",
          "| k | " + " | ".join(tasks) + " | mean |", "|---|" + "---|" * (len(tasks) + 1)]
    for k in avail:
        cells = [f"{mean_sd(per[(t, k)])[0]*100:.2f} ({len(per[(t, k)])} seeds)" for t in tasks]
        md.append(f"| {k}{' **(chosen)**' if k == chosen else ''} | " + " | ".join(cells) + f" | {score[k]*100:.2f} |")
    md += ["", f"best of {{2,4,8,22}} = {ref*100:.2f}; k* = {chosen}"]
    out, rep = a.out or "out/chosen_k.txt", a.report or "RESULTS_split_pick.md"
    open(out, "w").write(f"{chosen}\n")
else:
    rows, best = [], None
    for lr in a.lrs.split(","):
        fs = sorted(glob.glob(f"RESULTS_{a.task}_{a.kind}_lr{lr}_s*.json"))
        accs = [json.load(open(f))["dev_acc"] for f in fs]
        if not accs:
            continue
        m, sd = mean_sd(accs); rows.append((lr, accs, m, sd))
        if best is None or m > best[2]:
            best = (lr, accs, m, sd)
    md = [f"# Baseline lr selection, {a.task} {a.kind} (DEV split only)", "", "| lr | dev acc per seed | mean ± sd |", "|---|---|---|"]
    md += [f"| {lr}{' **(chosen)**' if lr == best[0] else ''} | {', '.join(f'{x*100:.2f}' for x in accs)} | {m*100:.2f} ± {sd*100:.2f} |"
           for lr, accs, m, sd in rows]
    out, rep = a.out or f"out/chosen_lr_{a.task}_{a.kind}.txt", a.report or f"RESULTS_lr_pick_{a.task}_{a.kind}.md"
    open(out, "w").write(f"{best[0]}\n")
open(rep, "w").write("\n".join(md) + "\n"); print("\n".join(md))
