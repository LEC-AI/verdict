# Paired significance: Verdict-MQ cls k=0 vs Laya

Matched items: 4934 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (1407 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=0 acc | Laya acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| race | 4934 | 76.3% | 45.5% | +30.8 [+29.1, +32.5] | 1893 / 372 | 0.0002 | 0.0002 | 1.8e-244 |
| overall | 4934 | 76.3% | 45.5% | +30.8 [+29.1, +32.5] | 1893 / 372 | 0.0002 | nan | 1.8e-244 |

| task | ECE-10 Verdict-MQ cls k=0 | ECE-10 Laya | Δ ECE [95% CI] |
|---|---|---|---|
| race | 0.1062 | 0.0137 | +0.0925 [+0.0733, +0.1029] |
| overall | 0.1062 | 0.0137 | +0.0925 [+0.0729, +0.1030] |
