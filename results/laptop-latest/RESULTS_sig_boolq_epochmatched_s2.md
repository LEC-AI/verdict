# Paired significance: Verdict-MQ cls k=0 (stable, epoch-matched) vs pair classifier (6 epochs, epoch-matched)

Matched items: 3270 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `idx` (3270 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=0 (stable, epoch-matched) acc | pair classifier (6 epochs, epoch-matched) acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| boolq | 3270 | 74.1% | 80.1% | -5.9 [-7.5, -4.4] | 221 / 415 | 0 | 0 | 1.2e-14 |
| overall | 3270 | 74.1% | 80.1% | -5.9 [-7.5, -4.4] | 221 / 415 | 0 | nan | 1.2e-14 |

| task | ECE-10 Verdict-MQ cls k=0 (stable, epoch-matched) | ECE-10 pair classifier (6 epochs, epoch-matched) | Δ ECE [95% CI] |
|---|---|---|---|
| boolq | 0.2348 | 0.1821 | +0.0527 [+0.0378, +0.0681] |
| overall | 0.2348 | 0.1821 | +0.0527 [+0.0380, +0.0682] |
