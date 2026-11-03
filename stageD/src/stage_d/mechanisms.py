"""Validation for review-pending Stage D mechanism evidence candidates."""
from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any


class MechanismContractError(ValueError):
    """Raised when a mechanism evidence record breaks a safety invariant."""


REVIEW_CRITERIA = (
    "primary_source_match",
    "record_to_source_match",
    "compound_identity",
    "target_identity",
    "mechanistic_directness",
    "assay_context",
    "study_design_and_confounding",
    "endpoint_reconciliation",
    "independent_replication",
    "food_context",
    "human_exposure_relevance",
    "clinical_interpretation",
)
CRITERION_STATES = {"meets", "does_not_meet", "not_assessed", "conflicting", "not_applicable"}
REVIEW_REASON_CODES = {
    "manual_review_required",
    "primary_source_page_checked",
    "release_record_identifiers_match_article",
    "compound_identity_not_adjudicated",
    "target_mapping_not_adjudicated",
    "probe_phenotype_not_direct_binding_assay",
    "mechanistic_causality_not_adjudicated",
    "assay_model_requires_human_review",
    "study_design_and_population_require_review",
    "primary_source_endpoint_text_conflict",
    "source_table_abstract_discussion_corroboration",
    "endpoint_semantics_not_adjudicated",
    "independent_replication_not_assessed",
    "food_preparation_not_studied",
    "food_exposure_bridge_not_established",
    "clinical_interpretation_not_performed",
    "direct_transport_assay_still_requires_review",
}
SOURCE_OUTCOME_STATES = {
    "reported_effect",
    "negative_under_tested_conditions",
    "null_or_non_significant",
    "mixed",
    "conflicting",
    "unclear",
}
OUTCOME_REASON_CODES = {
    "explicit_conflict_group",
    "source_label_reports_discrepancy",
    "source_label_reports_mixed_endpoints",
    "explicit_null_or_non_significant_source_label",
    "explicit_no_effect_under_tested_conditions",
    "explicit_source_effect_label",
    "source_text_requires_manual_interpretation",
}
MECHANISM_FAMILIES = {
    "drug_metabolizing_enzyme",
    "membrane_transporter",
    "metabolism_or_transport_unresolved",
}
MECHANISM_RELATIONS = {
    "inhibition_or_reduced_activity",
    "induction_or_increased_activity",
    "substrate_or_transport",
    "unresolved_or_mixed",
}


