# Large-model recipe selection on the DEV split (15% of typed-decisions TRAIN cases, held out by case)

| config | args | dev acc per seed | mean ± sd |
|---|---|---|---|
| lr2e5e6 **(chosen)** | `--lr 2e-5 --epochs 6` | 0.792, 0.805 | 0.798 ± 0.009 |
| lr1e5e6 | `--lr 1e-5 --epochs 6` | 0.793, 0.782 | 0.788 ± 0.008 |
| lr1e5e10 | `--lr 1e-5 --epochs 10` | 0.787, 0.792 | 0.789 ± 0.003 |
| lr5e6e10 | `--lr 5e-6 --epochs 10` | 0.786, 0.791 | 0.788 ± 0.003 |
| const2e5e6 | `--lr 2e-5 --epochs 6 --schedule constant` | 0.801, 0.757 | 0.779 ± 0.031 |
| const1e5e6 | `--lr 1e-5 --epochs 6 --schedule constant` | 0.795, 0.773 | 0.784 ± 0.016 |
