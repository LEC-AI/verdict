# Verdict-MQ evaluation — out/stable-s32

## typed-decisions TEST (400 cases, 2000 decisions)

| Model | Kind | Acc | Soft acc | Macro F1 | KL | TV | Brier | ECE | Score MAE | Within 1 level |
|---|---|---|---|---|---|---|---|---|---|---|
| stable-s32 | specialist | 0.794 | 0.613 | 0.688 | 0.086 | 0.134 | 0.048 | 0.150 | 0.211 | 0.984 |
| Laya typed-decisions ckpt (measured) | specialist? | 0.767 | 0.605 | 0.661 | 0.117 | 0.174 | 0.061 | 0.214 | 0.242 | 0.981 |
| ModernBERT-base (card) | specialist | 0.646 | 0.542 | 0.469 | 0.223 | 0.249 | 0.119 | 0.179 | 0.444 | 0.931 |
| TypeSafe Jev 1.13.0 (card) | general | 0.727 | 0.580 | 0.613 | 1.442 | 0.251 | 0.148 | 0.144 | 0.391 | 0.952 |
| meraGPT Decider 1 (card) | general | 0.768 | 0.608 | 0.641 | 0.096 | 0.149 | 0.052 | 0.180 | 0.219 | 0.984 |

by primitive: choice 75.0%, noul 86.5%, score 77.5%

