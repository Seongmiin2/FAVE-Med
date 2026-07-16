# FAVE-Med / Applicability-QA-Lab

Cross-domain quantitative QA research framework for Telecom and Medical calculations. The primary research target is evidence that is relevant and factually true but unusable for the current computation because units, variable bindings, conditions, conventions, or approximation ranges do not match.

## Research status

| Area | Status |
|---|---|
| Runtime/gold separation and leakage tests | implemented, integration-tested |
| Telecom/Medical deterministic executors | implemented, integration-tested |
| Strict structured output and evaluator statistics | implemented, integration-tested |
| GPT-5.4 Telecom three-item run | real-model-piloted |
| Typed FAVE-DeMo | under implementation |
| Human annotations | not human-reviewed |
| Telecom/Medical test benchmarks | not benchmark-frozen |
| Primary thesis experiment | not experiment-completed |
| Paper claims | not paper-ready |

The historical Telecom seed and mock scores are engineering fixtures. Oracle formula/calculator methods are upper bounds and are never primary results.

## Supported deterministic rules

Telecom currently has ten seed executors. Medical has ten exact-ID executors: BMI, MAP, anion gap, Cockcroft-Gault, corrected calcium, Mosteller BSA, serum osmolality, FENa, Bazett QTc, and MELD-Na.

## Setup and verification

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
pytest -q
```

## Reproducible smoke runs

```powershell
python -m applicability_qa.cli.run --config configs/experiments/telecom_end_to_end_mock_v3.yaml
python -m applicability_qa.cli.evaluate --config configs/experiments/telecom_end_to_end_mock_v3.yaml
```

The tracked real-API pilot summary is in `reports/telecom/openai_3_gpt54_v4_20260716/`. Raw outputs and `.env` are ignored. Never put an API key in source control.

## Source projects

- FAVE-RAG: https://github.com/Seongmiin2/FAVE-RAG
- DeMo-Med: https://github.com/Seongmiin2/DeMo-Med
- MedCalc-Bench-Verified pin and attribution: `data/medical/MEDCALC_BENCH_VERIFIED_PIN.md`

This project evaluates calculator tool use and is not a clinical decision system.
