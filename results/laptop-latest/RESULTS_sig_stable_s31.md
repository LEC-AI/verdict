# Paired significance: Verdict-MQ-large-stable-s31 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large-stable-s31 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 69.0% | 70.0% | -1.0 [-8.0, +6.0] | 5 / 6 | 1 | 1 |
| agent_trace_observability:needs_review | 100 | 87.0% | 84.0% | +3.0 [-1.0, +8.0] | 4 / 1 | 0.38 | 1 |
| agent_trace_observability:outcome | 100 | 67.0% | 65.0% | +2.0 [-2.0, +6.0] | 3 / 1 | 0.62 | 1 |
| agent_trace_observability:risk | 100 | 81.0% | 82.0% | -1.0 [-5.0, +3.0] | 2 / 3 | 1 | 1 |
| agent_trace_observability:urgency | 100 | 67.0% | 65.0% | +2.0 [-5.0, +9.0] | 7 / 5 | 0.77 | 1 |
| customer_service:action | 100 | 71.0% | 58.0% | +13.0 [+5.0, +21.0] | 16 / 3 | 0.0044 | 0.084 |
| customer_service:category | 100 | 96.0% | 94.0% | +2.0 [-3.0, +7.0] | 4 / 2 | 0.69 | 1 |
| customer_service:churn_risk | 100 | 85.0% | 80.0% | +5.0 [-1.0, +12.0] | 8 / 3 | 0.23 | 1 |
| customer_service:needs_human | 100 | 84.0% | 76.0% | +8.0 [+0.0, +16.0] | 12 / 4 | 0.077 | 1 |
| customer_service:urgency | 100 | 81.0% | 74.0% | +7.0 [-2.0, +16.0] | 15 / 8 | 0.21 | 1 |
| invoice_processing:discrepancy_severity | 100 | 82.0% | 85.0% | -3.0 [-10.0, +4.0] | 5 / 8 | 0.58 | 1 |
| invoice_processing:disposition | 100 | 71.0% | 79.0% | -8.0 [-15.0, -2.0] | 1 / 9 | 0.021 | 0.39 |
| invoice_processing:duplicate | 100 | 92.0% | 92.0% | +0.0 [-5.0, +5.0] | 3 / 3 | 1 | 1 |
| invoice_processing:matches_order | 100 | 96.0% | 94.0% | +2.0 [+0.0, +5.0] | 2 / 0 | 0.5 | 1 |
| invoice_processing:urgency | 100 | 79.0% | 52.0% | +27.0 [+17.0, +37.0] | 30 / 3 | 1.4e-06 | 2.8e-05 |
| security_incidents:credential_compromise | 100 | 76.0% | 81.0% | -5.0 [-14.0, +3.0] | 7 / 12 | 0.36 | 1 |
| security_incidents:disposition | 100 | 73.0% | 73.0% | +0.0 [-6.0, +6.0] | 5 / 5 | 1 | 1 |
| security_incidents:severity | 100 | 78.0% | 78.0% | +0.0 [-6.0, +6.0] | 5 / 5 | 1 | 1 |
| security_incidents:true_positive | 100 | 84.0% | 87.0% | -3.0 [-10.0, +4.0] | 5 / 8 | 0.58 | 1 |
| security_incidents:urgency | 100 | 67.0% | 65.0% | +2.0 [-7.0, +11.0] | 12 / 10 | 0.83 | 1 |
| overall | 2000 | 79.3% | 76.7% | +2.6 [+1.1, +4.2] | 151 / 99 | 0.0012 | nan |

| task | ECE-10 Verdict-MQ-large-stable-s31 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.1734 | 0.2861 | -0.1127 [-0.1717, -0.0242] |
| agent_trace_observability:needs_review | 0.1493 | 0.2163 | -0.0669 [-0.1049, -0.0021] |
| agent_trace_observability:outcome | 0.1403 | 0.2706 | -0.1303 [-0.1827, -0.0135] |
| agent_trace_observability:risk | 0.2298 | 0.2754 | -0.0457 [-0.0800, +0.0079] |
| agent_trace_observability:urgency | 0.1563 | 0.1784 | -0.0221 [-0.0758, +0.0595] |
| customer_service:action | 0.1563 | 0.1789 | -0.0226 [-0.0945, +0.0798] |
| customer_service:category | 0.1085 | 0.2708 | -0.1623 [-0.2069, -0.1251] |
| customer_service:churn_risk | 0.2274 | 0.2501 | -0.0227 [-0.0882, +0.0475] |
| customer_service:needs_human | 0.1599 | 0.1772 | -0.0173 [-0.0877, +0.0699] |
| customer_service:urgency | 0.2265 | 0.1866 | +0.0399 [-0.0536, +0.1176] |
| invoice_processing:discrepancy_severity | 0.1310 | 0.2179 | -0.0868 [-0.1439, -0.0100] |
| invoice_processing:disposition | 0.1739 | 0.2926 | -0.1187 [-0.1708, -0.0226] |
| invoice_processing:duplicate | 0.0456 | 0.1152 | -0.0696 [-0.1156, -0.0358] |
| invoice_processing:matches_order | 0.0903 | 0.1601 | -0.0697 [-0.0969, -0.0175] |
| invoice_processing:urgency | 0.2265 | 0.0427 | +0.1838 [+0.0511, +0.2396] |
| security_incidents:credential_compromise | 0.1178 | 0.2335 | -0.1157 [-0.1822, -0.0278] |
| security_incidents:disposition | 0.1882 | 0.2940 | -0.1059 [-0.1468, -0.0359] |
| security_incidents:severity | 0.2703 | 0.3277 | -0.0574 [-0.1095, +0.0145] |
| security_incidents:true_positive | 0.1394 | 0.2540 | -0.1146 [-0.1653, -0.0419] |
| security_incidents:urgency | 0.1414 | 0.1445 | -0.0031 [-0.0872, +0.0749] |
| overall | 0.1537 | 0.2141 | -0.0604 [-0.0750, -0.0436] |
