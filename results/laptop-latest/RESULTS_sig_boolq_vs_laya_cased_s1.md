# Paired significance: Verdict-MQ cls k=0 (stable) vs Laya

Matched items: 3270 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (2938 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=0 (stable) acc | Laya acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| boolq | 3270 | 72.3% | 76.0% | -3.7 [-5.7, -1.8] | 441 / 563 | 0.0004 | 0.0004 | 0.00013 |
| overall | 3270 | 72.3% | 76.0% | -3.7 [-5.7, -1.8] | 441 / 563 | 0.0002 | nan | 0.00013 |

| task | ECE-10 Verdict-MQ cls k=0 (stable) | ECE-10 Laya | Δ ECE [95% CI] |
|---|---|---|---|
| boolq | 0.2499 | 0.0732 | +0.1767 [+0.1580, +0.1957] |
| overall | 0.2499 | 0.0732 | +0.1767 [+0.1579, +0.1958] |
