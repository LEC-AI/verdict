# Paired significance: Verdict-MQ cls k=22 vs Laya

Matched items: 4847 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (83 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=22 acc | Laya acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| multirc | 4847 | 80.1% | 54.9% | +25.2 [+22.2, +28.0] | 1678 / 458 | 0.0002 | 0.0002 | 8.2e-163 |
| overall | 4847 | 80.1% | 54.9% | +25.2 [+22.4, +28.0] | 1678 / 458 | 0.0002 | nan | 8.2e-163 |

| task | ECE-10 Verdict-MQ cls k=22 | ECE-10 Laya | Δ ECE [95% CI] |
|---|---|---|---|
| multirc | 0.0846 | 0.2105 | -0.1260 [-0.1571, -0.0942] |
| overall | 0.0846 | 0.2105 | -0.1260 [-0.1573, -0.0946] |
