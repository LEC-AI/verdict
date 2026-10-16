# Paired significance: Verdict-MQ cls k=22 vs Laya

Matched items: 4934 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (1407 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=22 acc | Laya acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| race | 4934 | 77.4% | 45.5% | +31.9 [+30.3, +33.6] | 1903 / 328 | 0.0002 | 0.0002 | 4.9e-269 |
| overall | 4934 | 77.4% | 45.5% | +31.9 [+30.3, +33.5] | 1903 / 328 | 0.0002 | nan | 4.9e-269 |

| task | ECE-10 Verdict-MQ cls k=22 | ECE-10 Laya | Δ ECE [95% CI] |
|---|---|---|---|
| race | 0.1099 | 0.0137 | +0.0962 [+0.0760, +0.1064] |
| overall | 0.1099 | 0.0137 | +0.0962 [+0.0763, +0.1065] |
