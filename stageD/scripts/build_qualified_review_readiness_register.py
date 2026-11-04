"""Build a minimal, pending-only reviewer index from Stage D artifacts.

The index intentionally excludes source payloads and records only identifiers,
provenance references, review state, and fields/questions a reviewer must resolve.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
STAGE_D = ROOT / "stageD"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_readiness_register(review_register: dict[str, Any], queue: dict[str, Any], *,
                             review_register_sha256: str, queue_sha256: str) -> dict[str, Any]:
    queue_by_id = {row["review_id"]: row for row in queue["records"]}
    reviews: list[dict[str, Any]] = []
    for row in review_register["reviews"]:
        kind = row["review_type"]
        ref = row["source_reference"]
        if kind == "evidence":
            queued = queue_by_id.get(row["register_id"])
            if queued is None:
                raise ValueError(f"Stage D queue is missing review ID {row['register_id']}")
            questions = [f"Supply or verify {field}." for field in row.get("missing_evidence_fields", [])]
            questions.extend([
                "Confirm the source locator and that the cited evidence matches this record.",
                "Assess compound identity and study context; record rationale and uncertainty.",
            ])
            identity = queued.get("source_record", {}).get("Identity_Status", "")
            identity_review = "PENDING_QUALIFIED_REVIEW"
            reviewer_requirement = "Qualified evidence reviewer; authenticated identity and source-located rationale required."
            schema_reference = "stageD/schemas/evidence_review_queue.schema.json"
            context = {
                "identity_status_as_recorded": identity,
                "identity_review_status": identity_review,
                "evidence_id": ref.get("evidence_id"),
                "compound_id": ref.get("compound_id"),
                "study_id": ref.get("study_id"),
                "source_locator": ref.get("source_locator"),
                "release_id": ref.get("release_id"),
                "source_sha256": ref.get("source_sha256"),
            }
            open_fields = list(row.get("missing_evidence_fields", []))
        elif kind == "mechanism":
            questions = [
                f"Review criterion: {item.get('criterion', 'unspecified')}"
                for item in row.get("review_worksheet", [])
                if item.get("reviewer_decision") is None
            ]
            questions.extend([
                "Verify source access level, locator, target/analyte identity, and assay context.",
                "Record supporting and contradictory evidence, uncertainty, and rationale.",
            ])
            reviewer_requirement = "Qualified mechanism reviewer; source-located independent rationale required."
            schema_reference = "stageD/schemas/mechanism_registry.schema.json"
            context = {
                "evidence_id": ref.get("evidence_id"),
                "compound_id": ref.get("compound_id"),
                "study_id": ref.get("study_id"),
                "source_locator": ref.get("source_locator"),
                "source_access_level": ref.get("access_level"),
                "release_id": ref.get("release_id"),
                "source_sha256": ref.get("source_sha256"),
                "identity_review_status": "PENDING_QUALIFIED_REVIEW",
            }
            open_fields = []
        else:
            raise ValueError(f"Unsupported review type: {kind}")
        reviews.append({
            "review_type": kind,
            "review_id": row["register_id"],
            "identity_and_evidence": context,
            "evidence_schema_reference": schema_reference,
            "review_status": "PENDING_HUMAN_REVIEW",
            "reviewer_requirement": reviewer_requirement,
            "unresolved_questions": questions,
            "missing_metadata_fields": open_fields,
            "reviewer_identity": None,
            "reviewer_rationale": None,
            "decision": None,
            "approval_evidence": None,
        })

    evidence = [r for r in reviews if r["review_type"] == "evidence"]
    mechanisms = [r for r in reviews if r["review_type"] == "mechanism"]
    evidence_ids = [r["identity_and_evidence"]["evidence_id"] for r in evidence]
    evidence_id_counts = Counter(evidence_ids)
    missing_source = sum(not r["identity_and_evidence"].get("source_locator") for r in reviews)
    missing_evidence_ids = sum(not x for x in evidence_ids)
    missing_identity = sum(not r["identity_and_evidence"].get("identity_status_as_recorded") for r in evidence)
    missing_metadata = Counter(field for r in evidence for field in r["missing_metadata_fields"])
    invalid = []
    for row in reviews:
        if (row["review_status"] != "PENDING_HUMAN_REVIEW" or row["decision"] is not None
                or row["approval_evidence"] is not None or row["reviewer_identity"] is not None):
            invalid.append(row["review_id"])

    return {
        "register_version": "1.1.0",
        "purpose": "Minimal qualified-review readiness index; no scientific decisions or approvals are made.",
        "inputs": {
            "stage_d_review_register": "stageD/reports/closure/human_review_register_v1.0.0.json",
            "stage_d_review_register_sha256": review_register_sha256,
            "stage_d_evidence_queue": "stageD/data/evidence_review_queue.json",
            "stage_d_evidence_queue_sha256": queue_sha256,
        },
        "schemas": {
            "evidence_records": "stageD/schemas/evidence_review_queue.schema.json",
            "mechanism_candidates": "stageD/schemas/mechanism_registry.schema.json",
        },
        "summary": {
            "evidence_records": len(evidence),
            "mechanism_candidates": len(mechanisms),
            "pending_reviews": sum(r["review_status"] == "PENDING_HUMAN_REVIEW" for r in reviews),
            "evidence_ids_missing": missing_evidence_ids,
            "source_locators_missing": missing_source,
            "identity_status_missing": missing_identity,
            "evidence_id_duplicate_groups": sum(n > 1 for n in evidence_id_counts.values()),
            "evidence_id_duplicate_rows": sum(n for n in evidence_id_counts.values() if n > 1),
            "evidence_missing_metadata_fields": dict(sorted(missing_metadata.items())),
            "records_with_invalid_or_prefilled_decisions": len(invalid),
            "decisions_or_approvals_recorded": 0,
        },
        "reviews": reviews,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=STAGE_D / "reports/closure/qualified_review_readiness_register_v1.1.0.json")
    args = parser.parse_args()
    register_path = STAGE_D / "reports/closure/human_review_register_v1.0.0.json"
    queue_path = STAGE_D / "data/evidence_review_queue.json"
    review_register = json.loads(register_path.read_text(encoding="utf-8"))
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    result = build_readiness_register(review_register, queue,
                                     review_register_sha256=sha256(register_path),
                                     queue_sha256=sha256(queue_path))
    payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)
    print(json.dumps(result["summary"], sort_keys=True))
    print("register_sha256=" + hashlib.sha256(payload.encode("utf-8")).hexdigest())


if __name__ == "__main__":
    main()
