"""Command-line interface for read-only Stage B import and Phase 1 calculations."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from .compound_mapping import build_mappings, load_mappings, mapping_coverage, write_mappings
from .exceptions import StageCError, ValidationError
from .exposure_engine import aggregate_exposures, calculate_exposure
from .food_composition import FIELDS, ingest_food_data, load_food_data
from .provenance import project_root, sha256_file
from .stage_b_connector import SOURCE_FILES, create_snapshot, default_release_path, detect_source_changes, load_stage_b, verify_release
from .validation import validate_all

ROOT = project_root()
STAGE = ROOT / "stageC"
SNAPSHOT = STAGE / "data" / "stage_b_snapshot_20261102"
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
    return {"selected_release": release, "import_allowlist": SOURCE_FILES, "compound_count": len(compounds), "compound_ids": [x["Compound_ID"] for x in compounds], "source_record_counts": {name: len(rows) for name, rows in loaded["source_files"].items()}, "food_context_is_qualitative": True, "quantitative_food_composition_records": 0}


def command_import(args: argparse.Namespace) -> dict[str, Any]:
    return create_snapshot(args.destination, args.release)


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
    report.update({"stage_b_release": b["release"]["release_id"], "stage_b_compounds": len(compounds), "food_records": len(foods), "mapping_records": len(mappings), "mapping_orphan_ids": mapping_errors})
    if mapping_errors or snapshot_changes: report["status"] = "FAIL"
    _json_write(args.report, report)
    if report["status"] != "PASS": raise ValidationError(f"Phase 1 validation failed; see {args.report}")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cookrisk-stagec", description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    p = subs.add_parser("inspect", help="verify and summarize StageB_Final"); p.set_defaults(handler=command_inspect)
    p = subs.add_parser("import-stage-b", help="copy the read-only Stage B allowlist into a checksummed snapshot")
    p.add_argument("--release", type=Path, default=default_release_path()); p.add_argument("--destination", type=Path, default=SNAPSHOT); p.set_defaults(handler=command_import)
    p = subs.add_parser("ingest-food", help="validate a source-backed food-composition CSV and normalize mass units")
    p.add_argument("source", type=Path); p.add_argument("--destination", type=Path, default=COMPOSITION); p.add_argument("--manifest", type=Path, default=STAGE/"reports"/"ingestion"/"food_import_manifest.json"); p.set_defaults(handler=command_ingest)
    p = subs.add_parser("map", help="map exact/verified chemical identifiers to food records")
    p.add_argument("--composition", type=Path, default=COMPOSITION); p.add_argument("--output", type=Path, default=MAPPING); p.add_argument("--report", type=Path, default=STAGE/"reports"/"validation"/"mapping_coverage.json"); p.set_defaults(handler=command_map)
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
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__": raise SystemExit(main())
