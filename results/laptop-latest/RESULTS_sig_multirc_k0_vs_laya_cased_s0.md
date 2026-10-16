# Paired significance: Verdict-MQ cls k=0 vs Laya

Matched items: 4847 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (83 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=0 acc | Laya acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| multirc | 4847 | 79.2% | 54.9% | +24.3 [+21.2, +27.2] | 1655 / 479 | 0.0002 | 0.0002 | 7.5e-151 |
| overall | 4847 | 79.2% | 54.9% | +24.3 [+21.3, +27.2] | 1655 / 479 | 0.0002 | nan | 7.5e-151 |

| task | ECE-10 Verdict-MQ cls k=0 | ECE-10 Laya | Δ ECE [95% CI] |
|---|---|---|---|
| multirc | 0.0939 | 0.2105 | -0.1166 [-0.1459, -0.0846] |
| overall | 0.0939 | 0.2105 | -0.1166 [-0.1459, -0.0852] |
