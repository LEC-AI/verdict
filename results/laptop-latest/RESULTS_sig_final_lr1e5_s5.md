# Paired significance: Verdict-MQ-large-lr1e5-s5 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large-lr1e5-s5 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 67.0% | 70.0% | -3.0 [-9.0, +3.0] | 4 / 7 | 0.55 | 1 |
| agent_trace_observability:needs_review | 100 | 84.0% | 84.0% | +0.0 [-4.0, +4.0] | 2 / 2 | 1 | 1 |
| agent_trace_observability:outcome | 100 | 65.0% | 65.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1 | 1 |
| agent_trace_observability:risk | 100 | 83.0% | 82.0% | +1.0 [-4.0, +6.0] | 4 / 3 | 1 | 1 |
| agent_trace_observability:urgency | 100 | 67.0% | 65.0% | +2.0 [-4.0, +8.0] | 5 / 3 | 0.73 | 1 |
| customer_service:action | 100 | 65.0% | 58.0% | +7.0 [-1.0, +15.0] | 12 / 5 | 0.14 | 1 |
| customer_service:category | 100 | 94.0% | 94.0% | +0.0 [-5.0, +5.0] | 3 / 3 | 1 | 1 |
| customer_service:churn_risk | 100 | 83.0% | 80.0% | +3.0 [-4.0, +10.0] | 8 / 5 | 0.58 | 1 |
| customer_service:needs_human | 100 | 82.0% | 76.0% | +6.0 [-3.0, +15.0] | 13 / 7 | 0.26 | 1 |
| customer_service:urgency | 100 | 73.0% | 74.0% | -1.0 [-12.0, +10.0] | 14 / 15 | 1 | 1 |
| invoice_processing:discrepancy_severity | 100 | 84.0% | 85.0% | -1.0 [-8.0, +6.0] | 6 / 7 | 1 | 1 |
| invoice_processing:disposition | 100 | 76.0% | 79.0% | -3.0 [-9.0, +4.0] | 4 / 7 | 0.55 | 1 |
| invoice_processing:duplicate | 100 | 90.0% | 92.0% | -2.0 [-6.0, +2.0] | 1 / 3 | 0.62 | 1 |
| invoice_processing:matches_order | 100 | 96.0% | 94.0% | +2.0 [-2.0, +6.0] | 3 / 1 | 0.62 | 1 |
| invoice_processing:urgency | 100 | 78.0% | 52.0% | +26.0 [+17.0, +36.0] | 28 / 2 | 8.7e-07 | 1.7e-05 |
| security_incidents:credential_compromise | 100 | 77.0% | 81.0% | -4.0 [-12.0, +4.0] | 7 / 11 | 0.48 | 1 |
| security_incidents:disposition | 100 | 76.0% | 73.0% | +3.0 [-2.0, +8.0] | 5 / 2 | 0.45 | 1 |
| security_incidents:severity | 100 | 78.0% | 78.0% | +0.0 [-7.0, +7.0] | 6 / 6 | 1 | 1 |
| security_incidents:true_positive | 100 | 85.0% | 87.0% | -2.0 [-7.0, +3.0] | 2 / 4 | 0.69 | 1 |
| security_incidents:urgency | 100 | 67.0% | 65.0% | +2.0 [-7.0, +11.0] | 11 / 9 | 0.82 | 1 |
| overall | 2000 | 78.5% | 76.7% | +1.8 [+0.3, +3.3] | 138 / 102 | 0.024 | nan |

| task | ECE-10 Verdict-MQ-large-lr1e5-s5 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.1540 | 0.2861 | -0.1321 [-0.1969, -0.0607] |
| agent_trace_observability:needs_review | 0.1501 | 0.2163 | -0.0662 [-0.1096, +0.0274] |
| agent_trace_observability:outcome | 0.1714 | 0.2706 | -0.0992 [-0.1766, -0.0035] |
| agent_trace_observability:risk | 0.2310 | 0.2754 | -0.0445 [-0.0899, +0.0121] |
| agent_trace_observability:urgency | 0.1436 | 0.1784 | -0.0348 [-0.0863, +0.0392] |
| customer_service:action | 0.0812 | 0.1789 | -0.0977 [-0.1457, +0.0278] |
| customer_service:category | 0.1139 | 0.2708 | -0.1569 [-0.1928, -0.1149] |
| customer_service:churn_risk | 0.2203 | 0.2501 | -0.0298 [-0.0925, +0.0444] |
| customer_service:needs_human | 0.1122 | 0.1772 | -0.0650 [-0.1303, +0.0345] |
| customer_service:urgency | 0.1476 | 0.1866 | -0.0390 [-0.1187, +0.0641] |
| invoice_processing:discrepancy_severity | 0.1300 | 0.2179 | -0.0879 [-0.1456, -0.0129] |
| invoice_processing:disposition | 0.1536 | 0.2926 | -0.1391 [-0.1954, -0.0463] |
| invoice_processing:duplicate | 0.0571 | 0.1152 | -0.0581 [-0.1147, -0.0263] |
| invoice_processing:matches_order | 0.0869 | 0.1601 | -0.0732 [-0.1141, -0.0239] |
| invoice_processing:urgency | 0.2313 | 0.0427 | +0.1886 [+0.0588, +0.2478] |
| security_incidents:credential_compromise | 0.1141 | 0.2335 | -0.1195 [-0.1712, -0.0204] |
| security_incidents:disposition | 0.2262 | 0.2940 | -0.0678 [-0.1247, +0.0108] |
| security_incidents:severity | 0.2733 | 0.3277 | -0.0544 [-0.1216, +0.0136] |
| security_incidents:true_positive | 0.1473 | 0.2540 | -0.1067 [-0.1495, -0.0501] |
| security_incidents:urgency | 0.1545 | 0.1445 | +0.0100 [-0.0698, +0.0948] |
| overall | 0.1428 | 0.2141 | -0.0713 [-0.0866, -0.0558] |
