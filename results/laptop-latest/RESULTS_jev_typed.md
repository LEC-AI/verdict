# Jev (TypeSafe AI, typesafe-ai/jev) on typed-decisions TEST, native questions — measured by us via Vercel AI Gateway

overall **73.4%** (n=1935 decisions, 400 cases attempted, 13 errors), ECE-10 0.028, 1193s

by primitive: choice 73.5%, noul 77.5%, score 70.3%
by workflow: agent_trace_observability 63.5%, customer_service 79.0%, invoice_processing 77.5%, security_incidents 73.8%

| Model | Kind | Acc | Soft acc | Macro F1 | KL | TV | Brier | ECE | Score MAE | Within 1 level |
|---|---|---|---|---|---|---|---|---|---|---|
| Jev (measured) | see note | 0.734 | 0.583 | 0.639 | 0.829 | 0.251 | 0.148 | 0.028 | 0.391 | 0.966 |

Measured ourselves via the Vercel AI Gateway /v1/evaluate endpoint, one call per case (all 5 questions batched, same protocol as Laya/Verdict-MQ). Card leaderboard (self-reported, undisclosed methodology): Jev 0.727.

**13 errors** (first 5): Jev call failed (503): {"error":{"message":"Service temporarily unavailable. Please try again shortly.","type":"service_unavailable_error","param":{"error":"Service temporarily unavailable. Please try again shortly.","type":"service_unavailable_error","statusCode":503}},"providerMetadata":{"gateway":{"routing":{"originalModelId":"typesafe-ai/jev","resolvedProvider":"digitalocean","fallbacksAvailable":["typesafe-ai"],"canonicalSlug":"typesafe-ai/jev","modelAttemptCount":1,"modelAttempts":[{"canonicalSlug":"typesafe-ai/; HTTPSConnectionPool(host='ai-gateway.vercel.sh', port=443): Read timed out. (read timeout=60); HTTPSConnectionPool(host='ai-gateway.vercel.sh', port=443): Read timed out. (read timeout=60); HTTPSConnectionPool(host='ai-gateway.vercel.sh', port=443): Read timed out. (read timeout=60); HTTPSConnectionPool(host='ai-gateway.vercel.sh', port=443): Read timed out. (read timeout=60)
