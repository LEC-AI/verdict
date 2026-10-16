# Paired significance: Verdict-MQ-large-stable-s33 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large-stable-s33 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 74.0% | 70.0% | +4.0 [+0.0, +9.0] | 5 / 1 | 0.22 | 1 |
| agent_trace_observability:needs_review | 100 | 88.0% | 84.0% | +4.0 [-1.0, +10.0] | 6 / 2 | 0.29 | 1 |
| agent_trace_observability:outcome | 100 | 65.0% | 65.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1 | 1 |
| agent_trace_observability:risk | 100 | 85.0% | 82.0% | +3.0 [-2.0, +8.0] | 5 / 2 | 0.45 | 1 |
| agent_trace_observability:urgency | 100 | 67.0% | 65.0% | +2.0 [-3.0, +8.0] | 5 / 3 | 0.73 | 1 |
| customer_service:action | 100 | 63.0% | 58.0% | +5.0 [-3.0, +13.0] | 11 / 6 | 0.33 | 1 |
| customer_service:category | 100 | 94.0% | 94.0% | +0.0 [-5.0, +5.0] | 3 / 3 | 1 | 1 |
| customer_service:churn_risk | 100 | 81.0% | 80.0% | +1.0 [-6.0, +8.0] | 7 / 6 | 1 | 1 |
| customer_service:needs_human | 100 | 77.0% | 76.0% | +1.0 [-7.0, +9.0] | 9 / 8 | 1 | 1 |
| customer_service:urgency | 100 | 77.0% | 74.0% | +3.0 [-6.0, +12.0] | 13 / 10 | 0.68 | 1 |
| invoice_processing:discrepancy_severity | 100 | 79.0% | 85.0% | -6.0 [-13.0, +1.0] | 4 / 10 | 0.18 | 1 |
| invoice_processing:disposition | 100 | 76.0% | 79.0% | -3.0 [-11.0, +4.0] | 6 / 9 | 0.61 | 1 |
| invoice_processing:duplicate | 100 | 90.0% | 92.0% | -2.0 [-8.0, +3.0] | 3 / 5 | 0.73 | 1 |
| invoice_processing:matches_order | 100 | 97.0% | 94.0% | +3.0 [-1.0, +7.0] | 4 / 1 | 0.38 | 1 |
| invoice_processing:urgency | 100 | 74.0% | 52.0% | +22.0 [+12.0, +32.0] | 27 / 5 | 0.00011 | 0.0023 |
| security_incidents:credential_compromise | 100 | 74.0% | 81.0% | -7.0 [-16.0, +2.0] | 8 / 15 | 0.21 | 1 |
| security_incidents:disposition | 100 | 74.0% | 73.0% | +1.0 [-3.0, +5.0] | 3 / 2 | 1 | 1 |
| security_incidents:severity | 100 | 78.0% | 78.0% | +0.0 [-7.0, +7.0] | 7 / 7 | 1 | 1 |
| security_incidents:true_positive | 100 | 83.0% | 87.0% | -4.0 [-11.0, +3.0] | 4 / 8 | 0.39 | 1 |
| security_incidents:urgency | 100 | 69.0% | 65.0% | +4.0 [-5.0, +13.0] | 13 / 9 | 0.52 | 1 |
| overall | 2000 | 78.2% | 76.7% | +1.5 [-0.0, +3.1] | 143 / 112 | 0.06 | nan |

| task | ECE-10 Verdict-MQ-large-stable-s33 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.2277 | 0.2861 | -0.0584 [-0.1161, -0.0065] |
| agent_trace_observability:needs_review | 0.1741 | 0.2163 | -0.0421 [-0.0874, +0.0213] |
| agent_trace_observability:outcome | 0.1598 | 0.2706 | -0.1108 [-0.1878, -0.0014] |
| agent_trace_observability:risk | 0.2561 | 0.2754 | -0.0194 [-0.0594, +0.0405] |
| agent_trace_observability:urgency | 0.1598 | 0.1784 | -0.0187 [-0.0706, +0.0462] |
| customer_service:action | 0.0974 | 0.1789 | -0.0815 [-0.1529, +0.0245] |
| customer_service:category | 0.0932 | 0.2708 | -0.1775 [-0.2117, -0.1357] |
| customer_service:churn_risk | 0.1893 | 0.2501 | -0.0608 [-0.1271, +0.0135] |
| customer_service:needs_human | 0.0876 | 0.1772 | -0.0896 [-0.1429, +0.0375] |
| customer_service:urgency | 0.1832 | 0.1866 | -0.0034 [-0.0889, +0.0757] |
| invoice_processing:discrepancy_severity | 0.1454 | 0.2179 | -0.0725 [-0.1403, -0.0011] |
| invoice_processing:disposition | 0.1261 | 0.2926 | -0.1665 [-0.2117, -0.0721] |
| invoice_processing:duplicate | 0.0579 | 0.1152 | -0.0573 [-0.1091, -0.0197] |
| invoice_processing:matches_order | 0.0996 | 0.1601 | -0.0604 [-0.1016, -0.0085] |
| invoice_processing:urgency | 0.2028 | 0.0427 | +0.1601 [+0.0426, +0.2229] |
| security_incidents:credential_compromise | 0.0877 | 0.2335 | -0.1458 [-0.2105, -0.0440] |
| security_incidents:disposition | 0.1713 | 0.2940 | -0.1228 [-0.1579, -0.0462] |
| security_incidents:severity | 0.2769 | 0.3277 | -0.0508 [-0.1151, +0.0278] |
| security_incidents:true_positive | 0.1304 | 0.2540 | -0.1236 [-0.1781, -0.0531] |
| security_incidents:urgency | 0.1595 | 0.1445 | +0.0150 [-0.0728, +0.0903] |
| overall | 0.1411 | 0.2141 | -0.0730 [-0.0890, -0.0571] |
