# Paired significance: Verdict-MQ-large (fixed marker) vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `idx` (400 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ-large (fixed marker) acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 73.0% | 70.0% | +3.0 [-3.0, +9.0] | 6 / 3 | 0.4 | 1 | 0.51 |
| agent_trace_observability:needs_review | 100 | 87.0% | 84.0% | +3.0 [-1.0, +8.0] | 4 / 1 | 0.25 | 1 | 0.38 |
| agent_trace_observability:outcome | 100 | 69.0% | 65.0% | +4.0 [-2.0, +10.0] | 7 / 3 | 0.26 | 1 | 0.34 |
| agent_trace_observability:risk | 100 | 81.0% | 82.0% | -1.0 [-7.0, +5.0] | 4 / 5 | 0.87 | 1 | 1 |
| agent_trace_observability:urgency | 100 | 67.0% | 65.0% | +2.0 [-4.0, +8.0] | 5 / 3 | 0.6 | 1 | 0.73 |
| customer_service:action | 100 | 72.0% | 58.0% | +14.0 [+6.0, +23.0] | 17 / 3 | 0.0018 | 0.034 | 0.0026 |
| customer_service:category | 100 | 96.0% | 94.0% | +2.0 [-3.0, +7.0] | 4 / 2 | 0.52 | 1 | 0.69 |
| customer_service:churn_risk | 100 | 87.0% | 80.0% | +7.0 [+0.0, +14.0] | 10 / 3 | 0.062 | 1 | 0.092 |
| customer_service:needs_human | 100 | 82.0% | 76.0% | +6.0 [-1.0, +14.0] | 10 / 4 | 0.13 | 1 | 0.18 |
| customer_service:urgency | 100 | 76.0% | 74.0% | +2.0 [-8.0, +12.0] | 13 / 11 | 0.75 | 1 | 0.84 |
| invoice_processing:discrepancy_severity | 100 | 85.0% | 85.0% | +0.0 [-5.0, +6.0] | 4 / 4 | 1 | 1 | 1 |
| invoice_processing:disposition | 100 | 77.0% | 79.0% | -2.0 [-8.0, +4.0] | 4 / 6 | 0.65 | 1 | 0.75 |
| invoice_processing:duplicate | 100 | 90.0% | 92.0% | -2.0 [-7.0, +3.0] | 2 / 4 | 0.54 | 1 | 0.69 |
| invoice_processing:matches_order | 100 | 96.0% | 94.0% | +2.0 [-2.0, +6.0] | 3 / 1 | 0.44 | 1 | 0.62 |
| invoice_processing:urgency | 100 | 82.0% | 52.0% | +30.0 [+20.0, +40.0] | 33 / 3 | 0.0002 | 0.004 | 2.3e-07 |
| security_incidents:credential_compromise | 100 | 78.0% | 81.0% | -3.0 [-11.0, +6.0] | 8 / 11 | 0.58 | 1 | 0.65 |
| security_incidents:disposition | 100 | 77.0% | 73.0% | +4.0 [-2.0, +10.0] | 7 / 3 | 0.26 | 1 | 0.34 |
| security_incidents:severity | 100 | 80.0% | 78.0% | +2.0 [-5.0, +9.0] | 7 / 5 | 0.66 | 1 | 0.77 |
| security_incidents:true_positive | 100 | 82.0% | 87.0% | -5.0 [-12.0, +2.0] | 4 / 9 | 0.19 | 1 | 0.27 |
| security_incidents:urgency | 100 | 70.0% | 65.0% | +5.0 [-4.0, +14.0] | 13 / 8 | 0.32 | 1 | 0.38 |
| overall | 2000 | 80.3% | 76.7% | +3.6 [+1.9, +5.4] | 165 / 92 | 0.0002 | nan | 6.2e-06 |

| task | ECE-10 Verdict-MQ-large (fixed marker) | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.2221 | 0.2861 | -0.0640 [-0.1323, -0.0032] |
| agent_trace_observability:needs_review | 0.1662 | 0.2163 | -0.0500 [-0.0877, +0.0166] |
| agent_trace_observability:outcome | 0.1483 | 0.2706 | -0.1223 [-0.1805, -0.0159] |
| agent_trace_observability:risk | 0.2257 | 0.2754 | -0.0498 [-0.0886, +0.0123] |
| agent_trace_observability:urgency | 0.1576 | 0.1784 | -0.0208 [-0.0703, +0.0531] |
| customer_service:action | 0.1622 | 0.1789 | -0.0167 [-0.0903, +0.0637] |
| customer_service:category | 0.1094 | 0.2708 | -0.1613 [-0.1972, -0.1246] |
| customer_service:churn_risk | 0.2375 | 0.2501 | -0.0126 [-0.0755, +0.0641] |
| customer_service:needs_human | 0.1279 | 0.1772 | -0.0493 [-0.1045, +0.0471] |
| customer_service:urgency | 0.1820 | 0.1866 | -0.0047 [-0.0829, +0.0796] |
| invoice_processing:discrepancy_severity | 0.1442 | 0.2179 | -0.0737 [-0.1237, +0.0081] |
| invoice_processing:disposition | 0.1842 | 0.2926 | -0.1085 [-0.1610, -0.0413] |
| invoice_processing:duplicate | 0.0484 | 0.1152 | -0.0668 [-0.1125, -0.0319] |
| invoice_processing:matches_order | 0.0877 | 0.1601 | -0.0724 [-0.1119, -0.0332] |
| invoice_processing:urgency | 0.2758 | 0.0427 | +0.2331 [+0.0999, +0.2852] |
| security_incidents:credential_compromise | 0.1276 | 0.2335 | -0.1060 [-0.1785, -0.0132] |
| security_incidents:disposition | 0.2240 | 0.2940 | -0.0701 [-0.1240, +0.0134] |
| security_incidents:severity | 0.2814 | 0.3277 | -0.0463 [-0.1119, +0.0239] |
| security_incidents:true_positive | 0.1550 | 0.2540 | -0.0990 [-0.1511, -0.0209] |
| security_incidents:urgency | 0.1658 | 0.1445 | +0.0213 [-0.0628, +0.1078] |
| overall | 0.1597 | 0.2141 | -0.0544 [-0.0705, -0.0353] |
