# Paired significance: Verdict-MQ cls k=22 vs MC baseline

Matched items: 4934 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (1407 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=22 acc | MC baseline acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| race | 4934 | 77.1% | 78.7% | -1.7 [-2.7, -0.6] | 316 / 399 | 0.0024 | 0.0024 | 0.0021 |
| overall | 4934 | 77.1% | 78.7% | -1.7 [-2.7, -0.6] | 316 / 399 | 0.0026 | nan | 0.0021 |

| task | ECE-10 Verdict-MQ cls k=22 | ECE-10 MC baseline | Δ ECE [95% CI] |
|---|---|---|---|
| race | 0.1158 | 0.1612 | -0.0454 [-0.0555, -0.0342] |
| overall | 0.1158 | 0.1612 | -0.0454 [-0.0556, -0.0343] |
