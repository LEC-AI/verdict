# Paired significance: Verdict-MQ cls k=22 vs Laya

Matched items: 4934 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (1407 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=22 acc | Laya acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| race | 4934 | 77.8% | 45.5% | +32.3 [+30.7, +33.9] | 1937 / 343 | 0.0002 | 0.0002 | 5.3e-269 |
| overall | 4934 | 77.8% | 45.5% | +32.3 [+30.7, +33.9] | 1937 / 343 | 0.0002 | nan | 5.3e-269 |

| task | ECE-10 Verdict-MQ cls k=22 | ECE-10 Laya | Δ ECE [95% CI] |
|---|---|---|---|
| race | 0.1087 | 0.0137 | +0.0950 [+0.0755, +0.1046] |
| overall | 0.1087 | 0.0137 | +0.0950 [+0.0754, +0.1049] |
