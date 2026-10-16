# Laya (typed-decisions) on typed-decisions TEST, native questions — measured by us

overall **76.7%** (n=2000 decisions, 400 cases), ECE-10 0.214, 15s

by primitive: choice 73.2%, noul 85.7%, score 72.6%
by workflow: agent_trace_observability 73.2%, customer_service 76.4%, invoice_processing 80.4%, security_incidents 76.8%

| Model | Kind | Acc | Soft acc | Macro F1 | KL | TV | Brier | ECE | Score MAE | Within 1 level |
|---|---|---|---|---|---|---|---|---|---|---|
| Laya (typed-decisions) | see note | 0.767 | 0.605 | 0.661 | 0.117 | 0.174 | 0.061 | 0.214 | 0.242 | 0.981 |

Mode: the 'typed-decisions' checkpoint may have been fitted on this benchmark's train split (specialist); the default checkpoint is a general model scored zero-shot. Card leaderboard: Decider 1 0.768, Jev 0.727 (general).
