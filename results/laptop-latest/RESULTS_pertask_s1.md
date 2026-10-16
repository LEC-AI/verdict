# Verdict on OrgBench — out/verdict-base-s1

| task | acc | macro-F1 | ECE | n | mean lat (ms) | p50 lat (ms) |
|---|---|---|---|---|---|---|
| route_topic | 92.0% | 91.9% | 0.0165 | 2000 | 3.02 | 2.96 |
| signal_positive | 77.8% | 77.4% | 0.0909 | 872 | 1.57 | 1.52 |
| affect | 92.2% | 89.4% | 0.0162 | 2000 | 2.10 | 2.12 |
| **overall** | **89.6%** | **86.2%** | **0.0283** | **4872** | **2.38** | **2.23** |

_macro-F1 overall = mean of per-task macro-F1; acc/ECE/latency pooled across tasks; latency batched + warm._
