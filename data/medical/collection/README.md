# Medical candidate selection

`verified_selection_v0.3.jsonl` contains only source identifiers, proposed splits, calculator IDs, version/license provenance, and audit status. It deliberately excludes patient notes and evaluator-only gold fields.

The 20 development and 100 test rows are **not frozen benchmark items**. Admission requires deterministic consistency checking, ambiguity review, unit verification, runtime/gold leakage tests, and appropriate medical review. The test split must not be used for prompt tuning.
