# Verdict on typed-decisions (matched protocol) vs Laya / Jev

Fine-tuned Verdict (answerdotai/ModernBERT-base); 6000 train / 2000 test decisions.

| metric | Verdict | Laya | Jev | teacher |
|---|---|---|---|---|
| **overall** | **58.7%** | 76.6% | 72.7% | 73.5% |
| noul | 70.0% | 85.7% | - | - |
| choice | 61.2% | 73.3% | - | - |
| score | 48.4% | 72.3% | - | - |

By workflow:

| workflow | Verdict | Laya |
|---|---|---|
| invoice_processing | 56.8% | 80.4% |
| security_incidents | 61.8% | 76.6% |
| customer_service | 48.0% | 76.4% |
| agent_trace_observability | 68.2% | 73.0% |

Verdict ECE: 0.065 (Laya reported 0.081 after temp scaling; Jev 0.144).