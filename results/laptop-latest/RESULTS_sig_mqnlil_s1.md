# Paired significance: Verdict-MQ-large_s1 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large_s1 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 73.0% | 70.0% | +3.0 [-3.0, +9.0] | 7 / 4 | 0.55 | 1 |
| agent_trace_observability:needs_review | 100 | 85.0% | 84.0% | +1.0 [-4.0, +6.0] | 4 / 3 | 1 | 1 |
| agent_trace_observability:outcome | 100 | 66.0% | 65.0% | +1.0 [+0.0, +3.0] | 1 / 0 | 1 | 1 |
| agent_trace_observability:risk | 100 | 74.0% | 82.0% | -8.0 [-14.0, -2.0] | 1 / 9 | 0.021 | 0.34 |
| agent_trace_observability:urgency | 100 | 65.0% | 65.0% | +0.0 [-8.0, +8.0] | 8 / 8 | 1 | 1 |
| customer_service:action | 100 | 56.0% | 58.0% | -2.0 [-12.0, +8.0] | 11 / 13 | 0.84 | 1 |
| customer_service:category | 100 | 84.0% | 94.0% | -10.0 [-17.0, -3.0] | 2 / 12 | 0.013 | 0.22 |
| customer_service:churn_risk | 100 | 59.0% | 80.0% | -21.0 [-32.0, -10.0] | 8 / 29 | 0.00075 | 0.014 |
| customer_service:needs_human | 100 | 73.0% | 76.0% | -3.0 [-12.0, +5.0] | 8 / 11 | 0.65 | 1 |
| customer_service:urgency | 100 | 62.0% | 74.0% | -12.0 [-23.0, -1.0] | 11 / 23 | 0.058 | 0.75 |
| invoice_processing:discrepancy_severity | 100 | 67.0% | 85.0% | -18.0 [-27.0, -10.0] | 2 / 20 | 0.00012 | 0.0024 |
| invoice_processing:disposition | 100 | 75.0% | 79.0% | -4.0 [-11.0, +3.0] | 4 / 8 | 0.39 | 1 |
| invoice_processing:duplicate | 100 | 91.0% | 92.0% | -1.0 [-5.0, +3.0] | 2 / 3 | 1 | 1 |
| invoice_processing:matches_order | 100 | 96.0% | 94.0% | +2.0 [+0.0, +5.0] | 2 / 0 | 0.5 | 1 |
| invoice_processing:urgency | 100 | 46.0% | 52.0% | -6.0 [-12.0, +0.0] | 2 / 8 | 0.11 | 1 |
| security_incidents:credential_compromise | 100 | 74.0% | 81.0% | -7.0 [-16.0, +2.0] | 7 / 14 | 0.19 | 1 |
| security_incidents:disposition | 100 | 74.0% | 73.0% | +1.0 [-5.0, +7.0] | 5 / 4 | 1 | 1 |
| security_incidents:severity | 100 | 64.0% | 78.0% | -14.0 [-24.0, -4.0] | 6 / 20 | 0.0094 | 0.17 |
| security_incidents:true_positive | 100 | 78.0% | 87.0% | -9.0 [-17.0, -1.0] | 4 / 13 | 0.049 | 0.71 |
| security_incidents:urgency | 100 | 52.0% | 65.0% | -13.0 [-25.0, -1.0] | 12 / 25 | 0.047 | 0.71 |
| overall | 2000 | 70.7% | 76.7% | -6.0 [-7.8, -4.2] | 107 / 227 | 4.6e-11 | nan |

| task | ECE-10 Verdict-MQ-large_s1 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.2617 | 0.2861 | -0.0244 [-0.0961, +0.0469] |
| agent_trace_observability:needs_review | 0.1507 | 0.2163 | -0.0655 [-0.1155, -0.0124] |
| agent_trace_observability:outcome | 0.1307 | 0.2706 | -0.1399 [-0.1810, -0.0331] |
| agent_trace_observability:risk | 0.2334 | 0.2754 | -0.0420 [-0.1050, +0.0167] |
| agent_trace_observability:urgency | 0.1734 | 0.1784 | -0.0050 [-0.0604, +0.0947] |
| customer_service:action | 0.0886 | 0.1789 | -0.0903 [-0.1696, +0.0406] |
| customer_service:category | 0.1092 | 0.2708 | -0.1616 [-0.2127, -0.0785] |
| customer_service:churn_risk | 0.1046 | 0.2501 | -0.1455 [-0.2213, -0.0273] |
| customer_service:needs_human | 0.0801 | 0.1772 | -0.0971 [-0.1570, +0.0078] |
| customer_service:urgency | 0.1385 | 0.1866 | -0.0481 [-0.1501, +0.0543] |
| invoice_processing:discrepancy_severity | 0.0919 | 0.2179 | -0.1260 [-0.1949, -0.0301] |
| invoice_processing:disposition | 0.1479 | 0.2926 | -0.1448 [-0.2008, -0.0619] |
| invoice_processing:duplicate | 0.0443 | 0.1152 | -0.0709 [-0.1156, -0.0363] |
| invoice_processing:matches_order | 0.0943 | 0.1601 | -0.0658 [-0.0916, -0.0285] |
| invoice_processing:urgency | 0.0623 | 0.0427 | +0.0196 [-0.0875, +0.1121] |
| security_incidents:credential_compromise | 0.1253 | 0.2335 | -0.1082 [-0.1765, -0.0057] |
| security_incidents:disposition | 0.2453 | 0.2940 | -0.0488 [-0.0999, +0.0270] |
| security_incidents:severity | 0.1857 | 0.3277 | -0.1420 [-0.1972, -0.0352] |
| security_incidents:true_positive | 0.1127 | 0.2540 | -0.1413 [-0.1953, -0.0522] |
| security_incidents:urgency | 0.0885 | 0.1445 | -0.0561 [-0.1428, +0.0466] |
| overall | 0.1193 | 0.2141 | -0.0948 [-0.1118, -0.0773] |
