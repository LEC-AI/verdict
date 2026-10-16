# Paired significance: Verdict-MQ vs classifier

Matched items: 3079 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ acc | classifier acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| banking77 | 3079 | 92.0% | 91.8% | +0.2 [-0.7, +1.0] | 99 / 94 | 0.77 | 0.77 |
| overall | 3079 | 92.0% | 91.8% | +0.2 [-0.7, +1.0] | 99 / 94 | 0.77 | nan |

| task | ECE-10 Verdict-MQ | ECE-10 classifier | Δ ECE [95% CI] |
|---|---|---|---|
| banking77 | 0.0535 | 0.0171 | +0.0363 [+0.0250, +0.0441] |
| overall | 0.0535 | 0.0171 | +0.0363 [+0.0250, +0.0440] |
