"""Run a preapproved, locked Phase 7 categorical benchmark case set."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import platform
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "stageD" / "src"))
from stage_d.interpretation import INTERPRETATION_CATEGORIES, classify_interpretation  # noqa: E402
from stage_d.schema_validation import validate_draft_2020_12  # noqa: E402

STAGE_D = ROOT / "stageD"
SCHEMA_PATH = STAGE_D / "schemas/risk_interpretation.schema.json"
PROTOCOL_VERSION = "1.0.0"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_nonstandard_constant(value: str) -> None:
    raise ValueError(f"Non-standard JSON constant: {value}")


def _load_json_object(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys,
                           parse_constant=_reject_nonstandard_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"{label} is not unambiguous UTF-8 JSON: {exc}") from None
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def run_benchmark(case_set: dict[str, Any], approval: dict[str, Any], *,
                  case_set_sha256: str, approval_sha256: str, schema_text: str,
                  schema_sha256: str | None = None) -> dict[str, Any]:
    for label, digest in (("case-set", case_set_sha256), ("approval", approval_sha256)):
        if not isinstance(digest, str) or len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValueError(f"A valid exact-byte {label} SHA-256 is required")
    if not isinstance(approval, dict):
        raise ValueError("Approval record must be a JSON object")
    if approval.get("status") != "APPROVED" or not str(approval.get("approval_reference", "")).strip():
        raise ValueError("An owner-approved protocol record is required")
    for field in ("approver_identity", "approver_role", "approval_date", "signature_reference"):
        if not isinstance(approval.get(field), str) or not approval[field].strip():
            raise ValueError(f"Owner approval is missing {field}")
    if approval.get("protocol_version") != PROTOCOL_VERSION:
        raise ValueError("Approval protocol version does not match the runner")
    if approval.get("case_set_sha256") != case_set_sha256:
        raise ValueError("Approved case-set SHA-256 does not match exact input bytes")
    if not str(approval.get("implementation_release_id", "")).strip():
        raise ValueError("Approval must identify the implementation release")
    dependency_hash = approval.get("dependency_lock_sha256")
    if not isinstance(dependency_hash, str) or len(dependency_hash) != 64 or any(ch not in "0123456789abcdef" for ch in dependency_hash):
        raise ValueError("Approval must record the exact dependency-lock SHA-256")
    thresholds = approval.get("thresholds")
    if (not isinstance(thresholds, dict)
            or isinstance(thresholds.get("minimum_exact_agreement"), bool)
            or not isinstance(thresholds.get("minimum_exact_agreement"), (int, float))
            or not 0 <= thresholds["minimum_exact_agreement"] <= 1
            or isinstance(thresholds.get("minimum_coverage"), bool)
            or not isinstance(thresholds.get("minimum_coverage"), (int, float))
            or not 0 <= thresholds["minimum_coverage"] <= 1
            or not isinstance(thresholds.get("minimum_per_category_agreement"), dict)):
        raise ValueError("Owner approval must define exact, coverage, and per-category thresholds")
    if not isinstance(case_set, dict):
        raise ValueError("Case set must be a JSON object")
    cases = case_set.get("cases")
    if (case_set.get("schema_version") != "1.0.0"
            or not isinstance(case_set.get("case_set_id"), str) or not case_set["case_set_id"].strip()
            or case_set.get("protocol_version") != PROTOCOL_VERSION or not isinstance(cases, list) or not cases):
        raise ValueError("Case set must be a nonempty, versioned, locked benchmark input")
    categories = set(INTERPRETATION_CATEGORIES)
    abstain = approval.get("abstention_categories")
    if (not isinstance(abstain, list) or any(not isinstance(item, str) for item in abstain)
            or not set(abstain) <= categories):
        raise ValueError("Owner approval must define valid abstention categories")
    per_category = thresholds["minimum_per_category_agreement"]
    if any(category not in categories or isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1
           for category, value in per_category.items()):
        raise ValueError("Per-category thresholds contain invalid categories or values")

    labels: list[str] = []
    predictions: list[str] = []
    case_ids: set[str] = set()
    predictions_by_case: list[dict[str, str]] = []
    for index, item in enumerate(cases, start=1):
        case_id = item.get("case_id") if isinstance(item, dict) else None
        case = item.get("input") if isinstance(item, dict) else None
        reference = item.get("reference_category") if isinstance(item, dict) else None
        independent_refs = item.get("independent_review_refs") if isinstance(item, dict) else None
        adjudication = item.get("adjudication_reference") if isinstance(item, dict) else None
        if (not isinstance(case_id, str) or not case_id.strip() or case_id in case_ids
                or not isinstance(case, dict) or case.get("assessment_id") != case_id
                or not isinstance(reference, str) or reference not in categories or not isinstance(independent_refs, list)
                or len(independent_refs) < 2 or any(not isinstance(ref, str) or not ref.strip() for ref in independent_refs)
                or len(set(independent_refs)) < 2
                or not isinstance(adjudication, str) or not adjudication.strip()):
            raise ValueError(f"Case {index} lacks a unique ID or complete independent adjudication trace")
        case_ids.add(case_id)
        validation = validate_draft_2020_12(case, schema_text)
        if validation.status != "VALID":
            raise ValueError(f"Case {case_id} failed formal Draft 2020-12 validation: {validation.status}: {validation.errors}")
        predicted = classify_interpretation(case)["category"]
        labels.append(reference)
        predictions.append(predicted)
        predictions_by_case.append({"case_id": case_id, "reference_category": reference,
                                    "predicted_category": predicted, "agreement": reference == predicted})

    confusion: dict[str, dict[str, int]] = {
        actual: {predicted: 0 for predicted in sorted(categories)} for actual in sorted(categories)
    }
    for actual, predicted in zip(labels, predictions):
        confusion[actual][predicted] += 1
    exact = sum(actual == predicted for actual, predicted in zip(labels, predictions))
    non_abstained = [(actual, predicted) for actual, predicted in zip(labels, predictions) if predicted not in abstain]
    by_reference = Counter(labels)
    by_category = {
        category: {"correct": confusion[category][category], "denominator": by_reference[category],
                   "agreement": confusion[category][category] / by_reference[category] if by_reference[category] else None}
        for category in sorted(categories) if by_reference[category]
    }
    coverage = len(non_abstained) / len(cases)
    exact_agreement = exact / len(cases)
    unmet = []
    if exact_agreement < thresholds["minimum_exact_agreement"]:
        unmet.append("minimum_exact_agreement")
    if coverage < thresholds["minimum_coverage"]:
        unmet.append("minimum_coverage")
    for category, minimum in per_category.items():
        observed = by_category.get(category, {}).get("agreement")
        if observed is None or observed < minimum:
            unmet.append(f"minimum_per_category_agreement:{category}")
    interpretation_path = Path(importlib.import_module("stage_d.interpretation").__file__)
    return {
        "result_schema_version": "1.0.0", "protocol_version": PROTOCOL_VERSION,
        "approval_reference": approval["approval_reference"], "case_set_id": case_set["case_set_id"],
        "case_set_sha256_exact_bytes": case_set_sha256,
        "approval_sha256_exact_bytes": approval_sha256,
        "runner_script_sha256_exact_bytes": _sha256(Path(__file__).resolve()),
        "interpretation_module_sha256_exact_bytes": _sha256(interpretation_path),
        "schema_sha256_exact_bytes": schema_sha256 or hashlib.sha256(schema_text.encode("utf-8")).hexdigest(),
        "dependency_lock_sha256_exact_bytes": dependency_hash,
        "implementation_release_id": approval["implementation_release_id"],
        "case_count": len(cases), "reference_counts": dict(sorted(by_reference.items())),
        "confusion_matrix": confusion, "exact_agreement": exact_agreement,
        "per_category_agreement": by_category,
        "abstention_categories": abstain,
        "abstained_predictions": len(cases) - len(non_abstained), "coverage": coverage,
        "non_abstained_exact_agreement": (sum(a == p for a, p in non_abstained) / len(non_abstained)) if non_abstained else None,
        "thresholds": thresholds, "thresholds_met": not unmet, "thresholds_unmet": unmet,
        "case_results": predictions_by_case,
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "run_status": "RESULTS_PENDING_INDEPENDENT_REVIEW",
        "scientific_acceptance": "NOT_GRANTED",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-set", required=True, type=Path)
    parser.add_argument("--approval", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if not args.case_set.is_file() or not args.approval.is_file():
        raise SystemExit("Approved case-set and approval files must exist")
    case_bytes = args.case_set.read_bytes()
    approval_bytes = args.approval.read_bytes()
    case_set = _load_json_object(case_bytes, "Case set")
    approval = _load_json_object(approval_bytes, "Approval")
    schema_text = SCHEMA_PATH.read_text(encoding="utf-8")
    result = run_benchmark(case_set, approval, case_set_sha256=hashlib.sha256(case_bytes).hexdigest(),
                           approval_sha256=hashlib.sha256(approval_bytes).hexdigest(),
                           schema_text=schema_text, schema_sha256=_sha256(SCHEMA_PATH))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)
    print(json.dumps({"case_count": result["case_count"], "exact_agreement": result["exact_agreement"],
                      "coverage": result["coverage"], "thresholds_met": result["thresholds_met"],
                      "scientific_acceptance": result["scientific_acceptance"]}, sort_keys=True))


if __name__ == "__main__":
    main()
