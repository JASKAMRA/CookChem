"""Command-line interface for read-only Stage B import and Phase 1 calculations."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from .compound_mapping import assess_mapping_compatibility, build_mappings, load_mappings, mapping_coverage, write_mappings
from .exceptions import StageCError, ValidationError
from .exposure_engine import aggregate_exposures, calculate_exposure
from .food_composition import FIELDS, ingest_food_data, load_food_data
from .provenance import project_root, sha256_file
from .stage_b_connector import SOURCE_FILES, create_snapshot, detect_source_changes, load_stage_b, verify_release
from .validation import validate_all

ROOT = project_root()
STAGE = ROOT / "stageC"
SNAPSHOT = STAGE / "data" / "stage_b_snapshot_v20_20261103"
COMPOSITION = STAGE / "data" / "food_composition" / "food_composition.csv"
MAPPING = STAGE / "data" / "compound_food_mapping" / "compound_food_mapping.csv"


def _json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def _portable_artifact_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(STAGE.resolve()).as_posix()
    except ValueError:
        # Keep validation artifacts portable instead of embedding a machine-specific path.
        return path.name


def _read_exposure_input(path: Path) -> tuple[list[dict[str, str]], str]:
    if path.suffix.casefold() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as stream: return list(csv.DictReader(stream)), ""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list): return payload, ""
    if not isinstance(payload, dict) or not isinstance(payload.get("ingredients"), list):
        raise ValidationError("Exposure JSON must be a list or an object with an 'ingredients' list")
    period = str(payload.get("period_id", ""))
    return [{**row, "period_id": row.get("period_id", period)} for row in payload["ingredients"]], period


def _write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore"); writer.writeheader()
        for row in rows: writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for k, v in row.items()})


def command_inspect(_: argparse.Namespace) -> dict[str, Any]:
    release = verify_release()
    loaded = load_stage_b()
    compounds = loaded["source_files"]["compound_registry.csv"]
    return {"selected_release": release, "import_allowlist": SOURCE_FILES, "compound_count": len(compounds), "source_record_counts": {name: len(rows) for name, rows in loaded["source_files"].items()}, "identity_review_compounds": sum(row.get("StageC_Identity_Verification_Status") != "Complete" for row in compounds), "food_context_is_qualitative": True, "quantitative_food_composition_records": 0}


def command_import(args: argparse.Namespace) -> dict[str, Any]:
    return create_snapshot(args.destination)


def command_ingest(args: argparse.Namespace) -> dict[str, Any]:
    return ingest_food_data(args.source, args.destination, args.manifest)


def command_map(args: argparse.Namespace) -> dict[str, Any]:
    loaded = load_stage_b()
    compounds = loaded["source_files"]["compound_registry.csv"]
    food = load_food_data(args.composition)
    mappings = build_mappings(compounds, food)
    write_mappings(args.output, mappings)
    coverage = mapping_coverage(compounds, food, mappings)
    coverage["mapping_file"] = _portable_artifact_path(args.output)
    _json_write(args.report, coverage)
    return coverage


def command_exposure(args: argparse.Namespace) -> dict[str, Any]:
    inputs, _ = _read_exposure_input(args.input)
    foods = {r["food_record_id"]: r for r in load_food_data(args.composition)}
    mappings = load_mappings(args.mapping)
    b = load_stage_b()
    compounds = {r["Compound_ID"]: r for r in b["source_files"]["compound_registry.csv"]}
    manifest_sha = b["release"]["manifest_sha256"]
    exposures = [calculate_exposure(item, foods, mappings, compounds, manifest_sha) for item in inputs]
    can_aggregate = len(exposures) > 1 and all(r.get("period_id") for r in exposures)
    aggregate = aggregate_exposures(exposures) if can_aggregate else []
    payload = {"estimates": exposures, "aggregates": aggregate, "aggregation_status": "performed" if can_aggregate else "not performed: each input needs an explicit period_id"}
    if args.output.suffix.casefold() == ".csv": _write_rows(args.output, exposures)
    else: _json_write(args.output, payload)
    return {"output": str(args.output.resolve()), "estimate_count": len(exposures), "complete": sum(r["calculation_status"] == "Complete" for r in exposures), "incomplete_or_unverified": sum(r["calculation_status"] != "Complete" for r in exposures), "aggregate_count": len(aggregate), "status": "PASS"}


def command_validate(args: argparse.Namespace) -> dict[str, Any]:
    b = load_stage_b()
    compounds = b["source_files"]["compound_registry.csv"]
    foods = load_food_data(args.composition)
    mappings = load_mappings(args.mapping)
    food_ids = {r["food_record_id"] for r in foods}
    mapping_errors = []
    for mapping in mappings:
        if mapping.get("food_record_id") not in food_ids: mapping_errors.append(mapping.get("mapping_id", ""))
    report = validate_all(foods, mappings, [], {c["Compound_ID"] for c in compounds})
    snapshot_changes = detect_source_changes(SNAPSHOT)
    report["stage_b_snapshot_changes"] = snapshot_changes
    report["mapping_coverage"] = mapping_coverage(compounds, foods, mappings)
    pending_identity = [
        {"compound_id": row["Compound_ID"], "canonical_name": row["Canonical_Name"], "status": row["StageC_Identity_Verification_Status"]}
        for row in compounds if row.get("StageC_Identity_Verification_Status") != "Complete"
    ]
    compatibility_review = assess_mapping_compatibility(compounds, mappings)
    report.update({"stage_b_release": b["release"]["release_id"], "stage_b_manifest_sha256": b["release"]["manifest_sha256"], "stage_b_compounds": len(compounds), "stage_b_identity_review_items": pending_identity, "repeated_nonstereospecific_smiles_review_groups": b["release"]["repeated_nonstereospecific_smiles_review_groups"], "food_records": len(foods), "mapping_records": len(mappings), "mapping_orphan_ids": mapping_errors, "legacy_mappings_blocked_by_current_identity_review": compatibility_review, "legacy_mapping_rows_blocked_by_current_identity_review": len(compatibility_review)})
    if mapping_errors or snapshot_changes: report["status"] = "FAIL"
    _json_write(args.report, report)
    if report["status"] != "PASS": raise ValidationError(f"Phase 1 validation failed; see {args.report}")
    return {
        "status": report["status"],
        "report": _portable_artifact_path(args.report),
        "stage_b_release": report["stage_b_release"],
        "stage_b_compounds": report["stage_b_compounds"],
        "food_records": report["food_records"],
        "mapping_records": report["mapping_records"],
        "identity_complete_quantitative_coverage": report["mapping_coverage"]["compounds_with_verified_quantitative_food_data"],
        "legacy_mapping_rows_blocked_by_identity_review": report["legacy_mapping_rows_blocked_by_current_identity_review"],
        "identity_review_items": len(report["stage_b_identity_review_items"]),
        "food_errors": len(report["food_errors"]),
        "mapping_errors": len(report["mapping_errors"]),
        "snapshot_changes": len(snapshot_changes),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cookrisk-stagec", description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    p = subs.add_parser("inspect", help="verify and summarize StageB_FINALIZED"); p.set_defaults(handler=command_inspect)
    p = subs.add_parser("import-stage-b", help="copy the read-only Stage B allowlist into a checksummed snapshot")
    p.add_argument("--destination", type=Path, default=SNAPSHOT); p.set_defaults(handler=command_import)
    p = subs.add_parser("ingest-food", help="validate a source-backed food-composition CSV and normalize mass units")
    p.add_argument("source", type=Path); p.add_argument("--destination", type=Path, default=COMPOSITION); p.add_argument("--manifest", type=Path, default=STAGE/"reports"/"ingestion"/"food_import_manifest.json"); p.set_defaults(handler=command_ingest)
    p = subs.add_parser("map", help="map exact/verified chemical identifiers to food records")
    p.add_argument("--composition", type=Path, default=COMPOSITION); p.add_argument("--output", type=Path, default=STAGE/"reports"/"validation"/"mapping_rebuild.csv"); p.add_argument("--report", type=Path, default=STAGE/"reports"/"validation"/"mapping_coverage.json"); p.set_defaults(handler=command_map)
    p = subs.add_parser("exposure", help="calculate raw-food exposure from JSON or CSV input")
    p.add_argument("input", type=Path); p.add_argument("--composition", type=Path, default=COMPOSITION); p.add_argument("--mapping", type=Path, default=MAPPING); p.add_argument("--output", type=Path, default=STAGE/"reports"/"validation"/"exposure_results.json"); p.set_defaults(handler=command_exposure)
    p = subs.add_parser("validate", help="run data and scientific integrity validation")
    p.add_argument("--composition", type=Path, default=COMPOSITION); p.add_argument("--mapping", type=Path, default=MAPPING); p.add_argument("--report", type=Path, default=STAGE/"reports"/"validation"/"phase1_validation.json"); p.set_defaults(handler=command_validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = args.handler(args)
    except (StageCError, OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__": raise SystemExit(main())
