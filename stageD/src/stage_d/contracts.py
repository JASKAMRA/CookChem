"""Stage D normalization and comparison gates.

Normalization preserves the source labels and leaves records pending review.
It does not score evidence, adjudicate identity, infer clinical relevance, or
calculate a dietary-to-study dose ratio.
"""
from __future__ import annotations

import re
from collections.abc import Mapping
from decimal import Decimal, InvalidOperation
from typing import Any


class ContractError(ValueError):
    """Raised when a contract cannot be constructed from the supplied input."""


_STUDY_TYPE_MAP = {
    "human pharmacokinetic": "human_pharmacokinetic",
    "controlled clinical": "controlled_clinical",
    "animal": "animal",
    "in vitro": "in_vitro",
    "other human clinical": "other_human_clinical",
}
_REQUIRED_COMPARISON_CRITERIA = (
    "compound_identity",
    "exposure_route",
    "dose_units_and_basis",
    "time_window",
    "population_or_model",
    "preparation_or_matrix",
)


def _text(row: Mapping[str, Any], key: str) -> str:
    value = row.get(key, "")
    if value is None:
        return ""
    return str(value).strip()


def _study_type(label: str) -> tuple[str, str]:
    normalized = " ".join(label.casefold().split())
    category = _STUDY_TYPE_MAP.get(normalized)
    if category is None:
        return "other_unclassified", "unrecognized_source_label_requires_manual_review"
    return category, "casefolded_exact_label_match"


def _finding_polarity(outcome: str, direction: str, conflict_group: str) -> tuple[str, str]:
    if conflict_group:
        return "conflicting", "source_conflict_group_present"

    value = " ".join(outcome.casefold().replace("_", " ").split())
    if not value:
        return "unclear", "source_outcome_missing"

    if any(term in value for term in ("null finding", "null/no effect", "no significant effect", "not statistically significant")):
        return "null", "explicit_null_or_non_significant_outcome_text"
    if any(term in value for term in ("negative finding", "negative result", "no inhibition reported", "no effect reported", "no effect detected")):
        return "negative", "explicit_no_effect_outcome_text"
    if any(term in value for term in ("positive finding", "positive result", "observed effect", "observed experimental result", "observed in vitro effect", "inhibited ", "synergy observed", "synergy detected")):
        return "positive", "explicit_reported_effect_outcome_text"

    # Direction is preserved but is not enough by itself to classify a finding.
    if direction and value in {"observed effect", "observed experimental result"}:
        return "positive", "explicit_reported_effect_outcome_text"
    return "unclear", "free_text_requires_manual_interpretation"


