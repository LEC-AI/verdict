# Paired significance: Verdict-MQ cls k=22 vs Laya

Matched items: 4847 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (83 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=22 acc | Laya acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| multirc | 4847 | 81.1% | 54.9% | +26.2 [+23.4, +28.9] | 1694 / 425 | 0.0002 | 0.0002 | 1.3e-178 |
| overall | 4847 | 81.1% | 54.9% | +26.2 [+23.4, +28.9] | 1694 / 425 | 0.0002 | nan | 1.3e-178 |

| task | ECE-10 Verdict-MQ cls k=22 | ECE-10 Laya | Δ ECE [95% CI] |
|---|---|---|---|
| multirc | 0.0866 | 0.2105 | -0.1239 [-0.1537, -0.0931] |
| overall | 0.0866 | 0.2105 | -0.1239 [-0.1541, -0.0932] |
