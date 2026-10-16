# Paired significance: Verdict-MQ-large-chosen-s4 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large-chosen-s4 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 66.0% | 70.0% | -4.0 [-11.0, +3.0] | 5 / 9 | 0.42 | 1 |
| agent_trace_observability:needs_review | 100 | 84.0% | 84.0% | +0.0 [-5.0, +5.0] | 3 / 3 | 1 | 1 |
| agent_trace_observability:outcome | 100 | 65.0% | 65.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1 | 1 |
| agent_trace_observability:risk | 100 | 78.0% | 82.0% | -4.0 [-11.0, +3.0] | 4 / 8 | 0.39 | 1 |
| agent_trace_observability:urgency | 100 | 63.0% | 65.0% | -2.0 [-8.0, +4.0] | 4 / 6 | 0.75 | 1 |
| customer_service:action | 100 | 64.0% | 58.0% | +6.0 [-3.0, +15.0] | 13 / 7 | 0.26 | 1 |
| customer_service:category | 100 | 95.0% | 94.0% | +1.0 [-4.0, +6.0] | 4 / 3 | 1 | 1 |
| customer_service:churn_risk | 100 | 86.0% | 80.0% | +6.0 [-1.0, +13.0] | 9 / 3 | 0.15 | 1 |
| customer_service:needs_human | 100 | 80.0% | 76.0% | +4.0 [-4.0, +12.0] | 10 / 6 | 0.45 | 1 |
| customer_service:urgency | 100 | 79.0% | 74.0% | +5.0 [-6.0, +16.0] | 17 / 12 | 0.46 | 1 |
| invoice_processing:discrepancy_severity | 100 | 82.0% | 85.0% | -3.0 [-9.0, +3.0] | 4 / 7 | 0.55 | 1 |
| invoice_processing:disposition | 100 | 76.0% | 79.0% | -3.0 [-9.0, +3.0] | 4 / 7 | 0.55 | 1 |
| invoice_processing:duplicate | 100 | 91.0% | 92.0% | -1.0 [-6.0, +4.0] | 3 / 4 | 1 | 1 |
| invoice_processing:matches_order | 100 | 96.0% | 94.0% | +2.0 [-2.0, +6.0] | 3 / 1 | 0.62 | 1 |
| invoice_processing:urgency | 100 | 76.0% | 52.0% | +24.0 [+13.0, +35.0] | 29 / 5 | 3.9e-05 | 0.00077 |
| security_incidents:credential_compromise | 100 | 80.0% | 81.0% | -1.0 [-10.0, +8.0] | 10 / 11 | 1 | 1 |
| security_incidents:disposition | 100 | 76.0% | 73.0% | +3.0 [-3.0, +10.0] | 7 / 4 | 0.55 | 1 |
| security_incidents:severity | 100 | 78.0% | 78.0% | +0.0 [-6.0, +6.0] | 5 / 5 | 1 | 1 |
| security_incidents:true_positive | 100 | 84.0% | 87.0% | -3.0 [-9.0, +3.0] | 3 / 6 | 0.51 | 1 |
| security_incidents:urgency | 100 | 72.0% | 65.0% | +7.0 [-1.0, +15.0] | 12 / 5 | 0.14 | 1 |
| overall | 2000 | 78.5% | 76.7% | +1.8 [+0.3, +3.5] | 149 / 112 | 0.026 | nan |

| task | ECE-10 Verdict-MQ-large-chosen-s4 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.1497 | 0.2861 | -0.1364 [-0.1983, -0.0548] |
| agent_trace_observability:needs_review | 0.1345 | 0.2163 | -0.0817 [-0.1165, +0.0071] |
| agent_trace_observability:outcome | 0.1795 | 0.2706 | -0.0911 [-0.1797, +0.0065] |
| agent_trace_observability:risk | 0.1812 | 0.2754 | -0.0943 [-0.1417, -0.0191] |
| agent_trace_observability:urgency | 0.1332 | 0.1784 | -0.0453 [-0.1008, +0.0280] |
| customer_service:action | 0.1314 | 0.1789 | -0.0475 [-0.1249, +0.0691] |
| customer_service:category | 0.0998 | 0.2708 | -0.1710 [-0.2095, -0.1331] |
| customer_service:churn_risk | 0.2409 | 0.2501 | -0.0092 [-0.0809, +0.0648] |
| customer_service:needs_human | 0.1231 | 0.1772 | -0.0541 [-0.1074, +0.0441] |
| customer_service:urgency | 0.2164 | 0.1866 | +0.0298 [-0.0681, +0.1255] |
| invoice_processing:discrepancy_severity | 0.1503 | 0.2179 | -0.0675 [-0.1225, +0.0214] |
| invoice_processing:disposition | 0.1619 | 0.2926 | -0.1308 [-0.1961, -0.0516] |
| invoice_processing:duplicate | 0.0408 | 0.1152 | -0.0744 [-0.1240, -0.0434] |
| invoice_processing:matches_order | 0.0823 | 0.1601 | -0.0778 [-0.1059, -0.0344] |
| invoice_processing:urgency | 0.1848 | 0.0427 | +0.1421 [+0.0303, +0.2094] |
| security_incidents:credential_compromise | 0.1663 | 0.2335 | -0.0672 [-0.1502, +0.0326] |
| security_incidents:disposition | 0.1896 | 0.2940 | -0.1044 [-0.1613, -0.0301] |
| security_incidents:severity | 0.2604 | 0.3277 | -0.0674 [-0.1248, -0.0029] |
| security_incidents:true_positive | 0.1490 | 0.2540 | -0.1050 [-0.1574, -0.0415] |
| security_incidents:urgency | 0.1950 | 0.1445 | +0.0504 [-0.0377, +0.1202] |
| overall | 0.1456 | 0.2141 | -0.0685 [-0.0842, -0.0518] |
