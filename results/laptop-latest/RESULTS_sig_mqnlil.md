# Paired significance: Verdict-MQ-large vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 70.0% | 70.0% | +0.0 [-7.0, +7.0] | 6 / 6 | 1 | 1 |
| agent_trace_observability:needs_review | 100 | 85.0% | 84.0% | +1.0 [-2.0, +5.0] | 2 / 1 | 1 | 1 |
| agent_trace_observability:outcome | 100 | 66.0% | 65.0% | +1.0 [+0.0, +3.0] | 1 / 0 | 1 | 1 |
| agent_trace_observability:risk | 100 | 81.0% | 82.0% | -1.0 [-5.0, +2.0] | 1 / 2 | 1 | 1 |
| agent_trace_observability:urgency | 100 | 67.0% | 65.0% | +2.0 [-4.0, +8.0] | 5 / 3 | 0.73 | 1 |
| customer_service:action | 100 | 68.0% | 58.0% | +10.0 [+1.0, +19.0] | 16 / 6 | 0.052 | 1 |
| customer_service:category | 100 | 93.0% | 94.0% | -1.0 [-7.0, +5.0] | 4 / 5 | 1 | 1 |
| customer_service:churn_risk | 100 | 84.0% | 80.0% | +4.0 [-3.0, +11.0] | 9 / 5 | 0.42 | 1 |
| customer_service:needs_human | 100 | 80.0% | 76.0% | +4.0 [-4.0, +12.0] | 10 / 6 | 0.45 | 1 |
| customer_service:urgency | 100 | 75.0% | 74.0% | +1.0 [-9.0, +11.0] | 14 / 13 | 1 | 1 |
| invoice_processing:discrepancy_severity | 100 | 78.0% | 85.0% | -7.0 [-14.0, +0.0] | 3 / 10 | 0.092 | 1 |
| invoice_processing:disposition | 100 | 78.0% | 79.0% | -1.0 [-9.0, +7.0] | 8 / 9 | 1 | 1 |
| invoice_processing:duplicate | 100 | 88.0% | 92.0% | -4.0 [-8.0, -1.0] | 0 / 4 | 0.12 | 1 |
| invoice_processing:matches_order | 100 | 96.0% | 94.0% | +2.0 [-3.0, +7.0] | 4 / 2 | 0.69 | 1 |
| invoice_processing:urgency | 100 | 81.0% | 52.0% | +29.0 [+19.0, +39.0] | 31 / 2 | 1.3e-07 | 2.6e-06 |
| security_incidents:credential_compromise | 100 | 78.0% | 81.0% | -3.0 [-12.0, +6.0] | 9 / 12 | 0.66 | 1 |
| security_incidents:disposition | 100 | 78.0% | 73.0% | +5.0 [-1.0, +11.0] | 8 / 3 | 0.23 | 1 |
| security_incidents:severity | 100 | 76.0% | 78.0% | -2.0 [-10.0, +5.0] | 6 / 8 | 0.79 | 1 |
| security_incidents:true_positive | 100 | 85.0% | 87.0% | -2.0 [-9.0, +5.0] | 5 / 7 | 0.77 | 1 |
| security_incidents:urgency | 100 | 71.0% | 65.0% | +6.0 [-3.0, +15.0] | 14 / 8 | 0.29 | 1 |
| overall | 2000 | 78.9% | 76.7% | +2.2 [+0.6, +3.8] | 156 / 112 | 0.0085 | nan |

| task | ECE-10 Verdict-MQ-large | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.1823 | 0.2861 | -0.1038 [-0.1679, -0.0333] |
| agent_trace_observability:needs_review | 0.1397 | 0.2163 | -0.0766 [-0.1022, +0.0220] |
| agent_trace_observability:outcome | 0.1719 | 0.2706 | -0.0987 [-0.1816, +0.0081] |
| agent_trace_observability:risk | 0.2071 | 0.2754 | -0.0683 [-0.1004, -0.0259] |
| agent_trace_observability:urgency | 0.1471 | 0.1784 | -0.0314 [-0.0773, +0.0404] |
| customer_service:action | 0.1561 | 0.1789 | -0.0228 [-0.1079, +0.0878] |
| customer_service:category | 0.0749 | 0.2708 | -0.1958 [-0.2296, -0.1516] |
| customer_service:churn_risk | 0.2285 | 0.2501 | -0.0216 [-0.0972, +0.0581] |
| customer_service:needs_human | 0.1100 | 0.1772 | -0.0672 [-0.1141, +0.0419] |
| customer_service:urgency | 0.2006 | 0.1866 | +0.0140 [-0.0829, +0.1024] |
| invoice_processing:discrepancy_severity | 0.1099 | 0.2179 | -0.1079 [-0.1667, -0.0267] |
| invoice_processing:disposition | 0.1563 | 0.2926 | -0.1363 [-0.1985, -0.0508] |
| invoice_processing:duplicate | 0.0745 | 0.1152 | -0.0407 [-0.0995, -0.0067] |
| invoice_processing:matches_order | 0.0848 | 0.1601 | -0.0753 [-0.1165, -0.0184] |
| invoice_processing:urgency | 0.2458 | 0.0427 | +0.2031 [+0.0747, +0.2576] |
| security_incidents:credential_compromise | 0.1318 | 0.2335 | -0.1018 [-0.1838, -0.0101] |
| security_incidents:disposition | 0.2211 | 0.2940 | -0.0730 [-0.1331, -0.0034] |
| security_incidents:severity | 0.2463 | 0.3277 | -0.0814 [-0.1448, -0.0041] |
| security_incidents:true_positive | 0.1592 | 0.2540 | -0.0948 [-0.1502, -0.0235] |
| security_incidents:urgency | 0.1855 | 0.1445 | +0.0410 [-0.0528, +0.1142] |
| overall | 0.1471 | 0.2141 | -0.0670 [-0.0825, -0.0502] |
