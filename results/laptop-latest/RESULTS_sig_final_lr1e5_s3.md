# Paired significance: Verdict-MQ-large-lr1e5-s3 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large-lr1e5-s3 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 69.0% | 70.0% | -1.0 [-8.0, +6.0] | 6 / 7 | 1 | 1 |
| agent_trace_observability:needs_review | 100 | 82.0% | 84.0% | -2.0 [-6.0, +2.0] | 1 / 3 | 0.62 | 1 |
| agent_trace_observability:outcome | 100 | 65.0% | 65.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1 | 1 |
| agent_trace_observability:risk | 100 | 81.0% | 82.0% | -1.0 [-5.0, +3.0] | 2 / 3 | 1 | 1 |
| agent_trace_observability:urgency | 100 | 62.0% | 65.0% | -3.0 [-8.0, +2.0] | 2 / 5 | 0.45 | 1 |
| customer_service:action | 100 | 67.0% | 58.0% | +9.0 [+1.0, +17.0] | 13 / 4 | 0.049 | 0.93 |
| customer_service:category | 100 | 92.0% | 94.0% | -2.0 [-7.0, +3.0] | 2 / 4 | 0.69 | 1 |
| customer_service:churn_risk | 100 | 81.0% | 80.0% | +1.0 [-6.0, +8.0] | 7 / 6 | 1 | 1 |
| customer_service:needs_human | 100 | 82.0% | 76.0% | +6.0 [-2.0, +14.0] | 11 / 5 | 0.21 | 1 |
| customer_service:urgency | 100 | 68.0% | 74.0% | -6.0 [-18.0, +6.0] | 16 / 22 | 0.42 | 1 |
| invoice_processing:discrepancy_severity | 100 | 82.0% | 85.0% | -3.0 [-9.0, +3.0] | 4 / 7 | 0.55 | 1 |
| invoice_processing:disposition | 100 | 75.0% | 79.0% | -4.0 [-11.0, +3.0] | 4 / 8 | 0.39 | 1 |
| invoice_processing:duplicate | 100 | 89.0% | 92.0% | -3.0 [-8.0, +2.0] | 2 / 5 | 0.45 | 1 |
| invoice_processing:matches_order | 100 | 95.0% | 94.0% | +1.0 [-2.0, +4.0] | 2 / 1 | 1 | 1 |
| invoice_processing:urgency | 100 | 77.0% | 52.0% | +25.0 [+15.0, +36.0] | 29 / 4 | 1.1e-05 | 0.00022 |
| security_incidents:credential_compromise | 100 | 78.0% | 81.0% | -3.0 [-12.0, +6.0] | 8 / 11 | 0.65 | 1 |
| security_incidents:disposition | 100 | 75.0% | 73.0% | +2.0 [-3.0, +7.0] | 4 / 2 | 0.69 | 1 |
| security_incidents:severity | 100 | 76.0% | 78.0% | -2.0 [-9.0, +5.0] | 6 / 8 | 0.79 | 1 |
| security_incidents:true_positive | 100 | 83.0% | 87.0% | -4.0 [-11.0, +3.0] | 4 / 8 | 0.39 | 1 |
| security_incidents:urgency | 100 | 69.0% | 65.0% | +4.0 [-5.0, +13.0] | 13 / 9 | 0.52 | 1 |
| overall | 2000 | 77.4% | 76.7% | +0.7 [-0.8, +2.3] | 136 / 122 | 0.42 | nan |

| task | ECE-10 Verdict-MQ-large-lr1e5-s3 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.1923 | 0.2861 | -0.0938 [-0.1618, -0.0283] |
| agent_trace_observability:needs_review | 0.1541 | 0.2163 | -0.0622 [-0.1197, +0.0375] |
| agent_trace_observability:outcome | 0.1648 | 0.2706 | -0.1058 [-0.1800, -0.0055] |
| agent_trace_observability:risk | 0.2170 | 0.2754 | -0.0584 [-0.0917, -0.0102] |
| agent_trace_observability:urgency | 0.1320 | 0.1784 | -0.0465 [-0.0927, +0.0164] |
| customer_service:action | 0.1129 | 0.1789 | -0.0660 [-0.1245, +0.0361] |
| customer_service:category | 0.0946 | 0.2708 | -0.1762 [-0.2097, -0.1329] |
| customer_service:churn_risk | 0.2125 | 0.2501 | -0.0376 [-0.1033, +0.0401] |
| customer_service:needs_human | 0.1342 | 0.1772 | -0.0430 [-0.1088, +0.0423] |
| customer_service:urgency | 0.1144 | 0.1866 | -0.0722 [-0.1621, +0.0464] |
| invoice_processing:discrepancy_severity | 0.1404 | 0.2179 | -0.0775 [-0.1297, +0.0003] |
| invoice_processing:disposition | 0.1529 | 0.2926 | -0.1398 [-0.2026, -0.0619] |
| invoice_processing:duplicate | 0.0569 | 0.1152 | -0.0583 [-0.1106, -0.0228] |
| invoice_processing:matches_order | 0.0828 | 0.1601 | -0.0773 [-0.1044, -0.0359] |
| invoice_processing:urgency | 0.2297 | 0.0427 | +0.1870 [+0.0504, +0.2525] |
| security_incidents:credential_compromise | 0.1370 | 0.2335 | -0.0966 [-0.1747, -0.0075] |
| security_incidents:disposition | 0.2126 | 0.2940 | -0.0814 [-0.1344, +0.0138] |
| security_incidents:severity | 0.2704 | 0.3277 | -0.0573 [-0.1307, +0.0176] |
| security_incidents:true_positive | 0.1399 | 0.2540 | -0.1141 [-0.1653, -0.0387] |
| security_incidents:urgency | 0.1625 | 0.1445 | +0.0180 [-0.0584, +0.0997] |
| overall | 0.1380 | 0.2141 | -0.0761 [-0.0913, -0.0597] |
