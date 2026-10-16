# Paired significance: Verdict-MQ k=22 vs Verdict-MQ k=0

Matched items: 4934 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (1407 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ k=22 acc | Verdict-MQ k=0 acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| race | 4934 | 77.1% | 76.0% | +1.0 [+0.0, +2.0] | 352 / 301 | 0.048 | 0.048 | 0.05 |
| overall | 4934 | 77.1% | 76.0% | +1.0 [+0.0, +2.0] | 352 / 301 | 0.045 | nan | 0.05 |

| task | ECE-10 Verdict-MQ k=22 | ECE-10 Verdict-MQ k=0 | Δ ECE [95% CI] |
|---|---|---|---|
| race | 0.1158 | 0.1104 | +0.0054 [-0.0044, +0.0157] |
| overall | 0.1158 | 0.1104 | +0.0054 [-0.0045, +0.0154] |
