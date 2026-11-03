"""Read-only validation and Phase 3 selection contract for Phase 4 records."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ACCEPTED_IDENTITY = {"STRICT_IDENTITY_MATCH", "SUPPORTED_STRUCTURE_EQUIVALENCE"}


class RegistryError(ValueError):
    """Raised for malformed or internally inconsistent Phase 4 registries."""


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def validate_registry(sources: list[dict[str, Any]], evidence: list[dict[str, Any]]) -> list[str]:
    """Validate registry cross-references and non-negotiable evidence gates.

    This is an application-level validator. It supplements, but does not claim to
    replace, a Draft 2020-12 JSON Schema validator.
    """
    errors: list[str] = []
    source_ids = [row.get("source_id") for row in sources]
    evidence_ids = [row.get("evidence_id") for row in evidence]
    if len(source_ids) != len(set(source_ids)):
        errors.append("duplicate source_id")
    if len(evidence_ids) != len(set(evidence_ids)):
        errors.append("duplicate evidence_id")
    known_sources = set(source_ids)
    for row in evidence:
        eid = row.get("evidence_id", "<missing>")
        if row.get("source_id") not in known_sources:
            errors.append(f"{eid}: source_id does not reference a registered source")
        if row.get("compound_reference", {}).get("match_status") != row.get("identity_assessment", {}).get("match_status"):
            errors.append(f"{eid}: compound and identity assessment statuses disagree")
        result = row.get("outcome", {})
        if result.get("result_type") in {"qualitative_observation", "review_conclusion", "not_reported"} and result.get("numeric_value") is not None:
            errors.append(f"{eid}: qualitative/not-reported evidence cannot carry a numeric_value")
        if row.get("review", {}).get("status") in {"accepted_context_only", "accepted_quantitative"}:
            if row.get("review", {}).get("decision_rationale", "").strip() == "":
                errors.append(f"{eid}: accepted evidence requires a decision rationale")
            if row.get("identity_assessment", {}).get("match_status") not in ACCEPTED_IDENTITY:
                errors.append(f"{eid}: accepted evidence has unresolved identity")
            if row.get("identity_assessment", {}).get("review_status") != "adjudicated":
                errors.append(f"{eid}: accepted evidence identity has not been adjudicated")
            if row.get("applicability_assessment", {}).get("status") != "APPLICABLE":
                errors.append(f"{eid}: accepted evidence is not marked applicable")
        if row.get("review", {}).get("status") == "accepted_quantitative":
            if result.get("result_type") not in {"measured_numeric", "derived_numeric"} or not isinstance(result.get("numeric_value"), (int, float)) or not result.get("unit") or not result.get("denominator"):
                errors.append(f"{eid}: accepted quantitative evidence requires a numeric result, unit, and denominator")
    return errors


def phase3_context_records(evidence: list[dict[str, Any]], *, category: str | None = None) -> tuple[dict[str, Any], ...]:
    """Return immutable copies of human-reviewed, identity/applicability-passed records.

    This selector is context-only. It never calculates food dose, concentration,
    retention, risk, or clinical meaning. Quantitative results require a separate
    downstream contract and are intentionally not exposed by this adapter.
    """
    selected = []
    for row in evidence:
        if row.get("review", {}).get("status") != "accepted_context_only":
            continue
        if row.get("identity_assessment", {}).get("match_status") not in ACCEPTED_IDENTITY:
            continue
        if row.get("identity_assessment", {}).get("review_status") != "adjudicated":
            continue
        if row.get("applicability_assessment", {}).get("status") != "APPLICABLE":
            continue
        if category and row.get("category") != category:
            continue
        selected.append(json.loads(json.dumps(row)))
    return tuple(selected)


def validate_jsonschema_if_installed(schema_path: Path, data: Any) -> str:
    """Run a real Draft 2020-12 validator when the optional dev dependency exists."""
    try:
        import jsonschema
    except ImportError:
        return "NOT_RUN: install stageC/phase4/requirements-dev.txt for Draft 2020-12 validation"
    schema = load_json(schema_path)
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.absolute_path))
    if errors:
        raise RegistryError("; ".join(f"{list(error.absolute_path)}: {error.message}" for error in errors))
    return "PASS: Draft 2020-12 schema and instance"
