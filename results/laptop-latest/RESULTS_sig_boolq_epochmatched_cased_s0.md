# Paired significance: Verdict-MQ cls k=0 (stable, epoch-matched) vs pair classifier (6 epochs, epoch-matched)

Matched items: 3270 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (2938 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=0 (stable, epoch-matched) acc | pair classifier (6 epochs, epoch-matched) acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| boolq | 3270 | 79.2% | 80.8% | -1.6 [-3.0, -0.2] | 234 / 287 | 0.025 | 0.025 | 0.023 |
| overall | 3270 | 79.2% | 80.8% | -1.6 [-3.0, -0.2] | 234 / 287 | 0.025 | nan | 0.023 |

| task | ECE-10 Verdict-MQ cls k=0 (stable, epoch-matched) | ECE-10 pair classifier (6 epochs, epoch-matched) | Δ ECE [95% CI] |
|---|---|---|---|
| boolq | 0.1927 | 0.1776 | +0.0151 [+0.0021, +0.0300] |
| overall | 0.1927 | 0.1776 | +0.0151 [+0.0020, +0.0301] |
