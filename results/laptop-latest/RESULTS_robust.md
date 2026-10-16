# Verdict on OrgBench — out/verdict-base

| task | acc | macro-F1 | ECE | n | mean lat (ms) | p50 lat (ms) |
|---|---|---|---|---|---|---|
| route_topic | 91.6% | 91.3% | 0.0209 | 2000 | 58.57 | 54.45 |
| signal_positive | 77.8% | 77.4% | 0.1169 | 872 | 29.15 | 29.10 |
| affect | 92.0% | 89.5% | 0.0151 | 2000 | 39.33 | 39.06 |
| **overall** | **89.3%** | **86.1%** | **0.0346** | **4872** | **45.40** | **41.47** |

_macro-F1 overall = mean of per-task macro-F1; acc/ECE/latency pooled across tasks; latency batched + warm._

## Robustness (R10): perturbations that must not change the answer
| task | acc | option-permutation acc | flip rate | prompt-paraphrase acc | flip rate |
|---|---|---|---|---|---|
| route_topic | 91.6% | 25.7% | 75.0% | 91.1% | 1.5% |
| signal_positive | 77.8% | 48.9% | 49.3% | 78.3% | 4.0% |
| affect | 92.0% | 19.7% | 79.5% | 91.8% | 2.5% |
