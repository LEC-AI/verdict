# Paired significance: Verdict-MQ-base-s7 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-base-s7 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 48.0% | 70.0% | -22.0 [-31.0, -13.0] | 2 / 24 | 1e-05 | 0.00021 |
| agent_trace_observability:needs_review | 100 | 80.0% | 84.0% | -4.0 [-14.0, +6.0] | 10 / 14 | 0.54 | 1 |
| agent_trace_observability:outcome | 100 | 70.0% | 65.0% | +5.0 [+0.0, +10.0] | 6 / 1 | 0.12 | 1 |
| agent_trace_observability:risk | 100 | 78.0% | 82.0% | -4.0 [-8.0, -1.0] | 0 / 4 | 0.12 | 1 |
| agent_trace_observability:urgency | 100 | 61.0% | 65.0% | -4.0 [-9.0, +0.0] | 1 / 5 | 0.22 | 1 |
| customer_service:action | 100 | 60.0% | 58.0% | +2.0 [-8.0, +11.0] | 13 / 11 | 0.84 | 1 |
| customer_service:category | 100 | 91.0% | 94.0% | -3.0 [-8.0, +2.0] | 2 / 5 | 0.45 | 1 |
| customer_service:churn_risk | 100 | 75.0% | 80.0% | -5.0 [-14.0, +4.0] | 9 / 14 | 0.4 | 1 |
| customer_service:needs_human | 100 | 75.0% | 76.0% | -1.0 [-10.0, +9.0] | 11 / 12 | 1 | 1 |
| customer_service:urgency | 100 | 58.0% | 74.0% | -16.0 [-27.0, -5.0] | 10 / 26 | 0.011 | 0.2 |
| invoice_processing:discrepancy_severity | 100 | 76.0% | 85.0% | -9.0 [-17.0, -1.0] | 5 / 14 | 0.064 | 1 |
| invoice_processing:disposition | 100 | 76.0% | 79.0% | -3.0 [-9.0, +3.0] | 3 / 6 | 0.51 | 1 |
| invoice_processing:duplicate | 100 | 93.0% | 92.0% | +1.0 [-3.0, +5.0] | 3 / 2 | 1 | 1 |
| invoice_processing:matches_order | 100 | 95.0% | 94.0% | +1.0 [+0.0, +3.0] | 1 / 0 | 1 | 1 |
| invoice_processing:urgency | 100 | 71.0% | 52.0% | +19.0 [+8.0, +30.0] | 26 / 7 | 0.0013 | 0.025 |
| security_incidents:credential_compromise | 100 | 75.0% | 81.0% | -6.0 [-16.0, +4.0] | 9 / 15 | 0.31 | 1 |
| security_incidents:disposition | 100 | 74.0% | 73.0% | +1.0 [-5.0, +7.0] | 5 / 4 | 1 | 1 |
| security_incidents:severity | 100 | 74.0% | 78.0% | -4.0 [-12.0, +4.0] | 7 / 11 | 0.48 | 1 |
| security_incidents:true_positive | 100 | 85.0% | 87.0% | -2.0 [-10.0, +6.0] | 8 / 10 | 0.81 | 1 |
| security_incidents:urgency | 100 | 58.0% | 65.0% | -7.0 [-18.0, +4.0] | 12 / 19 | 0.28 | 1 |
| overall | 2000 | 73.7% | 76.7% | -3.0 [-4.8, -1.2] | 143 / 204 | 0.0012 | nan |

| task | ECE-10 Verdict-MQ-base-s7 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.1244 | 0.2861 | -0.1618 [-0.2810, -0.0273] |
| agent_trace_observability:needs_review | 0.1091 | 0.2163 | -0.1072 [-0.1738, -0.0103] |
| agent_trace_observability:outcome | 0.1654 | 0.2706 | -0.1052 [-0.1587, -0.0344] |
| agent_trace_observability:risk | 0.2155 | 0.2754 | -0.0599 [-0.0940, -0.0137] |
| agent_trace_observability:urgency | 0.1177 | 0.1784 | -0.0607 [-0.1075, +0.0061] |
| customer_service:action | 0.0966 | 0.1789 | -0.0823 [-0.1617, +0.0429] |
| customer_service:category | 0.1019 | 0.2708 | -0.1689 [-0.2072, -0.1090] |
| customer_service:churn_risk | 0.1874 | 0.2501 | -0.0627 [-0.1538, +0.0338] |
| customer_service:needs_human | 0.0694 | 0.1772 | -0.1079 [-0.1685, +0.0045] |
| customer_service:urgency | 0.0275 | 0.1866 | -0.1591 [-0.1947, -0.0118] |
| invoice_processing:discrepancy_severity | 0.0867 | 0.2179 | -0.1312 [-0.1840, -0.0285] |
| invoice_processing:disposition | 0.0945 | 0.2926 | -0.1982 [-0.2356, -0.0951] |
| invoice_processing:duplicate | 0.0270 | 0.1152 | -0.0882 [-0.1277, -0.0552] |
| invoice_processing:matches_order | 0.0524 | 0.1601 | -0.1077 [-0.1258, -0.0539] |
| invoice_processing:urgency | 0.1765 | 0.0427 | +0.1337 [+0.0052, +0.1944] |
| security_incidents:credential_compromise | 0.1120 | 0.2335 | -0.1215 [-0.1918, -0.0222] |
| security_incidents:disposition | 0.1897 | 0.2940 | -0.1044 [-0.1551, -0.0429] |
| security_incidents:severity | 0.2298 | 0.3277 | -0.0979 [-0.1778, -0.0072] |
| security_incidents:true_positive | 0.1450 | 0.2540 | -0.1090 [-0.1828, -0.0211] |
| security_incidents:urgency | 0.0555 | 0.1445 | -0.0890 [-0.1361, +0.0357] |
| overall | 0.1047 | 0.2141 | -0.1094 [-0.1277, -0.0907] |
