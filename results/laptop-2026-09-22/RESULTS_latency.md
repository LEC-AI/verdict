# Verdict latency / throughput / cost — 2026-09-22 18:18 UTC

- **Verdict ckpt:** `out/verdict-base`  
- **LLM-judge:** `qwen2.5:7b-instruct` @ `http://localhost:11434/v1`  
- **Items:** n=256 (source: cached OrgBench val splits), batches=[1, 8, 32], warmup=3, repeats=3 (median)  
- **torch** 2.11.0+cu130 · cpu-threads=24 · gpu=NVIDIA GeForce RTX 4090 Laptop GPU

## Verdict — per-decision latency (one forward pass, no generation)

| device | dtype | batch | ms / decision | decisions / sec |
|---|---|---:|---:|---:|
| cpu | float32 | 1 | 34.80 | 29 |
| cpu | float32 | 8 | 37.91 | 26 |
| cpu | float32 | 32 | 42.63 | 23 |
| cuda:NVIDIA GeForce RTX 4090 Laptop GPU | float32 | 1 | 5.20 | 192 |
| cuda:NVIDIA GeForce RTX 4090 Laptop GPU | float32 | 8 | 2.39 | 418 |
| cuda:NVIDIA GeForce RTX 4090 Laptop GPU | float32 | 32 | 2.39 | 418 |

## LLM-judge — per-decision latency (generative, sequential)

| model | mean ms | p50 ms | p90 ms | decisions / sec |
|---|---:|---:|---:|---:|
| qwen2.5:7b-instruct | 121 | 95 | 102 | 8.27 |
  _(n=50 successful calls, 0 errors)_

## Cost — estimated $ / 1000 decisions

| system | $/1000 decisions | basis |
|---|---:|---|
| Verdict | $0.0000 | amortized local compute assumed negligible (owned hardware, no per-call fee) |
| Verdict (electricity floor) | $0.0000 | 350 W @ $0.15/kWh at 418 dec/s (cuda) |
| Cloud LLM (qwen2.5:7b-instruct) | $0.5000 | --llm-cost-per-1k (user-supplied $/1000 decisions) |

## Headline

- Verdict single decision: **5.20 ms** on cuda.
- Verdict peak throughput: **418 decisions/sec** (cuda, batch 32).
- LLM-judge: 121 ms/decision (8.27 decisions/sec).
- **Speed:** Verdict is ~**23x** lower single-decision latency and ~**51x** higher throughput than the LLM-judge.
- **Cost:** ~$0.5000 saved per 1000 decisions vs the cloud LLM (Verdict local compute assumed negligible).
