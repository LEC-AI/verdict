# Paired significance: Verdict-MQ vs classifier

Matched items: 5500 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ acc | classifier acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| clinc | 5500 | 90.1% | 89.4% | +0.7 [-0.0, +1.4] | 219 / 182 | 0.072 | 0.072 |
| overall | 5500 | 90.1% | 89.4% | +0.7 [-0.0, +1.4] | 219 / 182 | 0.072 | nan |

| task | ECE-10 Verdict-MQ | ECE-10 classifier | Δ ECE [95% CI] |
|---|---|---|---|
| clinc | 0.0823 | 0.0152 | +0.0671 [+0.0571, +0.0730] |
| overall | 0.0823 | 0.0152 | +0.0671 [+0.0568, +0.0728] |
