# Paired significance: Verdict-MQ cls k=0 vs MC baseline

Matched items: 4934 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (1407 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=0 acc | MC baseline acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| race | 4934 | 76.0% | 78.7% | -2.7 [-3.8, -1.6] | 336 / 470 | 0.0002 | 0.0002 | 2.7e-06 |
| overall | 4934 | 76.0% | 78.7% | -2.7 [-3.8, -1.6] | 336 / 470 | 0.0002 | nan | 2.7e-06 |

| task | ECE-10 Verdict-MQ cls k=0 | ECE-10 MC baseline | Δ ECE [95% CI] |
|---|---|---|---|
| race | 0.1104 | 0.1612 | -0.0508 [-0.0611, -0.0397] |
| overall | 0.1104 | 0.1612 | -0.0508 [-0.0611, -0.0395] |
