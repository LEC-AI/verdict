# Paired significance: Verdict-MQ-large cls k=22 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large cls k=22 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 72.0% | 70.0% | +2.0 [-3.0, +7.0] | 4 / 2 | 0.69 | 1 |
| agent_trace_observability:needs_review | 100 | 86.0% | 84.0% | +2.0 [-3.0, +8.0] | 5 / 3 | 0.73 | 1 |
| agent_trace_observability:outcome | 100 | 75.0% | 65.0% | +10.0 [+4.0, +17.0] | 11 / 1 | 0.0063 | 0.11 |
| agent_trace_observability:risk | 100 | 81.0% | 82.0% | -1.0 [-7.0, +5.0] | 4 / 5 | 1 | 1 |
| agent_trace_observability:urgency | 100 | 65.0% | 65.0% | +0.0 [-6.0, +6.0] | 4 / 4 | 1 | 1 |
| customer_service:action | 100 | 73.0% | 58.0% | +15.0 [+8.0, +23.0] | 16 / 1 | 0.00027 | 0.0052 |
| customer_service:category | 100 | 94.0% | 94.0% | +0.0 [-6.0, +6.0] | 4 / 4 | 1 | 1 |
| customer_service:churn_risk | 100 | 89.0% | 80.0% | +9.0 [+3.0, +16.0] | 10 / 1 | 0.012 | 0.2 |
| customer_service:needs_human | 100 | 78.0% | 76.0% | +2.0 [-6.0, +11.0] | 10 / 8 | 0.81 | 1 |
| customer_service:urgency | 100 | 74.0% | 74.0% | +0.0 [-9.0, +9.0] | 10 / 10 | 1 | 1 |
| invoice_processing:discrepancy_severity | 100 | 84.0% | 85.0% | -1.0 [-8.0, +7.0] | 7 / 8 | 1 | 1 |
| invoice_processing:disposition | 100 | 71.0% | 79.0% | -8.0 [-15.0, -2.0] | 2 / 10 | 0.039 | 0.58 |
| invoice_processing:duplicate | 100 | 92.0% | 92.0% | +0.0 [-5.0, +5.0] | 3 / 3 | 1 | 1 |
| invoice_processing:matches_order | 100 | 96.0% | 94.0% | +2.0 [+0.0, +5.0] | 2 / 0 | 0.5 | 1 |
| invoice_processing:urgency | 100 | 78.0% | 52.0% | +26.0 [+16.0, +36.0] | 29 / 3 | 2.6e-06 | 5.1e-05 |
| security_incidents:credential_compromise | 100 | 78.0% | 81.0% | -3.0 [-12.0, +6.0] | 9 / 12 | 0.66 | 1 |
| security_incidents:disposition | 100 | 76.0% | 73.0% | +3.0 [-3.0, +9.0] | 6 / 3 | 0.51 | 1 |
| security_incidents:severity | 100 | 84.0% | 78.0% | +6.0 [-1.0, +13.0] | 10 / 4 | 0.18 | 1 |
| security_incidents:true_positive | 100 | 88.0% | 87.0% | +1.0 [-5.0, +8.0] | 6 / 5 | 1 | 1 |
| security_incidents:urgency | 100 | 76.0% | 65.0% | +11.0 [+3.0, +19.0] | 14 / 3 | 0.013 | 0.2 |
| overall | 2000 | 80.5% | 76.7% | +3.8 [+2.2, +5.4] | 166 / 90 | 2.4e-06 | nan |

| task | ECE-10 Verdict-MQ-large cls k=22 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.2133 | 0.2861 | -0.0728 [-0.1299, -0.0218] |
| agent_trace_observability:needs_review | 0.1516 | 0.2163 | -0.0647 [-0.1001, +0.0177] |
| agent_trace_observability:outcome | 0.2007 | 0.2706 | -0.0699 [-0.1259, +0.0010] |
| agent_trace_observability:risk | 0.2285 | 0.2754 | -0.0470 [-0.0998, +0.0158] |
| agent_trace_observability:urgency | 0.1450 | 0.1784 | -0.0335 [-0.0890, +0.0281] |
| customer_service:action | 0.1622 | 0.1789 | -0.0167 [-0.0874, +0.0633] |
| customer_service:category | 0.1253 | 0.2708 | -0.1454 [-0.1907, -0.1113] |
| customer_service:churn_risk | 0.2642 | 0.2501 | +0.0141 [-0.0495, +0.0836] |
| customer_service:needs_human | 0.1453 | 0.1772 | -0.0320 [-0.0989, +0.0521] |
| customer_service:urgency | 0.1562 | 0.1866 | -0.0304 [-0.1154, +0.0472] |
| invoice_processing:discrepancy_severity | 0.1473 | 0.2179 | -0.0705 [-0.1327, +0.0028] |
| invoice_processing:disposition | 0.1468 | 0.2926 | -0.1459 [-0.1969, -0.0664] |
| invoice_processing:duplicate | 0.0241 | 0.1152 | -0.0911 [-0.1272, -0.0561] |
| invoice_processing:matches_order | 0.0965 | 0.1601 | -0.0636 [-0.0994, -0.0154] |
| invoice_processing:urgency | 0.2046 | 0.0427 | +0.1619 [+0.0408, +0.2215] |
| security_incidents:credential_compromise | 0.1306 | 0.2335 | -0.1029 [-0.1688, -0.0120] |
| security_incidents:disposition | 0.2311 | 0.2940 | -0.0629 [-0.1286, +0.0229] |
| security_incidents:severity | 0.3135 | 0.3277 | -0.0142 [-0.0692, +0.0612] |
| security_incidents:true_positive | 0.1836 | 0.2540 | -0.0704 [-0.1272, -0.0002] |
| security_incidents:urgency | 0.2167 | 0.1445 | +0.0721 [-0.0061, +0.1498] |
| overall | 0.1618 | 0.2141 | -0.0523 [-0.0670, -0.0358] |
