"""Structured Stage A owner-decision tracking without loading or using a model.

This module manages the RF-01--RF-15 target-contract decision handoff. It does
not verify scientific claims, validate Stage A artifacts, authorize inference,
or change the Phase 2 deployment gate.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from datetime import date
from typing import Any


DECISIONS: tuple[tuple[str, str], ...] = (
    ("RF-01", "Target equation and source-family derivation"),
    ("RF-02", "Output scale, unit, and inverse log1p transformation"),
    ("RF-03", "Numerator, denominator, and measurement basis"),
    ("RF-04", "Raw/cooked pairing and replicate definition"),
    ("RF-05", "Cooked yield and total-mass adjustment"),
    ("RF-06", "Moisture basis and fresh/dry-weight handling"),
    ("RF-07", "Solid/liquid compartments for liquid-contact cooking"),
    ("RF-08", "Analyte identity and chemical transformation"),
    ("RF-09", "Recovery, calibration, detection limits, and censoring"),
    ("RF-10", "Values above 100 and source-specific disposition"),
    ("RF-11", "Loss encoding, zeros, negatives, missingness, and sentinels"),
    ("RF-12", "Target aggregation and supported domain"),
    ("RF-13", "Meaning and scope of Initial_Unit_Standardized"),
    ("RF-14", "Imputation, normalization, clipping, and manual edits"),
    ("RF-15", "Apparent_Increase provenance and feature-leakage risk"),
)
_DECISION_BY_ID = dict(DECISIONS)
_ALLOWED_APPROVALS = {"PENDING", "APPROVED", "REJECTED"}


def create_initial_tracker() -> dict[str, Any]:
    """Return an honest empty RF-01--RF-15 owner tracker."""
    return {
        "schema_version": "1.0.0",
        "tracker_id": "RETENTION-FINAL-OWNER-DECISIONS",
        "overall_status": "OPEN",
        "decisions": [
            {
                "decision_id": decision_id,
                "topic": topic,
                "owner_response": None,
                "supporting_artifact": None,
                "source_locator": None,
                "decision_date": None,
                "scientific_reviewer": None,
                "approval_status": "PENDING",
                "unresolved_rationale": "Awaiting the documented owner response and source evidence.",
            }
            for decision_id, topic in DECISIONS
        ],
    }


def validate_decision_tracker(tracker: Any) -> dict[str, Any]:
    """Check completeness and lifecycle consistency; do not adjudicate content."""
    issues: list[str] = []
    decisions = tracker.get("decisions") if isinstance(tracker, Mapping) else None
    if not isinstance(tracker, Mapping):
        return _tracker_result(["Tracker must be a JSON object."], [], {})
    if tracker.get("schema_version") != "1.0.0":
        issues.append("schema_version must equal 1.0.0.")
    if not isinstance(tracker.get("tracker_id"), str) or not tracker["tracker_id"].strip():
        issues.append("tracker_id must be a nonempty string.")
    overall_status = tracker.get("overall_status")
    if not isinstance(overall_status, str) or overall_status not in {"OPEN", "IN_REVIEW", "CLOSED"}:
        issues.append("overall_status must be OPEN, IN_REVIEW, or CLOSED.")
    if not isinstance(decisions, list):
        return _tracker_result(issues + ["decisions must be an array."], [], {})

    observed: dict[str, Mapping[str, Any]] = {}
    for index, row in enumerate(decisions):
        if not isinstance(row, Mapping):
            issues.append(f"decisions[{index}] must be an object.")
            continue
        decision_id = row.get("decision_id")
        if not isinstance(decision_id, str) or not decision_id:
            issues.append(f"decisions[{index}].decision_id must be a nonempty string.")
            continue
        if decision_id in observed:
            issues.append(f"Duplicate decision_id: {decision_id}.")
            continue
        observed[decision_id] = row
        if decision_id not in _DECISION_BY_ID:
            issues.append(f"Unknown decision_id: {decision_id}.")
            continue
        if row.get("topic") != _DECISION_BY_ID[decision_id]:
            issues.append(f"{decision_id}.topic does not match the registered question.")
        for field in ("owner_response", "supporting_artifact", "source_locator", "decision_date", "scientific_reviewer", "unresolved_rationale"):
            value = row.get(field)
            if value is not None and not isinstance(value, str):
                issues.append(f"{decision_id}.{field} must be a string or null.")
        raw_date = row.get("decision_date")
        if isinstance(raw_date, str):
            try:
                date.fromisoformat(raw_date)
            except ValueError:
                issues.append(f"{decision_id}.decision_date must be an ISO date.")
        status = row.get("approval_status")
        if not isinstance(status, str) or status not in _ALLOWED_APPROVALS:
            issues.append(f"{decision_id}.approval_status must be one of {sorted(_ALLOWED_APPROVALS)}.")
            continue
        if status == "APPROVED":
            missing = [
                field for field in ("owner_response", "supporting_artifact", "source_locator", "decision_date", "scientific_reviewer")
                if not isinstance(row.get(field), str) or not row[field].strip()
            ]
            if missing:
                issues.append(f"{decision_id} cannot be approved; missing: {', '.join(missing)}.")
        else:
            rationale = row.get("unresolved_rationale")
            if not isinstance(rationale, str) or not rationale.strip():
                issues.append(f"{decision_id} requires unresolved_rationale while approval_status is {status}.")
        if status == "REJECTED":
            missing_review_fields = [
                field for field in ("decision_date", "scientific_reviewer")
                if not isinstance(row.get(field), str) or not row[field].strip()
            ]
            if missing_review_fields:
                issues.append(f"{decision_id} cannot be rejected without: {', '.join(missing_review_fields)}.")

    missing_ids = sorted(set(_DECISION_BY_ID) - set(observed))
    if missing_ids:
        issues.append("Missing decision rows: " + ", ".join(missing_ids) + ".")
    statuses = Counter(
        row.get("approval_status") for key, row in observed.items()
        if key in _DECISION_BY_ID and isinstance(row.get("approval_status"), str) and row.get("approval_status") in _ALLOWED_APPROVALS
    )
    pending_ids = sorted(
        key for key, row in observed.items()
        if key in _DECISION_BY_ID and row.get("approval_status") != "APPROVED"
    )
    return _tracker_result(issues, pending_ids, dict(statuses), len(observed))


def _tracker_result(issues: list[str], pending_ids: list[str], statuses: Mapping[str, int], row_count: int = 0) -> dict[str, Any]:
    return {
        "validation_status": "FAIL" if issues else "PASS",
        "decision_count": row_count,
        "expected_decision_count": len(DECISIONS),
        "approval_counts": {status: int(statuses.get(status, 0)) for status in sorted(_ALLOWED_APPROVALS)},
        "pending_decision_ids": pending_ids,
        "complete": not issues and not pending_ids and row_count == len(DECISIONS),
        "issues": issues,
    }


def build_readiness_dashboard(
    tracker: Any,
    package_validation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Summarize the gate using PASS/FAIL/PENDING/BLOCKED states.

    Even a complete response tracker cannot independently approve deployment;
    package integrity and independent scientific/operational acceptance remain
    separate required gates.
    """
    tracking = validate_decision_tracker(tracker)
    if tracking["validation_status"] == "FAIL":
        owner_status = "FAIL"
    elif tracking["complete"]:
        owner_status = "PASS"
    else:
        owner_status = "PENDING"

    if package_validation is None:
        package_status = "BLOCKED"
        package_detail = "No supplied Stage A package is available for metadata/hash validation."
    elif package_validation.get("validation_status") == "FAIL":
        package_status = "FAIL"
        package_detail = "The supplied package failed metadata/hash validation."
    elif package_validation.get("validation_status") == "PASS":
        package_status = "PASS"
        package_detail = "Package metadata and bytes pass structural checks; scientific acceptance is separate."
    else:
        package_status = "BLOCKED"
        package_detail = "Package validation did not return a recognized result."

    if owner_status == "FAIL" or package_status == "FAIL":
        overall = "FAIL"
        detail = "Correct the tracker completeness or package integrity failures before further review."
    elif package_status == "BLOCKED":
        overall = "BLOCKED"
        detail = "A complete supplied package and owner decisions are required before deployment review."
    else:
        overall = "PENDING"
        detail = "Independent target/scientific review, owner approval, and model-owner operational acceptance remain required."

    return {
        "dashboard_version": "1.0.0",
        "overall_status": overall,
        "deployment_readiness": overall,
        "inference_authorized": False,
        "gates": [
            {"gate": "owner_decision_tracker", "status": owner_status, "detail": f"{tracking['approval_counts']['APPROVED']}/15 decisions approved; {len(tracking['pending_decision_ids'])} remain open."},
            {"gate": "package_integrity", "status": package_status, "detail": package_detail},
            {"gate": "independent_scientific_and_operational_acceptance", "status": "PENDING", "detail": "This status requires actual independent review and cannot be inferred from metadata validation."},
            {"gate": "deployment_readiness", "status": overall, "detail": detail},
        ],
        "tracker_validation": tracking,
    }


