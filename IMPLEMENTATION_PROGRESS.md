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
- Collected 129 provenance-preserving Telecom candidates across 15 formula families from the locally cached WirelessMathBench sources.
- Added deterministic deduplication, a collection validator, review-sheet export/import, and independent-review agreement tooling.
- Kept every collected item in `needs_review`; dataset answers and source-paper licenses are not promoted to verified gold.
- Removed runtime derivation from `gold_unit`, added question-only requested-output extraction, and strengthened leakage tests.
- Added typed formula-registry models, exact-ID executor dispatch, physical input checks, and enforced `RunRecord` validation.
- Added the two complete retrieval-to-predicted-executor methods required by the roadmap.

## Validation

- Historical pilot tests remain supported.
- `pytest`: 27 passed, including leakage, exact dispatch, candidate collection, and full retrieval-executor tests.
- Mock end-to-end smoke completed four methods over all ten seed items; these fixture results are not model-performance evidence.
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
- The balanced collection target is short by 21 candidates: outage probability, Nyquist rate, MIMO capacity, and Eb/N0 relation need additional eligible sources.
- The 129 candidates are not experiment-ready until source-paper license verification, quantitative adaptation, independent recomputation, and double review are complete.
- Readiness audit found only 9 explicit calculation-worded candidates and only 3 that also have digit-bearing source answers; target a 180–200 raw pool rather than assuming only 21 more rows are needed.

## Next action

1. Add error taxonomy, conflict-type macro F1, paired bootstrap, and Holm correction.
2. Independently annotate two review-sheet copies, compute agreement, and adjudicate disagreements.
3. Verify source-paper licenses and collect the 21 missing candidates from eligible primary sources.
4. Adapt accepted candidates into `BenchmarkItem`, independently recompute answers/units, and freeze reviewed splits.

## Candidate collection commands

```powershell
python scripts/collect_telecom_candidates.py
python scripts/validate_candidate_pool.py
python scripts/export_annotation_sheet.py
python scripts/compute_annotation_agreement.py --reviewer-a reviewer_a.csv --reviewer-b reviewer_b.csv
python scripts/import_annotation_sheet.py --annotations adjudicated.csv --output data/telecom/collection/candidate_pool_reviewed.jsonl
```
