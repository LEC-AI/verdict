# Verdict operating curve — selective prediction / autonomy

Confidence = top calibrated class probability. An item is auto-handled when confidence >= tau and escalated otherwise. Selection by a threshold picks a confidence-ranked prefix, so every point below is realizable by some tau.

**Tasks:** email_needs_reply, email_escalate, email_priority  ·  **n = 898**  ·  **overall accuracy = 80.4%**

**AURC = 0.0580** (lower is better)  ·  random-selection baseline = 0.1960  ·  optimal ordering = 0.0207  ·  E-AURC = 0.0373

## Auto-handle P% at A% accuracy  (coverage @ target accuracy)

| target accuracy | coverage auto-handled | escalated | accuracy on covered | tau |
|---|---|---|---|---|
| 90% | 74.9% | 25.1% | 90.0% | 0.530 |
| 95% | 53.8% | 46.2% | 95.0% | 0.719 |
| 99% | 34.5% | 65.5% | 99.0% | 0.863 |

## Accuracy at fixed coverage

| coverage auto-handled | accuracy on covered | escalated | tau |
|---|---|---|---|
| 50.0% | 96.0% | 50.0% | 0.756 |
| 70.0% | 91.1% | 30.0% | 0.586 |
| 90.0% | 84.4% | 10.0% | 0.385 |
| 100.0% | 80.4% | 0.0% | 0.318 |

## Per task

| task | n | acc | AURC | E-AURC | cov@95% acc | acc@90% cov |
|---|---|---|---|---|---|---|
| email_needs_reply | 323 | 78.3% | 0.0865 | 0.0608 | 30.0% | 81.4% |
| email_escalate | 347 | 98.8% | 0.0029 | 0.0028 | 100.0% | 99.0% |
| email_priority | 228 | 55.3% | 0.2987 | 0.1781 | 11.4% | 57.1% |

## Held-out threshold transfer (tau picked on even items, applied to odd items)

| target accuracy | tau (fit half) | fit coverage | fit accuracy | eval coverage | **eval accuracy** |
|---|---|---|---|---|---|
| 90% | 0.571 | 71.3% | 90.0% | 70.6% | **91.5%** |
| 95% | 0.720 | 55.9% | 95.2% | 51.4% | **94.8%** |
| 99% | 0.865 | 35.2% | 99.4% | 32.3% | **99.3%** |
