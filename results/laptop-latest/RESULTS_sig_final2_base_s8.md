# Paired significance: Verdict-MQ-base-s8 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-base-s8 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 55.0% | 70.0% | -15.0 [-23.0, -7.0] | 2 / 17 | 0.00073 | 0.014 |
| agent_trace_observability:needs_review | 100 | 71.0% | 84.0% | -13.0 [-25.0, -1.0] | 12 / 25 | 0.047 | 0.61 |
| agent_trace_observability:outcome | 100 | 56.0% | 65.0% | -9.0 [-15.0, -4.0] | 0 / 9 | 0.0039 | 0.062 |
| agent_trace_observability:risk | 100 | 69.0% | 82.0% | -13.0 [-20.0, -7.0] | 0 / 13 | 0.00024 | 0.0049 |
| agent_trace_observability:urgency | 100 | 60.0% | 65.0% | -5.0 [-11.0, +1.0] | 2 / 7 | 0.18 | 1 |
| customer_service:action | 100 | 61.0% | 58.0% | +3.0 [-6.0, +12.0] | 12 / 9 | 0.66 | 1 |
| customer_service:category | 100 | 90.0% | 94.0% | -4.0 [-10.0, +1.0] | 2 / 6 | 0.29 | 1 |
| customer_service:churn_risk | 100 | 71.0% | 80.0% | -9.0 [-18.0, +0.0] | 6 / 15 | 0.078 | 0.94 |
| customer_service:needs_human | 100 | 74.0% | 76.0% | -2.0 [-11.0, +7.0] | 10 / 12 | 0.83 | 1 |
| customer_service:urgency | 100 | 56.0% | 74.0% | -18.0 [-29.0, -7.0] | 7 / 25 | 0.0021 | 0.038 |
| invoice_processing:discrepancy_severity | 100 | 84.0% | 85.0% | -1.0 [-8.0, +5.0] | 5 / 6 | 1 | 1 |
| invoice_processing:disposition | 100 | 79.0% | 79.0% | +0.0 [-8.0, +8.0] | 8 / 8 | 1 | 1 |
| invoice_processing:duplicate | 100 | 90.0% | 92.0% | -2.0 [-8.0, +4.0] | 4 / 6 | 0.75 | 1 |
| invoice_processing:matches_order | 100 | 96.0% | 94.0% | +2.0 [+0.0, +5.0] | 2 / 0 | 0.5 | 1 |
| invoice_processing:urgency | 100 | 69.0% | 52.0% | +17.0 [+7.0, +27.0] | 23 / 6 | 0.0023 | 0.039 |
| security_incidents:credential_compromise | 100 | 73.0% | 81.0% | -8.0 [-18.0, +2.0] | 8 / 16 | 0.15 | 1 |
| security_incidents:disposition | 100 | 76.0% | 73.0% | +3.0 [-4.0, +10.0] | 8 / 5 | 0.58 | 1 |
| security_incidents:severity | 100 | 64.0% | 78.0% | -14.0 [-24.0, -4.0] | 8 / 22 | 0.016 | 0.24 |
| security_incidents:true_positive | 100 | 79.0% | 87.0% | -8.0 [-17.0, +1.0] | 6 / 14 | 0.12 | 1 |
| security_incidents:urgency | 100 | 53.0% | 65.0% | -12.0 [-22.0, -2.0] | 8 / 20 | 0.036 | 0.5 |
| overall | 2000 | 71.3% | 76.7% | -5.4 [-7.3, -3.5] | 133 / 241 | 2.5e-08 | nan |

| task | ECE-10 Verdict-MQ-base-s8 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.0809 | 0.2861 | -0.2052 [-0.2757, -0.0606] |
| agent_trace_observability:needs_review | 0.1006 | 0.2163 | -0.1157 [-0.1731, -0.0339] |
| agent_trace_observability:outcome | 0.0903 | 0.2706 | -0.1802 [-0.2624, -0.0344] |
| agent_trace_observability:risk | 0.1342 | 0.2754 | -0.1413 [-0.1829, -0.0562] |
| agent_trace_observability:urgency | 0.1174 | 0.1784 | -0.0611 [-0.1188, +0.0039] |
| customer_service:action | 0.1710 | 0.1789 | -0.0079 [-0.1270, +0.1113] |
| customer_service:category | 0.1245 | 0.2708 | -0.1462 [-0.2010, -0.0975] |
| customer_service:churn_risk | 0.1835 | 0.2501 | -0.0666 [-0.1461, +0.0368] |
| customer_service:needs_human | 0.0995 | 0.1772 | -0.0777 [-0.1493, +0.0370] |
| customer_service:urgency | 0.0656 | 0.1866 | -0.1210 [-0.1811, -0.0016] |
| invoice_processing:discrepancy_severity | 0.1014 | 0.2179 | -0.1165 [-0.1629, -0.0228] |
| invoice_processing:disposition | 0.1404 | 0.2926 | -0.1522 [-0.2067, -0.0541] |
| invoice_processing:duplicate | 0.0570 | 0.1152 | -0.0582 [-0.1090, -0.0235] |
| invoice_processing:matches_order | 0.0695 | 0.1601 | -0.0906 [-0.1185, -0.0471] |
| invoice_processing:urgency | 0.1797 | 0.0427 | +0.1370 [+0.0290, +0.1987] |
| security_incidents:credential_compromise | 0.0894 | 0.2335 | -0.1441 [-0.1953, -0.0350] |
| security_incidents:disposition | 0.2638 | 0.2940 | -0.0302 [-0.0925, +0.0481] |
| security_incidents:severity | 0.1728 | 0.3277 | -0.1549 [-0.2404, -0.0509] |
| security_incidents:true_positive | 0.0841 | 0.2540 | -0.1699 [-0.2163, -0.0602] |
| security_incidents:urgency | 0.1009 | 0.1445 | -0.0437 [-0.1275, +0.0724] |
| overall | 0.0881 | 0.2141 | -0.1260 [-0.1443, -0.1071] |
