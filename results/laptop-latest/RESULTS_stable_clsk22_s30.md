# Verdict-MQ evaluation — out/stable-cls-k22-s30

## typed-decisions TEST (400 cases, 2000 decisions)

| Model | Kind | Acc | Soft acc | Macro F1 | KL | TV | Brier | ECE | Score MAE | Within 1 level |
|---|---|---|---|---|---|---|---|---|---|---|
| stable-cls-k22-s30 | specialist | 0.804 | 0.617 | 0.708 | 0.080 | 0.128 | 0.044 | 0.163 | 0.202 | 0.985 |
| Laya typed-decisions ckpt (measured) | specialist? | 0.767 | 0.605 | 0.661 | 0.117 | 0.174 | 0.061 | 0.214 | 0.242 | 0.981 |
| ModernBERT-base (card) | specialist | 0.646 | 0.542 | 0.469 | 0.223 | 0.249 | 0.119 | 0.179 | 0.444 | 0.931 |
| TypeSafe Jev 1.13.0 (card) | general | 0.727 | 0.580 | 0.613 | 1.442 | 0.251 | 0.148 | 0.144 | 0.391 | 0.952 |
| meraGPT Decider 1 (card) | general | 0.768 | 0.608 | 0.641 | 0.096 | 0.149 | 0.052 | 0.180 | 0.219 | 0.984 |

by primitive: choice 76.5%, noul 87.0%, score 78.4%

