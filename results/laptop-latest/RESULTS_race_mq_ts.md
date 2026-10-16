# Verdict-MQ evaluation — out/race-mq-ts

## tasks

| task | n | acc | macro-F1 | ECE |
|---|---|---|---|---|
| race | 4934 | 74.9% | 74.9% | 0.0952 |

## latency (race test cases, 3.37 questions per case, cuda:0, bf16)

| mode | batch (cases) | ms per case | ms per decision |
|---|---|---|---|
| packed | 1 | 11.43 | 3.39 |
| one-question-per-pass | 1 | 18.43 | 5.47 |
| packed | 8 | 11.29 | 3.35 |
| one-question-per-pass | 8 | 31.82 | 9.45 |
