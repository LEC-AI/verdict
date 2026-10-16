# Paired significance: Verdict-MQ cls k=22 vs pair classifier

Matched items: 4847 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ cls k=22 acc | pair classifier acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| multirc | 4847 | 80.1% | 66.4% | +13.7 [+12.3, +15.2] | 1038 / 372 | 5.8e-73 | 5.8e-73 |
| overall | 4847 | 80.1% | 66.4% | +13.7 [+12.3, +15.2] | 1038 / 372 | 5.8e-73 | nan |

| task | ECE-10 Verdict-MQ cls k=22 | ECE-10 pair classifier | Δ ECE [95% CI] |
|---|---|---|---|
| multirc | 0.0846 | 0.0672 | +0.0173 [+0.0025, +0.0303] |
| overall | 0.0846 | 0.0672 | +0.0173 [+0.0028, +0.0305] |
