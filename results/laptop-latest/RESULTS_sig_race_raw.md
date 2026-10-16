# Paired significance: Verdict-MQ vs MC-head

Matched items: 4934 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ acc | MC-head acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| race | 4934 | 76.4% | 57.9% | +18.5 [+17.0, +20.0] | 1262 / 350 | 7.5e-121 | 7.5e-121 |
| overall | 4934 | 76.4% | 57.9% | +18.5 [+16.9, +20.0] | 1262 / 350 | 7.5e-121 | nan |

| task | ECE-10 Verdict-MQ | ECE-10 MC-head | Δ ECE [95% CI] |
|---|---|---|---|
| race | 0.0660 | 0.1447 | -0.0787 [-0.0936, -0.0638] |
| overall | 0.0660 | 0.1447 | -0.0787 [-0.0935, -0.0640] |
