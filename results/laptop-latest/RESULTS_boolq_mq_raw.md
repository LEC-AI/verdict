# Verdict-MQ evaluation — out/boolq-mq-raw

## tasks

| task | n | acc | macro-F1 | ECE |
|---|---|---|---|---|
| boolq | 3270 | 64.6% | 59.9% | 0.0948 |

## latency (boolq test cases, 1.31 questions per case, cuda:0, bf16)

| mode | batch (cases) | ms per case | ms per decision |
|---|---|---|---|
| packed | 1 | 8.14 | 6.20 |
| one-question-per-pass | 1 | 8.46 | 6.44 |
| packed | 8 | 3.25 | 2.48 |
| one-question-per-pass | 8 | 3.54 | 2.69 |
