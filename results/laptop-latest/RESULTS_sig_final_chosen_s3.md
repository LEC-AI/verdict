# Paired significance: Verdict-MQ-large-chosen-s3 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large-chosen-s3 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 70.0% | 70.0% | +0.0 [-7.0, +7.0] | 6 / 6 | 1 | 1 |
| agent_trace_observability:needs_review | 100 | 81.0% | 84.0% | -3.0 [-7.0, +0.0] | 0 / 3 | 0.25 | 1 |
| agent_trace_observability:outcome | 100 | 73.0% | 65.0% | +8.0 [+3.0, +14.0] | 8 / 0 | 0.0078 | 0.15 |
| agent_trace_observability:risk | 100 | 81.0% | 82.0% | -1.0 [-7.0, +6.0] | 5 / 6 | 1 | 1 |
| agent_trace_observability:urgency | 100 | 69.0% | 65.0% | +4.0 [-1.0, +10.0] | 6 / 2 | 0.29 | 1 |
| customer_service:action | 100 | 69.0% | 58.0% | +11.0 [+2.0, +20.0] | 16 / 5 | 0.027 | 0.48 |
| customer_service:category | 100 | 96.0% | 94.0% | +2.0 [-3.0, +7.0] | 4 / 2 | 0.69 | 1 |
| customer_service:churn_risk | 100 | 85.0% | 80.0% | +5.0 [-1.0, +12.0] | 8 / 3 | 0.23 | 1 |
| customer_service:needs_human | 100 | 78.0% | 76.0% | +2.0 [-6.0, +10.0] | 9 / 7 | 0.8 | 1 |
| customer_service:urgency | 100 | 75.0% | 74.0% | +1.0 [-10.0, +12.0] | 17 / 16 | 1 | 1 |
| invoice_processing:discrepancy_severity | 100 | 82.0% | 85.0% | -3.0 [-10.0, +3.0] | 4 / 7 | 0.55 | 1 |
| invoice_processing:disposition | 100 | 75.0% | 79.0% | -4.0 [-10.0, +2.0] | 3 / 7 | 0.34 | 1 |
| invoice_processing:duplicate | 100 | 91.0% | 92.0% | -1.0 [-6.0, +4.0] | 3 / 4 | 1 | 1 |
| invoice_processing:matches_order | 100 | 97.0% | 94.0% | +3.0 [-1.0, +7.0] | 4 / 1 | 0.38 | 1 |
| invoice_processing:urgency | 100 | 79.0% | 52.0% | +27.0 [+17.0, +38.0] | 31 / 4 | 3.5e-06 | 6.9e-05 |
| security_incidents:credential_compromise | 100 | 79.0% | 81.0% | -2.0 [-10.0, +6.0] | 8 / 10 | 0.81 | 1 |
| security_incidents:disposition | 100 | 79.0% | 73.0% | +6.0 [+0.0, +12.0] | 8 / 2 | 0.11 | 1 |
| security_incidents:severity | 100 | 77.0% | 78.0% | -1.0 [-8.0, +6.0] | 6 / 7 | 1 | 1 |
| security_incidents:true_positive | 100 | 83.0% | 87.0% | -4.0 [-10.0, +2.0] | 3 / 7 | 0.34 | 1 |
| security_incidents:urgency | 100 | 72.0% | 65.0% | +7.0 [-1.0, +15.0] | 12 / 5 | 0.14 | 1 |
| overall | 2000 | 79.5% | 76.7% | +2.8 [+1.3, +4.4] | 161 / 104 | 0.00056 | nan |

| task | ECE-10 Verdict-MQ-large-chosen-s3 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.1954 | 0.2861 | -0.0907 [-0.1649, -0.0243] |
| agent_trace_observability:needs_review | 0.1915 | 0.2163 | -0.0248 [-0.1129, +0.0756] |
| agent_trace_observability:outcome | 0.1731 | 0.2706 | -0.0975 [-0.1534, -0.0225] |
| agent_trace_observability:risk | 0.2174 | 0.2754 | -0.0581 [-0.1032, +0.0095] |
| agent_trace_observability:urgency | 0.1790 | 0.1784 | +0.0005 [-0.0499, +0.0801] |
| customer_service:action | 0.1529 | 0.1789 | -0.0260 [-0.1076, +0.0639] |
| customer_service:category | 0.1040 | 0.2708 | -0.1668 [-0.2074, -0.1242] |
| customer_service:churn_risk | 0.2388 | 0.2501 | -0.0113 [-0.0792, +0.0615] |
| customer_service:needs_human | 0.1146 | 0.1772 | -0.0627 [-0.1254, +0.0276] |
| customer_service:urgency | 0.1648 | 0.1866 | -0.0219 [-0.1264, +0.0771] |
| invoice_processing:discrepancy_severity | 0.1212 | 0.2179 | -0.0966 [-0.1542, -0.0268] |
| invoice_processing:disposition | 0.1332 | 0.2926 | -0.1594 [-0.2079, -0.0678] |
| invoice_processing:duplicate | 0.0456 | 0.1152 | -0.0696 [-0.1096, -0.0244] |
| invoice_processing:matches_order | 0.0957 | 0.1601 | -0.0643 [-0.1090, -0.0219] |
| invoice_processing:urgency | 0.2261 | 0.0427 | +0.1834 [+0.0472, +0.2445] |
| security_incidents:credential_compromise | 0.1436 | 0.2335 | -0.0899 [-0.1500, +0.0071] |
| security_incidents:disposition | 0.2121 | 0.2940 | -0.0819 [-0.1377, -0.0116] |
| security_incidents:severity | 0.2554 | 0.3277 | -0.0723 [-0.1366, +0.0009] |
| security_incidents:true_positive | 0.1578 | 0.2540 | -0.0962 [-0.1414, -0.0228] |
| security_incidents:urgency | 0.1867 | 0.1445 | +0.0421 [-0.0437, +0.1230] |
| overall | 0.1539 | 0.2141 | -0.0603 [-0.0764, -0.0442] |
