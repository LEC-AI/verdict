# Laya (default English checkpoint) on email_needs_reply, email_escalate, email_priority — cache `data/jsonl_orgcons`

Reported row = **ft-epoch2** (last epoch, no selection). Raw marker logits; post-hoc T fit on even half of val, ECE on odd half.

| stage | email_needs_reply | email_escalate | email_priority | overall |
|---|---|---|---|---|
| 0-shot | 53.9% | 89.9% | 26.3% | 60.8% |
| ft-epoch0 | 91.6% | 97.7% | 72.8% | 89.2% |
| ft-epoch1 | 93.8% | 98.6% | 80.3% | 92.2% |
| ft-epoch2 | 93.5% | 95.1% | 80.3% | 90.8% |

| task | n | skipped | acc | macro-F1 | ECE raw | ECE raw (odd half) | ECE post-hoc (odd half) | T |
|---|---|---|---|---|---|---|---|---|
| email_needs_reply | 323 | 0 | 93.5% | 92.7% | 0.0631 | 0.0721 | 0.0292 | 3.043 |
| email_escalate | 347 | 0 | 95.1% | 58.3% | 0.0498 | 0.0477 | 0.0290 | 2.548 |
| email_priority | 228 | 0 | 80.3% | 59.5% | 0.1812 | 0.1808 | 0.0726 | 2.905 |
