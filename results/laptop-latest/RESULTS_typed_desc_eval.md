# typed-decisions TEST — out/verdict-typed-desc

overall **58.6%** (n=2000), ECE 0.066, option-permuted 34.9%

by primitive: choice 60.8%, noul 69.8%, score 48.4%
by workflow: agent_trace_observability 68.0%, customer_service 47.8%, invoice_processing 56.8%, security_incidents 61.6%

| Model | Kind | Acc | Soft acc | Macro F1 | KL | TV | Brier | ECE | Score MAE | Within 1 level |
|---|---|---|---|---|---|---|---|---|---|---|
| verdict-typed-desc | specialist (trained on these workflows) | 0.586 | 0.499 | 0.440 | 0.245 | 0.255 | 0.141 | 0.066 | 0.455 | 0.875 |
| ModernBERT-base (card) | specialist | 0.646 | 0.542 | 0.469 | 0.223 | 0.249 | 0.119 | 0.179 | 0.444 | 0.931 |
| TypeSafe Jev 1.13.0 (card) | general | 0.727 | 0.580 | 0.613 | 1.442 | 0.251 | 0.148 | 0.144 | 0.391 | 0.952 |
| meraGPT Decider 1 (card) | general | 0.768 | 0.608 | 0.641 | 0.096 | 0.149 | 0.052 | 0.180 | 0.219 | 0.984 |

Card ceilings: perfect scenario understanding 0.704, teacher self-agreement 0.735. KL/TV/Brier definitions reproduce the card's Uniform row exactly; ECE/Prior use unstated card choices.
