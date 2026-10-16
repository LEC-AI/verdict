# Laya (default English checkpoint) on route_topic, signal_positive, affect — cache `data/jsonl`

Reported row = **ft-epoch2** (last epoch, no selection). Raw marker logits; post-hoc T fit on even half of val, ECE on odd half.

| stage | route_topic | signal_positive | affect | overall |
|---|---|---|---|---|
| 0-shot | 94.3% | 49.1% | 60.6% | 72.4% |
| ft-epoch0 | 94.0% | 94.2% | 93.7% | 93.9% |
| ft-epoch1 | 94.7% | 93.9% | 93.2% | 94.0% |
| ft-epoch2 | 94.8% | 93.9% | 93.8% | 94.3% |

| task | n | skipped | acc | macro-F1 | ECE raw | ECE raw (odd half) | ECE post-hoc (odd half) | T |
|---|---|---|---|---|---|---|---|---|
| route_topic | 2000 | 0 | 94.8% | 94.7% | 0.0480 | 0.0427 | 0.0092 | 2.656 |
| signal_positive | 872 | 0 | 93.9% | 93.9% | 0.0587 | 0.0693 | 0.0291 | 2.965 |
| affect | 2000 | 0 | 93.8% | 91.1% | 0.0374 | 0.0410 | 0.0247 | 1.725 |
