# Paired significance: Verdict-MQ cls k=22 vs Laya

Matched items: 4847 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (83 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=22 acc | Laya acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| multirc | 4847 | 80.5% | 54.9% | +25.6 [+22.7, +28.5] | 1699 / 457 | 0.0002 | 0.0002 | 2.5e-167 |
| overall | 4847 | 80.5% | 54.9% | +25.6 [+22.8, +28.5] | 1699 / 457 | 0.0002 | nan | 2.5e-167 |

| task | ECE-10 Verdict-MQ cls k=22 | ECE-10 Laya | Δ ECE [95% CI] |
|---|---|---|---|
| multirc | 0.0777 | 0.2105 | -0.1329 [-0.1638, -0.1002] |
| overall | 0.0777 | 0.2105 | -0.1329 [-0.1642, -0.1002] |
