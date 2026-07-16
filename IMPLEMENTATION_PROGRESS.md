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
- Added explicit controlled-context method names and a separate BM25 retrieval track.
- Added an independently stored seed evidence corpus with formula cards and controlled distractors.
- Added retrieval rank/score/provenance records and formula/relevant-source metric columns.
- Added v0.3 `RunRecord` plus aggregate usage fields for multi-call FAVE v2 pipelines.

## Validation

- Historical pilot tests remain supported.
- `pytest`: 20 passed, including leakage and retrieval regression coverage.
- Formula retrieval selects the correct registry formula for all ten seed questions without reading `GoldAnnotation`.
- Mock smoke produced six successful predicted-mode records (two methods × three items) in a new `seed_smoke_v2` directory, with zero abstentions.
- No paid API call was made for this refactor.
- Retrieval smoke produced six records with retrieval provenance and relevant-source Recall@5 of 1.0.

## Remaining risks

- The evaluator is transitional: formula and relevant-source metrics are wired, but error taxonomy and conflict-type macro F1 remain incomplete.
- Formula retrieval remains a deterministic lexical baseline; evidence retrieval now uses BM25.
- Full intermediate-call accounting is implemented for the new FAVE predicted/retrieval paths but not every historical pilot method.
- The benchmark remains a ten-item seed set; no thesis test claim is supported.
- Human double annotation and agreement cannot be produced until actual independent labels exist.

## Next action

1. Add error taxonomy, conflict-type macro F1, paired bootstrap, and Holm correction.
2. Add annotation export/import/agreement scripts without fabricating human labels.
3. Validate the new controlled and retrieval tracks on all ten seed items.
4. Freeze prompts/evaluator before creating reviewed development and test splits.
