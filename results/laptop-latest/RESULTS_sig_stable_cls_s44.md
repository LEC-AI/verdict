# Paired significance: Verdict-MQ-large cls k=0 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large cls k=0 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 71.0% | 70.0% | +1.0 [-5.0, +7.0] | 5 / 4 | 1 | 1 |
| agent_trace_observability:needs_review | 100 | 87.0% | 84.0% | +3.0 [+0.0, +7.0] | 3 / 0 | 0.25 | 1 |
| agent_trace_observability:outcome | 100 | 70.0% | 65.0% | +5.0 [+0.0, +10.0] | 6 / 1 | 0.12 | 1 |
| agent_trace_observability:risk | 100 | 82.0% | 82.0% | +0.0 [-6.0, +6.0] | 4 / 4 | 1 | 1 |
| agent_trace_observability:urgency | 100 | 66.0% | 65.0% | +1.0 [-5.0, +7.0] | 5 / 4 | 1 | 1 |
| customer_service:action | 100 | 70.0% | 58.0% | +12.0 [+4.0, +20.0] | 15 / 3 | 0.0075 | 0.14 |
| customer_service:category | 100 | 94.0% | 94.0% | +0.0 [-5.0, +5.0] | 3 / 3 | 1 | 1 |
| customer_service:churn_risk | 100 | 89.0% | 80.0% | +9.0 [+3.0, +16.0] | 10 / 1 | 0.012 | 0.21 |
| customer_service:needs_human | 100 | 80.0% | 76.0% | +4.0 [-3.0, +11.0] | 9 / 5 | 0.42 | 1 |
| customer_service:urgency | 100 | 77.0% | 74.0% | +3.0 [-6.0, +12.0] | 12 / 9 | 0.66 | 1 |
| invoice_processing:discrepancy_severity | 100 | 82.0% | 85.0% | -3.0 [-10.0, +3.0] | 4 / 7 | 0.55 | 1 |
| invoice_processing:disposition | 100 | 75.0% | 79.0% | -4.0 [-10.0, +1.0] | 2 / 6 | 0.29 | 1 |
| invoice_processing:duplicate | 100 | 89.0% | 92.0% | -3.0 [-9.0, +3.0] | 3 / 6 | 0.51 | 1 |
| invoice_processing:matches_order | 100 | 96.0% | 94.0% | +2.0 [-3.0, +7.0] | 4 / 2 | 0.69 | 1 |
| invoice_processing:urgency | 100 | 82.0% | 52.0% | +30.0 [+19.0, +41.0] | 34 / 4 | 6e-07 | 1.2e-05 |
| security_incidents:credential_compromise | 100 | 78.0% | 81.0% | -3.0 [-11.0, +5.0] | 8 / 11 | 0.65 | 1 |
| security_incidents:disposition | 100 | 76.0% | 73.0% | +3.0 [-2.0, +8.0] | 5 / 2 | 0.45 | 1 |
| security_incidents:severity | 100 | 80.0% | 78.0% | +2.0 [-4.0, +8.0] | 6 / 4 | 0.75 | 1 |
| security_incidents:true_positive | 100 | 80.0% | 87.0% | -7.0 [-15.0, +1.0] | 5 / 12 | 0.14 | 1 |
| security_incidents:urgency | 100 | 66.0% | 65.0% | +1.0 [-7.0, +10.0] | 10 / 9 | 1 | 1 |
| overall | 2000 | 79.5% | 76.7% | +2.8 [+1.3, +4.3] | 153 / 97 | 0.00048 | nan |

| task | ECE-10 Verdict-MQ-large cls k=0 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.1983 | 0.2861 | -0.0878 [-0.1497, -0.0271] |
| agent_trace_observability:needs_review | 0.1554 | 0.2163 | -0.0609 [-0.0887, +0.0222] |
| agent_trace_observability:outcome | 0.1624 | 0.2706 | -0.1082 [-0.1682, +0.0064] |
| agent_trace_observability:risk | 0.2172 | 0.2754 | -0.0582 [-0.1032, +0.0068] |
| agent_trace_observability:urgency | 0.1474 | 0.1784 | -0.0310 [-0.0897, +0.0478] |
| customer_service:action | 0.1414 | 0.1789 | -0.0375 [-0.1045, +0.0596] |
| customer_service:category | 0.0907 | 0.2708 | -0.1801 [-0.2158, -0.1268] |
| customer_service:churn_risk | 0.2595 | 0.2501 | +0.0094 [-0.0513, +0.0866] |
| customer_service:needs_human | 0.1058 | 0.1772 | -0.0714 [-0.1224, +0.0269] |
| customer_service:urgency | 0.1624 | 0.1866 | -0.0242 [-0.1073, +0.0507] |
| invoice_processing:discrepancy_severity | 0.1222 | 0.2179 | -0.0957 [-0.1546, -0.0179] |
| invoice_processing:disposition | 0.1218 | 0.2926 | -0.1708 [-0.2007, -0.0737] |
| invoice_processing:duplicate | 0.0573 | 0.1152 | -0.0579 [-0.1131, -0.0250] |
| invoice_processing:matches_order | 0.0895 | 0.1601 | -0.0706 [-0.1180, -0.0197] |
| invoice_processing:urgency | 0.2415 | 0.0427 | +0.1988 [+0.0628, +0.2571] |
| security_incidents:credential_compromise | 0.1281 | 0.2335 | -0.1054 [-0.1783, -0.0152] |
| security_incidents:disposition | 0.1809 | 0.2940 | -0.1131 [-0.1520, -0.0329] |
| security_incidents:severity | 0.2720 | 0.3277 | -0.0557 [-0.1122, +0.0091] |
| security_incidents:true_positive | 0.1921 | 0.2540 | -0.0619 [-0.1227, +0.0051] |
| security_incidents:urgency | 0.1517 | 0.1445 | +0.0071 [-0.0781, +0.0817] |
| overall | 0.1472 | 0.2141 | -0.0670 [-0.0818, -0.0499] |
