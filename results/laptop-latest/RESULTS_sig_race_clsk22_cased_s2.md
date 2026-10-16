# Paired significance: Verdict-MQ cls k=22 vs MC baseline

Matched items: 4934 across 1 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks. Clustered by `case` (1407 clusters overall): the primary p-value is a two-sided cluster bootstrap, not exact McNemar (shown alongside, item-level, for continuity only).

| task | n | Verdict-MQ cls k=22 acc | MC baseline acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | cluster-bootstrap p | Holm p | item-level McNemar p |
|---|---|---|---|---|---|---|---|---|
| race | 4934 | 77.4% | 79.0% | -1.6 [-2.6, -0.5] | 324 / 401 | 0.0056 | 0.0056 | 0.0047 |
| overall | 4934 | 77.4% | 79.0% | -1.6 [-2.7, -0.5] | 324 / 401 | 0.0044 | nan | 0.0047 |

| task | ECE-10 Verdict-MQ cls k=22 | ECE-10 MC baseline | Δ ECE [95% CI] |
|---|---|---|---|
| race | 0.1099 | 0.1618 | -0.0519 [-0.0626, -0.0409] |
| overall | 0.1099 | 0.1618 | -0.0519 [-0.0628, -0.0406] |
