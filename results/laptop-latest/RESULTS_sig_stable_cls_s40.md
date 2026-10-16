# Paired significance: Verdict-MQ-large cls k=0 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large cls k=0 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 69.0% | 70.0% | -1.0 [-8.0, +6.0] | 6 / 7 | 1 | 1 |
| agent_trace_observability:needs_review | 100 | 87.0% | 84.0% | +3.0 [-1.0, +8.0] | 4 / 1 | 0.38 | 1 |
| agent_trace_observability:outcome | 100 | 66.0% | 65.0% | +1.0 [-3.0, +5.0] | 3 / 2 | 1 | 1 |
| agent_trace_observability:risk | 100 | 82.0% | 82.0% | +0.0 [-6.0, +6.0] | 5 / 5 | 1 | 1 |
| agent_trace_observability:urgency | 100 | 66.0% | 65.0% | +1.0 [-6.0, +8.0] | 6 / 5 | 1 | 1 |
| customer_service:action | 100 | 70.0% | 58.0% | +12.0 [+4.0, +20.0] | 16 / 4 | 0.012 | 0.21 |
| customer_service:category | 100 | 94.0% | 94.0% | +0.0 [-5.0, +5.0] | 3 / 3 | 1 | 1 |
| customer_service:churn_risk | 100 | 90.0% | 80.0% | +10.0 [+4.0, +17.0] | 11 / 1 | 0.0063 | 0.12 |
| customer_service:needs_human | 100 | 80.0% | 76.0% | +4.0 [-4.0, +12.0] | 10 / 6 | 0.45 | 1 |
| customer_service:urgency | 100 | 76.0% | 74.0% | +2.0 [-7.0, +11.0] | 12 / 10 | 0.83 | 1 |
| invoice_processing:discrepancy_severity | 100 | 84.0% | 85.0% | -1.0 [-7.0, +5.0] | 5 / 6 | 1 | 1 |
| invoice_processing:disposition | 100 | 76.0% | 79.0% | -3.0 [-9.0, +3.0] | 3 / 6 | 0.51 | 1 |
| invoice_processing:duplicate | 100 | 91.0% | 92.0% | -1.0 [-6.0, +4.0] | 3 / 4 | 1 | 1 |
| invoice_processing:matches_order | 100 | 95.0% | 94.0% | +1.0 [-2.0, +4.0] | 2 / 1 | 1 | 1 |
| invoice_processing:urgency | 100 | 79.0% | 52.0% | +27.0 [+16.0, +38.0] | 32 / 5 | 7.4e-06 | 0.00015 |
| security_incidents:credential_compromise | 100 | 74.0% | 81.0% | -7.0 [-15.0, +1.0] | 5 / 12 | 0.14 | 1 |
| security_incidents:disposition | 100 | 77.0% | 73.0% | +4.0 [-3.0, +11.0] | 8 / 4 | 0.39 | 1 |
| security_incidents:severity | 100 | 82.0% | 78.0% | +4.0 [-4.0, +12.0] | 10 / 6 | 0.45 | 1 |
| security_incidents:true_positive | 100 | 84.0% | 87.0% | -3.0 [-10.0, +4.0] | 5 / 8 | 0.58 | 1 |
| security_incidents:urgency | 100 | 74.0% | 65.0% | +9.0 [+1.0, +18.0] | 14 / 5 | 0.064 | 1 |
| overall | 2000 | 79.8% | 76.7% | +3.1 [+1.5, +4.7] | 163 / 101 | 0.00016 | nan |

| task | ECE-10 Verdict-MQ-large cls k=0 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.1809 | 0.2861 | -0.1052 [-0.1741, -0.0293] |
| agent_trace_observability:needs_review | 0.1573 | 0.2163 | -0.0590 [-0.0914, +0.0194] |
| agent_trace_observability:outcome | 0.1570 | 0.2706 | -0.1136 [-0.1797, -0.0047] |
| agent_trace_observability:risk | 0.2250 | 0.2754 | -0.0504 [-0.1088, +0.0139] |
| agent_trace_observability:urgency | 0.1495 | 0.1784 | -0.0290 [-0.0924, +0.0401] |
| customer_service:action | 0.1469 | 0.1789 | -0.0320 [-0.1036, +0.0579] |
| customer_service:category | 0.1012 | 0.2708 | -0.1696 [-0.2076, -0.1322] |
| customer_service:churn_risk | 0.2763 | 0.2501 | +0.0262 [-0.0367, +0.1082] |
| customer_service:needs_human | 0.1246 | 0.1772 | -0.0527 [-0.1105, +0.0554] |
| customer_service:urgency | 0.1526 | 0.1866 | -0.0340 [-0.1104, +0.0437] |
| invoice_processing:discrepancy_severity | 0.1401 | 0.2179 | -0.0778 [-0.1369, -0.0130] |
| invoice_processing:disposition | 0.1433 | 0.2926 | -0.1493 [-0.1899, -0.0620] |
| invoice_processing:duplicate | 0.0480 | 0.1152 | -0.0672 [-0.1112, -0.0275] |
| invoice_processing:matches_order | 0.1063 | 0.1601 | -0.0537 [-0.1006, -0.0066] |
| invoice_processing:urgency | 0.2183 | 0.0427 | +0.1756 [+0.0608, +0.2419] |
| security_incidents:credential_compromise | 0.1190 | 0.2335 | -0.1145 [-0.1760, -0.0012] |
| security_incidents:disposition | 0.1924 | 0.2940 | -0.1016 [-0.1463, -0.0151] |
| security_incidents:severity | 0.2999 | 0.3277 | -0.0278 [-0.0975, +0.0571] |
| security_incidents:true_positive | 0.1424 | 0.2540 | -0.1116 [-0.1508, -0.0341] |
| security_incidents:urgency | 0.2027 | 0.1445 | +0.0581 [-0.0232, +0.1375] |
| overall | 0.1552 | 0.2141 | -0.0589 [-0.0752, -0.0431] |
