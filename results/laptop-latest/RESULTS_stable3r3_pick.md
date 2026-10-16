# boolq stability search, round 2 (4 seeds/candidate, full training, judged by DEV ACCURACY not an early-loss proxy)

Stable = every seed's dev acc >= 0.70 and spread (max-min) <= 0.05.

| config | args | dev acc per seed | spread | stable | mean |
|---|---|---|---|---|---|
| lowlr_e6 **(chosen)** | `--lr 1e-5 --warmup-frac 0.06 --epochs 6` | 0.747, 0.761, 0.759, 0.749 | 0.014 | yes | 0.754 |
| verylow_e6 | `--lr 5e-6 --warmup-frac 0.1 --epochs 6` | 0.724, 0.717, 0.709, 0.705 | 0.018 | yes | 0.714 |

Chosen: `--lr 1e-5 --warmup-frac 0.06 --epochs 6`
