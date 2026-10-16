# Paired significance: Verdict-MQ k=22 vs Verdict-MQ k=0

Matched items: 4847 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (83 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ k=22 acc | Verdict-MQ k=0 acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| multirc | 4847 | 80.5% | 78.5% | +2.0 [+0.9, +3.2] | 348 / 249 | 0.001 | 0.001 | 5.8e-05 |
| overall | 4847 | 80.5% | 78.5% | +2.0 [+0.9, +3.2] | 348 / 249 | 0.0008 | nan | 5.8e-05 |

| task | ECE-10 Verdict-MQ k=22 | ECE-10 Verdict-MQ k=0 | Δ ECE [95% CI] |
|---|---|---|---|
| multirc | 0.0777 | 0.0916 | -0.0139 [-0.0251, -0.0048] |
| overall | 0.0777 | 0.0916 | -0.0139 [-0.0251, -0.0047] |
