"""Conservative nonclinical research interpretation gates for Stage D.

This module classifies the state of evidence review. It does not estimate risk,
predict patient outcomes, or provide medication advice. Categories are ordered
workflow states, not scores or evidence-quality grades.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class InterpretationError(ValueError):
    """Raised when the interpretation input is incomplete or inconsistent."""


SCHEMA_VERSION = "1.0.0"
ASSESSMENT_SCHEMA_VERSION = "1.1.0"
INTERPRETATION_CATEGORIES = {
    "INSUFFICIENT_EVIDENCE",
    "MECHANISTIC_EVIDENCE_ONLY",
    "EXPERIMENTAL_EVIDENCE",
    "EXPOSURE_COMPARABILITY_PENDING",
    "REQUIRES_EXPERT_REVIEW",
    "RESEARCH_RELEVANCE_SUPPORTED",
}
_ENUMS: dict[str, set[str]] = {
    "evidence_level": {"none", "mechanistic_only", "experimental", "human_pharmacokinetic", "human_clinical"},
    "evidence_strength": {"not_assessed", "single_source", "multiple_sources", "expert_assessed"},
    "source_review_status": {"unreviewed", "abstract_only", "full_text_reviewed"},
    "source_identity_status": {"verified", "pending", "unverified"},
    "mechanistic_plausibility": {"not_assessed", "proposed", "supported_by_direct_experiment", "not_supported", "conflicting"},
    "experimental_context": {"not_reported", "in_vitro", "animal", "human_pharmacokinetic", "human_clinical", "multiple"},
    "outcome": {"not_reported", "positive", "negative", "null", "conflicting", "unclear"},
    "exposure_comparability": {"not_assessed", "pending", "incompatible", "supported_by_expert"},
    "dietary_exposure_status": {"not_assessed", "unavailable", "available"},
    "uncertainty_status": {"not_assessed", "bounded", "material", "unquantified"},
    "conflict_status": {"not_assessed", "none_known", "source_discrepancy", "conflicting_studies"},
    "human_relevance_status": {"not_assessed", "preclinical_only", "plausible", "supported_by_human_evidence", "expert_reviewed"},
}
_EXPERT_STATUSES = {"not_reviewed", "in_progress", "completed"}
_EXPERT_ADJUDICATIONS = {"not_assessed", "supports_research_relevance", "does_not_support_research_relevance"}
_REQUIRED = {
    "schema_version", "assessment_id", "evidence_level", "evidence_strength", "source_review_status",
    "source_reference", "dietary_exposure_reference", "comparability_review_reference",
    "source_identity_status", "mechanistic_plausibility", "experimental_context", "outcome",
    "exposure_comparability", "dietary_exposure_status", "uncertainty_status", "conflict_status",
    "human_relevance_status", "expert_review",
}


def validate_interpretation_case(case: Mapping[str, Any]) -> None:
    """Validate a single review-state record without external dependencies."""
    if not isinstance(case, Mapping):
        raise InterpretationError("case must be an object")
    missing = sorted(_REQUIRED - set(case))
    extra = sorted(set(case) - _REQUIRED)
    if missing or extra:
        raise InterpretationError(f"case fields mismatch; missing={missing}, extra={extra}")
    if case.get("schema_version") != SCHEMA_VERSION:
        raise InterpretationError(f"schema_version must be {SCHEMA_VERSION}")
    if not isinstance(case.get("assessment_id"), str) or not case["assessment_id"].strip():
        raise InterpretationError("assessment_id must be a nonempty string")
    for field in ("source_reference", "dietary_exposure_reference", "comparability_review_reference"):
        if not isinstance(case.get(field), str):
            raise InterpretationError(f"{field} must be a string")
    for field, allowed in _ENUMS.items():
        value = case.get(field)
        if not isinstance(value, str) or value not in allowed:
            raise InterpretationError(f"{field} must be one of {sorted(allowed)}")
    if not case["source_reference"].strip():
        raise InterpretationError("source_reference is required")
    if case["dietary_exposure_status"] == "available" and not case["dietary_exposure_reference"].strip():
        raise InterpretationError("available dietary exposure requires dietary_exposure_reference")
    if case["exposure_comparability"] == "supported_by_expert" and not case["comparability_review_reference"].strip():
        raise InterpretationError("expert-supported comparability requires comparability_review_reference")
    if (case["exposure_comparability"] == "supported_by_expert"
            and case["dietary_exposure_status"] != "available"):
        raise InterpretationError("expert-supported comparability requires available dietary exposure")
    if case["evidence_level"] == "none" and case["outcome"] != "not_reported":
        raise InterpretationError("no-evidence records must use outcome=not_reported")
    if case["outcome"] == "conflicting" and case["conflict_status"] not in {"source_discrepancy", "conflicting_studies"}:
        raise InterpretationError("a conflicting outcome requires source_discrepancy or conflicting_studies")
    if case["human_relevance_status"] == "supported_by_human_evidence" and case["evidence_level"] not in {"human_pharmacokinetic", "human_clinical"}:
        raise InterpretationError("human-supported relevance requires a human evidence level")
    expert = case.get("expert_review")
    if not isinstance(expert, Mapping) or set(expert) != {"status", "adjudication", "reviewer_reference", "rationale"}:
        raise InterpretationError("expert_review requires status, adjudication, reviewer_reference, and rationale")
    if expert.get("status") not in _EXPERT_STATUSES:
        raise InterpretationError(f"expert_review.status must be one of {sorted(_EXPERT_STATUSES)}")
    if expert.get("adjudication") not in _EXPERT_ADJUDICATIONS:
        raise InterpretationError(f"expert_review.adjudication must be one of {sorted(_EXPERT_ADJUDICATIONS)}")
    if not isinstance(expert.get("reviewer_reference"), str) or not isinstance(expert.get("rationale"), str):
        raise InterpretationError("expert review reference and rationale must be strings")
    if expert.get("status") != "completed" and expert.get("adjudication") != "not_assessed":
        raise InterpretationError("an expert adjudication requires expert_review.status=completed")
    if expert.get("status") == "completed":
        if expert.get("adjudication") == "not_assessed":
            raise InterpretationError("completed expert review requires an explicit adjudication")
        if not expert.get("reviewer_reference", "").strip() or not expert.get("rationale", "").strip():
            raise InterpretationError("completed expert adjudication requires a reviewer reference and rationale")


def classify_interpretation(case: Mapping[str, Any]) -> dict[str, Any]:
    """Return a transparent, nonclinical evidence interpretation state.

    Precedence intentionally sends source conflicts, identity uncertainty,
    abstract-only review, and incomplete expert review to a human-review state.
    A mechanism-only record can never satisfy the research-relevance criteria.
    """
    validate_interpretation_case(case)
    reasons: list[str] = []
    checks: list[dict[str, Any]] = []
    expert = case["expert_review"]
    category: str | None = None
    matched_rule_id: str | None = None

    def consider(rule_id: str, matched: bool, category_on_match: str, detail: str) -> bool:
        nonlocal category, matched_rule_id
        checks.append({
            "order": len(checks) + 1,
            "rule_id": rule_id,
            "matched": matched,
            "category_on_match": category_on_match,
            "detail": detail,
        })
        if matched:
            category = category_on_match
            matched_rule_id = rule_id
            reasons.append(detail)
        return matched

    # A stated conflict is never hidden by missing outcomes. An entirely
    # uninterpretable record with no conflict is insufficient, not negative.
    if consider(
        "KNOWN_CONFLICT",
        case["conflict_status"] in {"source_discrepancy", "conflicting_studies"} or case["outcome"] == "conflicting",
        "REQUIRES_EXPERT_REVIEW",
        "A source discrepancy or conflicting finding is present; retain each result and require explicit adjudication.",
    ):
        pass
    elif consider(
        "NO_INTERPRETABLE_RESULT",
        case["evidence_level"] == "none" or case["outcome"] == "not_reported",
        "INSUFFICIENT_EVIDENCE",
        "No interpretable interaction outcome is available. Missing evidence remains unknown and is not coded as a negative finding.",
    ):
        pass
    elif consider(
        "UNRESOLVED_REVIEW_GATES",
        case["conflict_status"] == "not_assessed"
        or case["outcome"] == "unclear"
        or case["source_identity_status"] != "verified"
        or case["source_review_status"] != "full_text_reviewed"
        or expert["status"] == "in_progress",
        "REQUIRES_EXPERT_REVIEW",
        "At least one source, identity, conflict, outcome, or expert-review gate remains unresolved.",
    ):
        pass
    elif consider(
        "MECHANISM_ONLY",
        case["evidence_level"] == "mechanistic_only",
        "MECHANISTIC_EVIDENCE_ONLY",
        "Mechanism evidence alone cannot establish dietary exposure relevance or a human outcome.",
    ):
        pass
    elif consider(
        "EXPERT_DOES_NOT_SUPPORT_RESEARCH_RELEVANCE",
        expert["status"] == "completed" and expert["adjudication"] == "does_not_support_research_relevance",
        "EXPERIMENTAL_EVIDENCE",
        "The documented expert adjudication does not support research relevance; source outcomes and their tested context remain visible.",
    ):
        pass
    elif consider(
        "COMPARABILITY_PENDING",
        case["exposure_comparability"] in {"not_assessed", "pending"},
        "EXPOSURE_COMPARABILITY_PENDING",
        "Evidence exists, but experimental exposure has not been shown comparable to the dietary exposure context.",
    ):
        pass
    elif consider(
        "RESEARCH_RELEVANCE_REQUIREMENTS_MET",
        case["evidence_level"] in {"human_pharmacokinetic", "human_clinical"}
        and case["outcome"] == "positive"
        and case["source_review_status"] == "full_text_reviewed"
        and case["source_identity_status"] == "verified"
        and case["conflict_status"] == "none_known"
        and case["exposure_comparability"] == "supported_by_expert"
        and case["dietary_exposure_status"] == "available"
        and case["uncertainty_status"] == "bounded"
        and case["human_relevance_status"] in {"supported_by_human_evidence", "expert_reviewed"}
        and expert["status"] == "completed"
        and expert["adjudication"] == "supports_research_relevance",
        "RESEARCH_RELEVANCE_SUPPORTED",
        "The required source, identity, positive human evidence, conflict, exposure, bounded-uncertainty, and explicit expert-support gates are satisfied for this research classification only.",
    ):
        pass
    elif consider(
        "POSITIVE_HUMAN_UNCERTAINTY_UNBOUNDED",
        case["evidence_level"] in {"human_pharmacokinetic", "human_clinical"}
        and case["outcome"] == "positive"
        and case["exposure_comparability"] == "supported_by_expert"
        and case["uncertainty_status"] != "bounded",
        "REQUIRES_EXPERT_REVIEW",
        "Positive human evidence has an asserted exposure comparison, but uncertainty is not bounded for interpretation.",
    ):
        pass
    else:
        category = "EXPERIMENTAL_EVIDENCE"
        matched_rule_id = "EXPERIMENTAL_EVIDENCE_DEFAULT"
        if case["outcome"] in {"negative", "null"}:
            detail = "The negative or null result is limited to the tested conditions and does not establish absence of effects elsewhere."
        else:
            detail = "An observation is reported under the stated experimental context; dietary or clinical consequences are not inferred."
        reasons.append(detail)
        if case["exposure_comparability"] == "incompatible":
            reasons.append("The selected experimental and dietary exposure contexts are documented as incompatible.")
        if case["dietary_exposure_status"] != "available":
            reasons.append("Dietary exposure is unavailable or not assessed.")
        checks.append({
            "order": len(checks) + 1,
            "rule_id": "EXPERIMENTAL_EVIDENCE_DEFAULT",
            "matched": True,
            "category_on_match": category,
            "detail": detail,
        })

    # Preserve every dimension. This categorical state is not a risk score.
    return {
        "schema_version": ASSESSMENT_SCHEMA_VERSION,
        "assessment_id": case["assessment_id"],
        "category": category,
        "decision_reason": reasons,
        "decision_trace": {"matched_rule_id": matched_rule_id, "checks": checks},
        "dimensions": {field: case[field] for field in (*_ENUMS, "source_reference", "dietary_exposure_reference", "comparability_review_reference")},
        "expert_review": dict(expert),
        "claim_boundary": {
            "clinical_interpretation": "not_performed",
            "patient_specific_advice": "not_provided",
            "risk_score": "not_calculated",
            "mechanism_only_sufficient": False,
            "negative_or_null_is_not_generalized": True,
        },
    }


def decision_table() -> list[dict[str, str]]:
    """Return the fixed precedence table used by `classify_interpretation`."""
    return [
        {"order": "1", "rule_id": "KNOWN_CONFLICT", "category": "REQUIRES_EXPERT_REVIEW", "rule": "A source discrepancy, conflicting studies, or a conflicting outcome is retained and routed for explicit adjudication, even when another field is missing."},
        {"order": "2", "rule_id": "NO_INTERPRETABLE_RESULT", "category": "INSUFFICIENT_EVIDENCE", "rule": "No evidence level or no interpretable outcome; missingness remains unknown, never negative."},
        {"order": "3", "rule_id": "UNRESOLVED_REVIEW_GATES", "category": "REQUIRES_EXPERT_REVIEW", "rule": "For interpretable evidence, unassessed conflict, unclear outcome, unverified identity, incomplete source review, or review in progress blocks further interpretation."},
        {"order": "4", "rule_id": "MECHANISM_ONLY", "category": "MECHANISTIC_EVIDENCE_ONLY", "rule": "Mechanism-only evidence cannot establish dietary exposure relevance or a human outcome."},
        {"order": "5", "rule_id": "EXPERT_DOES_NOT_SUPPORT_RESEARCH_RELEVANCE", "category": "EXPERIMENTAL_EVIDENCE", "rule": "A completed expert decision not supporting research relevance leaves the source evidence visible as experimental evidence."},
        {"order": "6", "rule_id": "COMPARABILITY_PENDING", "category": "EXPOSURE_COMPARABILITY_PENDING", "rule": "Evidence is present but exposure comparison is pending or not assessed."},
        {"order": "7", "rule_id": "RESEARCH_RELEVANCE_REQUIREMENTS_MET", "category": "RESEARCH_RELEVANCE_SUPPORTED", "rule": "Positive human evidence, verified identity and full-text source review, no unresolved conflict, expert-supported comparison, available dietary exposure, bounded uncertainty, and completed expert support."},
        {"order": "8", "rule_id": "POSITIVE_HUMAN_UNCERTAINTY_UNBOUNDED", "category": "REQUIRES_EXPERT_REVIEW", "rule": "Positive human evidence with an asserted comparison and unbounded uncertainty requires review."},
        {"order": "9", "rule_id": "EXPERIMENTAL_EVIDENCE_DEFAULT", "category": "EXPERIMENTAL_EVIDENCE", "rule": "Other interpretable evidence; negative and null outcomes remain scoped to tested conditions."},
    ]
