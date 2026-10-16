# Paired significance: Verdict-MQ cls k=0 vs Laya

Matched items: 4934 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (1407 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=0 acc | Laya acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| race | 4934 | 76.1% | 45.5% | +30.6 [+29.0, +32.3] | 1889 / 378 | 0.0002 | 0.0002 | 1.1e-240 |
| overall | 4934 | 76.1% | 45.5% | +30.6 [+29.0, +32.3] | 1889 / 378 | 0.0002 | nan | 1.1e-240 |

| task | ECE-10 Verdict-MQ cls k=0 | ECE-10 Laya | Δ ECE [95% CI] |
|---|---|---|---|
| race | 0.1092 | 0.0137 | +0.0955 [+0.0754, +0.1056] |
| overall | 0.1092 | 0.0137 | +0.0955 [+0.0750, +0.1054] |
