"""Build a deterministic human-review register from Stage D snapshots only."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
STAGE_D = ROOT / "stageD"
sys.path.insert(0, str(STAGE_D / "src"))

from stage_d.evidence_queue import validate_review_queue  # noqa: E402
from stage_d.mechanisms import build_mechanism_review_packets  # noqa: E402


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_register(queue: dict, registry: dict, *, queue_digest: str, registry_digest: str) -> dict:
    validate_review_queue(queue)
    packets = build_mechanism_review_packets(registry)
    source_ref = queue["source"]
    evidence_reviews = []
    for record in queue["records"]:
        raw = record["source_record"]
        machine = record["machine_assessment"]
        missing = list(machine["missing_core_source_fields"])
        for field in ("Source_Title", "PMID", "DOI", "Source_URL", "Source_Locator"):
            if not str(raw.get(field, "")).strip() and field not in missing:
                missing.append(field)
        evidence_reviews.append({
            "review_type": "evidence",
            "register_id": record["review_id"],
            "status": "PENDING_HUMAN_REVIEW",
            "source_reference": {
                "release_id": source_ref["release_id"],
                "source_sha256": source_ref["sha256"],
                "evidence_id": record["source_reference"]["evidence_id"],
                "compound_id": record["source_reference"]["compound_id"],
                "study_id": raw.get("Study_ID", ""),
                "source_title": raw.get("Source_Title", ""),
                "doi": raw.get("DOI", ""),
                "pmid": raw.get("PMID", ""),
                "source_url": raw.get("Source_URL", ""),
                "source_locator": raw.get("Source_Locator", ""),
            },
            "evidence_context": {
                "evidence_type": raw.get("Evidence_Type", ""),
                "study_design": raw.get("Study_Design", ""),
                "population_or_model": raw.get("Population", ""),
                "preparation_context": raw.get("Preparation", ""),
                "machine_polarity_triage": machine.get("finding_polarity"),
            },
            "missing_evidence_fields": sorted(missing),
            "conflict_group": raw.get("Conflict_Group", ""),
            "supporting_findings": [],
            "contradicting_findings": [],
            "limitations_and_uncertainty": [],
            "exposure_comparability_status": "NOT_ASSESSED",
            "reviewer_rationale": None,
            "decision": None,
            "authorization_evidence": None,
        })
    mechanism_reviews = []
    for packet in packets:
        reference = packet["candidate_reference"]
        mechanism_reviews.append({
            "review_type": "mechanism",
            "register_id": reference["mechanism_record_id"],
            "status": packet["review_state"],
            "source_reference": {
                "release_id": reference["release_id"],
                "source_sha256": reference["source_file_sha256"],
                "evidence_id": reference["evidence_id"],
                "compound_id": reference["compound_id"],
                "study_id": reference.get("study_id", ""),
                **packet["primary_source"],
            },
            "machine_candidate": packet["machine_candidate"],
            "source_record": packet["source_record"],
            "supporting_findings": [],
            "contradicting_findings": [],
            "limitations_and_uncertainty": [],
            "review_worksheet": packet["review_worksheet"],
            "reviewer_rationale": None,
            "decision_options": ["EXPERT_ACCEPTED", "EXPERT_REJECTED"],
            "decision": None,
            "authorization_evidence": None,
        })
    return {
        "schema_version": "1.0.0",
        "purpose": "Human-review register; source evidence is preserved and no decisions are prefilled.",
        "inputs": {
            "stage_d_queue_sha256": queue_digest,
            "queue_source_release": source_ref["release_id"],
            "queue_source_sha256": source_ref["sha256"],
            "stage_d_mechanism_registry_sha256": registry_digest,
            "mechanism_source_release": registry["release_id"],
            "mechanism_source_sha256": registry["source_file_sha256"],
        },
        "summary": {
            "evidence_records_pending": len(evidence_reviews),
            "mechanism_candidates_pending": len(mechanism_reviews),
            "evidence_missing_source_field_records": sum(bool(row["missing_evidence_fields"]) for row in evidence_reviews),
            "evidence_records_with_conflict_group": sum(bool(row["conflict_group"]) for row in evidence_reviews),
            "mechanism_study_count": len({row["source_reference"]["study_id"] for row in mechanism_reviews if row["source_reference"]["study_id"]}),
            "decisions_created": 0,
        },
        "reviews": evidence_reviews + mechanism_reviews,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=STAGE_D / "reports/closure/human_review_register_v1.0.0.json")
    args = parser.parse_args()
    queue_path = STAGE_D / "data/evidence_review_queue.json"
    registry_path = STAGE_D / "data/mechanism_evidence_registry.json"
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    register = build_register(queue, registry, queue_digest=_digest(queue_path), registry_digest=_digest(registry_path))
    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(register, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)
    with output.with_suffix(output.suffix + ".sha256").open("x", encoding="ascii") as stream:
        stream.write(hashlib.sha256(payload.encode("utf-8")).hexdigest() + "  " + output.name + "\n")
    print(json.dumps(register["summary"], sort_keys=True))
    print("register_sha256=" + hashlib.sha256(payload.encode("utf-8")).hexdigest())


if __name__ == "__main__":
    main()
