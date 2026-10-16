# Verdict on OrgBench — out/verdict-org

| task | acc | macro-F1 | ECE | n | mean lat (ms) | p50 lat (ms) |
|---|---|---|---|---|---|---|
| email_needs_reply | 78.3% | 75.8% | 0.0388 | 323 | 11.57 | 11.62 |
| email_escalate | 98.8% | 49.7% | 0.1470 | 347 | 11.64 | 11.65 |
| email_priority | 55.3% | 39.6% | 0.1338 | 228 | 11.70 | 11.69 |
| **overall** | **80.4%** | **55.0%** | **0.0994** | **898** | **11.63** | **11.66** |

_macro-F1 overall = mean of per-task macro-F1; acc/ECE/latency pooled across tasks; latency batched + warm._

## Robustness (R10): perturbations that must not change the answer
| task | acc | option-permutation acc | flip rate | prompt-paraphrase acc | flip rate |
|---|---|---|---|---|---|
| email_needs_reply | 78.3% | 77.7% | 1.9% | - | - |
| email_escalate | 98.8% | 98.8% | 0.0% | - | - |
| email_priority | 55.3% | 46.1% | 19.3% | - | - |
