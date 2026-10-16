# Paired significance: Verdict-MQ cls k=0 vs Laya

Matched items: 4847 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (83 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=0 acc | Laya acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| multirc | 4847 | 77.6% | 54.9% | +22.7 [+19.7, +25.6] | 1588 / 488 | 0.0002 | 0.0002 | 3.2e-135 |
| overall | 4847 | 77.6% | 54.9% | +22.7 [+19.8, +25.6] | 1588 / 488 | 0.0002 | nan | 3.2e-135 |

| task | ECE-10 Verdict-MQ cls k=0 | ECE-10 Laya | Δ ECE [95% CI] |
|---|---|---|---|
| multirc | 0.0694 | 0.2105 | -0.1412 [-0.1710, -0.1071] |
| overall | 0.0694 | 0.2105 | -0.1412 [-0.1714, -0.1071] |
