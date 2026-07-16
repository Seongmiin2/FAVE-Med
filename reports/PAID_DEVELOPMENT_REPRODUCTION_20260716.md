# Paid development reproduction — 2026-07-16

This is a development check, not the frozen-test experiment.

## Official MedRaC subset

- Official commit: `900c54123ce03ca467ebdf0b2f28afb7dcaabc5e`
- Model: `gpt-4o-mini`, temperature 0
- Records: first 3 official test rows
- Stages: Formula-RAG, value extraction, model-generated Python, execution,
  regular evaluator
- Accuracy: 2/3 (66.7%)
- Tokens: 4,933 input / 840 output
- Estimated generation cost: USD 0.00124395; embeddings excluded
- Deviation: Python 3.13-compatible dependencies and an API-only import shim
  were necessary. The pinned official source was not edited.

## Typed Telecom pilot

- Model: `gpt-4o-mini-2024-07-18`, temperature 0
- Result: 3/3 correct and parsed, zero abstentions and trap hits
- Formula Accuracy@1 and relevant-source Recall@5: 3/3
- Tokens: 783 input / 196 output
- Estimated generation cost: USD 0.00023505

V1 safely abstained because unconstrained model keys failed strict extraction.
V2 enforces registry-exact variable names with strict JSON Schema.

## Typed Medical pilot

- Model: `gpt-4o-mini-2024-07-18`, temperature 0
- Supported Cockcroft-Gault record: correct, 25.238095 mL/min
- Unsupported HEART and CURB-65 records: safe low-confidence abstention
- Final-v3 tokens: 1,373 input / 74 output
- Estimated final-v3 generation cost: USD 0.00025035

V2 exposed arbitrary low-confidence calculator selection and string-valued
numeric facts. V3 adds a selector threshold, bounded gold-free patient context,
and numeric normalization before the execution gate.

## Cost boundary

Successful tracked generation charges total at least USD 0.00172935. This
excludes embedding queries and failed v1 calls whose usage was lost through the
pre-fix exception path. Spend remains far below the USD 5 development cap.

The estimate uses the official GPT-4o mini list price checked on 2026-07-16:
USD 0.15/M input tokens and USD 0.60/M output tokens.

## CRAG

The official source is pinned and prepared. Spending alone does not unblock a
faithful run: it also requires the authors' T5-large evaluator weights, a
compatible generator checkpoint, CUDA execution, and a Google-search-compatible
API key. Only an OpenAI key is configured locally, so `crag_proxy` remains
explicitly labeled as a proxy.
