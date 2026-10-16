# Paired significance: Verdict-MQ cls k=22 vs pair classifier

Matched items: 4847 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ cls k=22 acc | pair classifier acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| multirc | 4847 | 80.5% | 72.6% | +7.9 [+6.7, +9.2] | 707 / 322 | 8.7e-34 | 8.7e-34 |
| overall | 4847 | 80.5% | 72.6% | +7.9 [+6.7, +9.2] | 707 / 322 | 8.7e-34 | nan |

| task | ECE-10 Verdict-MQ cls k=22 | ECE-10 pair classifier | Δ ECE [95% CI] |
|---|---|---|---|
| multirc | 0.0777 | 0.0549 | +0.0228 [+0.0099, +0.0344] |
| overall | 0.0777 | 0.0549 | +0.0228 [+0.0102, +0.0347] |
