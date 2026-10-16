# Paired significance: Verdict-MQ-large cls k=0 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large cls k=0 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 70.0% | 70.0% | +0.0 [-5.0, +6.0] | 4 / 4 | 1 | 1 |
| agent_trace_observability:needs_review | 100 | 86.0% | 84.0% | +2.0 [-3.0, +8.0] | 5 / 3 | 0.73 | 1 |
| agent_trace_observability:outcome | 100 | 67.0% | 65.0% | +2.0 [+0.0, +5.0] | 2 / 0 | 0.5 | 1 |
| agent_trace_observability:risk | 100 | 83.0% | 82.0% | +1.0 [-4.0, +6.0] | 4 / 3 | 1 | 1 |
| agent_trace_observability:urgency | 100 | 63.0% | 65.0% | -2.0 [-8.0, +4.0] | 4 / 6 | 0.75 | 1 |
| customer_service:action | 100 | 71.0% | 58.0% | +13.0 [+4.0, +22.0] | 17 / 4 | 0.0072 | 0.14 |
| customer_service:category | 100 | 97.0% | 94.0% | +3.0 [-2.0, +8.0] | 5 / 2 | 0.45 | 1 |
| customer_service:churn_risk | 100 | 89.0% | 80.0% | +9.0 [+3.0, +16.0] | 10 / 1 | 0.012 | 0.21 |
| customer_service:needs_human | 100 | 85.0% | 76.0% | +9.0 [+2.0, +17.0] | 12 / 3 | 0.035 | 0.6 |
| customer_service:urgency | 100 | 78.0% | 74.0% | +4.0 [-5.0, +13.0] | 12 / 8 | 0.5 | 1 |
| invoice_processing:discrepancy_severity | 100 | 85.0% | 85.0% | +0.0 [-7.0, +7.0] | 6 / 6 | 1 | 1 |
| invoice_processing:disposition | 100 | 78.0% | 79.0% | -1.0 [-7.0, +5.0] | 4 / 5 | 1 | 1 |
| invoice_processing:duplicate | 100 | 92.0% | 92.0% | +0.0 [-5.0, +5.0] | 3 / 3 | 1 | 1 |
| invoice_processing:matches_order | 100 | 96.0% | 94.0% | +2.0 [-2.0, +6.0] | 3 / 1 | 0.62 | 1 |
| invoice_processing:urgency | 100 | 79.0% | 52.0% | +27.0 [+17.0, +37.0] | 30 / 3 | 1.4e-06 | 2.8e-05 |
| security_incidents:credential_compromise | 100 | 77.0% | 81.0% | -4.0 [-13.0, +5.0] | 8 / 12 | 0.5 | 1 |
| security_incidents:disposition | 100 | 78.0% | 73.0% | +5.0 [-2.0, +12.0] | 9 / 4 | 0.27 | 1 |
| security_incidents:severity | 100 | 79.0% | 78.0% | +1.0 [-6.0, +9.0] | 8 / 7 | 1 | 1 |
| security_incidents:true_positive | 100 | 88.0% | 87.0% | +1.0 [-5.0, +7.0] | 6 / 5 | 1 | 1 |
| security_incidents:urgency | 100 | 74.0% | 65.0% | +9.0 [+1.0, +17.0] | 13 / 4 | 0.049 | 0.78 |
| overall | 2000 | 80.8% | 76.7% | +4.0 [+2.5, +5.6] | 165 / 84 | 3.2e-07 | nan |

| task | ECE-10 Verdict-MQ-large cls k=0 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.1985 | 0.2861 | -0.0876 [-0.1450, -0.0280] |
| agent_trace_observability:needs_review | 0.1585 | 0.2163 | -0.0578 [-0.0981, +0.0342] |
| agent_trace_observability:outcome | 0.1338 | 0.2706 | -0.1368 [-0.1855, -0.0206] |
| agent_trace_observability:risk | 0.2325 | 0.2754 | -0.0429 [-0.0938, +0.0153] |
| agent_trace_observability:urgency | 0.1188 | 0.1784 | -0.0597 [-0.1042, +0.0644] |
| customer_service:action | 0.1496 | 0.1789 | -0.0293 [-0.0911, +0.0701] |
| customer_service:category | 0.1258 | 0.2708 | -0.1450 [-0.1861, -0.0983] |
| customer_service:churn_risk | 0.2637 | 0.2501 | +0.0136 [-0.0481, +0.0855] |
| customer_service:needs_human | 0.1648 | 0.1772 | -0.0124 [-0.0818, +0.0698] |
| customer_service:urgency | 0.1735 | 0.1866 | -0.0131 [-0.0865, +0.0640] |
| invoice_processing:discrepancy_severity | 0.1505 | 0.2179 | -0.0674 [-0.1351, +0.0000] |
| invoice_processing:disposition | 0.1733 | 0.2926 | -0.1193 [-0.1796, -0.0490] |
| invoice_processing:duplicate | 0.0249 | 0.1152 | -0.0903 [-0.1234, -0.0532] |
| invoice_processing:matches_order | 0.0897 | 0.1601 | -0.0704 [-0.1002, -0.0336] |
| invoice_processing:urgency | 0.2166 | 0.0427 | +0.1739 [+0.0540, +0.2330] |
| security_incidents:credential_compromise | 0.1304 | 0.2335 | -0.1032 [-0.1709, -0.0056] |
| security_incidents:disposition | 0.2261 | 0.2940 | -0.0679 [-0.1183, +0.0231] |
| security_incidents:severity | 0.2758 | 0.3277 | -0.0519 [-0.1138, +0.0335] |
| security_incidents:true_positive | 0.1874 | 0.2540 | -0.0666 [-0.1312, +0.0031] |
| security_incidents:urgency | 0.2011 | 0.1445 | +0.0565 [-0.0285, +0.1278] |
| overall | 0.1664 | 0.2141 | -0.0477 [-0.0636, -0.0318] |