def render_readiness_markdown(dashboard: Mapping[str, Any]) -> str:
    """Render a compact, reproducible dashboard for reports and handoffs."""
    lines = [
        "# Stage A deployment readiness dashboard",
        "",
        f"**Overall: {dashboard.get('overall_status', 'FAIL')}**  ",
        "**Inference authorized: NO**",
        "",
        "| Gate | Status | Detail |",
        "|---|---|---|",
    ]
    for gate in dashboard.get("gates", []):
        detail = str(gate.get("detail", "")).replace("|", "\\|")
        label = str(gate.get("gate", "")).replace("_", " ")
        lines.append(f"| {label} | **{gate.get('status', '')}** | {detail} |")
    tracking = dashboard.get("tracker_validation", {})
    counts = tracking.get("approval_counts", {})
    lines.extend([
        "",
        f"Owner responses: {counts.get('APPROVED', 0)} approved, {counts.get('PENDING', 0)} pending, {counts.get('REJECTED', 0)} rejected.",
        "",
        "This dashboard checks record completeness and package structure only. It does not establish scientific validity, authorize model use, or substitute for independent review.",
        "",
        "Reproduce with `python stageC/scripts/demo_phase2_owner_decisions.py --write-report`.",
        "",
    ])
    return "\n".join(lines)
