# Paired significance: Verdict-MQ-mix-base-s10 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-mix-base-s10 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 70.0% | 70.0% | +0.0 [-6.0, +6.0] | 5 / 5 | 1 | 1 |
| agent_trace_observability:needs_review | 100 | 83.0% | 84.0% | -1.0 [-6.0, +4.0] | 3 / 4 | 1 | 1 |
| agent_trace_observability:outcome | 100 | 67.0% | 65.0% | +2.0 [+0.0, +5.0] | 2 / 0 | 0.5 | 1 |
| agent_trace_observability:risk | 100 | 80.0% | 82.0% | -2.0 [-6.0, +2.0] | 1 / 3 | 0.62 | 1 |
| agent_trace_observability:urgency | 100 | 65.0% | 65.0% | +0.0 [-5.0, +5.0] | 3 / 3 | 1 | 1 |
| customer_service:action | 100 | 66.0% | 58.0% | +8.0 [-1.0, +17.0] | 15 / 7 | 0.13 | 1 |
| customer_service:category | 100 | 91.0% | 94.0% | -3.0 [-8.0, +2.0] | 2 / 5 | 0.45 | 1 |
| customer_service:churn_risk | 100 | 84.0% | 80.0% | +4.0 [-4.0, +12.0] | 11 / 7 | 0.48 | 1 |
| customer_service:needs_human | 100 | 79.0% | 76.0% | +3.0 [-5.0, +11.0] | 10 / 7 | 0.63 | 1 |
| customer_service:urgency | 100 | 65.0% | 74.0% | -9.0 [-20.0, +3.0] | 13 / 22 | 0.18 | 1 |
| invoice_processing:discrepancy_severity | 100 | 81.0% | 85.0% | -4.0 [-12.0, +4.0] | 6 / 10 | 0.45 | 1 |
| invoice_processing:disposition | 100 | 77.0% | 79.0% | -2.0 [-10.0, +6.0] | 7 / 9 | 0.8 | 1 |
| invoice_processing:duplicate | 100 | 91.0% | 92.0% | -1.0 [-6.0, +4.0] | 3 / 4 | 1 | 1 |
| invoice_processing:matches_order | 100 | 95.0% | 94.0% | +1.0 [-3.0, +5.0] | 3 / 2 | 1 | 1 |
| invoice_processing:urgency | 100 | 66.0% | 52.0% | +14.0 [+5.0, +23.0] | 19 / 5 | 0.0066 | 0.13 |
| security_incidents:credential_compromise | 100 | 74.0% | 81.0% | -7.0 [-15.0, +1.0] | 5 / 12 | 0.14 | 1 |
| security_incidents:disposition | 100 | 79.0% | 73.0% | +6.0 [-1.0, +13.0] | 10 / 4 | 0.18 | 1 |
| security_incidents:severity | 100 | 66.0% | 78.0% | -12.0 [-21.0, -4.0] | 4 / 16 | 0.012 | 0.22 |
| security_incidents:true_positive | 100 | 80.0% | 87.0% | -7.0 [-14.0, +0.0] | 3 / 10 | 0.092 | 1 |
| security_incidents:urgency | 100 | 69.0% | 65.0% | +4.0 [-6.0, +14.0] | 15 / 11 | 0.56 | 1 |
| overall | 2000 | 76.4% | 76.7% | -0.3 [-1.9, +1.4] | 140 / 146 | 0.77 | nan |

| task | ECE-10 Verdict-MQ-mix-base-s10 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.1924 | 0.2861 | -0.0937 [-0.1586, -0.0290] |
| agent_trace_observability:needs_review | 0.1787 | 0.2163 | -0.0375 [-0.1046, +0.0543] |
| agent_trace_observability:outcome | 0.1688 | 0.2706 | -0.1018 [-0.1404, -0.0003] |
| agent_trace_observability:risk | 0.2199 | 0.2754 | -0.0555 [-0.0996, -0.0115] |
| agent_trace_observability:urgency | 0.1373 | 0.1784 | -0.0412 [-0.0878, +0.0191] |
| customer_service:action | 0.1242 | 0.1789 | -0.0547 [-0.1174, +0.0645] |
| customer_service:category | 0.0917 | 0.2708 | -0.1791 [-0.2155, -0.1380] |
| customer_service:churn_risk | 0.2513 | 0.2501 | +0.0012 [-0.0787, +0.0942] |
| customer_service:needs_human | 0.0997 | 0.1772 | -0.0776 [-0.1336, +0.0268] |
| customer_service:urgency | 0.0879 | 0.1866 | -0.0987 [-0.1733, +0.0097] |
| invoice_processing:discrepancy_severity | 0.1162 | 0.2179 | -0.1016 [-0.1487, -0.0144] |
| invoice_processing:disposition | 0.1411 | 0.2926 | -0.1515 [-0.2113, -0.0704] |
| invoice_processing:duplicate | 0.0584 | 0.1152 | -0.0568 [-0.1061, -0.0200] |
| invoice_processing:matches_order | 0.0842 | 0.1601 | -0.0758 [-0.1083, -0.0244] |
| invoice_processing:urgency | 0.1462 | 0.0427 | +0.1035 [-0.0227, +0.1762] |
| security_incidents:credential_compromise | 0.1112 | 0.2335 | -0.1223 [-0.1919, -0.0356] |
| security_incidents:disposition | 0.2339 | 0.2940 | -0.0602 [-0.1187, +0.0182] |
| security_incidents:severity | 0.1897 | 0.3277 | -0.1380 [-0.2083, -0.0328] |
| security_incidents:true_positive | 0.1275 | 0.2540 | -0.1265 [-0.1733, -0.0361] |
| security_incidents:urgency | 0.1740 | 0.1445 | +0.0295 [-0.0654, +0.1262] |
| overall | 0.1330 | 0.2141 | -0.0812 [-0.0976, -0.0645] |
