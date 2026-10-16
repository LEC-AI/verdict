# Paired significance: Verdict-MQ-large-chosen-s5 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large-chosen-s5 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 68.0% | 70.0% | -2.0 [-8.0, +4.0] | 4 / 6 | 0.75 | 1 |
| agent_trace_observability:needs_review | 100 | 85.0% | 84.0% | +1.0 [-2.0, +5.0] | 2 / 1 | 1 | 1 |
| agent_trace_observability:outcome | 100 | 66.0% | 65.0% | +1.0 [+0.0, +3.0] | 1 / 0 | 1 | 1 |
| agent_trace_observability:risk | 100 | 77.0% | 82.0% | -5.0 [-10.0, +0.0] | 1 / 6 | 0.12 | 1 |
| agent_trace_observability:urgency | 100 | 69.0% | 65.0% | +4.0 [-2.0, +10.0] | 7 / 3 | 0.34 | 1 |
| customer_service:action | 100 | 66.0% | 58.0% | +8.0 [-1.0, +17.0] | 16 / 8 | 0.15 | 1 |
| customer_service:category | 100 | 95.0% | 94.0% | +1.0 [-4.0, +6.0] | 4 / 3 | 1 | 1 |
| customer_service:churn_risk | 100 | 84.0% | 80.0% | +4.0 [-2.0, +10.0] | 7 / 3 | 0.34 | 1 |
| customer_service:needs_human | 100 | 76.0% | 76.0% | +0.0 [-9.0, +9.0] | 11 / 11 | 1 | 1 |
| customer_service:urgency | 100 | 76.0% | 74.0% | +2.0 [-8.0, +12.0] | 15 / 13 | 0.85 | 1 |
| invoice_processing:discrepancy_severity | 100 | 82.0% | 85.0% | -3.0 [-10.0, +3.0] | 4 / 7 | 0.55 | 1 |
| invoice_processing:disposition | 100 | 74.0% | 79.0% | -5.0 [-11.0, +1.0] | 2 / 7 | 0.18 | 1 |
| invoice_processing:duplicate | 100 | 90.0% | 92.0% | -2.0 [-7.0, +3.0] | 2 / 4 | 0.69 | 1 |
| invoice_processing:matches_order | 100 | 96.0% | 94.0% | +2.0 [-2.0, +6.0] | 3 / 1 | 0.62 | 1 |
| invoice_processing:urgency | 100 | 77.0% | 52.0% | +25.0 [+14.0, +36.0] | 30 / 5 | 2.2e-05 | 0.00045 |
| security_incidents:credential_compromise | 100 | 81.0% | 81.0% | +0.0 [-8.0, +8.0] | 9 / 9 | 1 | 1 |
| security_incidents:disposition | 100 | 77.0% | 73.0% | +4.0 [-2.0, +10.0] | 7 / 3 | 0.34 | 1 |
| security_incidents:severity | 100 | 79.0% | 78.0% | +1.0 [-5.0, +7.0] | 6 / 5 | 1 | 1 |
| security_incidents:true_positive | 100 | 79.0% | 87.0% | -8.0 [-15.0, -1.0] | 3 / 11 | 0.057 | 1 |
| security_incidents:urgency | 100 | 69.0% | 65.0% | +4.0 [-4.0, +12.0] | 11 / 7 | 0.48 | 1 |
| overall | 2000 | 78.3% | 76.7% | +1.6 [+0.1, +3.1] | 145 / 113 | 0.053 | nan |

| task | ECE-10 Verdict-MQ-large-chosen-s5 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.1759 | 0.2861 | -0.1103 [-0.1742, -0.0454] |
| agent_trace_observability:needs_review | 0.1412 | 0.2163 | -0.0751 [-0.1010, +0.0115] |
| agent_trace_observability:outcome | 0.1656 | 0.2706 | -0.1050 [-0.1673, -0.0154] |
| agent_trace_observability:risk | 0.1765 | 0.2754 | -0.0990 [-0.1301, -0.0318] |
| agent_trace_observability:urgency | 0.1734 | 0.1784 | -0.0051 [-0.0574, +0.0868] |
| customer_service:action | 0.1065 | 0.1789 | -0.0724 [-0.1501, +0.0373] |
| customer_service:category | 0.1091 | 0.2708 | -0.1617 [-0.2120, -0.1135] |
| customer_service:churn_risk | 0.2144 | 0.2501 | -0.0357 [-0.0906, +0.0378] |
| customer_service:needs_human | 0.0862 | 0.1772 | -0.0910 [-0.1454, +0.0325] |
| customer_service:urgency | 0.1668 | 0.1866 | -0.0198 [-0.1137, +0.0691] |
| invoice_processing:discrepancy_severity | 0.1041 | 0.2179 | -0.1138 [-0.1585, -0.0248] |
| invoice_processing:disposition | 0.1268 | 0.2926 | -0.1658 [-0.2153, -0.0817] |
| invoice_processing:duplicate | 0.0468 | 0.1152 | -0.0684 [-0.1134, -0.0335] |
| invoice_processing:matches_order | 0.0776 | 0.1601 | -0.0825 [-0.1175, -0.0375] |
| invoice_processing:urgency | 0.1927 | 0.0427 | +0.1500 [+0.0296, +0.2153] |
| security_incidents:credential_compromise | 0.1522 | 0.2335 | -0.0813 [-0.1580, +0.0037] |
| security_incidents:disposition | 0.2089 | 0.2940 | -0.0852 [-0.1426, -0.0160] |
| security_incidents:severity | 0.2717 | 0.3277 | -0.0560 [-0.1064, +0.0140] |
| security_incidents:true_positive | 0.1896 | 0.2540 | -0.0644 [-0.1354, +0.0155] |
| security_incidents:urgency | 0.1489 | 0.1445 | +0.0043 [-0.0748, +0.0777] |
| overall | 0.1376 | 0.2141 | -0.0765 [-0.0917, -0.0601] |
