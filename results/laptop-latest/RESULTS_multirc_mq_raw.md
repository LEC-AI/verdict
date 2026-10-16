# Verdict-MQ evaluation — out/multirc-mq-raw

## tasks

| task | n | acc | macro-F1 | ECE |
|---|---|---|---|---|
| multirc | 4848 | 70.1% | 69.9% | 0.0719 |
| multirc (official) | 953 questions | F1a 67.0 | EM 18.8 | |

## latency (multirc test cases, 13.98 questions per case, cuda:0, bf16)

| mode | batch (cases) | ms per case | ms per decision |
|---|---|---|---|
| packed | 1 | 18.91 | 1.35 |
| one-question-per-pass | 1 | 56.74 | 4.06 |
| packed | 8 | 21.71 | 1.55 |
| one-question-per-pass | 8 | 90.76 | 6.49 |
