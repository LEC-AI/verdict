# Paired significance: Verdict-MQ-large_s2 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large_s2 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 36.0% | 70.0% | -34.0 [-44.0, -24.0] | 3 / 37 | 1.9e-08 | 3.5e-07 |
| agent_trace_observability:needs_review | 100 | 53.0% | 84.0% | -31.0 [-42.0, -20.0] | 6 / 37 | 1.6e-06 | 2.6e-05 |
| agent_trace_observability:outcome | 100 | 26.0% | 65.0% | -39.0 [-49.0, -29.0] | 2 / 41 | 2.2e-10 | 4.1e-09 |
| agent_trace_observability:risk | 100 | 28.0% | 82.0% | -54.0 [-65.0, -43.0] | 3 / 57 | 6.3e-14 | 1.3e-12 |
| agent_trace_observability:urgency | 100 | 36.0% | 65.0% | -29.0 [-39.0, -19.0] | 3 / 32 | 4.2e-07 | 7.1e-06 |
| customer_service:action | 100 | 68.0% | 58.0% | +10.0 [+1.0, +19.0] | 16 / 6 | 0.052 | 0.63 |
| customer_service:category | 100 | 95.0% | 94.0% | +1.0 [-3.0, +5.0] | 3 / 2 | 1 | 1 |
| customer_service:churn_risk | 100 | 83.0% | 80.0% | +3.0 [-4.0, +10.0] | 8 / 5 | 0.58 | 1 |
| customer_service:needs_human | 100 | 79.0% | 76.0% | +3.0 [-4.0, +10.0] | 8 / 5 | 0.58 | 1 |
| customer_service:urgency | 100 | 74.0% | 74.0% | +0.0 [-11.0, +11.0] | 15 / 15 | 1 | 1 |
| invoice_processing:discrepancy_severity | 100 | 66.0% | 85.0% | -19.0 [-29.0, -8.0] | 7 / 26 | 0.0013 | 0.02 |
| invoice_processing:disposition | 100 | 73.0% | 79.0% | -6.0 [-15.0, +3.0] | 7 / 13 | 0.26 | 1 |
| invoice_processing:duplicate | 100 | 89.0% | 92.0% | -3.0 [-10.0, +4.0] | 5 / 8 | 0.58 | 1 |
| invoice_processing:matches_order | 100 | 88.0% | 94.0% | -6.0 [-13.0, +1.0] | 4 / 10 | 0.18 | 1 |
| invoice_processing:urgency | 100 | 68.0% | 52.0% | +16.0 [+6.0, +26.0] | 22 / 6 | 0.0037 | 0.048 |
| security_incidents:credential_compromise | 100 | 65.0% | 81.0% | -16.0 [-25.0, -7.0] | 4 / 20 | 0.0015 | 0.022 |
| security_incidents:disposition | 100 | 74.0% | 73.0% | +1.0 [-5.0, +8.0] | 6 / 5 | 1 | 1 |
| security_incidents:severity | 100 | 77.0% | 78.0% | -1.0 [-7.0, +5.0] | 4 / 5 | 1 | 1 |
| security_incidents:true_positive | 100 | 78.0% | 87.0% | -9.0 [-18.0, +0.0] | 6 / 15 | 0.078 | 0.86 |
| security_incidents:urgency | 100 | 61.0% | 65.0% | -4.0 [-16.0, +7.0] | 15 / 19 | 0.61 | 1 |
| overall | 2000 | 65.8% | 76.7% | -10.9 [-13.0, -8.7] | 147 / 364 | 2.8e-22 | nan |

| task | ECE-10 Verdict-MQ-large_s2 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.0638 | 0.2861 | -0.2224 [-0.3418, -0.0806] |
| agent_trace_observability:needs_review | 0.0182 | 0.2163 | -0.1980 [-0.2544, -0.0796] |
| agent_trace_observability:outcome | 0.1254 | 0.2706 | -0.1452 [-0.2657, -0.0219] |
| agent_trace_observability:risk | 0.0753 | 0.2754 | -0.2002 [-0.3111, -0.0787] |
| agent_trace_observability:urgency | 0.0453 | 0.1784 | -0.1332 [-0.2245, +0.0144] |
| customer_service:action | 0.1492 | 0.1789 | -0.0297 [-0.1103, +0.0606] |
| customer_service:category | 0.0963 | 0.2708 | -0.1744 [-0.2177, -0.1296] |
| customer_service:churn_risk | 0.2080 | 0.2501 | -0.0421 [-0.1138, +0.0343] |
| customer_service:needs_human | 0.1172 | 0.1772 | -0.0600 [-0.1118, +0.0499] |
| customer_service:urgency | 0.1548 | 0.1866 | -0.0318 [-0.1189, +0.0691] |
| invoice_processing:discrepancy_severity | 0.0811 | 0.2179 | -0.1368 [-0.1865, -0.0108] |
| invoice_processing:disposition | 0.1105 | 0.2926 | -0.1822 [-0.2421, -0.0715] |
| invoice_processing:duplicate | 0.0567 | 0.1152 | -0.0585 [-0.1129, -0.0083] |
| invoice_processing:matches_order | 0.0631 | 0.1601 | -0.0970 [-0.1364, -0.0266] |
| invoice_processing:urgency | 0.1701 | 0.0427 | +0.1274 [-0.0019, +0.1941] |
| security_incidents:credential_compromise | 0.0758 | 0.2335 | -0.1577 [-0.2060, -0.0347] |
| security_incidents:disposition | 0.2119 | 0.2940 | -0.0822 [-0.1401, -0.0155] |
| security_incidents:severity | 0.2790 | 0.3277 | -0.0487 [-0.1116, +0.0121] |
| security_incidents:true_positive | 0.1425 | 0.2540 | -0.1115 [-0.1741, -0.0154] |
| security_incidents:urgency | 0.1383 | 0.1445 | -0.0063 [-0.0958, +0.0868] |
| overall | 0.0950 | 0.2141 | -0.1191 [-0.1396, -0.0965] |
