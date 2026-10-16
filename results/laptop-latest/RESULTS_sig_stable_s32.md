# Paired significance: Verdict-MQ-large-stable-s32 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large-stable-s32 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 70.0% | 70.0% | +0.0 [-6.0, +6.0] | 5 / 5 | 1 | 1 |
| agent_trace_observability:needs_review | 100 | 86.0% | 84.0% | +2.0 [-2.0, +6.0] | 3 / 1 | 0.62 | 1 |
| agent_trace_observability:outcome | 100 | 67.0% | 65.0% | +2.0 [+0.0, +5.0] | 2 / 0 | 0.5 | 1 |
| agent_trace_observability:risk | 100 | 82.0% | 82.0% | +0.0 [-5.0, +6.0] | 4 / 4 | 1 | 1 |
| agent_trace_observability:urgency | 100 | 64.0% | 65.0% | -1.0 [-8.0, +6.0] | 6 / 7 | 1 | 1 |
| customer_service:action | 100 | 65.0% | 58.0% | +7.0 [-2.0, +16.0] | 15 / 8 | 0.21 | 1 |
| customer_service:category | 100 | 94.0% | 94.0% | +0.0 [-5.0, +5.0] | 3 / 3 | 1 | 1 |
| customer_service:churn_risk | 100 | 84.0% | 80.0% | +4.0 [-3.0, +11.0] | 8 / 4 | 0.39 | 1 |
| customer_service:needs_human | 100 | 82.0% | 76.0% | +6.0 [-2.0, +14.0] | 11 / 5 | 0.21 | 1 |
| customer_service:urgency | 100 | 78.0% | 74.0% | +4.0 [-5.0, +13.0] | 13 / 9 | 0.52 | 1 |
| invoice_processing:discrepancy_severity | 100 | 85.0% | 85.0% | +0.0 [-5.0, +6.0] | 4 / 4 | 1 | 1 |
| invoice_processing:disposition | 100 | 75.0% | 79.0% | -4.0 [-10.0, +2.0] | 3 / 7 | 0.34 | 1 |
| invoice_processing:duplicate | 100 | 92.0% | 92.0% | +0.0 [-5.0, +5.0] | 3 / 3 | 1 | 1 |
| invoice_processing:matches_order | 100 | 96.0% | 94.0% | +2.0 [-2.0, +6.0] | 3 / 1 | 0.62 | 1 |
| invoice_processing:urgency | 100 | 80.0% | 52.0% | +28.0 [+18.0, +38.0] | 31 / 3 | 7.7e-07 | 1.5e-05 |
| security_incidents:credential_compromise | 100 | 79.0% | 81.0% | -2.0 [-11.0, +7.0] | 9 / 11 | 0.82 | 1 |
| security_incidents:disposition | 100 | 79.0% | 73.0% | +6.0 [-1.0, +13.0] | 9 / 3 | 0.15 | 1 |
| security_incidents:severity | 100 | 76.0% | 78.0% | -2.0 [-10.0, +6.0] | 7 / 9 | 0.8 | 1 |
| security_incidents:true_positive | 100 | 84.0% | 87.0% | -3.0 [-10.0, +4.0] | 5 / 8 | 0.58 | 1 |
| security_incidents:urgency | 100 | 71.0% | 65.0% | +6.0 [-3.0, +15.0] | 14 / 8 | 0.29 | 1 |
| overall | 2000 | 79.5% | 76.7% | +2.7 [+1.2, +4.4] | 158 / 103 | 0.0008 | nan |

| task | ECE-10 Verdict-MQ-large-stable-s32 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.1937 | 0.2861 | -0.0924 [-0.1557, -0.0257] |
| agent_trace_observability:needs_review | 0.1464 | 0.2163 | -0.0699 [-0.0976, +0.0203] |
| agent_trace_observability:outcome | 0.1741 | 0.2706 | -0.0965 [-0.1575, +0.0011] |
| agent_trace_observability:risk | 0.2237 | 0.2754 | -0.0518 [-0.1010, +0.0080] |
| agent_trace_observability:urgency | 0.1214 | 0.1784 | -0.0570 [-0.1134, +0.0358] |
| customer_service:action | 0.1128 | 0.1789 | -0.0661 [-0.1474, +0.0434] |
| customer_service:category | 0.0958 | 0.2708 | -0.1750 [-0.2180, -0.1338] |
| customer_service:churn_risk | 0.2212 | 0.2501 | -0.0289 [-0.0993, +0.0450] |
| customer_service:needs_human | 0.1320 | 0.1772 | -0.0452 [-0.1058, +0.0465] |
| customer_service:urgency | 0.1865 | 0.1866 | -0.0001 [-0.0916, +0.0778] |
| invoice_processing:discrepancy_severity | 0.1376 | 0.2179 | -0.0803 [-0.1242, -0.0010] |
| invoice_processing:disposition | 0.1188 | 0.2926 | -0.1739 [-0.2203, -0.0874] |
| invoice_processing:duplicate | 0.0578 | 0.1152 | -0.0574 [-0.1114, -0.0224] |
| invoice_processing:matches_order | 0.0727 | 0.1601 | -0.0873 [-0.1142, -0.0467] |
| invoice_processing:urgency | 0.2371 | 0.0427 | +0.1944 [+0.0582, +0.2547] |
| security_incidents:credential_compromise | 0.1365 | 0.2335 | -0.0971 [-0.1794, -0.0068] |
| security_incidents:disposition | 0.2267 | 0.2940 | -0.0673 [-0.1218, +0.0090] |
| security_incidents:severity | 0.2412 | 0.3277 | -0.0865 [-0.1593, -0.0011] |
| security_incidents:true_positive | 0.1421 | 0.2540 | -0.1119 [-0.1646, -0.0391] |
| security_incidents:urgency | 0.1792 | 0.1445 | +0.0347 [-0.0516, +0.1173] |
| overall | 0.1499 | 0.2141 | -0.0642 [-0.0801, -0.0478] |
