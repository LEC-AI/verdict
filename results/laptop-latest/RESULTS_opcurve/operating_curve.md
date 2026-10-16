# Verdict operating curve — selective prediction / autonomy

Confidence = top calibrated class probability. An item is auto-handled when confidence >= tau and escalated otherwise. Selection by a threshold picks a confidence-ranked prefix, so every point below is realizable by some tau.

**Tasks:** route_topic, signal_positive, affect  ·  **n = 4872**  ·  **overall accuracy = 89.3%**

**AURC = 0.0200** (lower is better)  ·  random-selection baseline = 0.1073  ·  optimal ordering = 0.0060  ·  E-AURC = 0.0140

## Auto-handle P% at A% accuracy  (coverage @ target accuracy)

| target accuracy | coverage auto-handled | escalated | accuracy on covered | tau |
|---|---|---|---|---|
| 90% | 98.5% | 1.5% | 90.0% | 0.503 |
| 95% | 85.4% | 14.6% | 95.0% | 0.814 |
| 99% | 59.9% | 40.1% | 99.0% | 0.983 |

## Accuracy at fixed coverage

| coverage auto-handled | accuracy on covered | escalated | tau |
|---|---|---|---|
| 50.0% | 99.3% | 50.0% | 0.993 |
| 70.0% | 98.2% | 30.0% | 0.959 |
| 90.0% | 93.4% | 10.0% | 0.708 |
| 100.0% | 89.3% | 0.0% | 0.260 |

## Per task

| task | n | acc | AURC | E-AURC | cov@95% acc | acc@90% cov |
|---|---|---|---|---|---|---|
| route_topic | 2000 | 91.6% | 0.0178 | 0.0142 | 89.7% | 94.9% |
| signal_positive | 872 | 77.8% | 0.0922 | 0.0653 | 39.3% | 81.3% |
| affect | 2000 | 92.0% | 0.0080 | 0.0047 | 93.9% | 96.8% |
