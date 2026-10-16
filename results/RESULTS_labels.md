# Org-task labels: qwen3vl32b (primary) vs deepseekv32 (independent check) vs qwen2.5-7b (original)

No human labels. Quality is measured as agreement between independent strong teachers; the consensus val subset (primary == check) is the evaluation set of record for the email tasks.

## email_needs_reply (yes/no)

| pair | split | n | agreement | Cohen's kappa |
|---|---|---|---|---|
| qwen2.5-7b vs qwen3vl32b | train | 3567 | 86.3% | 0.723 |
| qwen2.5-7b vs qwen3vl32b | val | 371 | 86.8% | 0.728 |
| qwen2.5-7b vs deepseekv32 | val | 371 | 80.9% | 0.597 |
| **qwen3vl32b vs deepseekv32** | val | 371 | 86.0% | 0.691 |

Label distributions (val): 7B {0: 208, 1: 163}, qwen3vl32b {0: 227, 1: 144}, deepseekv32 {0: 263, 1: 108}. Train qwen3vl32b: {0: 2120, 1: 1447}.
Consensus val items: **323** of 375.

## email_escalate (yes/no)

| pair | split | n | agreement | Cohen's kappa |
|---|---|---|---|---|
| qwen2.5-7b vs qwen3vl32b | train | 3567 | 89.7% | 0.350 |
| qwen2.5-7b vs qwen3vl32b | val | 371 | 92.5% | 0.331 |
| qwen2.5-7b vs deepseekv32 | val | 371 | 97.3% | 0.367 |
| **qwen3vl32b vs deepseekv32** | val | 371 | 92.5% | 0.164 |

Label distributions (val): 7B {0: 358, 1: 13}, qwen3vl32b {0: 340, 1: 31}, deepseekv32 {0: 368, 1: 3}. Train qwen3vl32b: {0: 3129, 1: 438}.
Consensus val items: **347** of 375.

## email_priority (score 0-3)

| pair | split | n | agreement | Cohen's kappa | quadratic kappa |
|---|---|---|---|---|---|
| qwen2.5-7b vs qwen3vl32b | train | 3567 | 54.3% | 0.329 | 0.511 |
| qwen2.5-7b vs qwen3vl32b | val | 371 | 53.9% | 0.332 | 0.479 |
| qwen2.5-7b vs deepseekv32 | val | 371 | 44.7% | 0.234 | 0.355 |
| **qwen3vl32b vs deepseekv32** | val | 371 | 60.9% | 0.419 | 0.613 |

Label distributions (val): 7B {0: 73, 1: 76, 2: 219, 3: 3}, qwen3vl32b {0: 145, 1: 104, 2: 110, 3: 12}, deepseekv32 {0: 146, 1: 151, 2: 74}. Train qwen3vl32b: {0: 1289, 1: 906, 2: 1220, 3: 152}.
Consensus val items: **228** of 375.

