# Paired significance: Verdict-MQ-large cls k=22 vs Laya-td

Matched items: 2000 across 20 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ-large cls k=22 acc | Laya-td acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| agent_trace_observability:action | 100 | 71.0% | 70.0% | +1.0 [-5.0, +7.0] | 5 / 4 | 1 | 1 |
| agent_trace_observability:needs_review | 100 | 87.0% | 84.0% | +3.0 [-1.0, +8.0] | 4 / 1 | 0.38 | 1 |
| agent_trace_observability:outcome | 100 | 69.0% | 65.0% | +4.0 [+1.0, +8.0] | 4 / 0 | 0.12 | 1 |
| agent_trace_observability:risk | 100 | 82.0% | 82.0% | +0.0 [-5.0, +5.0] | 3 / 3 | 1 | 1 |
| agent_trace_observability:urgency | 100 | 64.0% | 65.0% | -1.0 [-6.0, +4.0] | 3 / 4 | 1 | 1 |
| customer_service:action | 100 | 70.0% | 58.0% | +12.0 [+4.0, +20.0] | 15 / 3 | 0.0075 | 0.14 |
| customer_service:category | 100 | 95.0% | 94.0% | +1.0 [-3.0, +5.0] | 3 / 2 | 1 | 1 |
| customer_service:churn_risk | 100 | 90.0% | 80.0% | +10.0 [+4.0, +17.0] | 11 / 1 | 0.0063 | 0.12 |
| customer_service:needs_human | 100 | 86.0% | 76.0% | +10.0 [+3.0, +18.0] | 12 / 2 | 0.013 | 0.22 |
| customer_service:urgency | 100 | 80.0% | 74.0% | +6.0 [-2.0, +14.0] | 12 / 6 | 0.24 | 1 |
| invoice_processing:discrepancy_severity | 100 | 82.0% | 85.0% | -3.0 [-11.0, +4.0] | 6 / 9 | 0.61 | 1 |
| invoice_processing:disposition | 100 | 76.0% | 79.0% | -3.0 [-10.0, +3.0] | 4 / 7 | 0.55 | 1 |
| invoice_processing:duplicate | 100 | 89.0% | 92.0% | -3.0 [-8.0, +1.0] | 1 / 4 | 0.38 | 1 |
| invoice_processing:matches_order | 100 | 96.0% | 94.0% | +2.0 [-2.0, +6.0] | 3 / 1 | 0.62 | 1 |
| invoice_processing:urgency | 100 | 82.0% | 52.0% | +30.0 [+20.0, +41.0] | 33 / 3 | 2.3e-07 | 4.5e-06 |
| security_incidents:credential_compromise | 100 | 78.0% | 81.0% | -3.0 [-12.0, +6.0] | 9 / 12 | 0.66 | 1 |
| security_incidents:disposition | 100 | 78.0% | 73.0% | +5.0 [-2.0, +12.0] | 9 / 4 | 0.27 | 1 |
| security_incidents:severity | 100 | 77.0% | 78.0% | -1.0 [-10.0, +8.0] | 10 / 11 | 1 | 1 |
| security_incidents:true_positive | 100 | 86.0% | 87.0% | -1.0 [-8.0, +5.0] | 5 / 6 | 1 | 1 |
| security_incidents:urgency | 100 | 70.0% | 65.0% | +5.0 [-2.0, +13.0] | 10 / 5 | 0.3 | 1 |
| overall | 2000 | 80.4% | 76.7% | +3.7 [+2.2, +5.2] | 162 / 88 | 3.3e-06 | nan |

| task | ECE-10 Verdict-MQ-large cls k=22 | ECE-10 Laya-td | Δ ECE [95% CI] |
|---|---|---|---|
| agent_trace_observability:action | 0.2076 | 0.2861 | -0.0785 [-0.1405, -0.0176] |
| agent_trace_observability:needs_review | 0.1575 | 0.2163 | -0.0588 [-0.0971, +0.0032] |
| agent_trace_observability:outcome | 0.1470 | 0.2706 | -0.1236 [-0.1739, -0.0059] |
| agent_trace_observability:risk | 0.2276 | 0.2754 | -0.0478 [-0.0908, +0.0058] |
| agent_trace_observability:urgency | 0.1222 | 0.1784 | -0.0562 [-0.0990, +0.0197] |
| customer_service:action | 0.1440 | 0.1789 | -0.0349 [-0.0943, +0.0767] |
| customer_service:category | 0.1190 | 0.2708 | -0.1518 [-0.1986, -0.1177] |
| customer_service:churn_risk | 0.2766 | 0.2501 | +0.0265 [-0.0404, +0.0995] |
| customer_service:needs_human | 0.1816 | 0.1772 | +0.0043 [-0.0634, +0.0847] |
| customer_service:urgency | 0.1885 | 0.1866 | +0.0019 [-0.0761, +0.0723] |
| invoice_processing:discrepancy_severity | 0.1198 | 0.2179 | -0.0981 [-0.1575, -0.0146] |
| invoice_processing:disposition | 0.1505 | 0.2926 | -0.1422 [-0.1833, -0.0548] |
| invoice_processing:duplicate | 0.0623 | 0.1152 | -0.0529 [-0.1089, -0.0226] |
| invoice_processing:matches_order | 0.0853 | 0.1601 | -0.0748 [-0.1116, -0.0254] |
| invoice_processing:urgency | 0.2543 | 0.0427 | +0.2116 [+0.0762, +0.2697] |
| security_incidents:credential_compromise | 0.1378 | 0.2335 | -0.0958 [-0.1646, -0.0007] |
| security_incidents:disposition | 0.2244 | 0.2940 | -0.0697 [-0.1232, +0.0027] |
| security_incidents:severity | 0.2629 | 0.3277 | -0.0648 [-0.1356, +0.0204] |
| security_incidents:true_positive | 0.1722 | 0.2540 | -0.0818 [-0.1374, -0.0141] |
| security_incidents:urgency | 0.1635 | 0.1445 | +0.0190 [-0.0651, +0.0860] |
| overall | 0.1625 | 0.2141 | -0.0516 [-0.0664, -0.0350] |
