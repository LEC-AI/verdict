# Paired significance: Verdict-MQ cls k=0 (stable) vs Laya

Matched items: 3270 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (2938 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=0 (stable) acc | Laya acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| boolq | 3270 | 79.4% | 76.0% | +3.4 [+1.6, +5.2] | 478 / 367 | 0.0002 | 0.0002 | 0.00015 |
| overall | 3270 | 79.4% | 76.0% | +3.4 [+1.6, +5.1] | 478 / 367 | 0.0004 | nan | 0.00015 |

| task | ECE-10 Verdict-MQ cls k=0 (stable) | ECE-10 Laya | Δ ECE [95% CI] |
|---|---|---|---|
| boolq | 0.1911 | 0.0732 | +0.1179 [+0.1008, +0.1362] |
| overall | 0.1911 | 0.0732 | +0.1179 [+0.1014, +0.1358] |
