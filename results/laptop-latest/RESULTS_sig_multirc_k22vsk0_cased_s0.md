# Paired significance: Verdict-MQ k=22 vs Verdict-MQ k=0

Matched items: 4847 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (83 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ k=22 acc | Verdict-MQ k=0 acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| multirc | 4847 | 80.1% | 79.2% | +0.9 [-0.2, +2.0] | 294 / 250 | 0.11 | 0.11 | 0.065 |
| overall | 4847 | 80.1% | 79.2% | +0.9 [-0.2, +2.0] | 294 / 250 | 0.11 | nan | 0.065 |

| task | ECE-10 Verdict-MQ k=22 | ECE-10 Verdict-MQ k=0 | Δ ECE [95% CI] |
|---|---|---|---|
| multirc | 0.0846 | 0.0939 | -0.0094 [-0.0205, +0.0008] |
| overall | 0.0846 | 0.0939 | -0.0094 [-0.0210, +0.0006] |
