# Paired significance: Verdict-MQ cls k=22 vs pair baseline

Matched items: 4847 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (83 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=22 acc | pair baseline acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| multirc | 4847 | 80.5% | 72.6% | +7.9 [+6.0, +9.9] | 707 / 322 | 0.0002 | 0.0002 | 8.7e-34 |
| overall | 4847 | 80.5% | 72.6% | +7.9 [+6.0, +9.9] | 707 / 322 | 0.0002 | nan | 8.7e-34 |

| task | ECE-10 Verdict-MQ cls k=22 | ECE-10 pair baseline | Δ ECE [95% CI] |
|---|---|---|---|
| multirc | 0.0777 | 0.0549 | +0.0228 [+0.0065, +0.0372] |
| overall | 0.0777 | 0.0549 | +0.0228 [+0.0068, +0.0370] |