def normalize_stage_b_record(
    row: Mapping[str, Any],
    *,
    stage_b_release: str,
    stage_b_manifest_sha256: str,
    drug_id: str | None = None,
) -> dict[str, Any]:
    """Create a review-pending normalized view of one Stage B CSV row.

    A Stage B drug name is never promoted to a canonical drug ID by this
    function. A caller may supply an already adjudicated `drug_id`, but the
    record continues to preserve the Stage B name verbatim.
    """
    evidence_id = _text(row, "Evidence_ID")
    compound_id = _text(row, "Compound_ID")
    if not evidence_id or not compound_id:
        raise ContractError("Evidence_ID and Compound_ID are required and must be nonempty")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", stage_b_manifest_sha256):
        raise ContractError("stage_b_manifest_sha256 must be a 64-character SHA-256 hex digest")
    if not stage_b_release.strip():
        raise ContractError("stage_b_release is required")

    source_type = _text(row, "Evidence_Type")
    study_type, study_rule = _study_type(source_type)
    raw_outcome = _text(row, "Outcome")
    raw_direction = _text(row, "Direction")
    conflict_group = _text(row, "Conflict_Group")
    polarity, finding_rule = _finding_polarity(raw_outcome, raw_direction, conflict_group)
    requires_manual_review = (
        study_type == "other_unclassified"
        or polarity in {"unclear", "conflicting"}
        or not _text(row, "Identity_Status")
    )

    return {
        "schema_version": "1.0.0",
        "evidence_id": evidence_id,
        "compound": {
            "stage_b_compound_id": compound_id,
            "source_name": _text(row, "Compound"),
            "source_identity_status": _text(row, "Identity_Status"),
            "identity_review_status": "unassessed",
        },
        "drug_probe": {
            "stage_b_drug_id": drug_id,
            "source_name": _text(row, "Drug"),
            "identity_review_status": "unassessed",
        },
        "study_type": {
            "source_label": source_type,
            "normalized_category": study_type,
            "normalization_rule": study_rule,
        },
        "study_context": {
            "source_evidence_level": _text(row, "Evidence_Level"),
            "study_design": _text(row, "Study_Design"),
            "dose": _text(row, "Dose"),
            "population_or_model": _text(row, "Population"),
            "affected_entity": _text(row, "Affected_Entity"),
            "perpetrator": _text(row, "Perpetrator"),
            "limitations": _text(row, "Limitations"),
            "clinical_extrapolation_boundary": _text(row, "Clinical_Extrapolation"),
            "source_confidence_text": _text(row, "Confidence"),
        },
        "finding": {
            "raw_outcome": raw_outcome,
            "raw_direction": raw_direction,
            "raw_quantitative_outcome": _text(row, "Quantitative_Outcome"),
            "conflict_group": conflict_group or None,
            "polarity": polarity,
            "normalization_rule": finding_rule,
        },
        "mechanism_source_text": _text(row, "Mechanism"),
        "review_state": {
            "evidence_review": "needs_manual_review" if requires_manual_review else "normalized_pending_review",
            "manual_review_required": requires_manual_review,
            "acceptance_status": "pending",
        },
        "source_provenance": {
            "stage_b_release": stage_b_release,
            "stage_b_manifest_sha256": stage_b_manifest_sha256.lower(),
            "source_record_id": evidence_id,
            "study_id": _text(row, "Study_ID"),
            "source_title": _text(row, "Source_Title"),
            "authors": _text(row, "Authors"),
            "year": _text(row, "Year"),
            "doi": _text(row, "DOI"),
            "pmid": _text(row, "PMID"),
            "source_url": _text(row, "Source_URL"),
            "source_locator": _text(row, "Source_Locator"),
            "source_type": _text(row, "Source_Type"),
        },
    }


