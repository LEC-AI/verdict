# Verdict-MQ evaluation — out/mq-typed

## typed-decisions TEST (400 cases, 2000 decisions)

| Model | Kind | Acc | Soft acc | Macro F1 | KL | TV | Brier | ECE | Score MAE | Within 1 level |
|---|---|---|---|---|---|---|---|---|---|---|
| mq-typed | specialist | 0.692 | 0.559 | 0.560 | 0.184 | 0.207 | 0.103 | 0.101 | 0.353 | 0.936 |
| Laya typed-decisions ckpt (measured) | specialist? | 0.767 | 0.605 | 0.661 | 0.117 | 0.174 | 0.061 | 0.214 | 0.242 | 0.981 |
| ModernBERT-base (card) | specialist | 0.646 | 0.542 | 0.469 | 0.223 | 0.249 | 0.119 | 0.179 | 0.444 | 0.931 |
| TypeSafe Jev 1.13.0 (card) | general | 0.727 | 0.580 | 0.613 | 1.442 | 0.251 | 0.148 | 0.144 | 0.391 | 0.952 |
| meraGPT Decider 1 (card) | general | 0.768 | 0.608 | 0.641 | 0.096 | 0.149 | 0.052 | 0.180 | 0.219 | 0.984 |

by primitive: choice 67.0%, noul 78.5%, score 63.7%

## latency (typed-decisions test cases, 5.0 questions per case, cuda:0, bf16)

| mode | batch (cases) | ms per case | ms per decision |
|---|---|---|---|
| packed | 1 | 9.62 | 1.92 |
| one-question-per-pass | 1 | 12.54 | 2.51 |
| packed | 8 | 5.75 | 1.15 |
| one-question-per-pass | 8 | 15.36 | 3.07 |
