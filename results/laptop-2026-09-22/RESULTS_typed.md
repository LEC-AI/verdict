# Verdict on typed-decisions (matched protocol) vs Laya / Jev

Fine-tuned Verdict (answerdotai/ModernBERT-base); 6000 train / 2000 test decisions.

| metric | Verdict | Laya | Jev | teacher |
|---|---|---|---|---|
| **overall** | **58.8%** | 76.6% | 72.7% | 73.5% |
| noul | 67.4% | 85.7% | - | - |
| choice | 64.0% | 73.3% | - | - |
| score | 50.3% | 72.3% | - | - |

By workflow:

| workflow | Verdict | Laya |
|---|---|---|
| invoice_processing | 54.0% | 80.4% |
| security_incidents | 57.8% | 76.6% |
| customer_service | 54.6% | 76.4% |
| agent_trace_observability | 71.8% | 73.0% |

Verdict ECE: 0.109 (Laya reported 0.081 after temp scaling; Jev 0.144).