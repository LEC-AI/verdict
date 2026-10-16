# Verdict on OrgBench — out/verdict-base-s2

| task | acc | macro-F1 | ECE | n | mean lat (ms) | p50 lat (ms) |
|---|---|---|---|---|---|---|
| route_topic | 90.5% | 90.3% | 0.0342 | 2000 | 2.98 | 2.82 |
| signal_positive | 82.0% | 81.9% | 0.0787 | 872 | 1.55 | 1.53 |
| affect | 91.8% | 89.3% | 0.0126 | 2000 | 2.10 | 2.12 |
| **overall** | **89.5%** | **87.1%** | **0.0326** | **4872** | **2.36** | **2.23** |

_macro-F1 overall = mean of per-task macro-F1; acc/ECE/latency pooled across tasks; latency batched + warm._
