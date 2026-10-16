# Paired significance: Verdict-MQ cls k=0 vs pair baseline

Matched items: 4847 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (83 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=0 acc | pair baseline acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| multirc | 4847 | 78.5% | 72.6% | +5.9 [+4.0, +7.8] | 631 / 345 | 0.0002 | 0.0002 | 4e-20 |
| overall | 4847 | 78.5% | 72.6% | +5.9 [+4.1, +7.8] | 631 / 345 | 0.0002 | nan | 4e-20 |

| task | ECE-10 Verdict-MQ cls k=0 | ECE-10 pair baseline | Δ ECE [95% CI] |
|---|---|---|---|
| multirc | 0.0916 | 0.0549 | +0.0367 [+0.0215, +0.0515] |
| overall | 0.0916 | 0.0549 | +0.0367 [+0.0222, +0.0515] |
