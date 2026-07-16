from __future__ import annotations

from .signatures import RequirementSignature, SolutionPlan, TypedApplicabilityDecision


def build_solution_plan(executor_id: str, requirement: RequirementSignature, decisions: list[TypedApplicabilityDecision]) -> SolutionPlan:
    return SolutionPlan(
        executor_id=executor_id,
        ordered_inputs=[item.name for item in requirement.required_inputs],
        accepted_evidence_ids=[item.evidence_id for item in decisions if item.applicable],
        rejected_evidence_ids=[item.evidence_id for item in decisions if not item.applicable],
        output_quantity=requirement.target_quantity,
        output_unit=requirement.target_unit,
    )
