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
from .recipe_engine import (
    analyze_recipe_mass_balance, calculate_meal_exposure, calculate_recipe_exposure, load_meal, load_recipe,
    save_meal, save_recipe, validate_meal, validate_recipe,
)
from .release_adapters import load_phase1b_v131_inputs, load_phase2_v030_evidence, load_phase4_context_evidence
from .stage_b_connector import SOURCE_FILES, create_snapshot, detect_source_changes, load_stage_b, verify_release
from .validation import validate_all

ROOT = project_root()
STAGE = ROOT / "stageC"
SNAPSHOT = STAGE / "data" / "stage_b_snapshot_20261103"
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


def _load_recipe_collection(directory: Path) -> dict[str, dict[str, Any]]:
    if not directory.exists() or not directory.is_dir():
        raise ValidationError(f"Recipe directory does not exist: {directory}")
    recipes: dict[str, dict[str, Any]] = {}
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or "recipe_id" not in payload or "ingredients" not in payload:
            continue
        recipe = load_recipe(path)
        if recipe["recipe_id"] in recipes:
            raise ValidationError(f"Duplicate recipe_id in {directory}: {recipe['recipe_id']}")
        recipes[recipe["recipe_id"]] = recipe
    return recipes


def command_recipe_create(args: argparse.Namespace) -> dict[str, Any]:
    recipe = json.loads(args.input.read_text(encoding="utf-8"))
    destination = args.output or args.input
    save_recipe(recipe, destination)
    return {"status": "SAVED", "recipe_id": recipe["recipe_id"], "path": str(destination.resolve()),
            "ingredient_count": len(recipe["ingredients"])}


def command_recipe_add_ingredient(args: argparse.Namespace) -> dict[str, Any]:
    recipe = load_recipe(args.recipe)
    ingredient = json.loads(args.ingredient.read_text(encoding="utf-8"))
    recipe["ingredients"].append(ingredient)
    destination = args.output or args.recipe
    save_recipe(recipe, destination)
    return {"status": "SAVED", "recipe_id": recipe["recipe_id"], "path": str(destination.resolve()),
            "ingredient_count": len(recipe["ingredients"])}


def command_recipe_validate(args: argparse.Namespace) -> dict[str, Any]:
    recipe = json.loads(args.recipe.read_text(encoding="utf-8"))
    errors = validate_recipe(recipe)
    return {"status": "PASS" if not errors else "FAIL", "recipe_id": recipe.get("recipe_id", ""),
            "errors": errors, "mass_balance": analyze_recipe_mass_balance(recipe) if not errors else {"status": "NOT_EVALUATED", "reason": "recipe structure or measurement fields are invalid"}}


def command_recipe_calculate(args: argparse.Namespace) -> dict[str, Any]:
    recipe = load_recipe(args.recipe)
    foods, mappings, compounds, phase1b = load_phase1b_v131_inputs()
    phase2_evidence, phase2 = load_phase2_v030_evidence()
    phase4_context, phase4 = load_phase4_context_evidence()
    result = calculate_recipe_exposure(recipe, foods, mappings, compounds, phase2_evidence,
                                       stage_b_manifest_sha256=phase1b["stage_b_manifest_sha256"],
                                       phase2_release_metadata=phase2)
    result["phase4_context_records"] = phase4_context
    result["upstream_releases"] = {"phase1b": phase1b, "phase2": phase2, "phase4": phase4}
    output = args.output or STAGE / "reports" / "phase3" / "calculations" / f"{recipe['recipe_id']}_exposure.json"
    _json_write(output, result)
    return {"status": result["calculation_status"], "recipe_id": recipe["recipe_id"],
            "output": _portable_artifact_path(output), "ingredient_estimates": len(result["ingredient_results"]),
            "complete_estimates": sum(row["calculation_status"] == "Complete" for row in result["ingredient_results"]),
            "raw_reference_totals": result["raw_reference_totals"], "mass_balance_status": result["mass_balance"]["status"],
            "phase2_cooking_evidence_records": phase2["accepted_cooking_evidence"],
            "phase2_release": phase2["release_id"], "phase4_context_records": phase4["selected_context_record_count"],
            "phase4_release": phase4["release_id"]}


