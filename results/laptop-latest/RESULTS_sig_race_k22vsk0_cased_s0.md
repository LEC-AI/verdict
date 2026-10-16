# Paired significance: Verdict-MQ k=22 vs Verdict-MQ k=0

Matched items: 4934 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (1407 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ k=22 acc | Verdict-MQ k=0 acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| race | 4934 | 77.8% | 76.3% | +1.5 [+0.5, +2.5] | 359 / 286 | 0.0028 | 0.0028 | 0.0045 |
| overall | 4934 | 77.8% | 76.3% | +1.5 [+0.4, +2.5] | 359 / 286 | 0.0064 | nan | 0.0045 |

| task | ECE-10 Verdict-MQ k=22 | ECE-10 Verdict-MQ k=0 | Δ ECE [95% CI] |
|---|---|---|---|
| race | 0.1087 | 0.1062 | +0.0026 [-0.0077, +0.0121] |
| overall | 0.1087 | 0.1062 | +0.0026 [-0.0081, +0.0124] |
