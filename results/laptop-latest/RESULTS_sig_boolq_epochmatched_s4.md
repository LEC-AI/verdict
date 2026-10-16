# Paired significance: Verdict-MQ cls k=0 (stable, epoch-matched) vs pair classifier (6 epochs, epoch-matched)

Matched items: 3270 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `idx` (3270 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=0 (stable, epoch-matched) acc | pair classifier (6 epochs, epoch-matched) acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| boolq | 3270 | 79.4% | 81.5% | -2.1 [-3.4, -0.7] | 223 / 291 | 0.0026 | 0.0026 | 0.0031 |
| overall | 3270 | 79.4% | 81.5% | -2.1 [-3.5, -0.7] | 223 / 291 | 0.0022 | nan | 0.0031 |

| task | ECE-10 Verdict-MQ cls k=0 (stable, epoch-matched) | ECE-10 pair classifier (6 epochs, epoch-matched) | Δ ECE [95% CI] |
|---|---|---|---|
| boolq | 0.1911 | 0.1746 | +0.0166 [+0.0035, +0.0308] |
| overall | 0.1911 | 0.1746 | +0.0166 [+0.0038, +0.0305] |
