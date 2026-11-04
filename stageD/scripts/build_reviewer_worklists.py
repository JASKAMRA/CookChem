"""Verify the versioned Stage D index and emit unassigned worklists."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGE_D = ROOT / "stageD"
V11 = STAGE_D / "reports/closure/qualified_review_readiness_register_v1.1.0.json"
V12 = STAGE_D / "reports/closure/qualified_review_readiness_register_v1.2.0.json"
FIELDS = [
    "review_id", "review_type", "evidence_id", "compound_id", "study_id", "source_locator",
    "source_access_level", "release_id", "source_sha256", "schema_reference", "qualification_required",
    "status", "assigned_reviewer_issuer", "assigned_reviewer_subject_id", "review_date", "decision",
    "rationale", "evidence_references", "signoff_reference", "unresolved_questions", "missing_metadata_fields",
]


def validate_registers(v11: dict, v12: dict, schemas_root: Path) -> dict[str, int]:
    if v11.get("register_version") != "1.1.0" or v12.get("register_version") != "1.2.0":
        raise ValueError("Unsupported readiness-register version")
    expected_supersedes = hashlib.sha256((STAGE_D / "reports/closure/qualified_review_readiness_register_v1.1.0.json").read_bytes()).hexdigest()
    if v12.get("supersedes") != {"version": "1.1.0", "sha256": expected_supersedes}:
        raise ValueError("v1.2.0 does not correctly identify its v1.1.0 predecessor")
    left = {row["review_id"]: row for row in v11.get("reviews", [])}
    right = {row["review_id"]: row for row in v12.get("reviews", [])}
    if len(left) != len(v11.get("reviews", [])) or len(right) != len(v12.get("reviews", [])):
        raise ValueError("Duplicate stable review ID")
    if set(left) != set(right) or len(right) != 342:
        raise ValueError("The v1.1.0 and v1.2.0 review IDs do not map 1:1 across all 342 records")
    counts = {"evidence": 0, "mechanism": 0}
    for review_id, row in right.items():
        prior = left[review_id]
        for key in ("review_type", "identity_and_evidence", "evidence_schema_reference", "review_status",
                    "reviewer_requirement", "reviewer_identity", "reviewer_rationale", "decision", "approval_evidence"):
            if row.get(key) != prior.get(key):
                raise ValueError(f"v1.2.0 changed protected readiness field {key} for {review_id}")
        if row.get("review_status") != "PENDING_HUMAN_REVIEW" or row.get("decision") is not None or row.get("approval_evidence") is not None:
            raise ValueError(f"Review status/decision is not pending and blank for {review_id}")
        ref = row.get("identity_and_evidence", {})
        required = ("evidence_id", "compound_id", "study_id", "source_locator", "release_id", "source_sha256")
        if any(not isinstance(ref.get(field), str) or not ref[field].strip() for field in required):
            raise ValueError(f"Incomplete stable evidence reference for {review_id}")
        if len(ref["source_sha256"]) != 64 or any(c not in "0123456789abcdef" for c in ref["source_sha256"]):
            raise ValueError(f"Invalid source SHA-256 for {review_id}")
        schema = row.get("evidence_schema_reference", "")
        expected_schema = ("stageD/schemas/evidence_review_queue.schema.json" if row["review_type"] == "evidence"
                           else "stageD/schemas/mechanism_registry.schema.json")
        if schema != expected_schema or not (ROOT / schema).is_file():
            raise ValueError(f"Missing/unauthorized schema mapping for {review_id}")
        counts[row["review_type"]] += 1
    if counts != {"evidence": 317, "mechanism": 25}:
        raise ValueError(f"Unexpected review-type mapping counts: {counts}")
    metadata = v12.get("metadata_followup_summary", {})
    if metadata.get("identifiers_added") != 0 or metadata.get("scientific_or_review_status_changes") != 0:
        raise ValueError("Citation metadata follow-up changed identifiers or review/science status")
    unresolved = [item for row in right.values() for item in row.get("unresolved_metadata", [])]
    unresolved_counts = {field: sum(item.get("field") == field for item in unresolved) for field in ("DOI", "PMID")}
    if (len(unresolved) != 9 or unresolved_counts != {"DOI": 5, "PMID": 4}
            or any(item.get("status") != "UNRESOLVED" or item.get("candidate_value") is not None for item in unresolved)):
        raise ValueError("Citation metadata gaps are not explicitly retained as unresolved")
    return counts


def worklist_rows(register: dict, review_type: str) -> list[dict[str, str]]:
    rows = []
    for row in register["reviews"]:
        if row["review_type"] != review_type:
            continue
        ref = row["identity_and_evidence"]
        rows.append({
            "review_id": row["review_id"], "review_type": review_type,
            "evidence_id": ref["evidence_id"], "compound_id": ref["compound_id"],
            "study_id": ref["study_id"], "source_locator": ref["source_locator"],
            "source_access_level": ref.get("source_access_level", ""),
            "release_id": ref["release_id"], "source_sha256": ref["source_sha256"],
            "schema_reference": row["evidence_schema_reference"],
            "qualification_required": f"qualified_{review_type}_reviewer",
            "status": "pending", "assigned_reviewer_issuer": "", "assigned_reviewer_subject_id": "",
            "review_date": "", "decision": "", "rationale": "",
            "evidence_references": "", "signoff_reference": "",
            "unresolved_questions": json.dumps(row.get("unresolved_questions", []), ensure_ascii=False),
            "missing_metadata_fields": ",".join(row.get("missing_metadata_fields", [])),
        })
    return sorted(rows, key=lambda item: item["review_id"])


def write_worklist(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=STAGE_D / "reports/closure/worklists_v1.0.0")
    args = parser.parse_args()
    v11 = json.loads(V11.read_text(encoding="utf-8"))
    v12 = json.loads(V12.read_text(encoding="utf-8"))
    counts = validate_registers(v11, v12, STAGE_D / "schemas")
    for review_type, filename in (("evidence", "evidence_unassigned.csv"), ("mechanism", "mechanism_unassigned.csv")):
        write_worklist(args.output_dir / filename, worklist_rows(v12, review_type))
    print(json.dumps({"register_map": counts, "pending_total": sum(counts.values()), "assigned_total": 0,
                      "decisions_total": 0, "v11_sha256": hashlib.sha256(V11.read_bytes()).hexdigest(),
                      "v12_sha256": hashlib.sha256(V12.read_bytes()).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
