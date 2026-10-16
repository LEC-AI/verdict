# Verdict on typed-decisions (matched protocol) vs Laya / Jev

Fine-tuned Verdict (answerdotai/ModernBERT-large); 6000 train / 2000 test decisions.

| metric | Verdict | Laya | Jev | teacher |
|---|---|---|---|---|
| **overall** | **61.8%** | 76.6% | 72.7% | 73.5% |
| noul | 74.0% | 85.7% | - | - |
| choice | 61.6% | 73.3% | - | - |
| score | 54.9% | 72.3% | - | - |

By workflow:

| workflow | Verdict | Laya |
|---|---|---|
| invoice_processing | 62.4% | 80.4% |
| security_incidents | 65.7% | 76.6% |
| customer_service | 56.4% | 76.4% |
| agent_trace_observability | 66.0% | 73.0% |

Verdict ECE: 0.071 (Laya reported 0.081 after temp scaling; Jev 0.144).