"""Generalized version of pick_stable.py for the (marker, k) sweep's own stall problem (2026-09-25): BoolQ at
(cls, k=22) stalled on 2 of 5 final seeds (2, 4), the same signature as the large model's original instability
(healthy epoch-1 train loss ~0.6-0.65, stalled ~0.65-0.68 and barely moving after). Pre-registered choice using NO
test-split information:
  (1) stall check on TRAINING loss: a config fails if either of its full-data runs on the seeds that stalled before
      (2 and 4) has mean training loss after epoch 1 above --stall-loss;
  (2) among configs that pass, the highest mean DEV accuracy wins; if none pass, keep the baseline recipe.
Writes the winning train_mq arguments to --out and a report."""
import argparse, json, os, statistics as st

CFG = {"base": "", "warm20": "--warmup-frac 0.2", "llrd": "--lr 1e-5 --warmup-frac 0.1 --llrd 0.9"}
ap = argparse.ArgumentParser()
ap.add_argument("--task", required=True)
ap.add_argument("--configs", default="warm20,llrd")
ap.add_argument("--stall-seeds", default="2,4")
ap.add_argument("--dev-seeds", default="0,1")
ap.add_argument("--stall-loss", type=float, default=0.665)  # observed epoch-1 loss: healthy <=0.656 (s0,1,3), stalled >=0.672 (s2,4)
ap.add_argument("--baseline-dev", type=float, default=None, help="the un-fixed recipe's own dev accuracy, for the report")
ap.add_argument("--out", default="out/chosen_stable2.txt")
ap.add_argument("--report", default="RESULTS_stable2_pick.md")
a = ap.parse_args()
stall_seeds = [int(s) for s in a.stall_seeds.split(",")]
dev_seeds = [int(s) for s in a.dev_seeds.split(",")]

rows, best = [], None
for c in a.configs.split(","):
    losses = []
    for sd in stall_seeds:
        f = f"out/stab2-{a.task}-{c}-full-s{sd}/train_log.json"
        if os.path.isfile(f):
            ep = json.load(open(f))["epochs"]; losses.append(ep[0]["train_loss"] if ep else float("inf"))
    devs = []
    for sd in dev_seeds:
        f = f"RESULTS_{a.task}_stab2{c}_s{sd}_dev.json"
        if os.path.isfile(f):
            devs.append(json.load(open(f))[a.task]["acc"])
    stalled = any(x > a.stall_loss for x in losses) or len(losses) < len(stall_seeds)
    mdev = st.mean(devs) if devs else float("nan")
    rows.append((c, losses, devs, stalled, mdev))
    if not stalled and devs and (best is None or mdev > best[4]):
        best = (c, losses, devs, stalled, mdev)
choice = best[0] if best else "base"
open(a.out, "w").write(CFG[choice] + "\n")
md = [f"# {a.task} (cls, k=22) stabilization choice (epoch-1 train-loss stall check on seeds {a.stall_seeds} + DEV accuracy; no test data)", "",
      "| config | args | epoch-1 train loss, full data, seeds " + a.stall_seeds + " | stalled | dev acc seeds " + a.dev_seeds + " | dev mean |",
      "|---|---|---|---|---|---|"]
md += [f"| {c}{' **(chosen)**' if c == choice else ''} | `{CFG[c]}` | {', '.join(f'{x:.3f}' for x in l)} | {'yes' if s_ else 'no'} | "
       f"{', '.join(f'{x:.3f}' for x in d)} | {m:.3f} |" for c, l, d, s_, m in rows]
if a.baseline_dev is not None:
    md.append(f"\nReference (unfixed recipe, seeds {a.stall_seeds}): 2 of 5 final test seeds stalled (~64-67% vs ~82% healthy); dev baseline {a.baseline_dev:.3f}.")
md.append(f"\nChosen: `{CFG[choice]}`")
open(a.report, "w").write("\n".join(md) + "\n"); print("\n".join(md))
