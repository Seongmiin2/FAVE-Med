# Telecom Candidate Pool v0.3

## Status

This is a **candidate collection**, not a released benchmark or a gold test set. Every item is marked `needs_review`; no human judgment has been inferred or fabricated.

## Sources and license gates

- `XINLI1997/WirelessMathBench`: dataset repository declares CC BY 4.0.
- `XINLI1997/WirelessMATHBench-XL`: dataset card declares CC BY 4.0 and states that the content is derived from arXiv papers.
- Each XL candidate therefore retains `paper_id` where supplied and `source_paper_license=needs_verification`. A candidate cannot be accepted until its individual source and reuse eligibility are verified.

The original question, equation, answer field, dataset/source ID, fingerprint, and proposed formula family are retained for traceability. Dataset answers are not treated as verified numeric gold.

## Collection result

- 129 unique candidates across 15 formula families.
- Proposed split labels are planning aids only: 29 development and 100 test candidates.
- The target of 10 per family was not met for outage probability (6), Nyquist rate (5), MIMO capacity (7), and Eb/N0 relation (1). No duplicate or synthetic item was added to fill these gaps.

## Human review protocol

Two reviewers should independently copy `candidate_review_sheet.csv`, identify themselves, and label the four boolean review fields plus `decision` (`accept` or `reject`). Agreement must be calculated before adjudication. Accepted material must then be rewritten into the project `BenchmarkItem` schema, independently recomputed, unit-checked, and checked for answer/evidence leakage.

Commands are documented in the repository implementation progress file. Do not use this pool for final performance claims.