def validate_normalized_record(record: Mapping[str, Any]) -> None:
    """Validate essential contract invariants without a third-party package."""
    required_top = {
        "schema_version", "evidence_id", "compound", "drug_probe", "study_type", "study_context",
        "finding", "mechanism_source_text", "review_state", "source_provenance",
    }
    missing = sorted(required_top - set(record))
    if missing:
        raise ContractError(f"Missing normalized evidence fields: {', '.join(missing)}")
    if record["schema_version"] != "1.0.0" or not str(record["evidence_id"]).strip():
        raise ContractError("Unsupported schema version or empty evidence_id")
    nested_required = {
        "compound": {"stage_b_compound_id", "source_name", "source_identity_status", "identity_review_status"},
        "drug_probe": {"stage_b_drug_id", "source_name"},
        "study_type": {"source_label", "normalized_category", "normalization_rule"},
        "study_context": {"source_evidence_level", "study_design", "dose", "population_or_model", "affected_entity", "perpetrator", "limitations", "clinical_extrapolation_boundary", "source_confidence_text"},
        "finding": {"raw_outcome", "raw_direction", "raw_quantitative_outcome", "polarity", "normalization_rule"},
        "review_state": {"evidence_review", "manual_review_required", "acceptance_status"},
        "source_provenance": {"stage_b_release", "stage_b_manifest_sha256", "source_record_id", "study_id", "source_title", "authors", "year", "doi", "pmid", "source_url", "source_locator", "source_type"},
    }
    for parent, required_fields in nested_required.items():
        value = record.get(parent)
        if not isinstance(value, Mapping):
            raise ContractError(f"{parent} must be an object")
        missing_fields = sorted(required_fields - set(value))
        if missing_fields:
            raise ContractError(f"Missing {parent} fields: {', '.join(missing_fields)}")
    if record["review_state"].get("acceptance_status") != "pending":
        raise ContractError("Automated normalization cannot accept evidence")
    if record["review_state"].get("evidence_review") not in {"normalized_pending_review", "needs_manual_review"}:
        raise ContractError("Invalid evidence review state")
    if type(record["review_state"].get("manual_review_required")) is not bool:
        raise ContractError("manual_review_required must be boolean")
    provenance = record["source_provenance"]
    if not re.fullmatch(r"[0-9a-fA-F]{64}", str(provenance.get("stage_b_manifest_sha256", ""))):
        raise ContractError("Invalid Stage B manifest SHA-256")
    if provenance.get("source_record_id") != record["evidence_id"]:
        raise ContractError("Source record ID must remain the original Evidence_ID")
    if record["finding"].get("polarity") not in {"positive", "negative", "null", "conflicting", "unclear"}:
        raise ContractError("Invalid finding polarity")
    if record["study_type"].get("normalized_category") not in set(_STUDY_TYPE_MAP.values()) | {"other_unclassified"}:
        raise ContractError("Invalid normalized study category")


def evaluate_comparability(criteria: Mapping[str, bool | None]) -> dict[str, Any]:
    """Gate a possible comparison; never compute an exposure ratio or risk.

    Each criterion is an externally adjudicated boolean. `None` means the
    requirement has not been resolved. A fully positive gate is only ready for
    human comparability review.
    """
    if set(criteria) != set(_REQUIRED_COMPARISON_CRITERIA):
        missing = sorted(set(_REQUIRED_COMPARISON_CRITERIA) - set(criteria))
        extra = sorted(set(criteria) - set(_REQUIRED_COMPARISON_CRITERIA))
        raise ContractError(f"Comparability criteria mismatch; missing={missing}, extra={extra}")
    for name, value in criteria.items():
        if value is not None and type(value) is not bool:
            raise ContractError(f"Comparability criterion {name!r} must be true, false, or null")

    failed = [name for name, value in criteria.items() if value is False]
    pending = [name for name, value in criteria.items() if value is None]
    if failed:
        decision = "REJECTED"
        reason = "Unsupported comparison; failed criteria: " + ", ".join(sorted(failed))
    elif pending:
        decision = "PENDING"
        reason = "Comparison remains unresolved; criteria need review: " + ", ".join(sorted(pending))
    else:
        decision = "READY_FOR_REVIEW"
        reason = "All listed criteria are explicitly satisfied; human review is still required. No dose equivalence or clinical risk is inferred."
    return {
        "schema_version": "1.0.0",
        "criteria": dict(criteria),
        "decision": decision,
        "decision_reason": reason,
        "review_status": "automated_check_only",
        "clinical_interpretation": "not_performed",
    }


def _decimal_value(value: Any, label: str) -> Decimal:
    """Parse a finite, nonnegative reported quantity without coercing missing to zero."""
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ContractError(f"{label} is missing; missing values cannot be treated as zero")
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ContractError(f"{label} must be a decimal number") from None
    if not parsed.is_finite() or parsed < 0:
        raise ContractError(f"{label} must be finite and nonnegative")
    return parsed


