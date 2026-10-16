# Paired significance: Verdict-MQ vs Laya

Matched items: 3270 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict-MQ acc | Laya acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| boolq | 3270 | 79.2% | 76.0% | +3.2 [+1.4, +4.9] | 488 / 384 | 0.00048 | 0.00048 |
| overall | 3270 | 79.2% | 76.0% | +3.2 [+1.4, +5.0] | 488 / 384 | 0.00048 | nan |

| task | ECE-10 Verdict-MQ | ECE-10 Laya | Δ ECE [95% CI] |
|---|---|---|---|
| boolq | 0.1927 | 0.0732 | +0.1195 [+0.1031, +0.1380] |
| overall | 0.1927 | 0.0732 | +0.1195 [+0.1033, +0.1377] |
