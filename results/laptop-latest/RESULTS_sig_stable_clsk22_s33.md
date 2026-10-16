# Paired significance: Verdict-MQ-large cls k=22 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large cls k=22 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 73.0% | 70.0% | +3.0 [-3.0, +9.0] | 6 / 3 | 0.51 | 1 |
| agent_trace_observability:needs_review | 100 | 89.0% | 84.0% | +5.0 [+0.0, +10.0] | 6 / 1 | 0.12 | 1 |
| agent_trace_observability:outcome | 100 | 68.0% | 65.0% | +3.0 [-2.0, +8.0] | 5 / 2 | 0.45 | 1 |
| agent_trace_observability:risk | 100 | 83.0% | 82.0% | +1.0 [-4.0, +6.0] | 4 / 3 | 1 | 1 |
| agent_trace_observability:urgency | 100 | 66.0% | 65.0% | +1.0 [-4.0, +6.0] | 4 / 3 | 1 | 1 |
| customer_service:action | 100 | 74.0% | 58.0% | +16.0 [+8.0, +25.0] | 19 / 3 | 0.00086 | 0.016 |
| customer_service:category | 100 | 94.0% | 94.0% | +0.0 [-5.0, +6.0] | 4 / 4 | 1 | 1 |
| customer_service:churn_risk | 100 | 88.0% | 80.0% | +8.0 [+2.0, +14.0] | 9 / 1 | 0.021 | 0.39 |
| customer_service:needs_human | 100 | 83.0% | 76.0% | +7.0 [+0.0, +15.0] | 11 / 4 | 0.12 | 1 |
| customer_service:urgency | 100 | 76.0% | 74.0% | +2.0 [-6.0, +10.0] | 9 / 7 | 0.8 | 1 |
| invoice_processing:discrepancy_severity | 100 | 85.0% | 85.0% | +0.0 [-7.0, +7.0] | 7 / 7 | 1 | 1 |
| invoice_processing:disposition | 100 | 73.0% | 79.0% | -6.0 [-12.0, +0.0] | 2 / 8 | 0.11 | 1 |
| invoice_processing:duplicate | 100 | 90.0% | 92.0% | -2.0 [-7.0, +3.0] | 2 / 4 | 0.69 | 1 |
| invoice_processing:matches_order | 100 | 96.0% | 94.0% | +2.0 [+0.0, +5.0] | 2 / 0 | 0.5 | 1 |
| invoice_processing:urgency | 100 | 77.0% | 52.0% | +25.0 [+14.0, +36.0] | 31 / 6 | 4.1e-05 | 0.00083 |
| security_incidents:credential_compromise | 100 | 80.0% | 81.0% | -1.0 [-10.0, +8.0] | 11 / 12 | 1 | 1 |
| security_incidents:disposition | 100 | 79.0% | 73.0% | +6.0 [+0.0, +12.0] | 8 / 2 | 0.11 | 1 |
| security_incidents:severity | 100 | 82.0% | 78.0% | +4.0 [-3.0, +11.0] | 8 / 4 | 0.39 | 1 |
| security_incidents:true_positive | 100 | 87.0% | 87.0% | +0.0 [-6.0, +6.0] | 5 / 5 | 1 | 1 |
| security_incidents:urgency | 100 | 71.0% | 65.0% | +6.0 [-2.0, +14.0] | 12 / 6 | 0.24 | 1 |
| overall | 2000 | 80.7% | 76.7% | +4.0 [+2.4, +5.5] | 165 / 85 | 4.7e-07 | nan |

| task | ECE-10 Verdict-MQ-large cls k=22 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.2244 | 0.2861 | -0.0617 [-0.1292, -0.0010] |
| agent_trace_observability:needs_review | 0.1813 | 0.2163 | -0.0349 [-0.0830, +0.0250] |
| agent_trace_observability:outcome | 0.1807 | 0.2706 | -0.0899 [-0.1642, +0.0095] |
| agent_trace_observability:risk | 0.2432 | 0.2754 | -0.0322 [-0.0807, +0.0258] |
| agent_trace_observability:urgency | 0.1456 | 0.1784 | -0.0329 [-0.0821, +0.0250] |
| customer_service:action | 0.1858 | 0.1789 | +0.0069 [-0.0761, +0.0931] |
| customer_service:category | 0.1152 | 0.2708 | -0.1556 [-0.1994, -0.1197] |
| customer_service:churn_risk | 0.2602 | 0.2501 | +0.0101 [-0.0530, +0.0789] |
| customer_service:needs_human | 0.1393 | 0.1772 | -0.0379 [-0.1065, +0.0449] |
| customer_service:urgency | 0.1481 | 0.1866 | -0.0385 [-0.1021, +0.0494] |
| invoice_processing:discrepancy_severity | 0.1569 | 0.2179 | -0.0610 [-0.1272, +0.0111] |
| invoice_processing:disposition | 0.1404 | 0.2926 | -0.1523 [-0.2014, -0.0620] |
| invoice_processing:duplicate | 0.0454 | 0.1152 | -0.0698 [-0.1164, -0.0386] |
| invoice_processing:matches_order | 0.0991 | 0.1601 | -0.0610 [-0.0923, -0.0186] |
| invoice_processing:urgency | 0.1978 | 0.0427 | +0.1551 [+0.0507, +0.2263] |
| security_incidents:credential_compromise | 0.1471 | 0.2335 | -0.0864 [-0.1708, +0.0096] |
| security_incidents:disposition | 0.2083 | 0.2940 | -0.0857 [-0.1338, +0.0003] |
| security_incidents:severity | 0.2888 | 0.3277 | -0.0389 [-0.0992, +0.0305] |
| security_incidents:true_positive | 0.1589 | 0.2540 | -0.0951 [-0.1388, -0.0260] |
| security_incidents:urgency | 0.1753 | 0.1445 | +0.0308 [-0.0537, +0.1048] |
| overall | 0.1622 | 0.2141 | -0.0519 [-0.0675, -0.0359] |
