# Paired significance: Verdict-MQ-large cls k=0 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large cls k=0 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 74.0% | 70.0% | +4.0 [+1.0, +8.0] | 4 / 0 | 0.12 | 1 |
| agent_trace_observability:needs_review | 100 | 85.0% | 84.0% | +1.0 [-4.0, +6.0] | 4 / 3 | 1 | 1 |
| agent_trace_observability:outcome | 100 | 69.0% | 65.0% | +4.0 [-1.0, +9.0] | 5 / 1 | 0.22 | 1 |
| agent_trace_observability:risk | 100 | 79.0% | 82.0% | -3.0 [-8.0, +2.0] | 2 / 5 | 0.45 | 1 |
| agent_trace_observability:urgency | 100 | 67.0% | 65.0% | +2.0 [-3.0, +7.0] | 4 / 2 | 0.69 | 1 |
| customer_service:action | 100 | 70.0% | 58.0% | +12.0 [+4.0, +21.0] | 16 / 4 | 0.012 | 0.22 |
| customer_service:category | 100 | 96.0% | 94.0% | +2.0 [-3.0, +7.0] | 4 / 2 | 0.69 | 1 |
| customer_service:churn_risk | 100 | 87.0% | 80.0% | +7.0 [+0.0, +14.0] | 10 / 3 | 0.092 | 1 |
| customer_service:needs_human | 100 | 82.0% | 76.0% | +6.0 [-2.0, +15.0] | 13 / 7 | 0.26 | 1 |
| customer_service:urgency | 100 | 78.0% | 74.0% | +4.0 [-6.0, +14.0] | 14 / 10 | 0.54 | 1 |
| invoice_processing:discrepancy_severity | 100 | 82.0% | 85.0% | -3.0 [-9.0, +3.0] | 3 / 6 | 0.51 | 1 |
| invoice_processing:disposition | 100 | 77.0% | 79.0% | -2.0 [-7.0, +3.0] | 2 / 4 | 0.69 | 1 |
| invoice_processing:duplicate | 100 | 91.0% | 92.0% | -1.0 [-6.0, +4.0] | 3 / 4 | 1 | 1 |
| invoice_processing:matches_order | 100 | 96.0% | 94.0% | +2.0 [+0.0, +5.0] | 2 / 0 | 0.5 | 1 |
| invoice_processing:urgency | 100 | 77.0% | 52.0% | +25.0 [+15.0, +35.0] | 28 / 3 | 4.6e-06 | 9.3e-05 |
| security_incidents:credential_compromise | 100 | 76.0% | 81.0% | -5.0 [-15.0, +5.0] | 10 / 15 | 0.42 | 1 |
| security_incidents:disposition | 100 | 80.0% | 73.0% | +7.0 [+1.0, +13.0] | 9 / 2 | 0.065 | 1 |
| security_incidents:severity | 100 | 79.0% | 78.0% | +1.0 [-5.0, +7.0] | 6 / 5 | 1 | 1 |
| security_incidents:true_positive | 100 | 84.0% | 87.0% | -3.0 [-10.0, +4.0] | 5 / 8 | 0.58 | 1 |
| security_incidents:urgency | 100 | 70.0% | 65.0% | +5.0 [-3.0, +14.0] | 12 / 7 | 0.36 | 1 |
| overall | 2000 | 80.0% | 76.7% | +3.2 [+1.7, +4.8] | 156 / 91 | 4.2e-05 | nan |

| task | ECE-10 Verdict-MQ-large cls k=0 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.2345 | 0.2861 | -0.0516 [-0.1016, -0.0068] |
| agent_trace_observability:needs_review | 0.1713 | 0.2163 | -0.0450 [-0.0992, +0.0412] |
| agent_trace_observability:outcome | 0.1767 | 0.2706 | -0.0938 [-0.1641, +0.0073] |
| agent_trace_observability:risk | 0.1978 | 0.2754 | -0.0776 [-0.1262, -0.0229] |
| agent_trace_observability:urgency | 0.1585 | 0.1784 | -0.0199 [-0.0640, +0.0374] |
| customer_service:action | 0.1478 | 0.1789 | -0.0311 [-0.0982, +0.0595] |
| customer_service:category | 0.1117 | 0.2708 | -0.1590 [-0.1984, -0.1278] |
| customer_service:churn_risk | 0.2429 | 0.2501 | -0.0072 [-0.0711, +0.0682] |
| customer_service:needs_human | 0.1282 | 0.1772 | -0.0491 [-0.1173, +0.0463] |
| customer_service:urgency | 0.1729 | 0.1866 | -0.0137 [-0.1078, +0.0653] |
| invoice_processing:discrepancy_severity | 0.1305 | 0.2179 | -0.0873 [-0.1512, -0.0233] |
| invoice_processing:disposition | 0.1632 | 0.2926 | -0.1295 [-0.1868, -0.0525] |
| invoice_processing:duplicate | 0.0421 | 0.1152 | -0.0731 [-0.1136, -0.0359] |
| invoice_processing:matches_order | 0.0796 | 0.1601 | -0.0805 [-0.1061, -0.0302] |
| invoice_processing:urgency | 0.1938 | 0.0427 | +0.1511 [+0.0300, +0.2142] |
| security_incidents:credential_compromise | 0.1166 | 0.2335 | -0.1169 [-0.1857, -0.0151] |
| security_incidents:disposition | 0.2224 | 0.2940 | -0.0716 [-0.1201, +0.0080] |
| security_incidents:severity | 0.2737 | 0.3277 | -0.0540 [-0.1088, +0.0114] |
| security_incidents:true_positive | 0.1382 | 0.2540 | -0.1158 [-0.1550, -0.0457] |
| security_incidents:urgency | 0.1764 | 0.1445 | +0.0319 [-0.0524, +0.1090] |
| overall | 0.1537 | 0.2141 | -0.0604 [-0.0754, -0.0448] |
