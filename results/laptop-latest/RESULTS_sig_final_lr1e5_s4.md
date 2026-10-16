# Paired significance: Verdict-MQ-large-lr1e5-s4 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large-lr1e5-s4 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 70.0% | 70.0% | +0.0 [-7.0, +7.0] | 6 / 6 | 1 | 1 |
| agent_trace_observability:needs_review | 100 | 84.0% | 84.0% | +0.0 [-3.0, +3.0] | 1 / 1 | 1 | 1 |
| agent_trace_observability:outcome | 100 | 65.0% | 65.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1 | 1 |
| agent_trace_observability:risk | 100 | 81.0% | 82.0% | -1.0 [-6.0, +4.0] | 3 / 4 | 1 | 1 |
| agent_trace_observability:urgency | 100 | 65.0% | 65.0% | +0.0 [-4.0, +4.0] | 2 / 2 | 1 | 1 |
| customer_service:action | 100 | 66.0% | 58.0% | +8.0 [+0.0, +16.0] | 12 / 4 | 0.077 | 1 |
| customer_service:category | 100 | 91.0% | 94.0% | -3.0 [-8.0, +2.0] | 2 / 5 | 0.45 | 1 |
| customer_service:churn_risk | 100 | 80.0% | 80.0% | +0.0 [-8.0, +8.0] | 9 / 9 | 1 | 1 |
| customer_service:needs_human | 100 | 76.0% | 76.0% | +0.0 [-9.0, +9.0] | 10 / 10 | 1 | 1 |
| customer_service:urgency | 100 | 68.0% | 74.0% | -6.0 [-16.0, +4.0] | 11 / 17 | 0.34 | 1 |
| invoice_processing:discrepancy_severity | 100 | 81.0% | 85.0% | -4.0 [-11.0, +3.0] | 5 / 9 | 0.42 | 1 |
| invoice_processing:disposition | 100 | 71.0% | 79.0% | -8.0 [-15.0, -2.0] | 2 / 10 | 0.039 | 0.73 |
| invoice_processing:duplicate | 100 | 91.0% | 92.0% | -1.0 [-6.0, +4.0] | 3 / 4 | 1 | 1 |
| invoice_processing:matches_order | 100 | 95.0% | 94.0% | +1.0 [-2.0, +4.0] | 2 / 1 | 1 | 1 |
| invoice_processing:urgency | 100 | 72.0% | 52.0% | +20.0 [+9.0, +30.0] | 26 / 6 | 0.00054 | 0.011 |
| security_incidents:credential_compromise | 100 | 77.0% | 81.0% | -4.0 [-11.0, +3.0] | 5 / 9 | 0.42 | 1 |
| security_incidents:disposition | 100 | 76.0% | 73.0% | +3.0 [-3.0, +9.0] | 6 / 3 | 0.51 | 1 |
| security_incidents:severity | 100 | 71.0% | 78.0% | -7.0 [-15.0, +1.0] | 5 / 12 | 0.14 | 1 |
| security_incidents:true_positive | 100 | 83.0% | 87.0% | -4.0 [-10.0, +2.0] | 3 / 7 | 0.34 | 1 |
| security_incidents:urgency | 100 | 65.0% | 65.0% | +0.0 [-9.0, +9.0] | 10 / 10 | 1 | 1 |
| overall | 2000 | 76.4% | 76.7% | -0.3 [-1.8, +1.3] | 123 / 129 | 0.75 | nan |

| task | ECE-10 Verdict-MQ-large-lr1e5-s4 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.1959 | 0.2861 | -0.0902 [-0.1627, -0.0162] |
| agent_trace_observability:needs_review | 0.1407 | 0.2163 | -0.0755 [-0.0976, +0.0270] |
| agent_trace_observability:outcome | 0.1969 | 0.2706 | -0.0737 [-0.1614, +0.0371] |
| agent_trace_observability:risk | 0.2299 | 0.2754 | -0.0455 [-0.0843, +0.0111] |
| agent_trace_observability:urgency | 0.1442 | 0.1784 | -0.0343 [-0.0661, +0.0470] |
| customer_service:action | 0.1087 | 0.1789 | -0.0702 [-0.1296, +0.0427] |
| customer_service:category | 0.0877 | 0.2708 | -0.1831 [-0.2187, -0.1213] |
| customer_service:churn_risk | 0.2027 | 0.2501 | -0.0474 [-0.1297, +0.0370] |
| customer_service:needs_human | 0.0649 | 0.1772 | -0.1124 [-0.1603, +0.0050] |
| customer_service:urgency | 0.1059 | 0.1866 | -0.0807 [-0.1514, +0.0241] |
| invoice_processing:discrepancy_severity | 0.1006 | 0.2179 | -0.1173 [-0.1687, -0.0220] |
| invoice_processing:disposition | 0.1167 | 0.2926 | -0.1760 [-0.2175, -0.0709] |
| invoice_processing:duplicate | 0.0480 | 0.1152 | -0.0672 [-0.1068, -0.0218] |
| invoice_processing:matches_order | 0.0681 | 0.1601 | -0.0920 [-0.1185, -0.0564] |
| invoice_processing:urgency | 0.1675 | 0.0427 | +0.1248 [+0.0178, +0.2018] |
| security_incidents:credential_compromise | 0.1382 | 0.2335 | -0.0954 [-0.1623, -0.0102] |
| security_incidents:disposition | 0.2091 | 0.2940 | -0.0850 [-0.1318, +0.0002] |
| security_incidents:severity | 0.2289 | 0.3277 | -0.0988 [-0.1682, -0.0159] |
| security_incidents:true_positive | 0.1329 | 0.2540 | -0.1211 [-0.1656, -0.0469] |
| security_incidents:urgency | 0.1290 | 0.1445 | -0.0155 [-0.0913, +0.0793] |
| overall | 0.1286 | 0.2141 | -0.0855 [-0.1000, -0.0686] |
