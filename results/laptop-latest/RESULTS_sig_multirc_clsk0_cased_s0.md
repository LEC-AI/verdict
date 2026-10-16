# Paired significance: Verdict-MQ cls k=0 vs pair baseline

Matched items: 4847 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (83 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=0 acc | pair baseline acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| multirc | 4847 | 79.2% | 66.4% | +12.8 [+10.8, +14.8] | 999 / 377 | 0.0002 | 0.0002 | 3.7e-65 |
| overall | 4847 | 79.2% | 66.4% | +12.8 [+10.8, +14.8] | 999 / 377 | 0.0002 | nan | 3.7e-65 |

| task | ECE-10 Verdict-MQ cls k=0 | ECE-10 pair baseline | Δ ECE [95% CI] |
|---|---|---|---|
| multirc | 0.0939 | 0.0672 | +0.0267 [+0.0092, +0.0442] |
| overall | 0.0939 | 0.0672 | +0.0267 [+0.0095, +0.0444] |