def command_meal_create(args: argparse.Namespace) -> dict[str, Any]:
    meal = json.loads(args.input.read_text(encoding="utf-8"))
    recipes = _load_recipe_collection(args.recipes_dir) if args.recipes_dir else None
    destination = args.output or args.input
    save_meal(meal, destination, recipes)
    return {"status": "SAVED", "meal_id": meal["meal_id"], "path": str(destination.resolve()),
            "component_count": len(meal["components"])}


def command_meal_validate(args: argparse.Namespace) -> dict[str, Any]:
    meal = json.loads(args.meal.read_text(encoding="utf-8"))
    recipes = _load_recipe_collection(args.recipes_dir) if args.recipes_dir else None
    errors = validate_meal(meal, recipes)
    return {"status": "PASS" if not errors else "FAIL", "meal_id": meal.get("meal_id", ""), "errors": errors}


def command_meal_calculate(args: argparse.Namespace) -> dict[str, Any]:
    recipes = _load_recipe_collection(args.recipes_dir)
    meal = load_meal(args.meal, recipes)
    foods, mappings, compounds, phase1b = load_phase1b_v131_inputs()
    phase2_evidence, phase2 = load_phase2_v030_evidence()
    phase4_context, phase4 = load_phase4_context_evidence()
    result = calculate_meal_exposure(meal, recipes, foods, mappings, compounds, phase2_evidence,
                                     stage_b_manifest_sha256=phase1b["stage_b_manifest_sha256"],
                                     phase2_release_metadata=phase2)
    result["phase4_context_records"] = phase4_context
    result["upstream_releases"] = {"phase1b": phase1b, "phase2": phase2, "phase4": phase4}
    output = args.output or STAGE / "reports" / "phase3" / "calculations" / f"{meal['meal_id']}_exposure.json"
    _json_write(output, result)
    return {"status": result["calculation_status"], "meal_id": meal["meal_id"],
            "output": _portable_artifact_path(output), "components": len(result["component_results"]),
            "ingredient_estimates": sum(len(row["ingredient_results"]) for row in result["component_results"]),
            "raw_reference_totals": result["raw_reference_totals"],
            "phase2_cooking_evidence_records": phase2["accepted_cooking_evidence"],
            "phase2_release": phase2["release_id"], "phase4_context_records": phase4["selected_context_record_count"],
            "phase4_release": phase4["release_id"]}


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
    recipe = subs.add_parser("recipe", help="create, edit, validate, or calculate source-traceable recipes")
    rsubs = recipe.add_subparsers(dest="recipe_command", required=True)
    p = rsubs.add_parser("create", help="validate and save a structured recipe JSON document")
    p.add_argument("input", type=Path); p.add_argument("--output", type=Path); p.set_defaults(handler=command_recipe_create)
    p = rsubs.add_parser("add-ingredient", help="append one structured ingredient JSON object to a recipe")
    p.add_argument("recipe", type=Path); p.add_argument("--ingredient", type=Path, required=True); p.add_argument("--output", type=Path); p.set_defaults(handler=command_recipe_add_ingredient)
    p = rsubs.add_parser("validate", help="check recipe structure and measured mass-accounting status")
    p.add_argument("recipe", type=Path); p.set_defaults(handler=command_recipe_validate)
    p = rsubs.add_parser("calculate", help="calculate recipe exposure using verified Phase1B/Phase2 release inputs")
    p.add_argument("recipe", type=Path); p.add_argument("--output", type=Path); p.set_defaults(handler=command_recipe_calculate)
    meal = subs.add_parser("meal", help="create, validate, or calculate a meal of recipes and direct foods")
    msubs = meal.add_subparsers(dest="meal_command", required=True)
    p = msubs.add_parser("create", help="validate and save a structured meal JSON document")
    p.add_argument("input", type=Path); p.add_argument("--recipes-dir", type=Path); p.add_argument("--output", type=Path); p.set_defaults(handler=command_meal_create)
    p = msubs.add_parser("validate", help="validate meal components and double-counting guards")
    p.add_argument("meal", type=Path); p.add_argument("--recipes-dir", type=Path); p.set_defaults(handler=command_meal_validate)
    p = msubs.add_parser("calculate", help="calculate meal exposure with recipe JSON files from a directory")
    p.add_argument("meal", type=Path); p.add_argument("--recipes-dir", type=Path, required=True); p.add_argument("--output", type=Path); p.set_defaults(handler=command_meal_calculate)
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
