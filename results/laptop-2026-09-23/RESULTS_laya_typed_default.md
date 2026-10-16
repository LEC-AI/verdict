# Laya (default) on typed-decisions TEST, native questions — measured by us

overall **35.9%** (n=2000 decisions, 400 cases), ECE-10 0.178, 15s

by primitive: choice 28.3%, noul 48.5%, score 32.0%
by workflow: agent_trace_observability 38.4%, customer_service 37.8%, invoice_processing 36.0%, security_incidents 31.2%

| Model | Kind | Acc | Soft acc | Macro F1 | KL | TV | Brier | ECE | Score MAE | Within 1 level |
|---|---|---|---|---|---|---|---|---|---|---|
| Laya (default) | see note | 0.358 | 0.347 | 0.239 | 0.570 | 0.410 | 0.316 | 0.178 | 0.695 | 0.726 |

Mode: the 'typed-decisions' checkpoint may have been fitted on this benchmark's train split (specialist); the default checkpoint is a general model scored zero-shot. Card leaderboard: Decider 1 0.768, Jev 0.727 (general).
