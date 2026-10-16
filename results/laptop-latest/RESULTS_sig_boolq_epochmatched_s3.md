# Paired significance: Verdict-MQ cls k=0 (stable, epoch-matched) vs pair classifier (6 epochs, epoch-matched)

Matched items: 3270 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `idx` (3270 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=0 (stable, epoch-matched) acc | pair classifier (6 epochs, epoch-matched) acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| boolq | 3270 | 76.0% | 81.0% | -5.0 [-6.5, -3.6] | 216 / 381 | 0 | 0 | 1.4e-11 |
| overall | 3270 | 76.0% | 81.0% | -5.0 [-6.5, -3.6] | 216 / 381 | 0 | nan | 1.4e-11 |

| task | ECE-10 Verdict-MQ cls k=0 (stable, epoch-matched) | ECE-10 pair classifier (6 epochs, epoch-matched) | Δ ECE [95% CI] |
|---|---|---|---|
| boolq | 0.2145 | 0.1761 | +0.0384 [+0.0247, +0.0534] |
| overall | 0.2145 | 0.1761 | +0.0384 [+0.0246, +0.0530] |
