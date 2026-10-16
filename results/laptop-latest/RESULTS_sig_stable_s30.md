# Paired significance: Verdict-MQ-large-stable-s30 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large-stable-s30 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 71.0% | 70.0% | +1.0 [-5.0, +7.0] | 5 / 4 | 1 | 1 |
| agent_trace_observability:needs_review | 100 | 85.0% | 84.0% | +1.0 [-3.0, +6.0] | 3 / 2 | 1 | 1 |
| agent_trace_observability:outcome | 100 | 65.0% | 65.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1 | 1 |
| agent_trace_observability:risk | 100 | 85.0% | 82.0% | +3.0 [-2.0, +8.0] | 5 / 2 | 0.45 | 1 |
| agent_trace_observability:urgency | 100 | 65.0% | 65.0% | +0.0 [-6.0, +6.0] | 4 / 4 | 1 | 1 |
| customer_service:action | 100 | 66.0% | 58.0% | +8.0 [+0.0, +17.0] | 14 / 6 | 0.12 | 1 |
| customer_service:category | 100 | 94.0% | 94.0% | +0.0 [-5.0, +5.0] | 4 / 4 | 1 | 1 |
| customer_service:churn_risk | 100 | 84.0% | 80.0% | +4.0 [-3.0, +11.0] | 9 / 5 | 0.42 | 1 |
| customer_service:needs_human | 100 | 78.0% | 76.0% | +2.0 [-6.0, +11.0] | 10 / 8 | 0.81 | 1 |
| customer_service:urgency | 100 | 71.0% | 74.0% | -3.0 [-14.0, +8.0] | 15 / 18 | 0.73 | 1 |
| invoice_processing:discrepancy_severity | 100 | 79.0% | 85.0% | -6.0 [-14.0, +1.0] | 5 / 11 | 0.21 | 1 |
| invoice_processing:disposition | 100 | 79.0% | 79.0% | +0.0 [-7.0, +7.0] | 6 / 6 | 1 | 1 |
| invoice_processing:duplicate | 100 | 90.0% | 92.0% | -2.0 [-7.0, +3.0] | 2 / 4 | 0.69 | 1 |
| invoice_processing:matches_order | 100 | 95.0% | 94.0% | +1.0 [-2.0, +4.0] | 2 / 1 | 1 | 1 |
| invoice_processing:urgency | 100 | 79.0% | 52.0% | +27.0 [+17.0, +37.0] | 30 / 3 | 1.4e-06 | 2.8e-05 |
| security_incidents:credential_compromise | 100 | 76.0% | 81.0% | -5.0 [-14.0, +4.0] | 8 / 13 | 0.38 | 1 |
| security_incidents:disposition | 100 | 76.0% | 73.0% | +3.0 [-3.0, +9.0] | 6 / 3 | 0.51 | 1 |
| security_incidents:severity | 100 | 78.0% | 78.0% | +0.0 [-7.0, +7.0] | 6 / 6 | 1 | 1 |
| security_incidents:true_positive | 100 | 83.0% | 87.0% | -4.0 [-11.0, +3.0] | 4 / 8 | 0.39 | 1 |
| security_incidents:urgency | 100 | 65.0% | 65.0% | +0.0 [-10.0, +10.0] | 13 / 13 | 1 | 1 |
| overall | 2000 | 78.2% | 76.7% | +1.5 [-0.1, +3.2] | 151 / 121 | 0.078 | nan |

| task | ECE-10 Verdict-MQ-large-stable-s30 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.2108 | 0.2861 | -0.0753 [-0.1431, -0.0139] |
| agent_trace_observability:needs_review | 0.1470 | 0.2163 | -0.0693 [-0.1010, +0.0214] |
| agent_trace_observability:outcome | 0.1924 | 0.2706 | -0.0782 [-0.1671, +0.0240] |
| agent_trace_observability:risk | 0.2582 | 0.2754 | -0.0172 [-0.0651, +0.0397] |
| agent_trace_observability:urgency | 0.1440 | 0.1784 | -0.0345 [-0.0859, +0.0343] |
| customer_service:action | 0.1043 | 0.1789 | -0.0746 [-0.1373, +0.0311] |
| customer_service:category | 0.0797 | 0.2708 | -0.1911 [-0.2256, -0.1311] |
| customer_service:churn_risk | 0.2184 | 0.2501 | -0.0317 [-0.0989, +0.0476] |
| customer_service:needs_human | 0.0969 | 0.1772 | -0.0803 [-0.1334, +0.0196] |
| customer_service:urgency | 0.1539 | 0.1866 | -0.0328 [-0.1154, +0.0660] |
| invoice_processing:discrepancy_severity | 0.1520 | 0.2179 | -0.0658 [-0.1326, +0.0142] |
| invoice_processing:disposition | 0.1725 | 0.2926 | -0.1202 [-0.1705, -0.0422] |
| invoice_processing:duplicate | 0.0519 | 0.1152 | -0.0633 [-0.1088, -0.0257] |
| invoice_processing:matches_order | 0.0788 | 0.1601 | -0.0813 [-0.1167, -0.0337] |
| invoice_processing:urgency | 0.2239 | 0.0427 | +0.1812 [+0.0417, +0.2389] |
| security_incidents:credential_compromise | 0.1370 | 0.2335 | -0.0965 [-0.1580, +0.0119] |
| security_incidents:disposition | 0.1860 | 0.2940 | -0.1080 [-0.1533, -0.0361] |
| security_incidents:severity | 0.2698 | 0.3277 | -0.0579 [-0.1238, +0.0119] |
| security_incidents:true_positive | 0.1365 | 0.2540 | -0.1175 [-0.1583, -0.0433] |
| security_incidents:urgency | 0.1203 | 0.1445 | -0.0242 [-0.1014, +0.0646] |
| overall | 0.1418 | 0.2141 | -0.0723 [-0.0874, -0.0550] |
