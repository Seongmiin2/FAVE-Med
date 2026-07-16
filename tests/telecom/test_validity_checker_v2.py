from applicability_qa.core.schemas import RuntimeEvidence, RuntimeQuestion
from applicability_qa.domains.telecom.validity_checker import classify_evidence
from applicability_qa.providers.mock_provider import MockProvider


class Capture(MockProvider):
    def __init__(self):
        super().__init__()
        self.user_prompt = ""

    def generate_json(self, system_prompt, user_prompt, schema=None):
        self.user_prompt = user_prompt
        return super().generate_json(system_prompt, user_prompt, schema)


def test_classifier_receives_question_and_returns_decisions():
    provider = Capture()
    item = RuntimeQuestion(id="1", domain="telecom", question="Convert SNR 13 dB to linear", requested_output="linear SNR", evidence=[RuntimeEvidence(id="e1", text="Use a power-ratio conversion")])
    result = classify_evidence(item, item.evidence, provider)
    assert item.question in provider.user_prompt
    assert result.decisions[0].evidence_id == "e1"
    assert result.decisions[0].label in {"valid", "contested", "rejected"}


def test_mock_retrieval_trap_is_rejected():
    item = RuntimeQuestion(id="1", domain="telecom", question="Compute capacity", evidence=[RuntimeEvidence(id="doc_capacity_trap", text="Insert dB directly")])
    result = classify_evidence(item, item.evidence, MockProvider())
    assert result.decisions[0].label == "rejected"