def validate_mechanism_record(record: Mapping[str, Any]) -> None:
    """Validate a candidate without assigning an evidence score or approval."""
    required = {
        "schema_version", "mechanism_record_id", "stage_b_reference", "raw_stage_b_record",
        "mechanism_candidate", "source_verification", "source_outcome_classification", "review_criteria",
        "review_reasons", "source_discrepancies", "review_state",
    }
    missing = required - set(record)
    if missing:
        raise MechanismContractError(f"Missing fields: {', '.join(sorted(missing))}")
    if record["schema_version"] != "1.0.0":
        raise MechanismContractError("Unsupported mechanism evidence schema version")
    if not re.fullmatch(r"SBD-MECH-[0-9]{4}", str(record["mechanism_record_id"])):
        raise MechanismContractError("Invalid mechanism_record_id")

    reference = record["stage_b_reference"]
    raw = record["raw_stage_b_record"]
    if not isinstance(reference, Mapping) or not isinstance(raw, Mapping):
        raise MechanismContractError("Stage B reference and raw source row must be objects")
    if reference.get("evidence_id") != raw.get("Evidence_ID") or not reference.get("evidence_id"):
        raise MechanismContractError("Stage B Evidence_ID must be preserved exactly")
    if reference.get("release_id") != "StageB_V20_20261103":
        raise MechanismContractError("This tranche is pinned to StageB_V20_20261103")
    if not re.fullmatch(r"[0-9a-f]{64}", str(reference.get("source_file_sha256", ""))):
        raise MechanismContractError("Invalid Stage B source file SHA-256")
    if type(reference.get("row_count_at_build")) is not int or reference["row_count_at_build"] < 1:
        raise MechanismContractError("Stage B row count must be a positive integer")
    if any(not isinstance(key, str) or not isinstance(value, str) for key, value in raw.items()):
        raise MechanismContractError("Every raw CSV column name and value must remain a string")
    for required_raw in ("Evidence_ID", "Compound", "Compound_ID", "Drug", "Mechanism", "Outcome", "Quantitative_Outcome", "PMID", "DOI", "Source_URL", "Source_Locator"):
        if required_raw not in raw:
            raise MechanismContractError(f"Raw Stage B row is missing {required_raw}")

    candidate = record["mechanism_candidate"]
    if not isinstance(candidate, Mapping):
        raise MechanismContractError("mechanism_candidate must be an object")
    if candidate.get("candidate_family") not in MECHANISM_FAMILIES:
        raise MechanismContractError("Invalid candidate mechanism family")
    if candidate.get("source_reported_relation") not in MECHANISM_RELATIONS:
        raise MechanismContractError("Invalid source-reported mechanism relation")
    if not str(candidate.get("source_reported_target", "")).strip():
        raise MechanismContractError("Source-reported mechanism target is required")
    if candidate.get("classification_status") != "pending_manual_review":
        raise MechanismContractError("Mechanism classification must remain pending manual review")
    if candidate.get("canonical_target_id") is not None:
        raise MechanismContractError("This tranche does not adjudicate canonical target identities")

    verification = record["source_verification"]
    if not isinstance(verification, Mapping):
        raise MechanismContractError("source_verification must be an object")
    if verification.get("pmid") != raw.get("PMID") or verification.get("doi") != raw.get("DOI"):
        raise MechanismContractError("Verified primary source identifiers do not match the raw Stage B row")
    if not str(verification.get("verified_source_url", "")).startswith("https://"):
        raise MechanismContractError("A verified HTTPS source URL is required")
    if verification.get("access_level") not in {"primary_article_full_text_reviewed", "primary_article_abstract_reviewed"}:
        raise MechanismContractError("Source access must be explicitly characterized")

    criteria = record["review_criteria"]
    if not isinstance(criteria, Mapping) or set(criteria) != set(REVIEW_CRITERIA):
        raise MechanismContractError("Review criteria must match the declared nonnumeric criterion set")
    for criterion, item in criteria.items():
        if not isinstance(item, Mapping) or set(item) != {"state", "reason_codes"}:
            raise MechanismContractError(f"Review criterion {criterion!r} requires a state and structured reasons")
        if item["state"] not in CRITERION_STATES:
            raise MechanismContractError("Review criterion states must be nonnumeric controlled labels")
        if not isinstance(item["reason_codes"], list) or not item["reason_codes"]:
            raise MechanismContractError(f"Review criterion {criterion!r} requires at least one review reason")
        if any(code not in REVIEW_REASON_CODES for code in item["reason_codes"]):
            raise MechanismContractError(f"Review criterion {criterion!r} has an unknown reason code")
    outcome = record["source_outcome_classification"]
    if not isinstance(outcome, Mapping):
        raise MechanismContractError("source_outcome_classification must be an object")
    if outcome.get("raw_outcome") != raw.get("Outcome") or outcome.get("raw_direction") != raw.get("Direction") or outcome.get("raw_conflict_group") != raw.get("Conflict_Group"):
        raise MechanismContractError("Source outcome fields must be preserved exactly")
    if outcome.get("state") not in SOURCE_OUTCOME_STATES or outcome.get("reason_code") not in OUTCOME_REASON_CODES:
        raise MechanismContractError("Invalid source outcome state or reason code")
    if outcome.get("review_status") != "pending_manual_review":
        raise MechanismContractError("Source outcome interpretation must remain pending manual review")
    if not isinstance(record["review_reasons"], list) or not record["review_reasons"]:
        raise MechanismContractError("Record-level review_reasons must be a nonempty structured list")
    for reason in record["review_reasons"]:
        if not isinstance(reason, Mapping) or set(reason) != {"criterion", "code", "status"}:
            raise MechanismContractError("Each review reason must have criterion, code, and status")
        if reason["criterion"] not in REVIEW_CRITERIA or reason["code"] not in REVIEW_REASON_CODES:
            raise MechanismContractError("Unknown review reason criterion or code")
        if reason["status"] not in {"open", "verified_source_check"}:
            raise MechanismContractError("Review reason status must remain an explicit nonnumeric state")
        if reason["code"] not in criteria[reason["criterion"]]["reason_codes"]:
            raise MechanismContractError("Record-level review reason is not linked to its criterion")
        if (criteria[reason["criterion"]]["state"] == "meets") != (reason["status"] == "verified_source_check"):
            raise MechanismContractError("Only completed source-match criteria may be marked verified_source_check")
    if not isinstance(record["source_discrepancies"], list):
        raise MechanismContractError("source_discrepancies must be an array")
    for discrepancy in record["source_discrepancies"]:
        if not isinstance(discrepancy, Mapping) or set(discrepancy) != {"code", "status", "observations", "resolution"}:
            raise MechanismContractError("Each source discrepancy must have code, status, observations, and resolution")
        if discrepancy["code"] != "primary_source_endpoint_text_conflict" or discrepancy["status"] != "resolved_source_record_level":
            raise MechanismContractError("This tranche records the source-level dose-assignment adjudication")
        if not isinstance(discrepancy["observations"], list) or len(discrepancy["observations"]) < 2:
            raise MechanismContractError("A discrepancy must preserve at least two source observations")
        for observation in discrepancy["observations"]:
            if not isinstance(observation, Mapping) or set(observation) != {"locator", "summary"}:
                raise MechanismContractError("Source observations require a locator and summary")
            if not observation["locator"] or not observation["summary"]:
                raise MechanismContractError("Source observations cannot be blank")
        resolution = discrepancy.get("resolution")
        if not isinstance(resolution, Mapping) or set(resolution) != {
            "decision", "selected_assignment", "conflicting_assignment", "rationale", "manual_review_status", "scope"
        }:
            raise MechanismContractError("A resolved source discrepancy requires its explicit adjudication record")
        if resolution["decision"] != "source_record_level_assignment" or resolution["manual_review_status"] != "pending_manual_review":
            raise MechanismContractError("Source-level transcription adjudication must still await manual review")
        if any(not str(resolution[key]).strip() for key in ("selected_assignment", "conflicting_assignment", "rationale", "scope")):
            raise MechanismContractError("Source discrepancy resolution rationale and assignments cannot be blank")
    review_state = record["review_state"]
    if not isinstance(review_state, Mapping):
        raise MechanismContractError("review_state must be an object")
    if review_state.get("status") != "pending_manual_review" or review_state.get("acceptance") != "pending":
        raise MechanismContractError("Mechanism evidence cannot be accepted automatically")
    if review_state.get("identity_adjudication") != "not_performed":
        raise MechanismContractError("Compound or target identity adjudication was not performed")


