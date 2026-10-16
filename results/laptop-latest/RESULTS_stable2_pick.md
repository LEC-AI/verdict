# boolq (cls, k=22) stabilization choice (epoch-1 train-loss stall check on seeds 2,4 + DEV accuracy; no test data)

| config | args | epoch-1 train loss, full data, seeds 2,4 | stalled | dev acc seeds 2,4 | dev mean |
|---|---|---|---|---|---|
| warm20 | `--warmup-frac 0.2` | 0.670, 0.614 | yes | 0.618, 0.809 | 0.714 |
| llrd **(chosen)** | `--lr 1e-5 --warmup-frac 0.1 --llrd 0.9` | 0.655, 0.655 | no | 0.684, 0.684 | 0.684 |

Reference (unfixed recipe, seeds 2,4): 2 of 5 final test seeds stalled (~64-67% vs ~82% healthy); dev baseline 0.644.

Chosen: `--lr 1e-5 --warmup-frac 0.1 --llrd 0.9`
