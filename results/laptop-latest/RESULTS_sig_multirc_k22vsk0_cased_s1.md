# Paired significance: Verdict-MQ k=22 vs Verdict-MQ k=0

Matched items: 4847 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (83 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ k=22 acc | Verdict-MQ k=0 acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| multirc | 4847 | 81.1% | 77.6% | +3.5 [+2.3, +4.7] | 444 / 275 | 0.0002 | 0.0002 | 3.1e-10 |
| overall | 4847 | 81.1% | 77.6% | +3.5 [+2.3, +4.7] | 444 / 275 | 0.0002 | nan | 3.1e-10 |

| task | ECE-10 Verdict-MQ k=22 | ECE-10 Verdict-MQ k=0 | Δ ECE [95% CI] |
|---|---|---|---|
| multirc | 0.0866 | 0.0694 | +0.0172 [+0.0037, +0.0268] |
| overall | 0.0866 | 0.0694 | +0.0172 [+0.0038, +0.0271] |
