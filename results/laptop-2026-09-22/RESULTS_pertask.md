# Verdict on OrgBench — out/verdict-base

| task | acc | macro-F1 | ECE | n | mean lat (ms) | p50 lat (ms) |
|---|---|---|---|---|---|---|
| route_topic | 91.6% | 91.3% | 0.0209 | 2000 | 3.01 | 2.87 |
| signal_positive | 77.8% | 77.4% | 0.1169 | 872 | 1.55 | 1.52 |
| affect | 92.0% | 89.5% | 0.0151 | 2000 | 2.09 | 2.09 |
| **overall** | **89.3%** | **86.1%** | **0.0346** | **4872** | **2.37** | **2.23** |

_macro-F1 overall = mean of per-task macro-F1; acc/ECE/latency pooled across tasks; latency batched + warm._
