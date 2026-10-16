# Large-model stabilization choice (training-loss stall check on seeds 1-2 + DEV accuracy; no test data)

| config | args | epoch-1 train loss, full data, seeds 1/2 | stalled | dev acc seeds 0/1 | dev mean |
|---|---|---|---|---|---|
| warm20 **(chosen)** | `--lr 2e-5 --epochs 6 --warmup-frac 0.2` | 0.957, 1.028 | no | 0.754, 0.818 | 0.786 |
| llrd | `--lr 3e-5 --epochs 6 --warmup-frac 0.1 --llrd 0.9` | 0.964, 0.957 | no | 0.780, 0.789 | 0.785 |

Reference (current recipe `--lr 2e-5 --epochs 6`): full-data seeds 1 and 2 stalled (epoch-1 train loss ~1.2); dev 0.798 +- 0.009.
Chosen: `--lr 2e-5 --epochs 6 --warmup-frac 0.2`
