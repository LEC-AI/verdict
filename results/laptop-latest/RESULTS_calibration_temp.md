# Matched temperature-scaling calibration (T fit on one half of cases, applied to the other)

| system | n (eval) | fitted T | raw ECE-10 (eval) | calibrated ECE-10 (eval) |
|---|---|---|---|---|
| Laya-td | 995 | 0.320 | 0.2030 | 0.0299 |
| Verdict-MQ-large s40 | 995 | 0.420 | 0.1630 | 0.0232 |
| Verdict-MQ-large s41 | 995 | 0.440 | 0.1692 | 0.0174 |
| Verdict-MQ-large s42 | 995 | 0.420 | 0.1635 | 0.0230 |
| Verdict-MQ-large s43 | 995 | 0.440 | 0.1553 | 0.0187 |
| Verdict-MQ-large s44 | 995 | 0.440 | 0.1423 | 0.0316 |

T fit by grid-search NLL minimization on the FIT half; argmax (and thus accuracy/hit) is unchanged by temperature scaling, only confidence. Fit/eval split is case-level (idx hash), matching the autonomy dial's convention.

## Paired case-cluster bootstrap CI on calibrated ECE difference vs Laya-td (T=0.320)

| system | n matched | n clusters | ECE diff (system - Laya-td) | 95% CI | excludes 0? |
|---|---|---|---|---|---|
| Verdict-MQ-large s40 | 995 | 199 | -0.0067 | [-0.0313, +0.0183] | no |
| Verdict-MQ-large s41 | 995 | 199 | -0.0126 | [-0.0339, +0.0144] | no |
| Verdict-MQ-large s42 | 995 | 199 | -0.0069 | [-0.0295, +0.0176] | no |
| Verdict-MQ-large s43 | 995 | 199 | -0.0113 | [-0.0339, +0.0136] | no |
| Verdict-MQ-large s44 | 995 | 199 | +0.0017 | [-0.0246, +0.0251] | no |
