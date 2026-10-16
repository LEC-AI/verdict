# Held-out autonomy dial (tau fit on one half of the decisions, applied to the other half)

| system | acc | AURC | target 90%: coverage / realized acc | target 95%: coverage / realized acc | target 98%: coverage / realized acc |
|---|---|---|---|---|---|
| Laya | 76.7% | 0.1069 | 55.7% / 86.5% | 36.8% / 94.5% | 20.9% / 99.5% |
| Verdict-MQ large s40 | 79.8% | 0.0698 | 67.3% / 89.4% | 43.7% / 96.3% | 24.3% / 99.2% |
| Verdict-MQ large s41 | 80.3% | 0.0665 | 65.0% / 91.7% | 42.4% / 96.2% | 29.0% / 99.0% |
| Verdict-MQ large s42 | 80.8% | 0.0655 | 71.1% / 90.4% | 51.2% / 94.9% | 26.4% / 99.2% |
| Verdict-MQ large s43 | 80.0% | 0.0670 | 64.0% / 92.2% | 41.2% / 96.8% | 25.1% / 99.2% |
| Verdict-MQ large s44 | 79.5% | 0.0725 | 62.2% / 91.8% | 43.7% / 95.6% | 25.6% / 99.6% |
| Verdict-MQ base s0 | 76.3% | 0.1024 | 40.3% / 93.8% | 25.7% / 97.7% | 19.7% / 99.0% |
| Verdict-MQ base s1 | 77.5% | 0.0900 | 42.8% / 94.8% | 28.0% / 98.6% | 20.2% / 99.0% |
| Verdict-MQ base s2 | 76.1% | 0.0968 | 52.9% / 90.7% | 27.1% / 98.1% | 22.5% / 99.6% |

Coverage = share of decisions auto-handled on the EVAL half; realized acc = accuracy on those decisions. Acc is the full-dataset accuracy (both halves); AURC is computed on the EVAL half only, matching coverage/accuracy.
