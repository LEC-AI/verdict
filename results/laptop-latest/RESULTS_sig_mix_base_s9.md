# Paired significance: Verdict-MQ-mix-base-s9 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-mix-base-s9 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 68.0% | 70.0% | -2.0 [-9.0, +5.0] | 5 / 7 | 0.77 | 1 |
| agent_trace_observability:needs_review | 100 | 88.0% | 84.0% | +4.0 [-1.0, +10.0] | 6 / 2 | 0.29 | 1 |
| agent_trace_observability:outcome | 100 | 65.0% | 65.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1 | 1 |
| agent_trace_observability:risk | 100 | 82.0% | 82.0% | +0.0 [-3.0, +3.0] | 1 / 1 | 1 | 1 |
| agent_trace_observability:urgency | 100 | 66.0% | 65.0% | +1.0 [-5.0, +7.0] | 5 / 4 | 1 | 1 |
| customer_service:action | 100 | 63.0% | 58.0% | +5.0 [-3.0, +14.0] | 12 / 7 | 0.36 | 1 |
| customer_service:category | 100 | 90.0% | 94.0% | -4.0 [-9.0, +0.0] | 1 / 5 | 0.22 | 1 |
| customer_service:churn_risk | 100 | 79.0% | 80.0% | -1.0 [-9.0, +7.0] | 7 / 8 | 1 | 1 |
| customer_service:needs_human | 100 | 76.0% | 76.0% | +0.0 [-8.0, +8.0] | 9 / 9 | 1 | 1 |
| customer_service:urgency | 100 | 65.0% | 74.0% | -9.0 [-20.0, +2.0] | 12 / 21 | 0.16 | 1 |
| invoice_processing:discrepancy_severity | 100 | 84.0% | 85.0% | -1.0 [-9.0, +7.0] | 8 / 9 | 1 | 1 |
| invoice_processing:disposition | 100 | 73.0% | 79.0% | -6.0 [-14.0, +2.0] | 5 / 11 | 0.21 | 1 |
| invoice_processing:duplicate | 100 | 91.0% | 92.0% | -1.0 [-6.0, +4.0] | 3 / 4 | 1 | 1 |
| invoice_processing:matches_order | 100 | 96.0% | 94.0% | +2.0 [-2.0, +6.0] | 3 / 1 | 0.62 | 1 |
| invoice_processing:urgency | 100 | 74.0% | 52.0% | +22.0 [+13.0, +32.0] | 25 / 3 | 2.7e-05 | 0.00055 |
| security_incidents:credential_compromise | 100 | 76.0% | 81.0% | -5.0 [-14.0, +4.0] | 8 / 13 | 0.38 | 1 |
| security_incidents:disposition | 100 | 76.0% | 73.0% | +3.0 [-3.0, +9.0] | 6 / 3 | 0.51 | 1 |
| security_incidents:severity | 100 | 74.0% | 78.0% | -4.0 [-10.0, +2.0] | 3 / 7 | 0.34 | 1 |
| security_incidents:true_positive | 100 | 81.0% | 87.0% | -6.0 [-12.0, -1.0] | 1 / 7 | 0.07 | 1 |
| security_incidents:urgency | 100 | 72.0% | 65.0% | +7.0 [-3.0, +17.0] | 16 / 9 | 0.23 | 1 |
| overall | 2000 | 77.0% | 76.7% | +0.2 [-1.4, +1.9] | 136 / 131 | 0.81 | nan |

| task | ECE-10 Verdict-MQ-mix-base-s9 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.1730 | 0.2861 | -0.1131 [-0.1824, -0.0491] |
| agent_trace_observability:needs_review | 0.1701 | 0.2163 | -0.0461 [-0.0961, +0.0151] |
| agent_trace_observability:outcome | 0.1502 | 0.2706 | -0.1204 [-0.1979, -0.0105] |
| agent_trace_observability:risk | 0.2211 | 0.2754 | -0.0543 [-0.0842, -0.0166] |
| agent_trace_observability:urgency | 0.1543 | 0.1784 | -0.0242 [-0.0743, +0.0606] |
| customer_service:action | 0.1075 | 0.1789 | -0.0714 [-0.1387, +0.0287] |
| customer_service:category | 0.1208 | 0.2708 | -0.1500 [-0.1931, -0.0987] |
| customer_service:churn_risk | 0.2110 | 0.2501 | -0.0391 [-0.1111, +0.0409] |
| customer_service:needs_human | 0.0788 | 0.1772 | -0.0984 [-0.1532, +0.0116] |
| customer_service:urgency | 0.0713 | 0.1866 | -0.1153 [-0.1738, +0.0035] |
| invoice_processing:discrepancy_severity | 0.1279 | 0.2179 | -0.0900 [-0.1500, +0.0049] |
| invoice_processing:disposition | 0.1229 | 0.2926 | -0.1698 [-0.2239, -0.0791] |
| invoice_processing:duplicate | 0.0409 | 0.1152 | -0.0743 [-0.1164, -0.0411] |
| invoice_processing:matches_order | 0.0806 | 0.1601 | -0.0795 [-0.1159, -0.0435] |
| invoice_processing:urgency | 0.1835 | 0.0427 | +0.1408 [+0.0252, +0.2114] |
| security_incidents:credential_compromise | 0.1113 | 0.2335 | -0.1223 [-0.1832, -0.0285] |
| security_incidents:disposition | 0.2034 | 0.2940 | -0.0907 [-0.1464, -0.0266] |
| security_incidents:severity | 0.2297 | 0.3277 | -0.0980 [-0.1522, -0.0225] |
| security_incidents:true_positive | 0.1600 | 0.2540 | -0.0940 [-0.1659, -0.0038] |
| security_incidents:urgency | 0.1836 | 0.1445 | +0.0391 [-0.0588, +0.1179] |
| overall | 0.1309 | 0.2141 | -0.0832 [-0.0993, -0.0671] |
