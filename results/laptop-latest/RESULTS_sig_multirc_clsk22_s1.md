# Paired significance: Verdict-MQ cls k=22 vs pair classifier

Matched items: 4847 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ cls k=22 acc | pair classifier acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| multirc | 4847 | 81.1% | 75.9% | +5.2 [+4.0, +6.4] | 547 / 296 | 4.1e-18 | 4.1e-18 |
| overall | 4847 | 81.1% | 75.9% | +5.2 [+4.1, +6.3] | 547 / 296 | 4.1e-18 | nan |

| task | ECE-10 Verdict-MQ cls k=22 | ECE-10 pair classifier | Δ ECE [95% CI] |
|---|---|---|---|
| multirc | 0.0866 | 0.0609 | +0.0257 [+0.0144, +0.0372] |
| overall | 0.0866 | 0.0609 | +0.0257 [+0.0145, +0.0372] |
