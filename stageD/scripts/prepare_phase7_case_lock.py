"""Prepare (but do not approve) an exact-byte Phase 7 case-set lock candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
STAGE_D = ROOT / "stageD"
sys.path.insert(0, str(STAGE_D / "src"))
from stage_d.schema_validation import validate_draft_2020_12  # noqa: E402

PROTOCOL_VERSION = "1.0.0"
SCHEMA_PATH = STAGE_D / "schemas/risk_interpretation.schema.json"


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_nonstandard_constant(value: str) -> None:
    raise ValueError(f"Non-standard JSON constant: {value}")


def prepare_case_lock(case_bytes: bytes, schema_text: str, *, schema_sha256: str | None = None) -> dict[str, Any]:
    try:
        case_set = json.loads(case_bytes.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys,
                              parse_constant=_reject_nonstandard_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"Case set is not valid UTF-8 JSON: {exc}") from None
    if not isinstance(case_set, dict):
        raise ValueError("Case set must be a JSON object")
    cases = case_set.get("cases")
    if (case_set.get("schema_version") != "1.0.0" or not isinstance(case_set.get("case_set_id"), str)
            or not case_set["case_set_id"].strip() or case_set.get("protocol_version") != PROTOCOL_VERSION
            or not isinstance(cases, list) or not cases):
        raise ValueError("Case set must be nonempty and identify its case-set and protocol versions")
    seen: set[str] = set()
    for index, item in enumerate(cases, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Case {index} is not an object")
        case_id = item.get("case_id")
        independent_refs = item.get("independent_review_refs")
        reference_category = item.get("reference_category")
        if (not isinstance(case_id, str) or not case_id.strip() or case_id in seen
                or not isinstance(item.get("input"), dict)
                or item["input"].get("assessment_id") != case_id
                or not isinstance(reference_category, str) or reference_category not in {
                    "REQUIRES_EXPERT_REVIEW", "INSUFFICIENT_EVIDENCE", "MECHANISTIC_EVIDENCE_ONLY",
                    "EXPOSURE_COMPARABILITY_PENDING", "RESEARCH_RELEVANCE_SUPPORTED", "EXPERIMENTAL_EVIDENCE"
                }
                or not isinstance(independent_refs, list) or len(independent_refs) < 2
                or any(not isinstance(ref, str) or not ref.strip() for ref in independent_refs)
                or len(set(independent_refs)) < 2
                or not isinstance(item.get("adjudication_reference"), str)
                or not item["adjudication_reference"].strip()):
            raise ValueError(f"Case {case_id or index} lacks unique identity or independent adjudication references")
        validation = validate_draft_2020_12(item["input"], schema_text)
        if validation.status != "VALID":
            raise ValueError(f"Case {case_id} formal schema validation failed or unavailable: {validation.status}; {validation.errors}")
        seen.add(case_id)
    return {
        "lock_format_version": "1.0.0", "case_set_id": case_set["case_set_id"],
        "protocol_version": PROTOCOL_VERSION,
        "case_set_sha256_exact_bytes": hashlib.sha256(case_bytes).hexdigest(),
        "case_count": len(cases), "case_ids": [item["case_id"] for item in cases],
        "schema_sha256_exact_bytes": schema_sha256 or hashlib.sha256(schema_text.encode("utf-8")).hexdigest(),
        "status": "CANDIDATE_NOT_APPROVED",
        "owner_approval_reference": None, "owner_signature_reference": None,
        "thresholds": None,
        "note": "Exact-byte lock candidate only. Owner must verify sources, case adjudication, protocol, thresholds, and approve this digest before benchmark execution.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-set", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if not args.case_set.is_file():
        raise SystemExit("Case-set file does not exist")
    schema_text = SCHEMA_PATH.read_text(encoding="utf-8")
    lock = prepare_case_lock(args.case_set.read_bytes(), schema_text,
                             schema_sha256=hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(lock, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)
    print(json.dumps({"status": lock["status"], "case_set_id": lock["case_set_id"],
                      "case_count": lock["case_count"], "sha256": lock["case_set_sha256_exact_bytes"]}, sort_keys=True))


if __name__ == "__main__":
    main()
