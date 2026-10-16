# Verdict on OrgBench — out/verdict-base-shuf

| task | acc | macro-F1 | ECE | n | mean lat (ms) | p50 lat (ms) |
|---|---|---|---|---|---|---|
| route_topic | 90.3% | 90.1% | 0.0329 | 2000 | 3.31 | 3.11 |
| signal_positive | 78.6% | 78.2% | 0.0981 | 872 | 1.77 | 1.74 |
| affect | 92.5% | 90.2% | 0.0121 | 2000 | 2.34 | 2.33 |
| **overall** | **89.1%** | **86.1%** | **0.0338** | **4872** | **2.64** | **2.48** |

_macro-F1 overall = mean of per-task macro-F1; acc/ECE/latency pooled across tasks; latency batched + warm._

## Robustness (R10): perturbations that must not change the answer
| task | acc | option-permutation acc | flip rate | prompt-paraphrase acc | flip rate |
|---|---|---|---|---|---|
| route_topic | 90.3% | 90.3% | 2.5% | 87.8% | 5.9% |
| signal_positive | 78.6% | 78.8% | 1.4% | 79.1% | 1.9% |
| affect | 92.5% | 92.6% | 2.6% | 91.6% | 2.6% |
