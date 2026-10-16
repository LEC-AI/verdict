# Paired significance: Verdict-MQ vs pair-classifier

Matched items: 3270 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ acc | pair-classifier acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| boolq | 3270 | 64.6% | 79.7% | -15.2 [-17.0, -13.3] | 277 / 773 | 9.5e-55 | 9.5e-55 |
| overall | 3270 | 64.6% | 79.7% | -15.2 [-17.0, -13.3] | 277 / 773 | 9.5e-55 | nan |

| task | ECE-10 Verdict-MQ | ECE-10 pair-classifier | Δ ECE [95% CI] |
|---|---|---|---|
| boolq | 0.0948 | 0.1216 | -0.0268 [-0.0453, -0.0085] |
| overall | 0.0948 | 0.1216 | -0.0268 [-0.0450, -0.0091] |
