# Paired significance: Verdict-MQ-mix-base-s11 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-mix-base-s11 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 73.0% | 70.0% | +3.0 [-3.0, +9.0] | 7 / 4 | 0.55 | 1 |
| agent_trace_observability:needs_review | 100 | 86.0% | 84.0% | +2.0 [-2.0, +6.0] | 3 / 1 | 0.62 | 1 |
| agent_trace_observability:outcome | 100 | 65.0% | 65.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1 | 1 |
| agent_trace_observability:risk | 100 | 76.0% | 82.0% | -6.0 [-12.0, -1.0] | 1 / 7 | 0.07 | 1 |
| agent_trace_observability:urgency | 100 | 66.0% | 65.0% | +1.0 [-2.0, +5.0] | 2 / 1 | 1 | 1 |
| customer_service:action | 100 | 69.0% | 58.0% | +11.0 [+3.0, +19.0] | 15 / 4 | 0.019 | 0.37 |
| customer_service:category | 100 | 91.0% | 94.0% | -3.0 [-8.0, +2.0] | 2 / 5 | 0.45 | 1 |
| customer_service:churn_risk | 100 | 76.0% | 80.0% | -4.0 [-11.0, +3.0] | 5 / 9 | 0.42 | 1 |
| customer_service:needs_human | 100 | 77.0% | 76.0% | +1.0 [-7.0, +10.0] | 10 / 9 | 1 | 1 |
| customer_service:urgency | 100 | 63.0% | 74.0% | -11.0 [-23.0, +0.0] | 13 / 24 | 0.099 | 1 |
| invoice_processing:discrepancy_severity | 100 | 80.0% | 85.0% | -5.0 [-12.0, +3.0] | 5 / 10 | 0.3 | 1 |
| invoice_processing:disposition | 100 | 78.0% | 79.0% | -1.0 [-7.0, +5.0] | 5 / 6 | 1 | 1 |
| invoice_processing:duplicate | 100 | 89.0% | 92.0% | -3.0 [-8.0, +1.0] | 1 / 4 | 0.38 | 1 |
| invoice_processing:matches_order | 100 | 95.0% | 94.0% | +1.0 [+0.0, +3.0] | 1 / 0 | 1 | 1 |
| invoice_processing:urgency | 100 | 65.0% | 52.0% | +13.0 [+5.0, +22.0] | 17 / 4 | 0.0072 | 0.14 |
| security_incidents:credential_compromise | 100 | 77.0% | 81.0% | -4.0 [-14.0, +6.0] | 10 / 14 | 0.54 | 1 |
| security_incidents:disposition | 100 | 72.0% | 73.0% | -1.0 [-7.0, +5.0] | 4 / 5 | 1 | 1 |
| security_incidents:severity | 100 | 76.0% | 78.0% | -2.0 [-10.0, +6.0] | 7 / 9 | 0.8 | 1 |
| security_incidents:true_positive | 100 | 80.0% | 87.0% | -7.0 [-15.0, +0.0] | 4 / 11 | 0.12 | 1 |
| security_incidents:urgency | 100 | 65.0% | 65.0% | +0.0 [-10.0, +10.0] | 13 / 13 | 1 | 1 |
| overall | 2000 | 75.9% | 76.7% | -0.8 [-2.3, +0.8] | 125 / 140 | 0.39 | nan |

| task | ECE-10 Verdict-MQ-mix-base-s11 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.2144 | 0.2861 | -0.0717 [-0.1441, -0.0075] |
| agent_trace_observability:needs_review | 0.1646 | 0.2163 | -0.0516 [-0.0913, -0.0065] |
| agent_trace_observability:outcome | 0.1732 | 0.2706 | -0.0974 [-0.1838, +0.0167] |
| agent_trace_observability:risk | 0.2422 | 0.2754 | -0.0332 [-0.0845, +0.0280] |
| agent_trace_observability:urgency | 0.1599 | 0.1784 | -0.0186 [-0.0588, +0.0289] |
| customer_service:action | 0.1801 | 0.1789 | +0.0012 [-0.0779, +0.0960] |
| customer_service:category | 0.1108 | 0.2708 | -0.1600 [-0.2046, -0.1108] |
| customer_service:churn_risk | 0.1640 | 0.2501 | -0.0861 [-0.1323, -0.0010] |
| customer_service:needs_human | 0.1042 | 0.1772 | -0.0730 [-0.1351, +0.0397] |
| customer_service:urgency | 0.1071 | 0.1866 | -0.0795 [-0.1642, +0.0367] |
| invoice_processing:discrepancy_severity | 0.1511 | 0.2179 | -0.0667 [-0.1268, +0.0081] |
| invoice_processing:disposition | 0.1351 | 0.2926 | -0.1575 [-0.2010, -0.0666] |
| invoice_processing:duplicate | 0.0607 | 0.1152 | -0.0545 [-0.1027, -0.0166] |
| invoice_processing:matches_order | 0.0599 | 0.1601 | -0.1001 [-0.1174, -0.0402] |
| invoice_processing:urgency | 0.1353 | 0.0427 | +0.0926 [-0.0292, +0.1533] |
| security_incidents:credential_compromise | 0.1219 | 0.2335 | -0.1116 [-0.1946, -0.0078] |
| security_incidents:disposition | 0.1579 | 0.2940 | -0.1361 [-0.1806, -0.0574] |
| security_incidents:severity | 0.2315 | 0.3277 | -0.0962 [-0.1683, -0.0160] |
| security_incidents:true_positive | 0.1377 | 0.2540 | -0.1163 [-0.1766, -0.0391] |
| security_incidents:urgency | 0.1194 | 0.1445 | -0.0252 [-0.0997, +0.0819] |
| overall | 0.1276 | 0.2141 | -0.0865 [-0.1023, -0.0704] |
