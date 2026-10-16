# Paired significance: Verdict-MQ cls k=22 vs MC baseline

Matched items: 4934 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (1407 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=22 acc | MC baseline acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| race | 4934 | 77.8% | 79.0% | -1.2 [-2.2, -0.2] | 310 / 369 | 0.02 | 0.02 | 0.026 |
| overall | 4934 | 77.8% | 79.0% | -1.2 [-2.2, -0.2] | 310 / 369 | 0.021 | nan | 0.026 |

| task | ECE-10 Verdict-MQ cls k=22 | ECE-10 MC baseline | Δ ECE [95% CI] |
|---|---|---|---|
| race | 0.1087 | 0.1599 | -0.0511 [-0.0611, -0.0409] |
| overall | 0.1087 | 0.1599 | -0.0511 [-0.0614, -0.0408] |
