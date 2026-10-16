# Laya (default English checkpoint) on typed_decisions — cache `data/jsonl`

Reported row = **ft-epoch2** (last epoch, no selection). Raw marker logits; post-hoc T fit on even half of val, ECE on odd half.

| stage | typed_decisions | overall |
|---|---|---|
| 0-shot | 36.0% | 36.0% |
| ft-epoch0 | 73.7% | 73.7% |
| ft-epoch1 | 76.4% | 76.4% |
| ft-epoch2 | 77.4% | 77.4% |

| task | n | skipped | acc | macro-F1 | ECE raw | ECE raw (odd half) | ECE post-hoc (odd half) | T |
|---|---|---|---|---|---|---|---|---|
| typed_decisions | 2000 | 0 | 77.4% | 77.6% | 0.1811 | 0.1968 | 0.0360 | 3.249 |

typed-decisions card metrics (reported stage):
| Model | Kind | Acc | Soft acc | Macro F1 | KL | TV | Brier | ECE | Score MAE | Within 1 level |
|---|---|---|---|---|---|---|---|---|---|---|
| Laya (default) ft-epoch2 | specialist | 0.774 | 0.606 | 0.667 | 1.857 | 0.354 | 0.281 | 0.181 | 0.369 | 0.978 |
