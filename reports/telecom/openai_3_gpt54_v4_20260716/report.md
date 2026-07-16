# Telecom GPT-5.4 three-item pilot

This is a real-API execution and cost pilot, not a thesis result. With only three seed items, no significance or general performance claim is supported.

Model snapshot: `gpt-5.4-2026-03-05`

| Method | N | Accuracy | Parse success | Abstention | Invalid evidence F1 |
|---|---:|---:|---:|---:|---:|
| llm_only | 3 | 1.000 | 1.000 | 0.000 | 0.000 |
| vanilla_rag | 3 | 0.667 | 1.000 | 0.000 | 0.000 |
| fave_silent | 3 | 0.667 | 1.000 | 0.000 | 0.800 |
| demo_multi_executor | 3 | 1.000 | 1.000 | 0.000 | 0.000 |
| fave_demo | 3 | 1.000 | 1.000 | 0.000 | 0.800 |

Usage:

- Records: 15
- API calls: 21
- Input tokens: 4,912
- Output tokens: 3,362
- Estimated v4 cost: USD 0.06271
- Parse failures: 0
- Execution failures: 0

Earlier v1–v3 attempts exposed and fixed strict conflict-enum, JSON-schema, extraction, and multi-call accounting defects. They are diagnostic attempts and are excluded from this result table. Total pilot spend including those attempts is estimated below USD 0.10.
