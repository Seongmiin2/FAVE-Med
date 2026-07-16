# Gold Leakage Audit

Audit date: 2026-07-16

## Summary

The historical v0.2 pilot mixes runtime inputs and evaluator-only annotations in `BenchmarkItem`. Its executor results are oracle upper bounds and must not be reported as predicted-formula results.

| Location | Gold-bearing field | Current purpose | Required disposition |
|---|---|---|---|
| `domains/telecom/adapter.py` | `gold_answer`, `gold_formula`, `required_variables`, `expected_arbitration` | Builds one mixed object | Add `BenchmarkRecord(runtime, gold)` loader; retain legacy loader only for pilot reproduction |
| `pipelines/demo_multi_executor.py` | `item.formula.expression`, `item.formula.id` | Prompt and executor dispatch | Rename/alias as `demo_oracle_executor`; never use from predicted pipeline |
| `pipelines/fave_demo.py` | `item.formula.expression`, `item.formula.id` | Prompt and executor dispatch | Rename/alias as `fave_oracle_executor`; never use from predicted pipeline |
| `pipelines/vanilla_rag.py` | `mixed_context` IDs | Controlled evidence injection | Report as controlled-context, not real retrieval |
| `domains/telecom/validity_checker.py` | none directly, but receives mixed object | Evidence classification | Restrict interface to `RuntimeQuestion`; include question context |
| `cli/evaluate.py` | answer/evidence gold | Evaluation | Allowed; evaluator is the only consumer of `GoldAnnotation` in v0.3 |

## Enforcement

- Predicted pipelines accept `RuntimeQuestion`, which has no formula answer or gold annotation fields.
- Formula candidates come from a separate public formula registry.
- Selection failure abstains and never falls back to benchmark gold.
- Sentinel regression tests capture provider prompts and executor dispatch.
- Historical outputs remain `pilot_v1`/oracle upper-bound artifacts.
