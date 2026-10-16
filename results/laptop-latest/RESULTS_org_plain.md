# R1 plain-classifier baseline — answerdotai/ModernBERT-base (per-task seq-classification head)

| task | plain acc | plain macro-F1 | plain ECE | n |
|---|---|---|---|---|
| email_needs_reply | 91.3% | 90.1% | 0.049 | 323 |
| email_escalate | 96.3% | 60.8% | 0.038 | 347 |
| email_priority | 79.4% | 57.8% | 0.066 | 228 |

**Plain-head overall (n-weighted): 90.2%.** Compare per-task to Verdict (eval_orgbench.py); Verdict earns its keep if it matches/beats this AND is better calibrated with ONE shared model over arbitrary option sets.