def classify_source_outcome(
    outcome: str,
    *,
    direction: str = "",
    conflict_group: str = "",
) -> dict[str, str]:
    """Group only the source's outcome label; do not infer mechanism or risk.

    This deliberately conservative helper preserves the supplied values in the
    caller's record. Direction is never used as enough evidence to assign a
    state. The returned state is descriptive and still requires review.
    """
    del direction  # Raw direction is stored separately and is not a classifier.
    normalized = " ".join(str(outcome or "").casefold().replace("_", " ").split())
    group = " ".join(str(conflict_group or "").casefold().split())
    if group:
        state, code = "conflicting", "explicit_conflict_group"
    elif "discrepancy" in normalized or "conflict" in normalized:
        state, code = "conflicting", "source_label_reports_discrepancy"
    elif normalized.startswith("mixed") or ("null" in normalized and any(token in normalized for token in (" and ", " with ", "/"))):
        state, code = "mixed", "source_label_reports_mixed_endpoints"
    elif normalized in {"null", "null finding", "no significant effect", "no statistically significant effect", "nonsignificant mean changes"} or "not statistically significant" in normalized or normalized.startswith("no significant "):
        state, code = "null_or_non_significant", "explicit_null_or_non_significant_source_label"
    elif normalized.startswith("no inhibition reported") or normalized.startswith("no effect detected") or normalized.startswith("no inhibitory effect"):
        state, code = "negative_under_tested_conditions", "explicit_no_effect_under_tested_conditions"
    elif normalized in {"observed effect", "observed experimental result", "observed in vitro effect", "synergy observed", "synergy detected"} or normalized.startswith("observed in vitro effect ") or normalized.startswith("inhibited ") or normalized.startswith("inhibited cyp") or normalized.startswith("decreased drug metabolism"):
        state, code = "reported_effect", "explicit_source_effect_label"
    else:
        state, code = "unclear", "source_text_requires_manual_interpretation"
    return {
        "state": state,
        "reason_code": code,
        "review_status": "pending_manual_review",
        "interpretation_boundary": "Source-label grouping only; not evidence quality, clinical direction, or risk.",
    }
