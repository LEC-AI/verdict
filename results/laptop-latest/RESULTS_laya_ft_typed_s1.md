# Laya (default English checkpoint) on typed_decisions — cache `data/jsonl`

Reported row = **ft-epoch2** (last epoch, no selection). Raw marker logits; post-hoc T fit on even half of val, ECE on odd half.

| stage | typed_decisions | overall |
|---|---|---|
| 0-shot | 36.0% | 36.0% |
| ft-epoch0 | 71.8% | 71.8% |
| ft-epoch1 | 77.0% | 77.0% |
| ft-epoch2 | 76.7% | 76.7% |

| task | n | skipped | acc | macro-F1 | ECE raw | ECE raw (odd half) | ECE post-hoc (odd half) | T |
|---|---|---|---|---|---|---|---|---|
| typed_decisions | 2000 | 0 | 76.7% | 77.0% | 0.1878 | 0.1983 | 0.0377 | 3.127 |

typed-decisions card metrics (reported stage):
| Model | Kind | Acc | Soft acc | Macro F1 | KL | TV | Brier | ECE | Score MAE | Within 1 level |
|---|---|---|---|---|---|---|---|---|---|---|
| Laya (default) ft-epoch2 | specialist | 0.767 | 0.603 | 0.645 | 1.794 | 0.357 | 0.286 | 0.188 | 0.359 | 0.980 |
