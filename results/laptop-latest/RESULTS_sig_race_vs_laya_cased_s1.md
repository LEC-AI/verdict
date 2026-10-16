# Paired significance: Verdict-MQ cls k=22 vs Laya

Matched items: 4934 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (1407 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=22 acc | Laya acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| race | 4934 | 77.1% | 45.5% | +31.6 [+29.9, +33.2] | 1906 / 349 | 0.0002 | 0.0002 | 8.3e-259 |
| overall | 4934 | 77.1% | 45.5% | +31.6 [+29.9, +33.2] | 1906 / 349 | 0.0002 | nan | 8.3e-259 |

| task | ECE-10 Verdict-MQ cls k=22 | ECE-10 Laya | Δ ECE [95% CI] |
|---|---|---|---|
| race | 0.1158 | 0.0137 | +0.1021 [+0.0824, +0.1127] |
| overall | 0.1158 | 0.0137 | +0.1021 [+0.0826, +0.1128] |
