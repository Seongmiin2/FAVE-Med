# Thesis Improvement Implementation Progress

## Completed

- Audited all uses of formula, answer, required-variable, evidence-label, and controlled-context gold fields.
- Preserved the v0.2 pilot and documented it as an oracle-formula feasibility result.
- Added v0.3 `RuntimeQuestion`, `GoldAnnotation`, and `BenchmarkRecord` schemas.
- Added a legacy-seed converter that separates runtime input from evaluator-only gold.
- Added a context-aware applicability classifier with per-evidence label, reason, conflict type, correction, and confidence.
- Added a ten-family public Telecom formula registry and lexical formula retrieval/selection.
- Added explicit oracle method names and predicted-formula executor methods.
- Predicted methods accept `RuntimeQuestion`; selection failure abstains without oracle fallback.
- Added gold-leakage, classifier-context, formula registry, and predicted-pipeline regression coverage.

## Validation

- Historical pilot tests remain supported.
- `pytest`: 16 passed, including leakage regression coverage.
- Formula retrieval selects the correct registry formula for all ten seed questions without reading `GoldAnnotation`.
- Mock smoke produced six successful predicted-mode records (two methods × three items) in a new `seed_smoke_v2` directory, with zero abstentions.
- No paid API call was made for this refactor.

## Remaining risks

- The CLI evaluator still uses the legacy pilot evaluator; v2 formula/retrieval/error metrics are not yet wired into reports.
- Formula retrieval is a deterministic lexical baseline, not BM25 or dense retrieval.
- Controlled-context aliases and true retrieval methods are not yet fully separated in the registry.
- Complete intermediate-call token/latency accounting is not yet implemented.
- The benchmark remains a ten-item seed set; no thesis test claim is supported.
- Human double annotation and agreement cannot be produced until actual independent labels exist.

## Next action

1. Add formula Accuracy@1, Recall@3, and MRR to evaluator v2.
2. Implement controlled-context method names and a real BM25 evidence corpus track.
3. Add unified v0.3 `RunRecord` and full intermediate usage aggregation.
4. Freeze prompts/evaluator before creating reviewed development and test splits.
