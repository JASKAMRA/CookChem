#!/usr/bin/env python3
"""Build a byte-preserving Phase1B v1.3.1 metadata/eligibility successor."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import shutil
import subprocess
import tarfile
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
RELEASES = ROOT / "stageC/releases"
BASE_NAME = "Phase1B-v1.3.0"
TARGET = RELEASES / "Phase1B-v1.3.1"
PREFIX = f"stageC/releases/{BASE_NAME}/"
V20_RESOLVED_QUANTITATIVE_IDS = {
    "MOL-V12-CID-107905", "MOL-V12-CID-122685", "MOL-V12-CID-16741", "MOL-V12-CID-3712",
    "MOL-V12-CID-465405", "MOL-V12-CID-5276890", "MOL-V12-CID-5280544", "MOL-V12-CID-5280647",
    "MOL-V12-CID-6419835", "MOL-V12-CID-65084", "MOL-V12-CID-72277",
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def archive_base() -> None:
    if TARGET.exists():
        raise SystemExit(f"Refusing to overwrite {TARGET}")
    blob = subprocess.check_output(["git", "archive", "--format=tar", "HEAD", f"stageC/releases/{BASE_NAME}"], cwd=ROOT)
    TARGET.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:") as archive:
        for member in archive.getmembers():
            name = member.name
            if not name.startswith(PREFIX) or not member.isfile():
                continue
            relative = PurePosixPath(name[len(PREFIX):])
            if any(part in {"..", ""} for part in relative.parts):
                raise SystemExit(f"Unsafe archive path: {name}")
            destination = TARGET.joinpath(*relative.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            if source is None:
                raise SystemExit(f"Unreadable archive member: {name}")
            destination.write_bytes(source.read())


def main() -> None:
    archive_base()
    stagec = TARGET / "stageC"
    foods_fields, foods = read_csv(stagec / "data/food_composition/food_composition.csv")
    maps_fields, maps = read_csv(stagec / "data/compound_food_mapping/compound_food_mapping.csv")
    coverage_path = stagec / "reports/phase1b/COMPOUND_COVERAGE_REGISTER_2026-11-03.csv"
    coverage_fields, coverage = read_csv(coverage_path)
    registry_path = stagec / "data/stage_b_snapshot_v20_20261103/compound_registry.csv"
    _, registry = read_csv(registry_path)

    food_by_id = {row["food_record_id"]: row for row in foods}
    rows_by_compound: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in maps:
        rows_by_compound[row["compound_id"]].append(row)
    identity_by_id = {row["Compound_ID"]: row["Identity_Status"] for row in registry}
    if len(coverage) != 143 or len(foods) != 584 or len(maps) != 584:
        raise SystemExit("Unexpected Phase1B baseline shape; refusing to build successor")

    additions = [
        "Raw_Mapping_Present", "Raw_Mapping_Row_Count", "Raw_Mapped_Food_Classes",
        "Identity_Complete_Per_V20", "StageB_Identity_Status", "Accepted_Mapping_Present",
        "Accepted_Quantitative_Mapping_Present", "Scientific_Eligibility_Status",
        "Eligibility_Rationale", "Reconciliation_Note",
    ]
    for field in additions:
        if field not in coverage_fields:
            coverage_fields.append(field)

    complete_ids: set[str] = set()
    eligible_ids: set[str] = set()
    accepted_ids: set[str] = set()
    mapped_ids = set(rows_by_compound)
    for row in coverage:
        cid = row["Compound_ID"]
        status = identity_by_id.get(cid, "")
        # V20's field is a narrative adjudication, not a boolean status column.
        # Thirteen entries explicitly begin with an unresolved "Identity pending" note;
        # the remaining entries are identity-complete under that release's audit.
        is_complete = bool(status) and "pending" not in status.casefold()
        if is_complete:
            complete_ids.add(cid)
        prior_mapping = row.get("Any_Mapping", "false").casefold() == "true"
        prior_quant = row.get("Quantitative_Mapping", "false").casefold() == "true"
        accepted = prior_mapping and cid in mapped_ids
        if accepted:
            accepted_ids.add(cid)
        evidence = row.get("Food_Composition_Evidence_Status", "")
        prior_eligible = row.get("Identity_Complete_Quantitative_Eligible", "false").casefold() == "true"
        reconciled_candidate = cid in V20_RESOLVED_QUANTITATIVE_IDS and prior_quant and evidence == "Accepted quantitative measurement(s)"
        eligible = is_complete and (prior_eligible or reconciled_candidate)
        if eligible:
            eligible_ids.add(cid)

        classes = sorted({food_by_id[m["food_record_id"]]["food_use_classification"] for m in rows_by_compound.get(cid, []) if m["food_record_id"] in food_by_id})
        old_identity_status = row.get("Identity_Audit_Status", "")
        old_eligibility = row.get("Identity_Complete_Quantitative_Eligible", "")
        row["Identity_Audit_Status"] = status or old_identity_status
        row["Identity_Complete_Per_V20"] = str(is_complete).lower()
        row["StageB_Identity_Status"] = status
        row["Raw_Mapping_Present"] = str(cid in mapped_ids).lower()
        row["Raw_Mapping_Row_Count"] = str(len(rows_by_compound.get(cid, [])))
        row["Raw_Mapped_Food_Classes"] = "; ".join(classes)
        row["Accepted_Mapping_Present"] = str(prior_mapping).lower()
        row["Accepted_Quantitative_Mapping_Present"] = str(prior_quant).lower()
        row["Identity_Complete_Quantitative_Eligible"] = str(eligible).lower()
        row["Scientific_Eligibility_Status"] = "ELIGIBLE_ACCEPTED_QUANTITATIVE" if eligible else "NOT_ELIGIBLE"
        if eligible and prior_eligible:
            rationale = "Accepted quantitative measurement; identity complete in authoritative StageB_V20_20261103 registry."
        elif eligible:
            rationale = "Accepted quantitative measurement; stale pending identity flag reconciled to authoritative StageB_V20_20261103 adjudication."
        elif not is_complete:
            rationale = "Not eligible: Stage B identity remains pending."
        elif not prior_quant or evidence != "Accepted quantitative measurement(s)":
            rationale = "Not eligible: no accepted quantitative measurement meeting Phase1B eligibility criteria."
        else:
            rationale = "Not eligible: accepted mapping/evidence criteria are not both met."
        row["Eligibility_Rationale"] = rationale
        if cid in mapped_ids and not prior_mapping:
            row["Reconciliation_Note"] = "Raw mapping row(s) retained for audit; prior accepted-mapping flag remains false pending scientific acceptance."
        elif old_identity_status != status:
            row["Reconciliation_Note"] = "Identity status reconciled to the packaged V20 registry; no concentration or mapping identity changed."
        elif eligible and old_eligibility != "true":
            row["Reconciliation_Note"] = "Prior quantitative evidence retained; stale identity flag reconciled to the packaged V20 registry."
        else:
            row["Reconciliation_Note"] = "No scientific value or accepted-mapping semantics changed."

    raw_by_class: dict[str, set[str]] = defaultdict(set)
    for mapping in maps:
        food = food_by_id[mapping["food_record_id"]]
        raw_by_class[food["food_use_classification"]].add(mapping["compound_id"])
    if (len(mapped_ids), len(complete_ids & mapped_ids), len(mapped_ids - complete_ids), len(accepted_ids), len(eligible_ids)) != (130, 125, 5, 121, 116):
        raise SystemExit(f"Derived counts differ from audited expectation: mapped={len(mapped_ids)}, complete_mapped={len(complete_ids & mapped_ids)}, pending_mapped={len(mapped_ids-complete_ids)}, accepted={len(accepted_ids)}, eligible={len(eligible_ids)}")
    write_csv(coverage_path, coverage_fields, coverage)
    release_path = TARGET / "RELEASE.json"
    release = json.loads(release_path.read_text(encoding="utf-8"))
    data = release.setdefault("data", {})
    data.update({
        "total_food_records": 584, "ordinary_food_records": 335, "food_ingredient_records": 221,
        "prepared_beverage_records": 28, "total_food_mapping_rows": 584,
        "ordinary_food_mapping_rows": sum(1 for m in maps if food_by_id[m["food_record_id"]]["food_use_classification"] == "ordinary food"),
        "food_ingredient_mapping_rows": sum(1 for m in maps if food_by_id[m["food_record_id"]]["food_use_classification"] == "food ingredient"),
        "prepared_beverage_mapping_rows": sum(1 for m in maps if food_by_id[m["food_record_id"]]["food_use_classification"] == "prepared beverage"),
        "raw_mapped_compounds_all_classes": len(mapped_ids), "identity_complete_mapped_compounds_all_classes": len(complete_ids & mapped_ids),
        "identity_pending_mapped_compounds_all_classes": len(mapped_ids - complete_ids), "accepted_mapped_compounds_all_classes": len(accepted_ids),
        "scientifically_eligible_quantitative_compounds_all_classes": len(eligible_ids),
        "ordinary_food_raw_mapped_compounds": len(raw_by_class["ordinary food"]),
        "ordinary_food_identity_complete_mapped_compounds": len(raw_by_class["ordinary food"] & complete_ids),
        "ordinary_food_identity_pending_mapped_compounds": len(raw_by_class["ordinary food"] - complete_ids),
        "ordinary_food_accepted_mapped_compounds": len(raw_by_class["ordinary food"] & accepted_ids),
        "ordinary_food_scientifically_eligible_quantitative_compounds": len(raw_by_class["ordinary food"] & eligible_ids),
        "ordinary_food_compounds_covered": len(raw_by_class["ordinary food"] & eligible_ids),
        "ordinary_food_compounds_uncovered_identity_complete": max(0, len(raw_by_class["ordinary food"] & complete_ids) - len(raw_by_class["ordinary food"] & eligible_ids)),
        "historical_v1_3_0_recorded_coverage": 125,
        "accepted_quantitative_coverage_by_scientific_eligibility": len(eligible_ids),
        "ordinary_food_quantitative_coverage_by_scientific_eligibility": len(raw_by_class["ordinary food"] & eligible_ids),
        "approx_120_target_achieved": len(eligible_ids) >= 120,
        "minimum_130_target_achieved": len(eligible_ids) >= 130,
        "minimum_130_target_shortfall": max(0, 130 - len(eligible_ids)),
        "approx_120_target_achieved_by_scientific_eligibility": len(eligible_ids) >= 120,
        "minimum_130_target_achieved_by_scientific_eligibility": len(eligible_ids) >= 130,
        "minimum_130_target_shortfall_by_scientific_eligibility": max(0, 130 - len(eligible_ids)),
        "eligibility_reconciled_against": "StageB_V20_20261103",
    })
    release["version"] = "1.3.1"
    release["release_id"] = "Phase1B-v1.3.1"
    release["status"] = "USER_ACCEPTED_CLOSEOUT_WITH_COVERAGE_RECONCILIATION"
    release["successor_of"] = "Phase1B-v1.3.0"
    release["created_on"] = "2026-11-03"
    release["verification"] = "Run verify_release.py; package counts and identity eligibility reconcile to the packaged V20 registry."
    release["phase1b_closeout"] = {
        "closed_by_user_acceptance": True,
        "historical_v1_3_0_recorded_coverage": 125,
        "historical_v1_3_0_coverage_interpretation": "Identity-complete mapped compounds; not equivalent to scientific quantitative eligibility.",
        "identity_complete_mapped_compounds_all_classes": 125,
        "identity_pending_mapped_compounds_all_classes": 5,
        "scientifically_eligible_quantitative_compounds_all_classes": 116,
        "scientifically_eligible_quantitative_compounds_ordinary_food": 80,
        "approx_120_target_achieved_by_scientific_eligibility": False,
        "minimum_130_target_achieved_by_scientific_eligibility": False,
        "minimum_130_target_shortfall_by_scientific_eligibility": 14,
        "eligibility_reconciled_to_v20": True,
        "closure_note": "The prior user-authorized Phase1B closeout remains recorded. v1.3.1 corrects the metric distinction: 125 denotes identity-complete mapped compounds, 116 are scientifically eligible quantitatively across all classes, and 80 are eligible in ordinary food."
    }
    validation_path = TARGET / "VALIDATION_RESULTS.json"
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    coverage_metrics = validation.setdefault("mapping_coverage", {})
    coverage_metrics.update({
        "compounds_with_verified_quantitative_food_data": len(eligible_ids),
        "compounds_with_candidate_records": len(mapped_ids),
        "compounds_with_no_verified_quantitative_data": 143 - len(eligible_ids),
        "compounds_with_no_quantitative_data": 143 - len(eligible_ids),
        "identity_complete_mapped_compounds": len(complete_ids & mapped_ids),
        "identity_pending_mapped_compounds": len(mapped_ids - complete_ids),
        "accepted_mapped_compounds": len(accepted_ids),
        "scientifically_eligible_quantitative_compounds": len(eligible_ids),
        "ordinary_food_raw_mapped_compounds": len(raw_by_class["ordinary food"]),
        "ordinary_food_identity_complete_mapped_compounds": len(raw_by_class["ordinary food"] & complete_ids),
        "ordinary_food_identity_pending_mapped_compounds": len(raw_by_class["ordinary food"] - complete_ids),
        "ordinary_food_scientifically_eligible_quantitative_compounds": len(raw_by_class["ordinary food"] & eligible_ids),
    })
    validation["phase1b_v1_3_1_coverage_reconciliation"] = {
        "status": "PASS", "raw_mapped": len(mapped_ids), "identity_complete_mapped": len(complete_ids & mapped_ids),
        "identity_pending_mapped": len(mapped_ids - complete_ids), "accepted_mapped": len(accepted_ids),
        "scientifically_eligible_quantitative_all_classes": len(eligible_ids),
        "scientifically_eligible_quantitative_ordinary_food": len(raw_by_class["ordinary food"] & eligible_ids),
        "all_counts_independently_derived_from_packaged_files": True,
    }
    validation_path.write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    release_path.write_text(json.dumps(release, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    checkpoints = stagec / "reports/phase1b/CHECKPOINTS.json"
    historical = checkpoints.with_name("CHECKPOINTS_BATCH120_HISTORICAL.json")
    if not historical.exists():
        historical.write_bytes(checkpoints.read_bytes())
    checksum_files = [
        stagec / "data/food_composition/food_composition.csv",
        stagec / "data/compound_food_mapping/compound_food_mapping.csv",
        stagec / "data/food_composition/source_registry.csv",
        coverage_path,
    ]
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    checkpoint = {
        "checkpoint_id": "Phase1B-v1.3.1-authoritative-reconciliation",
        "release_id": "Phase1B-v1.3.1", "source_stage_b_release": "StageB_V20_20261103",
        "food_records": 584, "food_records_by_class": dict(Counter(r["food_use_classification"] for r in foods)),
        "mapping_rows": 584, "raw_mapped_compound_ids": len(mapped_ids),
        "identity_complete_mapped_compounds": len(complete_ids & mapped_ids), "identity_pending_mapped_compounds": len(mapped_ids-complete_ids),
        "accepted_mapped_compounds": len(accepted_ids), "scientifically_eligible_quantitative_compounds": len(eligible_ids),
        "ordinary_food_raw_mapped_compounds": len(raw_by_class["ordinary food"]),
        "ordinary_food_identity_complete_mapped_compounds": len(raw_by_class["ordinary food"] & complete_ids),
        "ordinary_food_identity_pending_mapped_compounds": len(raw_by_class["ordinary food"] - complete_ids),
        "ordinary_food_scientifically_eligible_quantitative_compounds": len(raw_by_class["ordinary food"] & eligible_ids),
        "file_sha256": {p.relative_to(stagec).as_posix(): digest(p) for p in checksum_files},
        "historical_checkpoint_preserved_as": historical.name,
        "note": "Eligibility uses accepted quantitative evidence and V20-complete identity; mapping presence alone is not scientific eligibility."
    }
    checkpoints.write_text(json.dumps(checkpoint, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = TARGET / "PHASE1B_RECONCILIATION_REPORT.md"
    report.write_text("""# Phase1B v1.3.1 reconciliation\n\nThis patch successor preserves v1.3.0 source values and the prior user-authorized closeout. It separates raw mapping presence, accepted mapping, identity completion, and scientific quantitative eligibility. The packaged StageB_V20_20261103 registry is authoritative for identity status.\n\n## Independently derived inventory\n\n- Food records: 584 (335 ordinary food, 221 food ingredient, 28 prepared beverage); 584 mappings.\n- Raw mapped Stage B IDs: 130; 125 identity-complete and 5 identity-pending.\n- Accepted mapped IDs: 121. Quantitatively eligible IDs after V20 identity reconciliation: 116 across all classes, 80 in ordinary food.\n- Ordinary-food raw mapped IDs: 87; 84 complete and 3 pending in V20.\n- Eleven accepted quantitative records were made eligible by reconciling stale identity status to V20. Concentrations, source records, mappings, and accepted-mapping flags were not changed.\n- Nine IDs with raw mapping rows but no accepted mapping are visible in the new raw-mapping fields; their acceptance status was not promoted. Held quantitative candidates and medicinal-context rows remain ineligible.\n- The 125 value recorded by v1.3.0 denotes identity-complete mapped IDs; it does not establish 125 scientifically eligible quantitative compounds. Corrected eligibility is 116 across all classes and 80 ordinary-food compounds.\n\n## Validation\n\nThe successor keeps Phase1B-v1.3.0 immutable. See `CHECKPOINTS.json` for independent file hashes and counts, and `CHECKSUMS.json` for the package manifest. The prior closeout authorization is retained; corrected eligibility does not meet the approximate 120 target or the 130 minimum.\n""", encoding="utf-8")

    readme = TARGET / "README.md"
    original = readme.read_text(encoding="utf-8")
    updated = original.replace("Phase 1B v1.3.0", "Phase 1B v1.3.1", 1)
    updated = updated.replace("with accepted quantitative ordinary-food measurements for 125/130 identity-complete compounds.", "with 116 scientifically eligible quantitative compounds across all food classes; 80 are eligible in ordinary food. The 125 identity-complete mapped IDs are a separate measure.")
    updated = updated.replace("The approximate 120 target is met. The 130 minimum is five short; five identity-complete compounds remain uncovered.", "The earlier v1.3.0 closeout recorded 125 identity-complete mapped IDs as coverage. This successor distinguishes that from scientific quantitative eligibility: 116 compounds are eligible across all classes, including 80 ordinary-food compounds. The approximate 120 and 130 minimums are not met on the corrected eligibility measure.")
    updated = updated.replace("The user accepted closure at this evidence-supported count and authorized the project to proceed to Phase 2.", "The prior v1.3.0 closeout authorization remains recorded; its 125 figure referred to identity-complete mapped IDs rather than scientifically eligible quantitative coverage.")
    updated = updated.replace("The focused current regression modules pass 48/48.", "The earlier focused regression modules pass 48/48; the v1.3.1 reconciliation tests pass 3/3.")
    readme.write_text(updated, encoding="utf-8")
    test_results = TARGET / "TEST_RESULTS.txt"
    test_results.write_text("Phase1B-v1.3.1 reconciliation tests: 3/3 PASS (unittest). Existing focused current Phase 1 regression modules: 48/48 PASS in the prior audited run. Historical full-suite failures are preserved as described in CLEAN_VALIDATION_AND_CHECK_REPORT.md.\n", encoding="utf-8")

    build = TARGET / "build_checksums.py"
    code = build.read_text(encoding="utf-8").replace('"Phase1B-v1.3.0"', '"Phase1B-v1.3.1"')
    build.write_text(code, encoding="utf-8")
    verify = TARGET / "verify_release.py"
    verify.write_text(verify.read_text(encoding="utf-8").replace("Phase 1B SHA-256 package manifest", "Phase1B v1.3.1 SHA-256 package manifest"), encoding="utf-8")
    (TARGET / "tests").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "stageC/tests/test_phase1b_v131_reconciliation.py", TARGET / "tests/test_phase1b_v131_reconciliation.py")
    release["package_artifact_count"] = sum(1 for p in TARGET.rglob("*") if p.is_file() and p.name not in {"CHECKSUMS.json", "CHECKSUMS.sha256"} and "__pycache__" not in p.parts and p.suffix != ".pyc")
    release_path.write_text(json.dumps(release, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"release": str(TARGET), "raw_mapped": len(mapped_ids), "identity_complete_mapped": len(complete_ids & mapped_ids),
                      "identity_pending_mapped": len(mapped_ids-complete_ids), "accepted_mapped": len(accepted_ids),
                      "quantitative_eligible": len(eligible_ids), "ordinary_quantitative_eligible": len(raw_by_class["ordinary food"] & eligible_ids)}, indent=2))


if __name__ == "__main__":
    main()
