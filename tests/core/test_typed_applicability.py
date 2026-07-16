from applicability_qa.core.compatibility import verify_applicability
from applicability_qa.core.execution_gate import build_execution_gate
from applicability_qa.core.planning import build_solution_plan
from applicability_qa.core.post_validation import validate_execution
from applicability_qa.core.signatures import ConditionPredicate, EvidenceSignature, QuantityRequirement, RequirementSignature


def requirement(**overrides):
    data = {
        "target_quantity": "capacity",
        "target_unit": "bps",
        "required_inputs": [QuantityRequirement(name="B", quantity="bandwidth", canonical_unit="Hz")],
        "conditions": [ConditionPredicate(field="snr_linear", operator="gt", value=0)],
        "convention": "linear_snr",
        "approximation_policy": "exact",
        "physical_constraints": [ConditionPredicate(field="B", operator="gt", value=0)],
    }
    data.update(overrides)
    return RequirementSignature(**data)


def evidence(**overrides):
    data = {
        "evidence_id": "e1", "quantities": {"capacity": "bps"},
        "variables": ["B"], "facts": {"B": 1_000_000, "snr_linear": 10},
        "convention": "linear_snr", "approximation": False,
    }
    data.update(overrides)
    return EvidenceSignature(**data)


def test_compatible_evidence_passes_gate_and_builds_plan():
    req = requirement()
    decision = verify_applicability(req, evidence())
    assert decision.applicable
    assert build_execution_gate([decision]).allowed
    plan = build_solution_plan("shannon_capacity", req, [decision])
    assert plan.accepted_evidence_ids == ["e1"]
    assert plan.ordered_inputs == ["B"]


def test_each_typed_mismatch_blocks_execution():
    cases = [
        evidence(quantities={"capacity": "bit"}),
        evidence(variables=[], facts={"snr_linear": 10}),
        evidence(facts={"B": 1, "snr_linear": 0}),
        evidence(convention="db_snr"),
        evidence(approximation=True),
        evidence(facts={"B": -1, "snr_linear": 10}),
    ]
    expected = {"unit_mismatch", "missing_variables", "condition_mismatch", "convention_mismatch", "approximation_mismatch", "physical_constraint_violation"}
    observed = set()
    for row in cases:
        decision = verify_applicability(requirement(), row)
        assert not decision.applicable
        assert not build_execution_gate([decision]).allowed
        observed.update(check.code for check in decision.checks if not check.passed)
    assert expected <= observed


def test_post_execution_validation_is_strict():
    assert validate_execution(42.0, "bps", "bps", minimum=0).passed
    assert not validate_execution(float("nan"), "bps", "bps").passed
    assert not validate_execution(42.0, "Hz", "bps").passed
