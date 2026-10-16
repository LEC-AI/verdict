# Paired significance: Verdict-MQ-large cls k=22 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large cls k=22 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 70.0% | 70.0% | +0.0 [-6.0, +6.0] | 4 / 4 | 1 | 1 |
| agent_trace_observability:needs_review | 100 | 86.0% | 84.0% | +2.0 [-4.0, +8.0] | 6 / 4 | 0.75 | 1 |
| agent_trace_observability:outcome | 100 | 70.0% | 65.0% | +5.0 [-1.0, +11.0] | 7 / 2 | 0.18 | 1 |
| agent_trace_observability:risk | 100 | 80.0% | 82.0% | -2.0 [-8.0, +4.0] | 3 / 5 | 0.73 | 1 |
| agent_trace_observability:urgency | 100 | 66.0% | 65.0% | +1.0 [-5.0, +7.0] | 5 / 4 | 1 | 1 |
| customer_service:action | 100 | 71.0% | 58.0% | +13.0 [+3.0, +23.0] | 20 / 7 | 0.019 | 0.36 |
| customer_service:category | 100 | 94.0% | 94.0% | +0.0 [-6.0, +6.0] | 4 / 4 | 1 | 1 |
| customer_service:churn_risk | 100 | 88.0% | 80.0% | +8.0 [+1.0, +15.0] | 11 / 3 | 0.057 | 0.98 |
| customer_service:needs_human | 100 | 81.0% | 76.0% | +5.0 [-3.0, +13.0] | 11 / 6 | 0.33 | 1 |
| customer_service:urgency | 100 | 80.0% | 74.0% | +6.0 [-2.0, +14.0] | 12 / 6 | 0.24 | 1 |
| invoice_processing:discrepancy_severity | 100 | 82.0% | 85.0% | -3.0 [-9.0, +3.0] | 3 / 6 | 0.51 | 1 |
| invoice_processing:disposition | 100 | 75.0% | 79.0% | -4.0 [-12.0, +3.0] | 5 / 9 | 0.42 | 1 |
| invoice_processing:duplicate | 100 | 91.0% | 92.0% | -1.0 [-4.0, +2.0] | 1 / 2 | 1 | 1 |
| invoice_processing:matches_order | 100 | 96.0% | 94.0% | +2.0 [-2.0, +6.0] | 3 / 1 | 0.62 | 1 |
| invoice_processing:urgency | 100 | 83.0% | 52.0% | +31.0 [+21.0, +42.0] | 34 / 3 | 1.2e-07 | 2.5e-06 |
| security_incidents:credential_compromise | 100 | 80.0% | 81.0% | -1.0 [-10.0, +8.0] | 10 / 11 | 1 | 1 |
| security_incidents:disposition | 100 | 80.0% | 73.0% | +7.0 [+2.0, +13.0] | 8 / 1 | 0.039 | 0.7 |
| security_incidents:severity | 100 | 79.0% | 78.0% | +1.0 [-6.0, +8.0] | 7 / 6 | 1 | 1 |
| security_incidents:true_positive | 100 | 88.0% | 87.0% | +1.0 [-6.0, +7.0] | 6 / 5 | 1 | 1 |
| security_incidents:urgency | 100 | 72.0% | 65.0% | +7.0 [-2.0, +16.0] | 14 / 7 | 0.19 | 1 |
| overall | 2000 | 80.6% | 76.7% | +3.9 [+2.3, +5.5] | 174 / 96 | 2.4e-06 | nan |

| task | ECE-10 Verdict-MQ-large cls k=22 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.1907 | 0.2861 | -0.0955 [-0.1574, -0.0377] |
| agent_trace_observability:needs_review | 0.1473 | 0.2163 | -0.0689 [-0.1068, +0.0157] |
| agent_trace_observability:outcome | 0.1464 | 0.2706 | -0.1242 [-0.1755, -0.0171] |
| agent_trace_observability:risk | 0.1983 | 0.2754 | -0.0771 [-0.1214, -0.0186] |
| agent_trace_observability:urgency | 0.1439 | 0.1784 | -0.0346 [-0.0927, +0.0372] |
| customer_service:action | 0.1546 | 0.1789 | -0.0243 [-0.1024, +0.0790] |
| customer_service:category | 0.1137 | 0.2708 | -0.1570 [-0.2026, -0.1101] |
| customer_service:churn_risk | 0.2476 | 0.2501 | -0.0025 [-0.0700, +0.0847] |
| customer_service:needs_human | 0.1199 | 0.1772 | -0.0573 [-0.1087, +0.0376] |
| customer_service:urgency | 0.1871 | 0.1866 | +0.0005 [-0.0710, +0.0728] |
| invoice_processing:discrepancy_severity | 0.1282 | 0.2179 | -0.0897 [-0.1446, -0.0210] |
| invoice_processing:disposition | 0.1283 | 0.2926 | -0.1644 [-0.2120, -0.0529] |
| invoice_processing:duplicate | 0.0372 | 0.1152 | -0.0780 [-0.1213, -0.0508] |
| invoice_processing:matches_order | 0.1102 | 0.1601 | -0.0499 [-0.0939, +0.0033] |
| invoice_processing:urgency | 0.2481 | 0.0427 | +0.2054 [+0.0722, +0.2643] |
| security_incidents:credential_compromise | 0.1535 | 0.2335 | -0.0800 [-0.1592, +0.0121] |
| security_incidents:disposition | 0.2130 | 0.2940 | -0.0810 [-0.1302, -0.0010] |
| security_incidents:severity | 0.2824 | 0.3277 | -0.0453 [-0.1083, +0.0237] |
| security_incidents:true_positive | 0.1780 | 0.2540 | -0.0760 [-0.1391, -0.0061] |
| security_incidents:urgency | 0.1945 | 0.1445 | +0.0500 [-0.0396, +0.1315] |
| overall | 0.1586 | 0.2141 | -0.0556 [-0.0716, -0.0391] |
