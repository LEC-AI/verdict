# Large-model recipe selection on the DEV split (15% of typed-decisions TRAIN cases, held out by case)

| config | args | dev acc per seed | mean ± sd |
|---|---|---|---|
| mix0 | `` | 0.762, 0.763 | 0.763 ± 0.001 |
| mix1 | `--option-mixer 1` | 0.764, 0.764 | 0.764 ± 0.000 |
| mix2 **(chosen)** | `--option-mixer 2` | 0.779, 0.768 | 0.773 ± 0.008 |
