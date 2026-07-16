import inspect
import random

from applicability_qa.core.compatibility import verify_applicability
from applicability_qa.core.model_evidence_parser import parse_evidence_with_model
from applicability_qa.core.signatures import ConditionPredicate, EvidenceSignature, ObservedVariable, QuantityRequirement, RequirementSignature, RuntimeFactExtraction
from applicability_qa.core.runtime_fact_extraction import build_execution_signature
from applicability_qa.core.signature_builders import evidence_signatures_from_extraction
from applicability_qa.domains.telecom.evidence_signature_parser import parse_evidence_signature


QUESTION = "Compute Shannon capacity for B=10 MHz and SNR=20 dB."
VALID_TEXT = "Shannon channel capacity uses bandwidth in hertz and SNR converted to a linear power ratio before log2(1+SNR)."
WRONG_TEXT = "Shannon channel capacity accepts the SNR value in dB directly inside log2(1+SNR)."


def requirement():
    return RequirementSignature(target_quantity="capacity", target_unit="bps", required_inputs=[QuantityRequirement(name="B", quantity="bandwidth", canonical_unit="Hz"), QuantityRequirement(name="snr_linear", quantity="snr", canonical_unit="linear")], formula_family_candidates=["shannon_capacity"], convention_tags=["linear_power_ratio"], required_procedural_steps=["convert_snr_to_linear"])


def decision(row):
    return verify_applicability(requirement(), parse_evidence_signature(row, QUESTION)).applicable


def test_rule_parser_is_invariant_to_id_and_label_revealing_metadata():
    rows = [
        {"evidence_id": "obvious_valid_name", "text": VALID_TEXT, "source_type": "controlled_distractor", "expected_label": "rejected", "gold": "trap"},
        {"evidence_id": "contains_trap_and_invalid", "text": VALID_TEXT},
        {"evidence_id": "random-91af", "text": VALID_TEXT, "source_type": "anything"},
    ]
    assert [decision(row) for row in rows] == [True, True, True]
    wrong = dict(rows[0], evidence_id="says_valid", text=WRONG_TEXT, source_type="trusted_valid", expected_label="valid")
    assert not decision(wrong)


def test_order_shuffle_and_metadata_removal_do_not_change_text_decisions():
    rows = [{"evidence_id": "a", "text": VALID_TEXT}, {"evidence_id": "b", "text": WRONG_TEXT}]
    baseline = {row["text"]: decision(row) for row in rows}
    random.Random(7).shuffle(rows)
    assert {row["text"]: decision(row) for row in rows} == baseline


def test_parser_source_has_no_label_revealing_reads():
    source = inspect.getsource(parse_evidence_signature)
    for forbidden in ('_trap', 'distractor', 'source_type")', "expected_label", "gold"):
        assert forbidden not in source


class CaptureProvider:
    def __init__(self):
        self.prompt = ""
    def generate_json(self, system, user, schema=None):
        self.prompt = system + user
        return {"asserted_formula_id": "shannon_capacity", "variable_units": {"B": "Hz", "snr_linear": "linear"}, "convention_tags": ["linear_power_ratio"], "procedural_steps": ["convert_snr_to_linear"], "facts": {}}


def test_model_parser_receives_only_question_context_and_passage_text():
    provider = CaptureProvider()
    parsed = parse_evidence_with_model(QUESTION, "", "id_contains_trap", VALID_TEXT, provider)
    assert parsed.evidence_id == "id_contains_trap"
    assert "id_contains_trap" not in provider.prompt
    assert "source_type" not in provider.prompt


def observed(value, unit, normalized, normalized_unit, operation, span):
    return ObservedVariable(observed_value=value, observed_unit=unit, normalized_value=normalized, normalized_unit=normalized_unit, conversion_operation=operation, source_span=span, confidence=1.0)


def test_execution_signature_does_not_copy_requirement_claims():
    extraction = RuntimeFactExtraction(variables={"B": observed(10, "MHz", 10_000_000, "Hz", "MHz_to_Hz_x1e6", "bandwidth B=10 MHz")})
    signature = build_execution_signature(extraction)
    assert signature.asserted_formula_id is None
    assert signature.convention_tags == []
    assert signature.procedural_steps == []
    assert signature.variable_units == {"B": "Hz"}

    legacy_signature = evidence_signatures_from_extraction(["neutral-id"], {"B": 10})[0]
    assert legacy_signature.quantities == {}
    assert legacy_signature.variable_units == {}
    assert legacy_signature.convention_tags == []
    assert legacy_signature.procedural_steps == []


def test_adversarial_unit_condition_binding_and_conversion_failures_block():
    req = requirement()
    wrong_unit = EvidenceSignature(evidence_id="valid_words_in_id", asserted_formula_id="shannon_capacity", variables=["B", "snr_linear"], variable_units={"B": "Hz", "snr_linear": "dB"}, convention_tags=["linear_power_ratio"], procedural_steps=["convert_snr_to_linear"])
    assert not verify_applicability(req, wrong_unit).applicable

    conditioned = req.model_copy(update={"conditions": [ConditionPredicate(field="channel", operator="eq", value="awgn")]})
    other_condition = wrong_unit.model_copy(update={"variable_units": {"B": "Hz", "snr_linear": "linear"}, "facts": {"channel": "rayleigh"}})
    assert not verify_applicability(conditioned, other_condition).applicable

    swapped = RuntimeFactExtraction(variables={"B": observed(10, "Hz", 10, "Hz", "identity", "SNR=10 Hz"), "snr_linear": observed(5, "linear", 5, "linear", "identity", "bandwidth=5 linear")}, asserted_formula_id="shannon_capacity", convention_tags=["linear_power_ratio"], procedural_steps=["convert_snr_to_linear"])
    assert not verify_applicability(req, build_execution_signature(swapped)).applicable

    omitted = RuntimeFactExtraction(variables={"B": observed(10, "MHz", 10_000_000, "Hz", None, "bandwidth=10 MHz"), "snr_linear": observed(100, "linear", 100, "linear", "identity", "SNR=100 linear")}, asserted_formula_id="shannon_capacity", convention_tags=["linear_power_ratio"], procedural_steps=["convert_snr_to_linear"])
    assert not verify_applicability(req, build_execution_signature(omitted)).applicable
