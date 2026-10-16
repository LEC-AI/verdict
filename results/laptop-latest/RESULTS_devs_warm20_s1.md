# Verdict-MQ evaluation — out/devs-warm20-s1

## typed-decisions DEV (169 cases, 845 decisions)

| Model | Kind | Acc | Soft acc | Macro F1 | KL | TV | Brier | ECE | Score MAE | Within 1 level |
|---|---|---|---|---|---|---|---|---|---|---|
| devs-warm20-s1 | specialist | 0.818 | 0.639 | 0.755 | 0.081 | 0.130 | 0.045 | 0.179 | 0.215 | 0.967 |
| Laya typed-decisions ckpt (measured) | specialist? | 0.767 | 0.605 | 0.661 | 0.117 | 0.174 | 0.061 | 0.214 | 0.242 | 0.981 |
| ModernBERT-base (card) | specialist | 0.646 | 0.542 | 0.469 | 0.223 | 0.249 | 0.119 | 0.179 | 0.444 | 0.931 |
| TypeSafe Jev 1.13.0 (card) | general | 0.727 | 0.580 | 0.613 | 1.442 | 0.251 | 0.148 | 0.144 | 0.391 | 0.952 |
| meraGPT Decider 1 (card) | general | 0.768 | 0.608 | 0.641 | 0.096 | 0.149 | 0.052 | 0.180 | 0.219 | 0.984 |

by primitive: choice 82.8%, noul 86.4%, score 77.5%

