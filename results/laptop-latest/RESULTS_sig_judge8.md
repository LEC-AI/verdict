# Paired significance: Verdict vs Qwen7B-8shot

Matched items: 600 across 3 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict acc | Qwen7B-8shot acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| affect | 200 | 91.5% | 57.0% | +34.5 [+27.0, +42.0] | 76 / 7 | 9.4e-16 | 2.8e-15 |
| route_topic | 200 | 90.0% | 78.0% | +12.0 [+6.0, +18.0] | 31 / 7 | 0.00012 | 0.00012 |
| signal_positive | 200 | 80.0% | 93.5% | -13.5 [-19.5, -8.0] | 5 / 32 | 7.4e-06 | 1.5e-05 |
| overall | 600 | 87.2% | 76.2% | +11.0 [+7.0, +15.0] | 112 / 46 | 1.6e-07 | nan |
