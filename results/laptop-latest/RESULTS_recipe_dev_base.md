# Large-model recipe selection on the DEV split (15% of typed-decisions TRAIN cases, held out by case)

| config | args | dev acc per seed | mean ± sd |
|---|---|---|---|
| lin3e5e6 | `--lr 3e-5 --epochs 6` | 0.762, 0.763 | 0.763 ± 0.001 |
| const2e5e6 | `--lr 2e-5 --epochs 6 --schedule constant` | 0.757, 0.753 | 0.755 ± 0.003 |
| const1e5e6 **(chosen)** | `--lr 1e-5 --epochs 6 --schedule constant` | 0.772, 0.756 | 0.764 ± 0.011 |
