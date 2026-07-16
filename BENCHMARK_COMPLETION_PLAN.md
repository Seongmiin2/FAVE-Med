# Telecom Benchmark Completion Plan

## Decision

Development continues on `master`; no additional working branch is required. The historical 10-item seed remains a smoke/oracle fixture and the 129 collected rows remain a source candidate pool. Neither is a thesis test set.

## Current readiness finding

The pool contains 129 unique candidates in 15 proposed families, but only 9 questions contain an explicit calculation cue and only 3 combine that cue with a digit-bearing source answer. This heuristic is not a rejection rule, but it shows that the apparent 21-item shortage substantially understates the benchmark work remaining.

The source dataset answer, formula completion, or option label must never become gold without an independent calculation. Every accepted benchmark item must include a numeric `answer.final_value`, `answer.final_unit`, tolerance, formula ID, normalized variables/units, applicability conditions, evidence labels, and provenance.

## Defensible collection strategy

Target a raw pool of 180–200 items to freeze 130 items after review:

1. **Adapt eligible source candidates (80–100 raw):** shortlist WirelessMathBench/XL items that can be converted into self-contained calculations. Preserve source ID and paper ID, record the transformation, verify the individual paper reuse condition, and independently recompute the answer.
2. **Project-authored parameterized items (80–100 raw):** write original problem statements from public mathematical relationships in the typed formula registry. Sample physically plausible parameters, calculate answers with exact-ID deterministic executors, and have a second reviewer recompute them. Formula facts may be used; source prose must not be copied.
3. **Scarce-family supplementation (20–30 raw):** prioritize Rayleigh outage, Nyquist rate, MIMO capacity, and Eb/N0–SNR relations. Do not duplicate a template by merely changing numbers in the final test split; vary conditions, requested quantities, unit conversions, and distractor mechanisms.

Planned frozen composition:

| Split | Items | Use |
|---|---:|---|
| Seed | 10 | Smoke and historical reproduction only |
| Development | 30 | Prompt/parser/retrieval tuning |
| Test | 100 | One-time primary evaluation |

Use at least 12 formula families with 8–12 items per retained family. Near-duplicate templates and source siblings must be group-split so that no template family crosses development and test.

## Evidence construction

Each retained question receives 3–6 evidence passages. Create one clean condition and balanced stress conditions: valid:invalid ratios of 2:1, 1:1, and 1:2, plus invalid-only and contested-heavy subsets. Assign one primary conflict type from:

- unit compatibility
- condition mismatch
- variable binding
- formula convention
- approximation misuse
- physical constraint
- solution step corruption
- insufficient context

Distractors must be generated from a documented transformation of a verified solution, such as dB/linear substitution, km/m mismatch, swapped variable binding, invalid approximation range, or corrupted intermediate step. Store the expected trap answer only in evaluator gold.

## Quality gates

An item is admitted only when all gates pass:

1. Source and adaptation metadata complete; reuse eligibility verified.
2. Question is self-contained and has exactly one intended requested quantity.
3. Formula registry exact ID exists and executor input validates.
4. Two independent computations agree within declared tolerance.
5. Final value and unit are explicitly reviewed; no first-number parsing.
6. Evidence and conflict labels are adjudicated.
7. Question/template/evidence fingerprints are unique across splits.
8. Runtime serialization contains no gold answer, unit, formula, variables, labels, or trap values.

## Human input required

The following cannot be fabricated or automated away:

1. Two independent reviewers for at least 40–60 evidence labels and all final test answers/units. Reviewer IDs may be pseudonyms.
2. Adjudication of disagreements and confirmation that reviewers worked independently.
3. Approval of individual source-paper reuse where an XL-derived item is retained.
4. Before paid experiments: API credentials, exact primary/secondary model names, and a cost ceiling.

## Execution order

1. Finish leakage, typed registry, exact executor dispatch, strict parse handling, and end-to-end mock tests.
2. Implement evaluator error taxonomy and statistical outputs.
3. Create and review development 30; tune only on development.
4. Create and independently review test 100; freeze prompts, evaluator, corpus, and config hashes.
5. Run a 10-item two-model cost pilot.
6. Run the primary model three times and secondary model once; save raw outputs and report all failures.

## Reproducible checks

```powershell
python scripts/validate_candidate_pool.py
python scripts/audit_candidate_readiness.py
pytest -q
python -m applicability_qa.cli.run --config configs/experiments/telecom_end_to_end_mock_v3.yaml
python -m applicability_qa.cli.evaluate --config configs/experiments/telecom_end_to_end_mock_v3.yaml
```
