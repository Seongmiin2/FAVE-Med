# Result-Driven Guideline Execution Report

## Scope completed in this iteration

- Cleaned the public project status and separated supported claims from planned claims.
- Implemented typed requirement and evidence signatures.
- Implemented deterministic checks for units, variable coverage, conditions, conventions, approximations, and physical constraints.
- Added explicit solution plans, an execution gate, and post-execution validation.
- Integrated the gate into Telecom and Medical predicted-executor paths.
- Added named proxy baselines using the same corpus and provider infrastructure.
- Added minimal-pair, difficulty, and benchmark-track authoring helpers.
- Extended evaluation output with typed gate allowance and blocking-failure counts.

## Verification

```text
python -m pytest -q
48 passed

python -m pip install -e .
Successfully installed applicability-qa-lab-0.1.0
```

No final paid API experiment was run in this iteration. The earlier three-item
Telecom pilot remains a feasibility artifact and is not promoted to thesis-level
evidence.

## Scientific boundary

The typed implementation is executable and regression-tested, but current
evidence signatures attribute extracted variables at the accepted-context claim
level. Passage-level attribution, structured parsing of registry condition text,
benchmark freeze, independent double review, and medical expert review remain
required before a main experimental claim.

The comparison methods labeled `*_proxy` are controlled local baselines rather
than claims of faithful reproduction of CRAG or MedRaC.

## Next experiment gate

The main paid run remains blocked until all of the following are true:

1. development and held-out records have frozen IDs and hashes;
2. evaluator gold is inaccessible from every runtime path;
3. two genuinely independent reviewers have completed annotation and adjudication;
4. Medical records have appropriate expert review;
5. mock and dry-run outputs pass the unified `RunRecord` JSONL schema;
6. the final model/method matrix and budget are preregistered.
