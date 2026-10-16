# Paired significance: Verdict-MQ k=22 vs Verdict-MQ k=0

Matched items: 4934 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (1407 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ k=22 acc | Verdict-MQ k=0 acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| race | 4934 | 77.4% | 76.1% | +1.3 [+0.3, +2.3] | 336 / 272 | 0.011 | 0.011 | 0.011 |
| overall | 4934 | 77.4% | 76.1% | +1.3 [+0.3, +2.3] | 336 / 272 | 0.014 | nan | 0.011 |

| task | ECE-10 Verdict-MQ k=22 | ECE-10 Verdict-MQ k=0 | Δ ECE [95% CI] |
|---|---|---|---|
| race | 0.1099 | 0.1092 | +0.0008 [-0.0096, +0.0111] |
| overall | 0.1099 | 0.1092 | +0.0008 [-0.0092, +0.0110] |
