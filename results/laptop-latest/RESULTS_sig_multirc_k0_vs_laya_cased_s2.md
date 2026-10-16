# Paired significance: Verdict-MQ cls k=0 vs Laya

Matched items: 4847 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (83 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=0 acc | Laya acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| multirc | 4847 | 78.5% | 54.9% | +23.6 [+20.6, +26.5] | 1630 / 487 | 0.0002 | 0.0002 | 2.2e-143 |
| overall | 4847 | 78.5% | 54.9% | +23.6 [+20.6, +26.5] | 1630 / 487 | 0.0002 | nan | 2.2e-143 |

| task | ECE-10 Verdict-MQ cls k=0 | ECE-10 Laya | Δ ECE [95% CI] |
|---|---|---|---|
| multirc | 0.0916 | 0.2105 | -0.1189 [-0.1490, -0.0851] |
| overall | 0.0916 | 0.2105 | -0.1189 [-0.1490, -0.0853] |