def _sha256(value: Any, label: str) -> str:
    digest = str(value or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ContractError(f"{label} must be a 64-character SHA-256 hex digest")
    return digest


def build_cross_stage_comparison(
    phase3_result: Mapping[str, Any],
    *,
    exposure_id: str,
    normalized_evidence: Mapping[str, Any],
    criteria: Mapping[str, bool | None],
    phase3_release_id: str,
    phase3_manifest_sha256: str,
    phase3_manifest_verification: str,
    stage_b_release: str,
    stage_b_manifest_sha256: str,
) -> dict[str, Any]:
    """Bind one Phase 3 recipe estimate to one exact Stage B evidence record.

    This is a provenance and review gate only. It preserves dietary quantities
    and the source's experimental-dose text as separate fields and never
    calculates a dose ratio, dose equivalence, or clinical risk.
    `phase3_manifest_verification` must be set by the caller only after checking
    the release manifest and all listed artifact hashes.
    """
    if not isinstance(phase3_result, Mapping):
        raise ContractError("phase3_result must be an object")
    if not isinstance(normalized_evidence, Mapping):
        raise ContractError("normalized_evidence must be an object")
    validate_normalized_record(normalized_evidence)
    if not isinstance(criteria, Mapping):
        raise ContractError("criteria must be an object")
    if phase3_result.get("calculation_status") != "COMPLETE":
        raise ContractError("Phase 3 result is not complete; incomplete exposure cannot be compared")
    if not str(phase3_result.get("recipe_id") or "").strip():
        raise ContractError("A single recipe result is required; meal aggregates need component-level selection")
    if phase3_manifest_verification != "verified":
        raise ContractError("Phase 3 release manifest must be verified before cross-stage linkage")
    if not str(phase3_release_id or "").strip():
        raise ContractError("phase3_release_id is required")
    phase3_hash = _sha256(phase3_manifest_sha256, "phase3_manifest_sha256")
    stage_b_hash = _sha256(stage_b_manifest_sha256, "stage_b_manifest_sha256")
    if not str(stage_b_release or "").strip():
        raise ContractError("stage_b_release is required")

    provenance = phase3_result.get("provenance")
    upstream = phase3_result.get("upstream_releases")
    phase1b = upstream.get("phase1b") if isinstance(upstream, Mapping) else None
    if not isinstance(provenance, Mapping) or not isinstance(phase1b, Mapping):
        raise ContractError("Phase 3 source provenance and Phase 1B upstream release are required")
    if phase1b.get("stage_b_release") != stage_b_release:
        raise ContractError("Stage B release does not match the Phase 3 upstream release reference")
    if _sha256(phase1b.get("stage_b_manifest_sha256"), "Phase 3 upstream Stage B hash") != stage_b_hash:
        raise ContractError("Stage B manifest hash does not match the Phase 3 upstream release")
    if _sha256(provenance.get("stage_b_manifest_sha256"), "Phase 3 result Stage B hash") != stage_b_hash:
        raise ContractError("Stage B manifest hash does not match the Phase 3 result provenance")

    if not isinstance(upstream, Mapping):
        raise ContractError("Phase 3 upstream release references must be an object")
    upstream_references: dict[str, dict[str, str]] = {}
    for phase_name in ("phase1b", "phase2", "phase4"):
        reference = upstream.get(phase_name)
        if not isinstance(reference, Mapping):
            raise ContractError(f"Phase 3 {phase_name} upstream release reference is required")
        release_id = str(reference.get("release_id") or "").strip()
        if not release_id:
            raise ContractError(f"Phase 3 {phase_name} release_id is required")
        digest_key = "manifest_sha256"
        upstream_references[phase_name] = {
            "release_id": release_id,
            "manifest_sha256": _sha256(reference.get(digest_key), f"Phase 3 {phase_name} manifest hash"),
        }
    upstream_references["phase1b"]["stage_b_release"] = stage_b_release
    upstream_references["phase1b"]["stage_b_manifest_sha256"] = stage_b_hash

    ingredient_results = phase3_result.get("ingredient_results")
    if not isinstance(ingredient_results, list):
        raise ContractError("Phase 3 ingredient_results must be a list")
    matches = [
        row for row in ingredient_results
        if isinstance(row, Mapping) and row.get("estimate_id") == exposure_id
    ]
    if len(matches) != 1:
        raise ContractError("exposure_id must resolve to exactly one Phase 3 ingredient estimate")
    exposure = matches[0]
    if str(exposure.get("calculation_status", "")).casefold() != "complete":
        raise ContractError("Selected ingredient estimate is not complete")
    if _sha256(exposure.get("stage_b_manifest_sha256"), "Exposure Stage B hash") != stage_b_hash:
        raise ContractError("Selected exposure Stage B hash is inconsistent")

    exp_provenance = exposure.get("provenance")
    if not isinstance(exp_provenance, Mapping):
        raise ContractError("Selected exposure lacks source provenance")
    if _sha256(exp_provenance.get("stage_b_manifest_sha256"), "Exposure provenance Stage B hash") != stage_b_hash:
        raise ContractError("Exposure source provenance Stage B hash is inconsistent")
    compound_id = str(exposure.get("compound_id") or "").strip()
    if not compound_id or exp_provenance.get("compound_id") != compound_id:
        raise ContractError("Exposure Compound_ID is missing or inconsistent with its provenance")

    evidence_id = str(normalized_evidence.get("evidence_id") or "").strip()
    evidence_compound = normalized_evidence.get("compound")
    evidence_provenance = normalized_evidence.get("source_provenance")
    if not evidence_id or not isinstance(evidence_compound, Mapping) or not isinstance(evidence_provenance, Mapping):
        raise ContractError("Normalized evidence requires exact Evidence_ID, Compound_ID, and provenance")
    if evidence_provenance.get("source_record_id") != evidence_id:
        raise ContractError("Stage B source_record_id must exactly match Evidence_ID")
    if evidence_compound.get("stage_b_compound_id") != compound_id:
        raise ContractError("Stage C Compound_ID and Stage B Compound_ID do not match exactly")
    if evidence_provenance.get("stage_b_release") != stage_b_release:
        raise ContractError("Evidence Stage B release does not match the selected source release")
    if _sha256(evidence_provenance.get("stage_b_manifest_sha256"), "Evidence Stage B hash") != stage_b_hash:
        raise ContractError("Evidence Stage B manifest hash does not match the selected source release")

    amount_low = _decimal_value(exposure.get("consumed_amount_low_mg"), "consumed_amount_low_mg")
    amount_high = _decimal_value(exposure.get("consumed_amount_high_mg"), "consumed_amount_high_mg")
    if amount_low > amount_high:
        raise ContractError("Consumed exposure lower bound cannot exceed upper bound")
    concentration = _decimal_value(exposure.get("raw_concentration"), "raw_concentration")
    concentration_unit = str(exposure.get("raw_concentration_unit") or "").strip()
    if not concentration_unit:
        raise ContractError("raw_concentration_unit is required and cannot be inferred")
    cooked_status = str(exposure.get("cooked_exposure_status") or "not_reported").strip()
    cooked_low_raw = exposure.get("cooked_concentration_low")
    cooked_high_raw = exposure.get("cooked_concentration_high")
    cooked_unit_raw = exposure.get("cooked_concentration_unit")
    has_cooked_values = cooked_low_raw not in (None, "") or cooked_high_raw not in (None, "")
    cooked_low: Decimal | None = None
    cooked_high: Decimal | None = None
    cooked_unit: str | None = None
    if has_cooked_values:
        if cooked_status in {"not_reported", "RAW_FOOD_NO_COOKING_ADJUSTMENT"}:
            raise ContractError("Cooked concentration values conflict with cooked_exposure_status")
        if not str(exposure.get("retention_evidence_id") or "").strip():
            raise ContractError("Cooked concentration values require a linked retention_evidence_id")
        cooked_low = _decimal_value(cooked_low_raw, "cooked_concentration_low")
        cooked_high = _decimal_value(cooked_high_raw, "cooked_concentration_high")
        if cooked_low > cooked_high:
            raise ContractError("Cooked concentration lower bound cannot exceed upper bound")
        cooked_unit = str(cooked_unit_raw or "").strip()
        if not cooked_unit:
            raise ContractError("Cooked concentration values require an explicit unit")

    missing_inputs = exposure.get("missing_inputs") or []
    source_warnings = exposure.get("warnings") or []
    input_source_ids = exposure.get("input_source_ids") or []
    if not isinstance(missing_inputs, list) or not isinstance(source_warnings, list) or not isinstance(input_source_ids, list):
        raise ContractError("Exposure missing_inputs, warnings, and input_source_ids must be arrays")

    gate = evaluate_comparability(criteria)
    study_context = normalized_evidence.get("study_context", {})
    source_dose = study_context.get("dose") if isinstance(study_context, Mapping) else None
    return {
        "schema_version": "1.1.0",
        "comparison_id": f"CMP-{exposure_id}-{evidence_id}",
        "exposure_id": exposure_id,
        "evidence_id": evidence_id,
        "criteria": gate["criteria"],
        "decision": gate["decision"],
        "decision_reason": gate["decision_reason"],
        "review_status": gate["review_status"],
        "clinical_interpretation": "not_performed",
        "exposure_reference": {
            "stage": "Stage C Phase 3",
            "phase3_release_id": phase3_release_id,
            "phase3_manifest_sha256": phase3_hash,
            "phase3_manifest_verification": "verified",
            "recipe_id": str(phase3_result["recipe_id"]),
            "estimate_id": exposure_id,
            "stage_b_compound_id": compound_id,
            "stage_b_release": stage_b_release,
            "stage_b_manifest_sha256": stage_b_hash,
            "food_record_id": str(exp_provenance.get("food_record_id") or ""),
            "mapping_id": str(exp_provenance.get("mapping_id") or ""),
            "food_source_title": str(exp_provenance.get("food_source_title") or ""),
            "food_source_url": str(exp_provenance.get("food_source_url") or ""),
            "food_doi": str(exp_provenance.get("food_doi") or ""),
            "food_pmid": str(exp_provenance.get("food_pmid") or ""),
            "input_source_ids": [str(value) for value in input_source_ids],
            "upstream_releases": upstream_references,
        },
        "dietary_exposure": {
            "quantity_type": "consumed_food_compound_amount",
            "lower": format(amount_low, "f"),
            "upper": format(amount_high, "f"),
            "unit": "mg",
            "raw_reference_amount_mg": (
                format(_decimal_value(exposure.get("raw_reference_amount_mg"), "raw_reference_amount_mg"), "f")
                if exposure.get("raw_reference_amount_mg") not in (None, "") else None
            ),
            "raw_food_concentration": format(concentration, "f"),
            "raw_food_concentration_unit": concentration_unit,
            "cooked_food_concentration_lower": format(cooked_low, "f") if cooked_low is not None else None,
            "cooked_food_concentration_upper": format(cooked_high, "f") if cooked_high is not None else None,
            "cooked_food_concentration_unit": cooked_unit,
            "cooked_exposure_status": cooked_status,
            "retention_evidence_id": str(exposure.get("retention_evidence_id") or ""),
            "food_state": str(exp_provenance.get("ingredient_state") or "unknown"),
            "preparation_description": str(exp_provenance.get("preparation_description") or ""),
            "cooking_operations": exp_provenance.get("cooking_operations") or [],
            "missing_inputs": [str(value) for value in missing_inputs],
            "source_warnings": [str(value) for value in source_warnings],
            "calculation_method": str(exposure.get("calculation_method") or ""),
        },
        "experimental_exposure": {
            "reported_dose_text": str(source_dose or ""),
            "normalized_dose_value": None,
            "normalized_dose_unit": None,
            "experimental_concentration_value": None,
            "experimental_concentration_unit": None,
            "normalization_status": "source_text_preserved_no_dimensional_conversion",
        },
    }
