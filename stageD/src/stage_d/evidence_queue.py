"""Reproducible, non-adjudicating review queue for the pinned Stage B source."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .contracts import ContractError, normalize_stage_b_record

SOURCE_RELEASE = "StageB_V20_20261103"
SOURCE_RELATIVE_PATH = "stageB/release/StageB_V20_20261103/data/interaction_evidence.csv"
SOURCE_SHA256 = "5c095c6ee22d8d998888d3d47bc4ae2fcabf17faf4df0bee8aad7d6bb9af1cec"
SOURCE_ROW_COUNT = 317
QUEUE_SCHEMA_VERSION = "1.1.0"
_MACHINE_STATES = {
    "NOT_REVIEWED", "IDENTITY_PENDING", "CONTEXT_PENDING", "CONFLICT_REVIEW",
    "READY_FOR_EXPERT_REVIEW",
}
_HUMAN_STATES = {
    "NOT_REVIEWED", "SOURCE_VERIFIED", "IDENTITY_PENDING", "CONTEXT_PENDING",
    "CONFLICT_REVIEW", "READY_FOR_EXPERT_REVIEW", "EXPERT_ACCEPTED", "EXPERT_REJECTED",
}
_CORE_SOURCE_FIELDS = (
    "Evidence_ID", "Compound", "Compound_ID", "Drug", "Evidence_Type", "Mechanism",
    "Study_ID", "Study_Design", "Source_Title", "Outcome", "Source_URL", "Source_Locator",
)
_GROUP_DIMENSIONS = (
    "evidence_category", "compound", "drug_name", "source_and_study", "study",
    "source_reported_target_context", "conflict_group", "exact_duplicate_candidate",
)


class QueueValidationError(ValueError):
    """A queue breaks provenance, coverage, or reviewer-state invariants."""


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _group_id(dimension: str, key: Any) -> str:
    digest = hashlib.sha256(_canonical(key).encode("utf-8")).hexdigest()[:12].upper()
    return f"G-{dimension.upper()}-{digest}"


def stable_review_id(evidence_id: str, source_sha256: str = SOURCE_SHA256) -> str:
    """Stable opaque queue ID scoped to the immutable source digest."""
    value = hashlib.sha256(f"{source_sha256}:{evidence_id}".encode("utf-8")).hexdigest()[:20].upper()
    return f"RV-{value}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_source(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise QueueValidationError(f"Pinned Stage B source is missing: {path}")
    digest = _sha256(path)
    if digest != SOURCE_SHA256:
        raise QueueValidationError("Pinned Stage B source SHA-256 does not match the expected immutable input")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or "Evidence_ID" not in reader.fieldnames:
            raise QueueValidationError("Pinned Stage B source is missing Evidence_ID header")
        rows = list(reader)
    if len(rows) != SOURCE_ROW_COUNT:
        raise QueueValidationError(f"Pinned Stage B source has {len(rows)} rows; expected {SOURCE_ROW_COUNT}")
    identifiers = [row.get("Evidence_ID", "") for row in rows]
    if any(not item for item in identifiers) or len(identifiers) != len(set(identifiers)):
        raise QueueValidationError("Stage B Evidence_ID values must be present and unique")
    return rows


def _key_fields(row: dict[str, str]) -> dict[str, Any]:
    """Build exact source-label grouping keys; these are not identity claims."""
    return {
        "evidence_category": row.get("Evidence_Type", ""),
        "compound": row.get("Compound_ID", ""),
        "drug_name": row.get("Drug", ""),
        "source_and_study": [row.get("Study_ID", ""), row.get("PMID", ""), row.get("DOI", ""), row.get("Source_Title", "")],
        "study": row.get("Study_ID", ""),
        "source_reported_target_context": [row.get("Affected_Entity", ""), row.get("Mechanism", "")],
        "conflict_group": row.get("Conflict_Group", ""),
        "exact_duplicate_candidate": {
            key: value for key, value in row.items() if key != "Evidence_ID"
        },
    }


def _triage(row: dict[str, str], missing: list[str], has_conflict: bool) -> tuple[str, list[str]]:
    if has_conflict:
        return "CONFLICT_REVIEW", ["EXPLICIT_SOURCE_CONFLICT_GROUP"]
    # The narrow exact label is used as a routing rule only. No identity is
    # independently verified or accepted by this queue builder.
    if row.get("Identity_Status", "") != "verified_exact":
        return "IDENTITY_PENDING", ["SOURCE_IDENTITY_LABEL_REQUIRES_REVIEW"]
    if missing:
        return "CONTEXT_PENDING", ["CORE_SOURCE_CONTEXT_FIELDS_MISSING"]
    return "READY_FOR_EXPERT_REVIEW", ["CORE_SOURCE_FIELDS_PRESENT_SOURCE_NOT_VERIFIED"]


def build_queue_from_rows(rows: list[dict[str, str]], *, source_path: str = SOURCE_RELATIVE_PATH,
                          source_sha256: str = SOURCE_SHA256,
                          source_release: str = SOURCE_RELEASE) -> dict[str, Any]:
    """Build deterministic queue content from rows already read from the pinned source."""
    if len(rows) != SOURCE_ROW_COUNT:
        raise QueueValidationError(f"Expected {SOURCE_ROW_COUNT} source rows; received {len(rows)}")
    ids = [str(row.get("Evidence_ID", "")) for row in rows]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        raise QueueValidationError("Evidence_ID values must be nonempty and unique")
    if source_sha256 != SOURCE_SHA256:
        raise QueueValidationError("Queue must remain pinned to the expected Stage B source hash")

    grouped: dict[str, dict[str, list[str]]] = {dimension: defaultdict(list) for dimension in _GROUP_DIMENSIONS}
    per_record: list[dict[str, Any]] = []
    for offset, raw_row in enumerate(rows):
        row = {str(key): str(value or "") for key, value in raw_row.items()}
        evidence_id = row["Evidence_ID"]
        normalized = normalize_stage_b_record(row, stage_b_release=source_release,
                                              stage_b_manifest_sha256=source_sha256)
        missing = sorted(field for field in _CORE_SOURCE_FIELDS if not row.get(field, "").strip())
        keys = _key_fields(row)
        record_groups = {}
        for dimension, key in keys.items():
            # Empty conflict keys do not create a single artificial group.
            if dimension == "conflict_group" and not key:
                continue
            record_groups[dimension] = _group_id(dimension, key)
            grouped[dimension][record_groups[dimension]].append(evidence_id)
        state, reason_codes = _triage(row, missing, bool(row.get("Conflict_Group", "").strip()))
        per_record.append({
            "queue_record_id": f"Q-{evidence_id}",
            "review_id": stable_review_id(evidence_id, source_sha256),
            "source_reference": {
                "release_id": source_release, "source_path": source_path,
                "source_sha256": source_sha256, "csv_row_number": offset + 2,
                "evidence_id": evidence_id, "compound_id": row["Compound_ID"],
            },
            "source_record": row,
            "machine_assessment": {
                "triage_state": state,
                "triage_reason_codes": reason_codes,
                "source_verification": "NOT_PERFORMED",
                "identity_source_label": row.get("Identity_Status", ""),
                "normalized_study_category": normalized["study_type"]["normalized_category"],
                "finding_polarity": normalized["finding"]["polarity"],
                "finding_normalization_rule": normalized["finding"]["normalization_rule"],
                "explicit_conflict_group": row.get("Conflict_Group", "") or None,
                "missing_core_source_fields": missing,
            },
            "groups": record_groups,
            "human_review": {
                "state": "NOT_REVIEWED", "reviewer_identity": None,
                "reviewed_at": None, "rationale": None, "cited_source_location": None,
                "negative_evidence_assessment": "NOT_ASSESSED",
            },
        })

    group_index: dict[str, list[dict[str, Any]]] = {}
    for dimension in _GROUP_DIMENSIONS:
        group_index[dimension] = []
        for group_id, member_ids in sorted(grouped[dimension].items()):
            if dimension == "exact_duplicate_candidate" and len(member_ids) < 2:
                continue
            # One conflict group or exact duplicate group should have multiple rows.
            group_index[dimension].append({
                "group_id": group_id,
                "member_evidence_ids": sorted(member_ids),
                "member_count": len(member_ids),
                "interpretation": (
                    "Exact source-field grouping candidate; review manually before treating as duplicate."
                    if dimension == "exact_duplicate_candidate" else
                    "Grouping uses preserved source labels/text only; it does not establish identity, mechanism, or conflict."
                ),
            })
    duplicate_group_ids = {group["group_id"] for group in group_index["exact_duplicate_candidate"]}
    for record in per_record:
        candidate_id = record["groups"].get("exact_duplicate_candidate")
        if candidate_id not in duplicate_group_ids:
            record["groups"].pop("exact_duplicate_candidate", None)

    machine_counts = Counter(record["machine_assessment"]["triage_state"] for record in per_record)
    human_counts = Counter(record["human_review"]["state"] for record in per_record)
    category_counts = Counter(record["machine_assessment"]["normalized_study_category"] for record in per_record)
    polarity_counts = Counter(record["machine_assessment"]["finding_polarity"] for record in per_record)
    identity_counts = Counter(record["source_record"].get("Identity_Status", "") or "(empty)" for record in per_record)
    missing_counts = Counter(field for record in per_record for field in record["machine_assessment"]["missing_core_source_fields"])
    conflict_records = sum(bool(row.get("Conflict_Group", "").strip()) for row in rows)
    duplicate_candidates = group_index["exact_duplicate_candidate"]
    queue = {
        "schema_version": QUEUE_SCHEMA_VERSION,
        "queue_id": "StageD-EvidenceReview-StageB_V20_20261103-v1.1.0",
        "source": {
            "release_id": source_release, "relative_path": source_path,
            "sha256": source_sha256, "source_row_count": len(rows),
            "records_preserved": len(per_record),
        },
        "purpose_and_limits": {
            "purpose": "Record-level reviewer work queue and completeness inventory for an immutable Stage B evidence source.",
            "machine_assessment_is_adjudication": False,
            "source_verification_performed": False,
            "expert_decisions_created": False,
            "negative_evidence_inferred": False,
            "grouping_note": "Groups are deterministic source-label or exact-text groupings. They are candidates for review, not scientific adjudications.",
        },
        "statistics": {
            "record_count": len(per_record),
            "machine_triage_counts": dict(sorted(machine_counts.items())),
            "human_review_state_counts": dict(sorted(human_counts.items())),
            "study_category_counts": dict(sorted(category_counts.items())),
            "finding_polarity_counts": dict(sorted(polarity_counts.items())),
            "identity_source_label_counts": dict(sorted(identity_counts.items())),
            "missing_core_field_counts": dict(sorted(missing_counts.items())),
            "explicit_conflict_record_count": conflict_records,
            "explicit_conflict_group_count": len(group_index["conflict_group"]),
            "exact_duplicate_candidate_group_count": len(duplicate_candidates),
            "exact_duplicate_candidate_record_count": sum(row["member_count"] for row in duplicate_candidates),
            "source_verified_count": 0,
            "expert_accepted_count": 0,
            "expert_rejected_count": 0,
        },
        "group_index": group_index,
        "records": per_record,
    }
    validate_review_queue(queue)
    return queue


def validate_review_queue(queue: dict[str, Any]) -> None:
    """Enforce source coverage, traceability and human/machine separation."""
    if not isinstance(queue, dict) or queue.get("schema_version") != QUEUE_SCHEMA_VERSION:
        raise QueueValidationError("Unsupported evidence queue schema version")
    source = queue.get("source")
    records = queue.get("records")
    if not isinstance(source, dict) or not isinstance(records, list):
        raise QueueValidationError("Queue source and records are required")
    if source.get("sha256") != SOURCE_SHA256 or source.get("release_id") != SOURCE_RELEASE:
        raise QueueValidationError("Queue source release/hash is not the pinned immutable source")
    if source.get("source_row_count") != SOURCE_ROW_COUNT or len(records) != SOURCE_ROW_COUNT:
        raise QueueValidationError("Queue must preserve every one of the 317 pinned source rows")
    evidence_ids = [row.get("source_reference", {}).get("evidence_id") for row in records]
    if len(evidence_ids) != len(set(evidence_ids)) or any(not item for item in evidence_ids):
        raise QueueValidationError("Evidence_ID values must be present and unique")
    observed_ids = set(evidence_ids)
    for record in records:
        reference = record.get("source_reference", {})
        raw = record.get("source_record", {})
        machine = record.get("machine_assessment", {})
        human = record.get("human_review", {})
        evidence_id = reference.get("evidence_id")
        if reference.get("source_sha256") != SOURCE_SHA256 or raw.get("Evidence_ID") != evidence_id:
            raise QueueValidationError(f"Source provenance is inconsistent for {evidence_id}")
        if reference.get("compound_id") != raw.get("Compound_ID"):
            raise QueueValidationError(f"Compound_ID source reference is inconsistent for {evidence_id}")
        if record.get("review_id") != stable_review_id(evidence_id, SOURCE_SHA256):
            raise QueueValidationError(f"Stable review ID is inconsistent for {evidence_id}")
        if set(raw) != set(rows_header_fields(records)):
            raise QueueValidationError("Source row fields are not structurally consistent across the queue")
        try:
            normalized = normalize_stage_b_record(raw, stage_b_release=SOURCE_RELEASE,
                                                  stage_b_manifest_sha256=SOURCE_SHA256)
        except ContractError as exc:
            raise QueueValidationError(f"Cannot normalize preserved source row {evidence_id}: {exc}") from None
        if machine.get("finding_polarity") != normalized["finding"]["polarity"]:
            raise QueueValidationError(f"Finding polarity no longer matches preserved source for {evidence_id}")
        if machine.get("normalized_study_category") != normalized["study_type"]["normalized_category"]:
            raise QueueValidationError(f"Study category no longer matches preserved source for {evidence_id}")
        if machine.get("source_verification") != "NOT_PERFORMED":
            raise QueueValidationError("Automated queue generation cannot claim source verification")
        triage = machine.get("triage_state")
        if triage not in _MACHINE_STATES:
            raise QueueValidationError(f"Invalid machine triage state for {evidence_id}")
        if human.get("state") not in _HUMAN_STATES:
            raise QueueValidationError(f"Invalid human review state for {evidence_id}")
        if human.get("state") != "NOT_REVIEWED":
            required = ("reviewer_identity", "reviewed_at", "rationale", "cited_source_location")
            if any(not str(human.get(key) or "").strip() for key in required):
                raise QueueValidationError(f"Human state {human['state']} requires reviewer, date, rationale, and source location")
        negative_status = human.get("negative_evidence_assessment")
        if human.get("state") == "NOT_REVIEWED" and negative_status != "NOT_ASSESSED":
            raise QueueValidationError("Unreviewed records cannot receive a negative-evidence assessment")
        if negative_status == "EXPLICIT_NEGATIVE_REVIEWED" and normalized["finding"]["polarity"] != "negative":
            raise QueueValidationError("Null, conflicting, unclear, or positive findings cannot be labeled explicit negative evidence")
        if human.get("state") in {"EXPERT_ACCEPTED", "EXPERT_REJECTED"} and not human.get("reviewer_identity"):
            raise QueueValidationError("Expert decisions cannot be set by the machine queue")
        if human.get("state") != "NOT_REVIEWED":
            raise QueueValidationError("Generated queue records remain NOT_REVIEWED; record human actions in the append-only audit log")
        groups = record.get("groups")
        if not isinstance(groups, dict):
            raise QueueValidationError(f"Group references are missing for {evidence_id}")
        if bool(raw.get("Conflict_Group")) != ("conflict_group" in groups):
            raise QueueValidationError(f"Explicit conflict group reference was lost for {evidence_id}")
    if queue.get("purpose_and_limits", {}).get("expert_decisions_created") is not False:
        raise QueueValidationError("Queue cannot claim that expert decisions were created")
    if queue.get("purpose_and_limits", {}).get("negative_evidence_inferred") is not False:
        raise QueueValidationError("Queue cannot infer negative evidence")
    records_by_id = {record["source_reference"]["evidence_id"]: record for record in records}
    for dimension, groups in queue.get("group_index", {}).items():
        for group in groups:
            members = group.get("member_evidence_ids", [])
            if group.get("member_count") != len(members) or not set(members).issubset(observed_ids):
                raise QueueValidationError(f"Group index contains invalid member references in {dimension}")
            for member in members:
                if records_by_id[member].get("groups", {}).get(dimension) != group.get("group_id"):
                    raise QueueValidationError(f"Group membership is inconsistent for {member} in {dimension}")
    stats = queue.get("statistics", {})
    if stats.get("record_count") != len(records) or sum(stats.get("human_review_state_counts", {}).values()) != len(records):
        raise QueueValidationError("Queue statistics do not reconcile with the record list")
    actual_human_counts = Counter(record["human_review"]["state"] for record in records)
    actual_machine_counts = Counter(record["machine_assessment"]["triage_state"] for record in records)
    if stats.get("machine_triage_counts") != dict(sorted(actual_machine_counts.items())):
        raise QueueValidationError("Machine triage statistics do not match queue records")
    if stats.get("human_review_state_counts") != dict(sorted(actual_human_counts.items())):
        raise QueueValidationError("Human review-state statistics do not match the queue records")
    if stats.get("source_verified_count") != actual_human_counts.get("SOURCE_VERIFIED", 0):
        raise QueueValidationError("Source verification statistics do not match human review states")
    if stats.get("expert_accepted_count") != actual_human_counts.get("EXPERT_ACCEPTED", 0):
        raise QueueValidationError("Expert acceptance statistics do not match human review states")
    if stats.get("expert_rejected_count") != actual_human_counts.get("EXPERT_REJECTED", 0):
        raise QueueValidationError("Expert rejection statistics do not match human review states")


def rows_header_fields(records: list[dict[str, Any]]) -> set[str]:
    return set(records[0].get("source_record", {})) if records else set()


def build_review_queue(source_path: Path | None = None) -> dict[str, Any]:
    root = project_root()
    path = source_path or (root / SOURCE_RELATIVE_PATH)
    rows = _read_source(path)
    return build_queue_from_rows(rows)


def write_review_queue(path: Path | None = None) -> dict[str, Any]:
    output = path or (project_root() / "stageD" / "data" / "evidence_review_queue.json")
    queue = build_review_queue()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return queue


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the pinned Stage B evidence review queue")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    queue = write_review_queue(args.output)
    print(json.dumps(queue["statistics"], sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
