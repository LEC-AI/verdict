"""Pre-registered choice of a large-model stabilization recipe, using NO test-split information:
  (1) stall check on TRAINING loss: a config fails if any of its full-data runs on the seeds that stalled before
      (1 and 2) has mean training loss after epoch 1 above --stall-loss (healthy runs: ~1.0; stalled: ~1.2);
  (2) among configs that pass, the highest mean DEV accuracy wins; if none pass, keep the baseline recipe.
Writes the winning train_mq arguments to --out and a report."""
import argparse, json, os, statistics as st

CFG = {"base": "--lr 2e-5 --epochs 6", "warm20": "--lr 2e-5 --epochs 6 --warmup-frac 0.2",
       "llrd": "--lr 3e-5 --epochs 6 --warmup-frac 0.1 --llrd 0.9"}
ap = argparse.ArgumentParser(); ap.add_argument("--configs", default="warm20,llrd"); ap.add_argument("--stall-loss", type=float, default=1.1)
ap.add_argument("--out", default="out/chosen_stable.txt"); ap.add_argument("--report", default="RESULTS_stable_pick.md")
a = ap.parse_args()
rows, best = [], None
for c in a.configs.split(","):
    losses = []
    for sd in (1, 2):
        f = f"out/stab-{c}-full-s{sd}/train_log.json"
        if os.path.isfile(f):
            ep = json.load(open(f))["epochs"]; losses.append(ep[1]["train_loss"] if len(ep) > 1 else ep[0]["train_loss"])
    devs = [json.load(open(f"RESULTS_devs_{c}_s{sd}.json"))["typed"]["acc"] for sd in (0, 1) if os.path.isfile(f"RESULTS_devs_{c}_s{sd}.json")]
    stalled = any(x > a.stall_loss for x in losses) or len(losses) < 2
    mdev = st.mean(devs) if devs else float("nan")
    rows.append((c, losses, devs, stalled, mdev))
    if not stalled and devs and (best is None or mdev > best[4]):
        best = (c, losses, devs, stalled, mdev)
choice = best[0] if best else "base"
open(a.out, "w").write(CFG[choice] + "\n")
md = ["# Large-model stabilization choice (training-loss stall check on seeds 1-2 + DEV accuracy; no test data)", "",
      "| config | args | epoch-1 train loss, full data, seeds 1/2 | stalled | dev acc seeds 0/1 | dev mean |", "|---|---|---|---|---|---|"]
md += [f"| {c}{' **(chosen)**' if c == choice else ''} | `{CFG[c]}` | {', '.join(f'{x:.3f}' for x in l)} | {'yes' if s_ else 'no'} | "
       f"{', '.join(f'{x:.3f}' for x in d)} | {m:.3f} |" for c, l, d, s_, m in rows]
md += ["", "Reference (current recipe `--lr 2e-5 --epochs 6`): full-data seeds 1 and 2 stalled (epoch-1 train loss ~1.2); dev 0.798 +- 0.009.",
       f"Chosen: `{CFG[choice]}`"]
open(a.report, "w").write("\n".join(md) + "\n"); print("\n".join(md))
