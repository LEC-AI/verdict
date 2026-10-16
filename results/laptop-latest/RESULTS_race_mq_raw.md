# Verdict-MQ evaluation — out/race-mq-raw

## tasks

| task | n | acc | macro-F1 | ECE |
|---|---|---|---|---|
| race | 4934 | 76.4% | 76.3% | 0.0660 |

## latency (race test cases, 3.37 questions per case, cuda:0, bf16)

| mode | batch (cases) | ms per case | ms per decision |
|---|---|---|---|
| packed | 1 | 12.30 | 3.65 |
| one-question-per-pass | 1 | 18.07 | 5.37 |
| packed | 8 | 11.36 | 3.37 |
| one-question-per-pass | 8 | 32.16 | 9.55 |
