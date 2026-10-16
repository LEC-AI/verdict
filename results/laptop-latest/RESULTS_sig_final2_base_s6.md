# Paired significance: Verdict-MQ-base-s6 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-base-s6 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 53.0% | 70.0% | -17.0 [-25.0, -9.0] | 2 / 19 | 0.00022 | 0.0044 |
| agent_trace_observability:needs_review | 100 | 88.0% | 84.0% | +4.0 [-3.0, +11.0] | 8 / 4 | 0.39 | 1 |
| agent_trace_observability:outcome | 100 | 64.0% | 65.0% | -1.0 [-3.0, +0.0] | 0 / 1 | 1 | 1 |
| agent_trace_observability:risk | 100 | 80.0% | 82.0% | -2.0 [-6.0, +2.0] | 1 / 3 | 0.62 | 1 |
| agent_trace_observability:urgency | 100 | 55.0% | 65.0% | -10.0 [-20.0, +0.0] | 8 / 18 | 0.076 | 1 |
| customer_service:action | 100 | 58.0% | 58.0% | +0.0 [-8.0, +8.0] | 9 / 9 | 1 | 1 |
| customer_service:category | 100 | 90.0% | 94.0% | -4.0 [-10.0, +2.0] | 3 / 7 | 0.34 | 1 |
| customer_service:churn_risk | 100 | 72.0% | 80.0% | -8.0 [-17.0, +1.0] | 7 / 15 | 0.13 | 1 |
| customer_service:needs_human | 100 | 66.0% | 76.0% | -10.0 [-19.0, -1.0] | 7 / 17 | 0.064 | 1 |
| customer_service:urgency | 100 | 61.0% | 74.0% | -13.0 [-25.0, -1.0] | 12 / 25 | 0.047 | 0.89 |
| invoice_processing:discrepancy_severity | 100 | 81.0% | 85.0% | -4.0 [-12.0, +4.0] | 6 / 10 | 0.45 | 1 |
| invoice_processing:disposition | 100 | 73.0% | 79.0% | -6.0 [-14.0, +2.0] | 6 / 12 | 0.24 | 1 |
| invoice_processing:duplicate | 100 | 90.0% | 92.0% | -2.0 [-6.0, +2.0] | 1 / 3 | 0.62 | 1 |
| invoice_processing:matches_order | 100 | 89.0% | 94.0% | -5.0 [-12.0, +2.0] | 4 / 9 | 0.27 | 1 |
| invoice_processing:urgency | 100 | 57.0% | 52.0% | +5.0 [-6.0, +16.0] | 19 / 14 | 0.49 | 1 |
| security_incidents:credential_compromise | 100 | 76.0% | 81.0% | -5.0 [-15.0, +5.0] | 10 / 15 | 0.42 | 1 |
| security_incidents:disposition | 100 | 76.0% | 73.0% | +3.0 [-3.0, +9.0] | 6 / 3 | 0.51 | 1 |
| security_incidents:severity | 100 | 68.0% | 78.0% | -10.0 [-19.0, -1.0] | 6 / 16 | 0.052 | 0.94 |
| security_incidents:true_positive | 100 | 82.0% | 87.0% | -5.0 [-12.0, +2.0] | 4 / 9 | 0.27 | 1 |
| security_incidents:urgency | 100 | 62.0% | 65.0% | -3.0 [-14.0, +7.0] | 13 / 16 | 0.71 | 1 |
| overall | 2000 | 72.0% | 76.7% | -4.6 [-6.5, -2.8] | 132 / 225 | 9.8e-07 | nan |

| task | ECE-10 Verdict-MQ-base-s6 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.0919 | 0.2861 | -0.1943 [-0.2793, -0.0532] |
| agent_trace_observability:needs_review | 0.1857 | 0.2163 | -0.0306 [-0.0975, +0.0408] |
| agent_trace_observability:outcome | 0.1250 | 0.2706 | -0.1456 [-0.2022, -0.0610] |
| agent_trace_observability:risk | 0.2544 | 0.2754 | -0.0211 [-0.0615, +0.0168] |
| agent_trace_observability:urgency | 0.0721 | 0.1784 | -0.1063 [-0.1808, +0.0095] |
| customer_service:action | 0.1104 | 0.1789 | -0.0685 [-0.1406, +0.0560] |
| customer_service:category | 0.0898 | 0.2708 | -0.1809 [-0.2208, -0.1202] |
| customer_service:churn_risk | 0.1655 | 0.2501 | -0.0846 [-0.1478, +0.0141] |
| customer_service:needs_human | 0.0655 | 0.1772 | -0.1117 [-0.1869, +0.0290] |
| customer_service:urgency | 0.1179 | 0.1866 | -0.0687 [-0.1475, +0.0459] |
| invoice_processing:discrepancy_severity | 0.1361 | 0.2179 | -0.0818 [-0.1301, +0.0066] |
| invoice_processing:disposition | 0.1170 | 0.2926 | -0.1756 [-0.2332, -0.0705] |
| invoice_processing:duplicate | 0.0460 | 0.1152 | -0.0692 [-0.1212, -0.0389] |
| invoice_processing:matches_order | 0.0379 | 0.1601 | -0.1222 [-0.1445, -0.0533] |
| invoice_processing:urgency | 0.1542 | 0.0427 | +0.1115 [-0.0252, +0.1927] |
| security_incidents:credential_compromise | 0.1301 | 0.2335 | -0.1035 [-0.1825, +0.0089] |
| security_incidents:disposition | 0.1883 | 0.2940 | -0.1057 [-0.1556, -0.0133] |
| security_incidents:severity | 0.2025 | 0.3277 | -0.1252 [-0.2073, -0.0363] |
| security_incidents:true_positive | 0.1545 | 0.2540 | -0.0995 [-0.1656, -0.0095] |
| security_incidents:urgency | 0.1430 | 0.1445 | -0.0015 [-0.0872, +0.0889] |
| overall | 0.1034 | 0.2141 | -0.1107 [-0.1289, -0.0925] |
