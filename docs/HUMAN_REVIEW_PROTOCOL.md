# Independent human-review protocol

Human agreement is accepted only from two distinct people. Model-generated,
duplicated, or self-reviewed labels must never be reported as independent
annotation.

1. Freeze a candidate snapshot and record its SHA-256 hash.
2. Generate reviewer A/B packets with independent row order.
3. Reviewers work without seeing each other's labels.
4. Each reviewer supplies a stable reviewer ID and role declaration.
5. For Medical, at least one reviewer must declare an appropriate clinical
   role; credentials are verified by the research owner, not by this software.
6. Validate completeness and reviewer separation.
7. Compute raw agreement, Cohen's kappa, and per-conflict agreement.
8. Adjudicate disagreements in a separate file while preserving both raw files.
9. Freeze the adjudicated benchmark, raw review hashes, prompt/config hashes,
   license manifest, and Git commit.

Commands:

```powershell
python scripts/create_blinded_review_packets.py --input INPUT.jsonl --output-dir reviews/telecom --domain telecom --sample-size 60
python scripts/validate_independent_reviews.py --reviewer-a reviews/telecom/telecom_reviewer_A.csv --reviewer-b reviews/telecom/telecom_reviewer_B.csv --domain telecom
python scripts/compute_annotation_agreement.py --reviewer-a reviews/telecom/telecom_reviewer_A.csv --reviewer-b reviews/telecom/telecom_reviewer_B.csv
```

The scripts validate declarations and separation but cannot authenticate a
person's professional credentials. That verification must be documented by the
research owner or institution.
