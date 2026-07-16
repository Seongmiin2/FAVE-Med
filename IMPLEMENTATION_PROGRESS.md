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
- Added strict classifier, selector, and variable-extraction schema failure codes with abstention in thesis mode.
- Split legacy compatibility evaluation from a GoldAnnotation-only thesis evaluator.
- Added primary error taxonomy, conflict-type Macro F1, exact McNemar, paired bootstrap CI, and Holm correction.
- Added tracked `reports/` summaries while keeping raw outputs and local results ignored.
- Pinned MedCalc-Bench-Verified at revision `591157b3343b4dda247294f9d929da4c75026fa8` with CC BY-SA 4.0 attribution and local SHA-256 verification.
- Added Medical v0.3 runtime/gold separation, patient-note prompt inclusion, ten typed calculator specifications, ten exact-ID executors, calculator selection, applicability cards, and five mock pipeline methods.
- Created a non-gold Medical selection manifest with 20 development and 100 test candidates across ten families.
- Completed a real GPT-5.4 snapshot Telecom 3-item pilot over five methods after strict-schema and usage-accounting fixes.
- Added typed requirement/evidence signatures, deterministic compatibility checks, solution plans, execution gates, and post-execution validation.
- Connected the typed gate to Telecom and Medical predicted-executor paths without exposing evaluator gold at runtime.
- Added explicitly named comparison proxy baselines and offline minimal-pair, difficulty, and benchmark-track helpers.

## Validation

- Historical pilot tests remain supported.
- `pytest`: 48 passed, including dual-domain leakage, typed mismatch gates, post-validation, benchmark tools, strict parsing, exact dispatch, statistics, and end-to-end mock coverage.
- `pip install -e .`: passed after build dependencies were available.
- Mock end-to-end smoke completed four methods over all ten seed items; these fixture results are not model-performance evidence.
- Real API v4 pilot produced 15 records through 21 calls with zero parse/execution failures; 4,912 input and 3,362 output tokens cost an estimated USD 0.06271.
- Formula retrieval selects the correct registry formula for all ten seed questions without reading `GoldAnnotation`.
- Mock smoke produced six successful predicted-mode records (two methods × three items) in a new `seed_smoke_v2` directory, with zero abstentions.
- Retrieval smoke produced six records with retrieval provenance and relevant-source Recall@5 of 1.0.

## Remaining risks

- Typed signatures currently derive claim-level variable attribution from accepted runtime context; passage-level extraction and condition parsing need stronger structured parsers.
- Named comparison methods are controlled proxy baselines, not exact reproductions of external repositories.
- Formula retrieval remains a deterministic lexical baseline; evidence retrieval now uses BM25.
- Full intermediate-call accounting is implemented for the new FAVE predicted/retrieval paths but not every historical pilot method.
- The benchmark remains a ten-item seed set; no thesis test claim is supported.
- Human double annotation and agreement cannot be produced until actual independent labels exist.
- The balanced collection target is short by 21 candidates: outage probability, Nyquist rate, MIMO capacity, and Eb/N0 relation need additional eligible sources.
- The 129 candidates are not experiment-ready until source-paper license verification, quantitative adaptation, independent recomputation, and double review are complete.
- Readiness audit found only 9 explicit calculation-worded candidates and only 3 that also have digit-bearing source answers; target a 180–200 raw pool rather than assuming only 21 more rows are needed.
- Medical 20/100 rows are selection candidates only; deterministic consistency and medical review remain incomplete.
- The Medical mock uses synthetic fixtures and is not evidence of clinical validity or model performance.

## Next action

1. Replace claim-level signature attribution with passage-level structured extraction and condition predicates.
2. Build reviewed development sets, then freeze independently reviewed test sets.
3. Validate proxy baselines and, where licensing permits, add faithful external-method reproductions.
4. Run the pre-registered two-model experiment only after benchmark freeze.

## Candidate collection commands

```powershell
python scripts/collect_telecom_candidates.py
python scripts/validate_candidate_pool.py
python scripts/export_annotation_sheet.py
python scripts/compute_annotation_agreement.py --reviewer-a reviewer_a.csv --reviewer-b reviewer_b.csv
python scripts/import_annotation_sheet.py --annotations adjudicated.csv --output data/telecom/collection/candidate_pool_reviewed.jsonl
```
