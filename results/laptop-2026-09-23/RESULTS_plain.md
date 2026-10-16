# R1 plain-classifier baseline — answerdotai/ModernBERT-base (per-task seq-classification head)

| task | plain acc | plain macro-F1 | plain ECE | n |
|---|---|---|---|---|
| route_topic | 93.0% | 92.9% | 0.024 | 2000 |
| signal_positive | 94.4% | 94.4% | 0.035 | 872 |
| affect | 93.5% | 91.6% | 0.025 | 2000 |

**Plain-head overall (n-weighted): 93.5%.** Compare per-task to Verdict (eval_orgbench.py); Verdict earns its keep if it matches/beats this AND is better calibrated with ONE shared model over arbitrary option sets.