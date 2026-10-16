# Paired significance: Verdict-MQ cls k=22 vs pair baseline

Matched items: 4847 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (83 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=22 acc | pair baseline acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| multirc | 4847 | 80.1% | 66.4% | +13.7 [+11.7, +15.7] | 1038 / 372 | 0.0002 | 0.0002 | 5.8e-73 |
| overall | 4847 | 80.1% | 66.4% | +13.7 [+11.7, +15.7] | 1038 / 372 | 0.0002 | nan | 5.8e-73 |

| task | ECE-10 Verdict-MQ cls k=22 | ECE-10 pair baseline | Δ ECE [95% CI] |
|---|---|---|---|
| multirc | 0.0846 | 0.0672 | +0.0173 [-0.0008, +0.0337] |
| overall | 0.0846 | 0.0672 | +0.0173 [-0.0008, +0.0338] |
