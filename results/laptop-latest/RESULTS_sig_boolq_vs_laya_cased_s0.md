# Paired significance: Verdict-MQ cls k=0 (stable) vs Laya

Matched items: 3270 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (2938 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=0 (stable) acc | Laya acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| boolq | 3270 | 79.2% | 76.0% | +3.2 [+1.4, +5.0] | 488 / 384 | 0.001 | 0.001 | 0.00048 |
| overall | 3270 | 79.2% | 76.0% | +3.2 [+1.3, +5.0] | 488 / 384 | 0.001 | nan | 0.00048 |

| task | ECE-10 Verdict-MQ cls k=0 (stable) | ECE-10 Laya | Δ ECE [95% CI] |
|---|---|---|---|
| boolq | 0.1927 | 0.0732 | +0.1195 [+0.1027, +0.1380] |
| overall | 0.1927 | 0.0732 | +0.1195 [+0.1028, +0.1384] |
