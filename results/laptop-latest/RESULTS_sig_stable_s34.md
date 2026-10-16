# Paired significance: Verdict-MQ-large-stable-s34 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large-stable-s34 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 72.0% | 70.0% | +2.0 [-5.0, +9.0] | 7 / 5 | 0.77 | 1 |
| agent_trace_observability:needs_review | 100 | 81.0% | 84.0% | -3.0 [-8.0, +1.0] | 1 / 4 | 0.38 | 1 |
| agent_trace_observability:outcome | 100 | 74.0% | 65.0% | +9.0 [+3.0, +15.0] | 10 / 1 | 0.012 | 0.22 |
| agent_trace_observability:risk | 100 | 80.0% | 82.0% | -2.0 [-8.0, +3.0] | 3 / 5 | 0.73 | 1 |
| agent_trace_observability:urgency | 100 | 67.0% | 65.0% | +2.0 [-5.0, +9.0] | 7 / 5 | 0.77 | 1 |
| customer_service:action | 100 | 68.0% | 58.0% | +10.0 [+2.0, +19.0] | 15 / 5 | 0.041 | 0.75 |
| customer_service:category | 100 | 94.0% | 94.0% | +0.0 [-5.0, +5.0] | 3 / 3 | 1 | 1 |
| customer_service:churn_risk | 100 | 87.0% | 80.0% | +7.0 [+0.0, +14.0] | 10 / 3 | 0.092 | 1 |
| customer_service:needs_human | 100 | 83.0% | 76.0% | +7.0 [+0.0, +15.0] | 11 / 4 | 0.12 | 1 |
| customer_service:urgency | 100 | 81.0% | 74.0% | +7.0 [-2.0, +16.0] | 14 / 7 | 0.19 | 1 |
| invoice_processing:discrepancy_severity | 100 | 85.0% | 85.0% | +0.0 [-6.0, +6.0] | 5 / 5 | 1 | 1 |
| invoice_processing:disposition | 100 | 77.0% | 79.0% | -2.0 [-8.0, +3.0] | 3 / 5 | 0.73 | 1 |
| invoice_processing:duplicate | 100 | 90.0% | 92.0% | -2.0 [-7.0, +3.0] | 2 / 4 | 0.69 | 1 |
| invoice_processing:matches_order | 100 | 96.0% | 94.0% | +2.0 [-2.0, +6.0] | 3 / 1 | 0.62 | 1 |
| invoice_processing:urgency | 100 | 79.0% | 52.0% | +27.0 [+16.0, +38.0] | 32 / 5 | 7.4e-06 | 0.00015 |
| security_incidents:credential_compromise | 100 | 75.0% | 81.0% | -6.0 [-15.0, +3.0] | 8 / 14 | 0.29 | 1 |
| security_incidents:disposition | 100 | 69.0% | 73.0% | -4.0 [-10.0, +2.0] | 3 / 7 | 0.34 | 1 |
| security_incidents:severity | 100 | 79.0% | 78.0% | +1.0 [-5.0, +8.0] | 6 / 5 | 1 | 1 |
| security_incidents:true_positive | 100 | 86.0% | 87.0% | -1.0 [-8.0, +6.0] | 6 / 7 | 1 | 1 |
| security_incidents:urgency | 100 | 70.0% | 65.0% | +5.0 [-3.0, +14.0] | 12 / 7 | 0.36 | 1 |
| overall | 2000 | 79.7% | 76.7% | +2.9 [+1.4, +4.5] | 161 / 102 | 0.00033 | nan |

| task | ECE-10 Verdict-MQ-large-stable-s34 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.2074 | 0.2861 | -0.0787 [-0.1493, -0.0119] |
| agent_trace_observability:needs_review | 0.1913 | 0.2163 | -0.0249 [-0.1030, +0.0652] |
| agent_trace_observability:outcome | 0.1918 | 0.2706 | -0.0788 [-0.1368, +0.0021] |
| agent_trace_observability:risk | 0.2006 | 0.2754 | -0.0748 [-0.1168, -0.0116] |
| agent_trace_observability:urgency | 0.1653 | 0.1784 | -0.0131 [-0.0761, +0.0696] |
| customer_service:action | 0.1451 | 0.1789 | -0.0338 [-0.1138, +0.0776] |
| customer_service:category | 0.0943 | 0.2708 | -0.1765 [-0.2116, -0.1382] |
| customer_service:churn_risk | 0.2472 | 0.2501 | -0.0029 [-0.0720, +0.0745] |
| customer_service:needs_human | 0.1273 | 0.1772 | -0.0499 [-0.1135, +0.0373] |
| customer_service:urgency | 0.2149 | 0.1866 | +0.0283 [-0.0607, +0.1014] |
| invoice_processing:discrepancy_severity | 0.1620 | 0.2179 | -0.0558 [-0.1199, +0.0208] |
| invoice_processing:disposition | 0.1479 | 0.2926 | -0.1448 [-0.1878, -0.0571] |
| invoice_processing:duplicate | 0.0549 | 0.1152 | -0.0603 [-0.1044, -0.0228] |
| invoice_processing:matches_order | 0.0957 | 0.1601 | -0.0644 [-0.1039, -0.0159] |
| invoice_processing:urgency | 0.2098 | 0.0427 | +0.1671 [+0.0532, +0.2327] |
| security_incidents:credential_compromise | 0.1081 | 0.2335 | -0.1254 [-0.1801, -0.0190] |
| security_incidents:disposition | 0.1932 | 0.2940 | -0.1008 [-0.1671, -0.0066] |
| security_incidents:severity | 0.2852 | 0.3277 | -0.0425 [-0.0967, +0.0269] |
| security_incidents:true_positive | 0.1708 | 0.2540 | -0.0832 [-0.1383, -0.0105] |
| security_incidents:urgency | 0.1671 | 0.1445 | +0.0226 [-0.0576, +0.0981] |
| overall | 0.1547 | 0.2141 | -0.0594 [-0.0756, -0.0435] |
