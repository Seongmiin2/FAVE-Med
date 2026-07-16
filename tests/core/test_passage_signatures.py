from applicability_qa.core.compatibility import verify_applicability
from applicability_qa.domains.medical.calculator_registry import load_calculator_registry
from applicability_qa.domains.medical.evidence_signature_parser import parse_evidence_signature as parse_medical
from applicability_qa.domains.medical.requirement_parser import parse_requirement as medical_requirement
from applicability_qa.domains.telecom.evidence_signature_parser import parse_evidence_signature as parse_telecom
from applicability_qa.domains.telecom.formula_registry import load_formula_registry
from applicability_qa.domains.telecom.requirement_parser import parse_requirement as telecom_requirement
from applicability_qa.retrieval import load_corpus


def test_all_telecom_formula_cards_accept_valid_and_reject_trap():
    corpus = {row["source_id"]: row for row in load_corpus("data/telecom/corpus/evidence_corpus_seed.jsonl")}
    for spec in load_formula_registry():
        requirement = telecom_requirement("runtime question", spec)
        assert verify_applicability(requirement, parse_telecom(corpus[spec.formula_id], requirement)).applicable
        assert not verify_applicability(requirement, parse_telecom(corpus[f"{spec.formula_id}_trap"], requirement)).applicable


def test_all_medical_calculator_cards_accept_valid_and_reject_trap():
    corpus = {row["source_id"]: row for row in load_corpus("data/medical/corpus/calculator_evidence_v0.3.jsonl")}
    for spec in load_calculator_registry():
        requirement = medical_requirement("patient note", "runtime question", spec)
        assert verify_applicability(requirement, parse_medical(corpus[spec.calculator_id], requirement)).applicable
        assert not verify_applicability(requirement, parse_medical(corpus[f"{spec.calculator_id}_trap"], requirement)).applicable
