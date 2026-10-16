# Paired significance: Verdict-MQ cls k=0 (stable, epoch-matched) vs pair classifier (6 epochs, epoch-matched)

Matched items: 3270 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `idx` (3270 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=0 (stable, epoch-matched) acc | pair classifier (6 epochs, epoch-matched) acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| boolq | 3270 | 72.3% | 81.6% | -9.3 [-11.0, -7.7] | 250 / 555 | 0 | 0 | 2e-27 |
| overall | 3270 | 72.3% | 81.6% | -9.3 [-11.0, -7.7] | 250 / 555 | 0 | nan | 2e-27 |

| task | ECE-10 Verdict-MQ cls k=0 (stable, epoch-matched) | ECE-10 pair classifier (6 epochs, epoch-matched) | Δ ECE [95% CI] |
|---|---|---|---|
| boolq | 0.2499 | 0.1690 | +0.0810 [+0.0647, +0.0976] |
| overall | 0.2499 | 0.1690 | +0.0810 [+0.0648, +0.0974] |
