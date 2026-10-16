# Paired significance: Verdict-MQ-s2 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-s2 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 71.0% | 70.0% | +1.0 [-5.0, +7.0] | 5 / 4 | 1 | 1 |
| agent_trace_observability:needs_review | 100 | 85.0% | 84.0% | +1.0 [-3.0, +6.0] | 3 / 2 | 1 | 1 |
| agent_trace_observability:outcome | 100 | 64.0% | 65.0% | -1.0 [-3.0, +0.0] | 0 / 1 | 1 | 1 |
| agent_trace_observability:risk | 100 | 80.0% | 82.0% | -2.0 [-7.0, +3.0] | 2 / 4 | 0.69 | 1 |
| agent_trace_observability:urgency | 100 | 60.0% | 65.0% | -5.0 [-12.0, +2.0] | 4 / 9 | 0.27 | 1 |
| customer_service:action | 100 | 69.0% | 58.0% | +11.0 [+3.0, +19.0] | 15 / 4 | 0.019 | 0.37 |
| customer_service:category | 100 | 87.0% | 94.0% | -7.0 [-14.0, -1.0] | 2 / 9 | 0.065 | 1 |
| customer_service:churn_risk | 100 | 82.0% | 80.0% | +2.0 [-6.0, +10.0] | 9 / 7 | 0.8 | 1 |
| customer_service:needs_human | 100 | 77.0% | 76.0% | +1.0 [-8.0, +10.0] | 11 / 10 | 1 | 1 |
| customer_service:urgency | 100 | 67.0% | 74.0% | -7.0 [-18.0, +4.0] | 13 / 20 | 0.3 | 1 |
| invoice_processing:discrepancy_severity | 100 | 83.0% | 85.0% | -2.0 [-9.0, +5.0] | 5 / 7 | 0.77 | 1 |
| invoice_processing:disposition | 100 | 74.0% | 79.0% | -5.0 [-13.0, +3.0] | 6 / 11 | 0.33 | 1 |
| invoice_processing:duplicate | 100 | 90.0% | 92.0% | -2.0 [-7.0, +3.0] | 2 / 4 | 0.69 | 1 |
| invoice_processing:matches_order | 100 | 95.0% | 94.0% | +1.0 [-3.0, +5.0] | 3 / 2 | 1 | 1 |
| invoice_processing:urgency | 100 | 75.0% | 52.0% | +23.0 [+13.0, +33.0] | 27 / 4 | 3.4e-05 | 0.00068 |
| security_incidents:credential_compromise | 100 | 76.0% | 81.0% | -5.0 [-13.0, +2.0] | 5 / 10 | 0.3 | 1 |
| security_incidents:disposition | 100 | 77.0% | 73.0% | +4.0 [+0.0, +9.0] | 5 / 1 | 0.22 | 1 |
| security_incidents:severity | 100 | 72.0% | 78.0% | -6.0 [-14.0, +2.0] | 5 / 11 | 0.21 | 1 |
| security_incidents:true_positive | 100 | 79.0% | 87.0% | -8.0 [-15.0, -1.0] | 3 / 11 | 0.057 | 1 |
| security_incidents:urgency | 100 | 59.0% | 65.0% | -6.0 [-16.0, +4.0] | 10 / 16 | 0.33 | 1 |
| overall | 2000 | 76.1% | 76.7% | -0.6 [-2.2, +1.1] | 135 / 147 | 0.51 | nan |

| task | ECE-10 Verdict-MQ-s2 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.2030 | 0.2861 | -0.0831 [-0.1417, -0.0184] |
| agent_trace_observability:needs_review | 0.1361 | 0.2163 | -0.0802 [-0.1140, -0.0002] |
| agent_trace_observability:outcome | 0.1470 | 0.2706 | -0.1236 [-0.2008, -0.0176] |
| agent_trace_observability:risk | 0.2017 | 0.2754 | -0.0738 [-0.1188, -0.0241] |
| agent_trace_observability:urgency | 0.1283 | 0.1784 | -0.0502 [-0.1197, +0.0782] |
| customer_service:action | 0.1609 | 0.1789 | -0.0180 [-0.0942, +0.0743] |
| customer_service:category | 0.0922 | 0.2708 | -0.1785 [-0.2210, -0.1247] |
| customer_service:churn_risk | 0.2385 | 0.2501 | -0.0116 [-0.0890, +0.0716] |
| customer_service:needs_human | 0.1037 | 0.1772 | -0.0736 [-0.1374, +0.0346] |
| customer_service:urgency | 0.1393 | 0.1866 | -0.0473 [-0.1422, +0.0578] |
| invoice_processing:discrepancy_severity | 0.1781 | 0.2179 | -0.0397 [-0.1081, +0.0315] |
| invoice_processing:disposition | 0.1135 | 0.2926 | -0.1791 [-0.2362, -0.0919] |
| invoice_processing:duplicate | 0.0601 | 0.1152 | -0.0551 [-0.1088, -0.0225] |
| invoice_processing:matches_order | 0.0788 | 0.1601 | -0.0813 [-0.1071, -0.0389] |
| invoice_processing:urgency | 0.1938 | 0.0427 | +0.1511 [+0.0286, +0.2088] |
| security_incidents:credential_compromise | 0.1241 | 0.2335 | -0.1094 [-0.1692, -0.0189] |
| security_incidents:disposition | 0.2138 | 0.2940 | -0.0802 [-0.1243, -0.0159] |
| security_incidents:severity | 0.2182 | 0.3277 | -0.1095 [-0.1750, -0.0240] |
| security_incidents:true_positive | 0.0923 | 0.2540 | -0.1617 [-0.1984, -0.0713] |
| security_incidents:urgency | 0.0861 | 0.1445 | -0.0585 [-0.1188, +0.0414] |
| overall | 0.1290 | 0.2141 | -0.0851 [-0.1014, -0.0684] |
