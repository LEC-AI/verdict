# Paired significance: Verdict-MQ vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 68.0% | 70.0% | -2.0 [-8.0, +3.0] | 3 / 5 | 0.73 | 1 |
| agent_trace_observability:needs_review | 100 | 85.0% | 84.0% | +1.0 [-4.0, +6.0] | 4 / 3 | 1 | 1 |
| agent_trace_observability:outcome | 100 | 69.0% | 65.0% | +4.0 [+1.0, +8.0] | 4 / 0 | 0.12 | 1 |
| agent_trace_observability:risk | 100 | 82.0% | 82.0% | +0.0 [-4.0, +4.0] | 2 / 2 | 1 | 1 |
| agent_trace_observability:urgency | 100 | 66.0% | 65.0% | +1.0 [-6.0, +8.0] | 6 / 5 | 1 | 1 |
| customer_service:action | 100 | 64.0% | 58.0% | +6.0 [-3.0, +15.0] | 13 / 7 | 0.26 | 1 |
| customer_service:category | 100 | 91.0% | 94.0% | -3.0 [-8.0, +2.0] | 2 / 5 | 0.45 | 1 |
| customer_service:churn_risk | 100 | 75.0% | 80.0% | -5.0 [-13.0, +3.0] | 7 / 12 | 0.36 | 1 |
| customer_service:needs_human | 100 | 78.0% | 76.0% | +2.0 [-6.0, +10.0] | 9 / 7 | 0.8 | 1 |
| customer_service:urgency | 100 | 66.0% | 74.0% | -8.0 [-19.0, +3.0] | 12 / 20 | 0.22 | 1 |
| invoice_processing:discrepancy_severity | 100 | 79.0% | 85.0% | -6.0 [-14.0, +1.0] | 5 / 11 | 0.21 | 1 |
| invoice_processing:disposition | 100 | 77.0% | 79.0% | -2.0 [-9.0, +5.0] | 6 / 8 | 0.79 | 1 |
| invoice_processing:duplicate | 100 | 92.0% | 92.0% | +0.0 [-5.0, +6.0] | 4 / 4 | 1 | 1 |
| invoice_processing:matches_order | 100 | 92.0% | 94.0% | -2.0 [-5.0, +0.0] | 0 / 2 | 0.5 | 1 |
| invoice_processing:urgency | 100 | 64.0% | 52.0% | +12.0 [+4.0, +21.0] | 16 / 4 | 0.012 | 0.24 |
| security_incidents:credential_compromise | 100 | 77.0% | 81.0% | -4.0 [-12.0, +4.0] | 6 / 10 | 0.45 | 1 |
| security_incidents:disposition | 100 | 77.0% | 73.0% | +4.0 [-1.0, +10.0] | 6 / 2 | 0.29 | 1 |
| security_incidents:severity | 100 | 76.0% | 78.0% | -2.0 [-11.0, +7.0] | 9 / 11 | 0.82 | 1 |
| security_incidents:true_positive | 100 | 84.0% | 87.0% | -3.0 [-11.0, +4.0] | 6 / 9 | 0.61 | 1 |
| security_incidents:urgency | 100 | 64.0% | 65.0% | -1.0 [-10.0, +9.0] | 11 / 12 | 1 | 1 |
| overall | 2000 | 76.3% | 76.7% | -0.4 [-2.0, +1.2] | 131 / 139 | 0.67 | nan |

| task | ECE-10 Verdict-MQ | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.1741 | 0.2861 | -0.1120 [-0.1673, -0.0570] |
| agent_trace_observability:needs_review | 0.1388 | 0.2163 | -0.0775 [-0.1145, +0.0089] |
| agent_trace_observability:outcome | 0.1505 | 0.2706 | -0.1200 [-0.1675, -0.0405] |
| agent_trace_observability:risk | 0.2343 | 0.2754 | -0.0411 [-0.0771, +0.0071] |
| agent_trace_observability:urgency | 0.1506 | 0.1784 | -0.0278 [-0.0883, +0.0410] |
| customer_service:action | 0.1096 | 0.1789 | -0.0693 [-0.1301, +0.0350] |
| customer_service:category | 0.0971 | 0.2708 | -0.1737 [-0.2155, -0.1302] |
| customer_service:churn_risk | 0.1508 | 0.2501 | -0.0993 [-0.1709, +0.0050] |
| customer_service:needs_human | 0.0967 | 0.1772 | -0.0805 [-0.1408, +0.0127] |
| customer_service:urgency | 0.1778 | 0.1866 | -0.0088 [-0.1098, +0.0858] |
| invoice_processing:discrepancy_severity | 0.0922 | 0.2179 | -0.1256 [-0.1764, -0.0182] |
| invoice_processing:disposition | 0.1351 | 0.2926 | -0.1575 [-0.2102, -0.0683] |
| invoice_processing:duplicate | 0.0647 | 0.1152 | -0.0506 [-0.1052, -0.0166] |
| invoice_processing:matches_order | 0.0674 | 0.1601 | -0.0927 [-0.1274, -0.0327] |
| invoice_processing:urgency | 0.1227 | 0.0427 | +0.0800 [-0.0444, +0.1499] |
| security_incidents:credential_compromise | 0.1176 | 0.2335 | -0.1160 [-0.1805, -0.0283] |
| security_incidents:disposition | 0.2256 | 0.2940 | -0.0685 [-0.1098, +0.0025] |
| security_incidents:severity | 0.2542 | 0.3277 | -0.0735 [-0.1616, +0.0161] |
| security_incidents:true_positive | 0.1483 | 0.2540 | -0.1057 [-0.1710, -0.0264] |
| security_incidents:urgency | 0.1364 | 0.1445 | -0.0081 [-0.0888, +0.0827] |
| overall | 0.1318 | 0.2141 | -0.0823 [-0.0985, -0.0658] |
