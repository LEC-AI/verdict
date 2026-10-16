# Held-out autonomy dial (tau fit on one half of the decisions, applied to the other half)

| system | acc | AURC | target 90%: coverage / realized acc | target 95%: coverage / realized acc | target 98%: coverage / realized acc |
|---|---|---|---|---|---|
| Laya (calibrated) | 76.7% | 0.1017 | 58.4% / 89.0% | 35.7% / 94.4% | 25.4% / 97.6% |
| Verdict-MQ s40 (calibrated) | 79.8% | 0.0695 | 68.1% / 90.0% | 44.4% / 95.9% | 28.6% / 98.2% |
| Verdict-MQ s41 (calibrated) | 80.3% | 0.0669 | 67.9% / 91.1% | 52.3% / 93.8% | 28.8% / 99.0% |
| Verdict-MQ s42 (calibrated) | 80.8% | 0.0680 | 71.1% / 88.8% | 50.5% / 95.2% | 28.7% / 97.9% |
| Verdict-MQ s43 (calibrated) | 80.0% | 0.0682 | 72.7% / 88.9% | 39.3% / 96.7% | 27.0% / 99.3% |
| Verdict-MQ s44 (calibrated) | 79.5% | 0.0723 | 66.0% / 91.5% | 48.5% / 95.0% | 29.6% / 98.0% |

Coverage = share of decisions auto-handled on the EVAL half; realized acc = accuracy on those decisions. Acc is the full-dataset accuracy (both halves); AURC is computed on the EVAL half only, matching coverage/accuracy.
