# Paired significance: Verdict-MQ-large cls k=22 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large cls k=22 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 71.0% | 70.0% | +1.0 [-5.0, +7.0] | 5 / 4 | 1 | 1 |
| agent_trace_observability:needs_review | 100 | 86.0% | 84.0% | +2.0 [+0.0, +5.0] | 2 / 0 | 0.5 | 1 |
| agent_trace_observability:outcome | 100 | 69.0% | 65.0% | +4.0 [+1.0, +8.0] | 4 / 0 | 0.12 | 1 |
| agent_trace_observability:risk | 100 | 80.0% | 82.0% | -2.0 [-7.0, +3.0] | 2 / 4 | 0.69 | 1 |
| agent_trace_observability:urgency | 100 | 64.0% | 65.0% | -1.0 [-8.0, +5.0] | 5 / 6 | 1 | 1 |
| customer_service:action | 100 | 73.0% | 58.0% | +15.0 [+6.0, +24.0] | 19 / 4 | 0.0026 | 0.049 |
| customer_service:category | 100 | 92.0% | 94.0% | -2.0 [-8.0, +4.0] | 4 / 6 | 0.75 | 1 |
| customer_service:churn_risk | 100 | 89.0% | 80.0% | +9.0 [+2.0, +16.0] | 11 / 2 | 0.022 | 0.4 |
| customer_service:needs_human | 100 | 81.0% | 76.0% | +5.0 [-2.0, +12.0] | 9 / 4 | 0.27 | 1 |
| customer_service:urgency | 100 | 77.0% | 74.0% | +3.0 [-5.0, +11.0] | 10 / 7 | 0.63 | 1 |
| invoice_processing:discrepancy_severity | 100 | 85.0% | 85.0% | +0.0 [-5.0, +5.0] | 3 / 3 | 1 | 1 |
| invoice_processing:disposition | 100 | 73.0% | 79.0% | -6.0 [-12.0, -1.0] | 1 / 7 | 0.07 | 1 |
| invoice_processing:duplicate | 100 | 91.0% | 92.0% | -1.0 [-6.0, +4.0] | 3 / 4 | 1 | 1 |
| invoice_processing:matches_order | 100 | 94.0% | 94.0% | +0.0 [-4.0, +4.0] | 2 / 2 | 1 | 1 |
| invoice_processing:urgency | 100 | 82.0% | 52.0% | +30.0 [+20.0, +40.0] | 33 / 3 | 2.3e-07 | 4.5e-06 |
| security_incidents:credential_compromise | 100 | 78.0% | 81.0% | -3.0 [-11.0, +5.0] | 7 / 10 | 0.63 | 1 |
| security_incidents:disposition | 100 | 75.0% | 73.0% | +2.0 [-5.0, +9.0] | 8 / 6 | 0.79 | 1 |
| security_incidents:severity | 100 | 81.0% | 78.0% | +3.0 [-3.0, +9.0] | 7 / 4 | 0.55 | 1 |
| security_incidents:true_positive | 100 | 82.0% | 87.0% | -5.0 [-12.0, +2.0] | 4 / 9 | 0.27 | 1 |
| security_incidents:urgency | 100 | 74.0% | 65.0% | +9.0 [+1.0, +17.0] | 13 / 4 | 0.049 | 0.83 |
| overall | 2000 | 79.8% | 76.7% | +3.1 [+1.6, +4.7] | 152 / 89 | 5.9e-05 | nan |

| task | ECE-10 Verdict-MQ-large cls k=22 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.1888 | 0.2861 | -0.0973 [-0.1580, -0.0288] |
| agent_trace_observability:needs_review | 0.1459 | 0.2163 | -0.0704 [-0.0939, +0.0185] |
| agent_trace_observability:outcome | 0.1384 | 0.2706 | -0.1322 [-0.1779, -0.0232] |
| agent_trace_observability:risk | 0.2212 | 0.2754 | -0.0542 [-0.0906, +0.0033] |
| agent_trace_observability:urgency | 0.1240 | 0.1784 | -0.0545 [-0.1129, +0.0192] |
| customer_service:action | 0.1691 | 0.1789 | -0.0098 [-0.0934, +0.0791] |
| customer_service:category | 0.1165 | 0.2708 | -0.1543 [-0.1963, -0.1069] |
| customer_service:churn_risk | 0.2626 | 0.2501 | +0.0125 [-0.0511, +0.0913] |
| customer_service:needs_human | 0.1187 | 0.1772 | -0.0585 [-0.1165, +0.0271] |
| customer_service:urgency | 0.1722 | 0.1866 | -0.0144 [-0.0895, +0.0672] |
| invoice_processing:discrepancy_severity | 0.1476 | 0.2179 | -0.0703 [-0.1237, -0.0169] |
| invoice_processing:disposition | 0.1464 | 0.2926 | -0.1463 [-0.1911, -0.0671] |
| invoice_processing:duplicate | 0.0385 | 0.1152 | -0.0767 [-0.1199, -0.0423] |
| invoice_processing:matches_order | 0.0794 | 0.1601 | -0.0807 [-0.1051, -0.0397] |
| invoice_processing:urgency | 0.2365 | 0.0427 | +0.1938 [+0.0652, +0.2464] |
| security_incidents:credential_compromise | 0.1312 | 0.2335 | -0.1023 [-0.1636, -0.0105] |
| security_incidents:disposition | 0.2010 | 0.2940 | -0.0930 [-0.1485, -0.0041] |
| security_incidents:severity | 0.2792 | 0.3277 | -0.0485 [-0.1057, +0.0183] |
| security_incidents:true_positive | 0.1288 | 0.2540 | -0.1252 [-0.1633, -0.0392] |
| security_incidents:urgency | 0.2026 | 0.1445 | +0.0581 [-0.0223, +0.1365] |
| overall | 0.1531 | 0.2141 | -0.0610 [-0.0765, -0.0454] |
