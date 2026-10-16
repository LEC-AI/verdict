# Large-model recipe selection on the DEV split (15% of typed-decisions TRAIN cases, held out by case)

| config | args | dev acc per seed | mean ± sd |
|---|---|---|---|
| lr2e5e6 **(chosen)** | `--lr 2e-5 --epochs 6` | 0.792, 0.805 | 0.798 ± 0.009 |
| lr2e5e6mix | `--lr 2e-5 --epochs 6 --option-mixer MIXER` | 0.800, 0.794 | 0.797 ± 0.004 |
