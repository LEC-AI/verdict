# Paired significance: Verdict-MQ-s1 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-s1 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 70.0% | 70.0% | +0.0 [-7.0, +7.0] | 6 / 6 | 1 | 1 |
| agent_trace_observability:needs_review | 100 | 85.0% | 84.0% | +1.0 [-4.0, +6.0] | 4 / 3 | 1 | 1 |
| agent_trace_observability:outcome | 100 | 67.0% | 65.0% | +2.0 [+0.0, +5.0] | 2 / 0 | 0.5 | 1 |
| agent_trace_observability:risk | 100 | 82.0% | 82.0% | +0.0 [-5.0, +5.0] | 3 / 3 | 1 | 1 |
| agent_trace_observability:urgency | 100 | 64.0% | 65.0% | -1.0 [-7.0, +5.0] | 4 / 5 | 1 | 1 |
| customer_service:action | 100 | 63.0% | 58.0% | +5.0 [-4.0, +14.0] | 13 / 8 | 0.38 | 1 |
| customer_service:category | 100 | 89.0% | 94.0% | -5.0 [-11.0, +1.0] | 2 / 7 | 0.18 | 1 |
| customer_service:churn_risk | 100 | 81.0% | 80.0% | +1.0 [-7.0, +8.0] | 8 / 7 | 1 | 1 |
| customer_service:needs_human | 100 | 83.0% | 76.0% | +7.0 [-1.0, +15.0] | 12 / 5 | 0.14 | 1 |
| customer_service:urgency | 100 | 66.0% | 74.0% | -8.0 [-20.0, +4.0] | 15 / 23 | 0.26 | 1 |
| invoice_processing:discrepancy_severity | 100 | 83.0% | 85.0% | -2.0 [-9.0, +5.0] | 5 / 7 | 0.77 | 1 |
| invoice_processing:disposition | 100 | 73.0% | 79.0% | -6.0 [-13.0, +1.0] | 4 / 10 | 0.18 | 1 |
| invoice_processing:duplicate | 100 | 90.0% | 92.0% | -2.0 [-6.0, +2.0] | 1 / 3 | 0.62 | 1 |
| invoice_processing:matches_order | 100 | 95.0% | 94.0% | +1.0 [-2.0, +4.0] | 2 / 1 | 1 | 1 |
| invoice_processing:urgency | 100 | 73.0% | 52.0% | +21.0 [+12.0, +31.0] | 24 / 3 | 4.9e-05 | 0.00098 |
| security_incidents:credential_compromise | 100 | 81.0% | 81.0% | +0.0 [-9.0, +9.0] | 10 / 10 | 1 | 1 |
| security_incidents:disposition | 100 | 79.0% | 73.0% | +6.0 [+0.0, +12.0] | 8 / 2 | 0.11 | 1 |
| security_incidents:severity | 100 | 77.0% | 78.0% | -1.0 [-9.0, +6.0] | 7 / 8 | 1 | 1 |
| security_incidents:true_positive | 100 | 84.0% | 87.0% | -3.0 [-11.0, +4.0] | 6 / 9 | 0.61 | 1 |
| security_incidents:urgency | 100 | 65.0% | 65.0% | +0.0 [-10.0, +10.0] | 13 / 13 | 1 | 1 |
| overall | 2000 | 77.5% | 76.7% | +0.8 [-0.8, +2.4] | 149 / 133 | 0.37 | nan |

| task | ECE-10 Verdict-MQ-s1 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.1949 | 0.2861 | -0.0912 [-0.1597, -0.0212] |
| agent_trace_observability:needs_review | 0.1489 | 0.2163 | -0.0674 [-0.1033, +0.0129] |
| agent_trace_observability:outcome | 0.1791 | 0.2706 | -0.0915 [-0.1644, +0.0117] |
| agent_trace_observability:risk | 0.2334 | 0.2754 | -0.0420 [-0.0879, +0.0143] |
| agent_trace_observability:urgency | 0.1475 | 0.1784 | -0.0310 [-0.0969, +0.0493] |
| customer_service:action | 0.1404 | 0.1789 | -0.0385 [-0.1208, +0.0487] |
| customer_service:category | 0.0847 | 0.2708 | -0.1861 [-0.2246, -0.1364] |
| customer_service:churn_risk | 0.2025 | 0.2501 | -0.0476 [-0.1160, +0.0365] |
| customer_service:needs_human | 0.1472 | 0.1772 | -0.0300 [-0.1046, +0.0568] |
| customer_service:urgency | 0.1568 | 0.1866 | -0.0298 [-0.1267, +0.0855] |
| invoice_processing:discrepancy_severity | 0.1313 | 0.2179 | -0.0865 [-0.1298, -0.0034] |
| invoice_processing:disposition | 0.1461 | 0.2926 | -0.1466 [-0.2084, -0.0645] |
| invoice_processing:duplicate | 0.0561 | 0.1152 | -0.0591 [-0.1057, -0.0242] |
| invoice_processing:matches_order | 0.0684 | 0.1601 | -0.0917 [-0.1140, -0.0441] |
| invoice_processing:urgency | 0.1935 | 0.0427 | +0.1508 [+0.0239, +0.2245] |
| security_incidents:credential_compromise | 0.1677 | 0.2335 | -0.0658 [-0.1520, +0.0252] |
| security_incidents:disposition | 0.2443 | 0.2940 | -0.0498 [-0.1038, +0.0225] |
| security_incidents:severity | 0.2626 | 0.3277 | -0.0651 [-0.1411, +0.0112] |
| security_incidents:true_positive | 0.1540 | 0.2540 | -0.1000 [-0.1573, -0.0211] |
| security_incidents:urgency | 0.1220 | 0.1445 | -0.0225 [-0.1023, +0.0656] |
| overall | 0.1440 | 0.2141 | -0.0701 [-0.0861, -0.0533] |
