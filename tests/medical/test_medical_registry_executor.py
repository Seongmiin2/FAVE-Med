import pytest

from applicability_qa.domains.medical.calculator_registry import load_calculator_registry
from applicability_qa.domains.medical.formula_executor import execute


def test_ten_typed_calculators_have_exact_executors():
    registry = load_calculator_registry()
    assert len(registry) == 10
    assert all(row.executor_name == row.calculator_id for row in registry)


def test_medical_executor_validates_branches_and_exact_id():
    with pytest.raises(ValueError):
        execute("cockcroft_gault", {"age_years": 60, "weight_kg": 70, "serum_creatinine": 1})
    with pytest.raises(ValueError, match="Unsupported medical calculator ID"):
        execute("body_mass_index_extra", {"weight_kg": 70, "height_m": 1.75})
