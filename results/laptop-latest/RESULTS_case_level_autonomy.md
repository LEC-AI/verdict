# Case-level (joint-acceptance) vs per-decision automation, target 90%

| system | decision coverage | case coverage (all 5 decisions clear tau) | whole-case accuracy |
|---|---|---|---|
| Laya | 55.7% | 2.5% (5/199) | 80.0% |
| Verdict-MQ s40 | 67.3% | 25.1% (50/199) | 76.0% |
| Verdict-MQ s41 | 65.0% | 22.6% (45/199) | 77.8% |
| Verdict-MQ s42 | 71.1% | 26.6% (53/199) | 69.8% |
| Verdict-MQ s43 | 64.0% | 22.6% (45/199) | 73.3% |
| Verdict-MQ s44 | 62.2% | 19.1% (38/199) | 81.6% |

Decision coverage/tau match autonomy_from_preds.py exactly (same FIT/EVAL split, same threshold). Case coverage additionally requires every one of a case's decisions in the EVAL half to individually clear tau. Whole-case accuracy is over only the auto-handled cases, and only counts a case correct if every one of its decisions is correct.
