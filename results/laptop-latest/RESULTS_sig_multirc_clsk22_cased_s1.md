# Paired significance: Verdict-MQ cls k=22 vs pair baseline

Matched items: 4847 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (83 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=22 acc | pair baseline acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| multirc | 4847 | 81.1% | 75.9% | +5.2 [+3.9, +6.5] | 547 / 296 | 0.0002 | 0.0002 | 4.1e-18 |
| overall | 4847 | 81.1% | 75.9% | +5.2 [+3.8, +6.6] | 547 / 296 | 0.0002 | nan | 4.1e-18 |

| task | ECE-10 Verdict-MQ cls k=22 | ECE-10 pair baseline | Δ ECE [95% CI] |
|---|---|---|---|
| multirc | 0.0866 | 0.0609 | +0.0257 [+0.0122, +0.0383] |
| overall | 0.0866 | 0.0609 | +0.0257 [+0.0123, +0.0382] |
