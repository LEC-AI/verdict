# Paired significance: Verdict-MQ cls k=0 vs Laya

Matched items: 4934 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (1407 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=0 acc | Laya acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| race | 4934 | 76.0% | 45.5% | +30.5 [+28.9, +32.2] | 1873 / 367 | 0.0002 | 0.0002 | 2e-242 |
| overall | 4934 | 76.0% | 45.5% | +30.5 [+28.9, +32.1] | 1873 / 367 | 0.0002 | nan | 2e-242 |

| task | ECE-10 Verdict-MQ cls k=0 | ECE-10 Laya | Δ ECE [95% CI] |
|---|---|---|---|
| race | 0.1104 | 0.0137 | +0.0967 [+0.0770, +0.1071] |
| overall | 0.1104 | 0.0137 | +0.0967 [+0.0772, +0.1069] |
