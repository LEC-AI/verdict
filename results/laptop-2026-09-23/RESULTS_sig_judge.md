# Paired significance: Verdict vs Qwen7B-0shot

Matched items: 600 across 3 tasks; 10000 bootstrap resamples; exact two-sided McNemar; Holm-Bonferroni over tasks.

| task | n | Verdict acc | Qwen7B-0shot acc | Δ acc [95% CI] | discordant (A✓B✗ / A✗B✓) | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| affect | 200 | 91.5% | 57.0% | +34.5 [+27.5, +41.5] | 73 / 4 | 1.9e-17 | 5.7e-17 |
| route_topic | 200 | 90.0% | 80.5% | +9.5 [+4.5, +14.5] | 24 / 5 | 0.00055 | 0.0011 |
| signal_positive | 200 | 80.0% | 91.0% | -11.0 [-17.5, -4.5] | 11 / 33 | 0.0013 | 0.0013 |
| overall | 600 | 87.2% | 76.2% | +11.0 [+7.0, +15.0] | 108 / 42 | 6.9e-08 | nan |
