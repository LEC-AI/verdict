# Paired significance: Verdict-MQ cls k=0 vs pair baseline

Matched items: 4847 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (83 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=0 acc | pair baseline acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| multirc | 4847 | 77.6% | 75.9% | +1.7 [+0.5, +3.0] | 469 / 387 | 0.0064 | 0.0064 | 0.0056 |
| overall | 4847 | 77.6% | 75.9% | +1.7 [+0.5, +3.0] | 469 / 387 | 0.008 | nan | 0.0056 |

| task | ECE-10 Verdict-MQ cls k=0 | ECE-10 pair baseline | Δ ECE [95% CI] |
|---|---|---|---|
| multirc | 0.0694 | 0.0609 | +0.0085 [-0.0021, +0.0221] |
| overall | 0.0694 | 0.0609 | +0.0085 [-0.0021, +0.0218] |
