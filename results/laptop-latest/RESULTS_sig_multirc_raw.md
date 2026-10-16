# Paired significance: Verdict-MQ vs pair-classifier

Matched items: 4847 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ acc | pair-classifier acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| multirc | 4847 | 70.1% | 65.6% | +4.6 [+3.2, +6.0] | 700 / 479 | 1.3e-10 | 1.3e-10 |
| overall | 4847 | 70.1% | 65.6% | +4.6 [+3.2, +6.0] | 700 / 479 | 1.3e-10 | nan |

| task | ECE-10 Verdict-MQ | ECE-10 pair-classifier | Δ ECE [95% CI] |
|---|---|---|---|
| multirc | 0.0720 | 0.1516 | -0.0796 [-0.0926, -0.0649] |
| overall | 0.0720 | 0.1516 | -0.0796 [-0.0922, -0.0650] |
