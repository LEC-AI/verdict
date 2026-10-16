# Paired significance: Verdict-MQ cls k=0 (stable) vs Laya

Matched items: 3270 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (2938 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=0 (stable) acc | Laya acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| boolq | 3270 | 74.1% | 76.0% | -1.9 [-3.7, -0.0] | 420 / 482 | 0.047 | 0.047 | 0.042 |
| overall | 3270 | 74.1% | 76.0% | -1.9 [-3.7, -0.1] | 420 / 482 | 0.048 | nan | 0.042 |

| task | ECE-10 Verdict-MQ cls k=0 (stable) | ECE-10 Laya | Δ ECE [95% CI] |
|---|---|---|---|
| boolq | 0.2348 | 0.0732 | +0.1616 [+0.1436, +0.1802] |
| overall | 0.2348 | 0.0732 | +0.1616 [+0.1438, +0.1805] |
