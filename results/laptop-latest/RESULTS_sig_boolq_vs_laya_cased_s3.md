# Paired significance: Verdict-MQ cls k=0 (stable) vs Laya

Matched items: 3270 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (2938 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=0 (stable) acc | Laya acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| boolq | 3270 | 76.0% | 76.0% | -0.0 [-1.9, +1.8] | 459 / 460 | 0.98 | 0.98 | 1 |
| overall | 3270 | 76.0% | 76.0% | -0.0 [-1.9, +1.8] | 459 / 460 | 1 | nan | 1 |

| task | ECE-10 Verdict-MQ cls k=0 (stable) | ECE-10 Laya | Δ ECE [95% CI] |
|---|---|---|---|
| boolq | 0.2145 | 0.0732 | +0.1413 [+0.1239, +0.1596] |
| overall | 0.2145 | 0.0732 | +0.1413 [+0.1235, +0.1597] |
