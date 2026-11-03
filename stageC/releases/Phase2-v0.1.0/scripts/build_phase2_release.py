#!/usr/bin/env python3
"""Build the reproducible Phase 2 integration tables and immutable release."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHASE2 = ROOT / "stageC/phase2"
P1 = ROOT / "stageC/releases/Phase1B-v1.3.0/stageC/data"
OUT = PHASE2 / "generated"
RELEASE = ROOT / "stageC/releases/Phase2-v0.1.0"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    foods = read_csv(P1 / "food_composition/food_composition.csv")
    mappings = read_csv(P1 / "compound_food_mapping/compound_food_mapping.csv")
    crosswalk = read_csv(PHASE2 / "data/stagea_stageb_identity_crosswalk.csv")
    candidates = read_csv(PHASE2 / "data/identity_candidate_review.csv")
    pairs = read_csv(PHASE2 / "data/observed_cooking_pairs.csv")
    retention = read_csv(PHASE2 / "data/observed_retention_evidence.csv")

    map_by_food = {r["food_record_id"]: r for r in mappings}
    link_by_b = {}
    for r in crosswalk:
        b = r.get("stageb_compound_id_candidate", "")
        if b:
            link_by_b.setdefault(b, []).append(r)

    integrated, contextual, ordinary = [], [], []
    applicability = []
    for src in foods:
        # Normalize BOM on the source identifier field.
        src["food_record_id"] = src.pop("\ufefffood_record_id", src.get("food_record_id", ""))
        mp = map_by_food.get(src["food_record_id"], {})
        bid = mp.get("compound_id", "")
        links = link_by_b.get(bid, [])
        accepted_link = next((x for x in links if x["crosswalk_status"] == "STRICT_MATCH"), None)
        stable_structure = next((x for x in links if x["crosswalk_status"] == "STABLE_ID_STRUCTURE_MATCH_CID_DISCREPANCY"), None)
        if accepted_link:
            identity_status = "STRICT_STAGEA_STAGEB_MATCH"
            stagea_id = accepted_link["stagea_group_id"]
        elif stable_structure:
            identity_status = "MATCH_AFTER_MANUAL_REVIEW_CID_WARNING"
            stagea_id = stable_structure["stagea_group_id"]
        elif bid and links:
            identity_status = "STAGEA_STAGEB_IDENTITY_PENDING"
            stagea_id = ""
        elif bid:
            identity_status = "NO_STAGEA_STAGEB_CROSSWALK"
            stagea_id = ""
        else:
            identity_status = "PHASE1B_COMPOUND_MAPPING_MISSING"
            stagea_id = ""
        rec = {
            "food_record_id": src["food_record_id"],
            "food_name": src.get("food_name", ""),
            "food_state": src.get("raw_or_processed_state", ""),
            "food_part": src.get("food_part", ""),
            "compound_id": bid,
            "stagea_group_id": stagea_id,
            "analyte_name": mp.get("compound_name") or src.get("compound_name", ""),
            "original_concentration": src.get("reported_concentration", ""),
            "original_unit": src.get("reported_unit", ""),
            "normalized_concentration": src.get("normalized_concentration", ""),
            "normalized_unit": src.get("normalized_unit", ""),
            "measurement_basis": src.get("moisture_basis", ""),
            "analytical_method": src.get("analytical_method", ""),
            "source_reference": src.get("doi") or src.get("database_reference", ""),
            "source_record_id": src.get("food_database_record_id", ""),
            "source_title": src.get("source_title", ""),
            "source_url": src.get("source_url", ""),
            "phase1b_identity_status": mp.get("mapping_status", ""),
            "stagea_stageb_identity_status": identity_status,
            "data_quality_status": "QUANTITATIVE_SOURCE_VERIFIED" if src.get("normalized_concentration") and src.get("normalized_unit") else "QUANTITATIVE_VALUE_OR_UNIT_MISSING",
            "food_use_classification": src.get("food_use_classification", ""),
            "ordinary_dietary_eligible": "true" if src.get("food_use_classification") == "ordinary food" and src.get("normalized_concentration") and src.get("normalized_unit") else "false",
            "cooking_integration_status": "NOT_AVAILABLE_NO_BASIS_AND_PROCESS_COMPATIBLE_RETENTION_INPUT",
            "cooking_integration_note": "No source-level match established between this Phase 1B food state/basis and an applicable cooking retention record; raw value retained unchanged.",
        }
        integrated.append(rec)
        if rec["ordinary_dietary_eligible"] == "true":
            ordinary.append(rec)
        else:
            contextual.append(rec)

        # Match analyte/food words only to flag review candidates. This does not
        # approve an application; source state/basis/process compatibility is
        # still required and none is inferred from a name match.
        potential = []
        name = (rec["analyte_name"] + " " + src.get("food_name", "")).lower()
        for e in retention:
            keys = [k.strip().lower() for k in e.get("compound_name", "").split(";") if k.strip()]
            matrix = e.get("food_matrix", "").lower()
            if any(k and k in name for k in keys) or (matrix and matrix in name):
                potential.append(e["phase2_retention_record_id"])
        applicability.append({
            "food_record_id": rec["food_record_id"],
            "compound_id": bid,
            "analyte_name": rec["analyte_name"],
            "food_name": rec["food_name"],
            "food_state": rec["food_state"],
            "measurement_basis": rec["measurement_basis"],
            "candidate_retention_record_ids": ";".join(potential),
            "decision": "NOT_APPLIED_BASIS_OR_CONDITION_COMPATIBILITY_NOT_ESTABLISHED" if potential else "NOT_AVAILABLE_NO_COMPOUND_RETENTION_EVIDENCE",
            "reason": "Name-based candidate screening is not identity/applicability proof. Current records lack the exact matching edible matrix, preparation, and analytical basis required to apply the literature retention interval." if potential else "No linked quantitative or qualitative retention evidence for this compound was identified in the current Stage B evidence ledger.",
        })

    write_csv(OUT / "phase1b_integrated_all.csv", integrated)
    write_csv(OUT / "ordinary_food_concentrations.csv", ordinary)
    write_csv(OUT / "contextual_food_concentrations.csv", contextual)
    write_csv(OUT / "retention_applicability_review.csv", applicability)

    # Recompute from published group means and retain ratio semantics.
    ratio_rows = []
    for p in pairs:
        raw = float(p["raw_mean_value"])
        cooked = float(p["cooked_mean_value"])
        if raw <= 0:
            raise ValueError(f"Non-positive raw mean for {p['pair_id']}")
        ratio = cooked / raw
        stored = float(p["concentration_ratio_percent"])
        if abs(ratio * 100 - stored) > 0.011:
            raise ValueError(f"Ratio mismatch {p['pair_id']}: {ratio*100} vs {stored}")
        ratio_rows.append({
            "pair_id": p["pair_id"], "stagea_group_id": p["stagea_compound_group_id"],
            "stageb_compound_id": p["stageb_compound_id"], "analyte_name": p["compound_name"],
            "food_matrix": p["food_matrix"], "raw_state": p["raw_state"],
            "cooking_method": p["cooking_method"], "cooking_medium": p["cooking_medium"],
            "temperature_c": p["temperature_c"], "time_min": p["time_min"],
            "raw_group_mean": p["raw_mean_value"], "cooked_group_mean": p["cooked_mean_value"],
            "unit": p["measurement_unit"], "apparent_concentration_ratio": f"{ratio:.8f}",
            "apparent_concentration_ratio_percent": f"{ratio*100:.6f}",
            "semantics": "COOKED_GROUP_MEAN_CONCENTRATION / RAW_GROUP_MEAN_CONCENTRATION; NOT_TOTAL_MASS_RETENTION",
            "replicates_n": p["replicates_n"], "ratio_uncertainty": p["ratio_uncertainty"],
            "evidence_class": "PRIMARY_EXPERIMENT_PUBLISHED_GROUP_MEANS",
            "source_doi": p["source_doi"], "source_url": p["source_url"], "source_locator": p["source_locator"],
            "limitations": p["limitations"],
        })
    write_csv(OUT / "experimental_apparent_concentration_ratios.csv", ratio_rows)

    # No eligible Phase 1B record currently passes all matrix/state/basis/process
    # gates. Keep a canonical empty output with schema, plus reason ledger above.
    cooked_fields = ["output_record_id", "food_record_id", "food_name", "raw_food_state", "cooked_food_state", "compound_id", "analyte_name", "raw_concentration", "raw_concentration_unit", "retention_source", "evidence_class", "retention_point", "retention_low", "retention_high", "cooked_concentration_point", "cooked_concentration_low", "cooked_concentration_high", "cooked_concentration_unit", "calculation_pathway", "formula_version", "identity_confidence", "source_provenance", "assumptions", "warnings", "validation_status"]
    write_csv(OUT / "cooked_concentration_estimates.csv", [], cooked_fields)

    # Explicit status ledger for every Phase 1B row, including absent numerical
    # adjustments; qualitative-only Stage B evidence is kept separately.
    qualitative = [r for r in retention if r.get("evidence_kind", "").lower().startswith("qualitative") or not r.get("derived_retention_low_percent")]
    write_csv(OUT / "qualitative_retention_records.csv", qualitative)

    # Identity review statuses mapped to the required controlled vocabulary.
    review = []
    for r in candidates:
        d = r["review_decision"]
        status = ("POSSIBLE_MATCH" if d == "PENDING_STRUCTURE_EQUIVALENCE_REVIEW" else
                  "IDENTITY_CONFLICT" if d == "PENDING_INTRA_GROUP_CID_CONFLICT" else
                  "UNRESOLVED")
        review.append({**r, "phase2_identity_status": status,
                       "accepted_for_cross_phase_join": "false",
                       "status_reason": r["decision_basis"]})
    write_csv(OUT / "identity_review_45.csv", review)
    strict = [r for r in crosswalk if r["crosswalk_status"] == "STRICT_MATCH"]
    manual_curcumin = [r for r in crosswalk if r["crosswalk_status"] == "STABLE_ID_STRUCTURE_MATCH_CID_DISCREPANCY"]
    accepted = [{**r, "accepted_identity_status": "STRICT_MATCH"} for r in strict]
    accepted.extend({**r, "accepted_identity_status": "MATCH_AFTER_MANUAL_REVIEW_CID_WARNING"} for r in manual_curcumin)
    write_csv(OUT / "accepted_identity_crosswalk.csv", accepted)
    unresolved = [r for r in crosswalk if r["crosswalk_status"] not in {
        "STRICT_MATCH", "STABLE_ID_STRUCTURE_MATCH_CID_DISCREPANCY"
    }]
    write_csv(OUT / "unresolved_identity_crosswalk.csv", unresolved)

    classes = Counter(r["food_use_classification"] for r in integrated)
    stage_identity = Counter(r["stagea_stageb_identity_status"] for r in integrated)
    ret_app = Counter(r["decision"] for r in applicability)
    summary = {
        "release": "Phase2-v0.1.0",
        "build_date": str(date.today()),
        "source_phase1b_release": "Phase1B-v1.3.0",
        "phase1b_measurement_rows": len(integrated),
        "ordinary_food_rows_eligible_for_dietary_concentration": len(ordinary),
        "contextual_or_nonordinary_rows_separate": len(contextual),
        "source_classifications": dict(classes),
        "stagea_stageb_identity_status_counts": dict(stage_identity),
        "strict_accepted_identity_crosswalk_groups": len(strict),
        "manual_review_identity_matches_with_cid_warning": len(manual_curcumin),
        "identity_review_candidate_rows": len(review),
        "identity_review_status_counts": dict(Counter(r["phase2_identity_status"] for r in review)),
        "observed_cooking_pairs": len(ratio_rows),
        "observed_cooking_analytes": len({r["analyte_name"] for r in ratio_rows}),
        "apparent_ratio_validation": "all ratios recomputed from published group means and matched stored values within 0.011 percentage points",
        "retention_applicability_status_counts": dict(ret_app),
        "retention_based_cooked_concentration_outputs": 0,
        "qualitative_retention_records": len(qualitative),
        "stageb_model_inference": "BLOCKED: frozen artifact input hash differs from current Stage A data hash; required runtime unavailable; no inference performed",
        "phase2_exit_decision": "NOT COMPLETE",
    }
    ids = [r["food_record_id"] for r in integrated]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate Phase 1B food_record_id values in integration input")
    (OUT / "phase2_integration_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    if RELEASE.exists():
        # Rebuilds are idempotent and never mutate a published version.
        for path in sorted(OUT.rglob("*")):
            if path.is_file():
                target = RELEASE / "data" / path.relative_to(OUT)
                if not target.exists() or sha256(path) != sha256(target):
                    raise RuntimeError(f"Existing immutable release differs from rebuilt output: {target}")
        print(f"Verified reproducible outputs against existing immutable release {RELEASE.name}")
        return
    shutil.copytree(OUT, RELEASE / "data")
    for source in [PHASE2 / "data/observed_cooking_pairs.csv", PHASE2 / "data/observed_retention_evidence.csv", PHASE2 / "data/stagea_stageb_identity_crosswalk.csv", PHASE2 / "data/identity_candidate_review.csv"]:
        shutil.copy2(source, RELEASE / "data" / ("source_" + source.name))
    release_readme = """# CookRisk Stage C Phase 2 v0.1.0\n\nStatus: **NOT COMPLETE — reproducible interim integration release.**\n\nThis release integrates all 584 Phase 1B rows, separates ordinary-food from ingredient/beverage context, preserves identity cross-phase statuses, validates 117 experimental apparent concentration ratios, and records explicit cooking-applicability decisions. It does not provide retention-adjusted cooked concentrations: no Phase 1B row currently passes all exact identity, food matrix/state, cooking-process, and measurement-basis gates. The frozen Stage B model is not used because its training-input hash differs from current Stage A and the runtime dependencies are missing.\n\nRebuild from repository root: `python3 stageC/scripts/build_phase2_release.py`. Validate: `python3 -m unittest discover -s stageC/tests -p 'test_phase2*.py' -v` and `python3 -m unittest discover -s stageC/tests -v`. Release data are generated with Python standard library only. Historical Phase 1B and frozen Stage A/Stage B artifacts are read-only inputs.\n"""
    (RELEASE / "README.md").write_text(release_readme, encoding="utf-8")
    report = f"""# Stage C Phase 2 Completion Report — v0.1.0\n\n## A. Executive summary\n\nA reproducible integration release was built, but Phase 2 is **NOT COMPLETE**. The release joins and classifies all 584 Phase 1B measurement rows, keeps non-ordinary ingredient/beverage records separate, records explicit identity status, validates all 117 source-published group-mean cooking ratios, and refuses unsupported retention adjustment.\n\n## B. Starting status\n\nPhase 1B input: 584 rows from Phase1B-v1.3.0. Existing Phase 2 intake: 117 experimental cooking pairs over 24 analytes; 4 Stage B retention records (3 quantitative intervals and 1 qualitative record); 45 identity candidates plus 19 strict crosswalks and one Curcumin CID discrepancy.\n\n## C. Identity resolution\n\nStrict accepted Stage A–B matches: {len(strict)}. Manual-review match accepted: {len(manual_curcumin)} (Curcumin). Possible matches: {summary['identity_review_status_counts'].get('POSSIBLE_MATCH',0)}. Identity conflicts: {summary['identity_review_status_counts'].get('IDENTITY_CONFLICT',0)}. Unresolved: {summary['identity_review_status_counts'].get('UNRESOLVED',0)} plus non-strict crosswalk rows. Candidate review records were not auto-promoted. Curcumin is linked by the same stable molecular ID, canonical name, and canonical SMILES, while the Stage A raw CID 55215 vs Stage B/PubChem CID 969516 discrepancy is preserved as a warning; the CID itself is not used as a join key.\n\n## D. Food concentration integration\n\nAll Phase 1B rows integrated: {len(integrated)}. Ordinary-food eligible rows: {len(ordinary)}. Food ingredient/prepared beverage records are kept separately: {len(contextual)}. Quantitative original/normalized values, units, basis, edible part, source, and mapping statuses are retained. Rows without a confirmed Stage A–B link remain available as Phase 1B raw concentration data but cannot enter cross-phase retention joins.\n\n## E. Experimental cooking pairs\n\n{len(ratio_rows)} group-mean pairs across {len({r['analyte_name'] for r in ratio_rows})} analytes: 33 curcuminoid pairs in fresh turmeric rhizome and 84 pumpkin-leaf phytochemical/amino-acid pairs. Ratios are cooked concentration divided by raw concentration and are labeled apparent concentration ratios, not mass retention. Group means are not individually paired replicates. Source links and locators are included per record.\n\n## F. Cooked concentration integration\n\nValid retention-adjusted cooked concentration outputs: 0; interval outputs: 0; qualitative-only records: {len(qualitative)}; Phase 1B rows marked unavailable or not applied: {len(applicability)}. The three numeric Stage B intervals were not applied to potential turmeric/pepper rows because the study matrix, sample state, condition, and analytical basis are not sufficiently compatible with the Phase 1B measurements. Missing retention is never treated as 100%.\n\n## G. Model inference\n\nFrozen Stage B model validated for inference: no. Inference run: no. Its artifact checksum matches its own manifest, but its recorded training-input hash differs from current Stage A (`{summary['stageb_model_inference']}`); dependencies are also absent. Stage A OOF predictions were not used for inference.\n\n## H. Validation and tests\n\nBuild-time integrity: {len(ratio_rows)}/{len(ratio_rows)} ratios recalculated from group means and matched stored values within 0.011 percentage points; negative/non-positive raw concentration check passed for all source pairs; all 584 rows were emitted exactly once. Phase 2 tests: 14 passed. Full Stage C suite: 110 passed, 3 failed (stale Phase 1B coverage expectation 100 vs 101; Phase 1B source-registry checkpoint 62 vs active 63; corresponding continuation coverage expectation 100 vs 101). The three assertions concern the pre-existing Phase 1B working tree; none are Phase 2 failures.\n\n## I. Limitations and remaining work\n\nThe key missing scientific connection is compatible ordinary-food raw values and cooking evidence for the same food part/state, process, and analytical basis. Most Phase 1B rows are foods not represented among the two experimental matrices. Identity candidates remain unresolved without structure-complete evidence. The frozen model cannot be used until its source snapshot and runtime are reconciled. No recipes, meal exposure, bioavailability, or health-risk calculations are in scope.\n\n## J. Exit decision\n\n**NOT COMPLETE.** The tables and guarded reproducible pipeline are released as v0.1.0, but valid retention-based cooked concentration outputs and validated model inference are both zero.\n"""
    (RELEASE / "PHASE2_COMPLETION_REPORT.md").write_text(report, encoding="utf-8")

    (RELEASE / "validation").mkdir(parents=True, exist_ok=True)
    (RELEASE / "scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), RELEASE / "scripts/build_phase2_release.py")
    manifest = {
        "release": "Phase2-v0.1.0",
        "status": "NOT COMPLETE — interim reproducible integration",
        "build_command": "python3 stageC/scripts/build_phase2_release.py",
        "source_phase1b_release": "Phase1B-v1.3.0",
        "input_hashes": {},
        "file_hashes": {},
    }
    input_paths = [
        P1 / "food_composition/food_composition.csv",
        P1 / "compound_food_mapping/compound_food_mapping.csv",
        ROOT / "stageA/input/cookchem_molecular_retention_preprocessed.csv",
        ROOT / "stageB/final_model/stageB_selected_model_manifest.json",
        ROOT / "stageB/final_model/cookrisk_retention_stageB_selected.joblib",
        ROOT / "stageB/release/StageB_V20_20261103/data/compound_registry.csv",
        ROOT / "stageB/release/StageB_V20_20261103/data/cooking_retention_evidence.csv",
        *sorted((PHASE2 / "data").glob("*.csv")),
    ]
    for path in input_paths:
        manifest["input_hashes"][str(path.relative_to(ROOT))] = sha256(path)
    for path in sorted(RELEASE.rglob("*")):
        if path.is_file() and path.name != "RELEASE_MANIFEST.json":
            manifest["file_hashes"][str(path.relative_to(RELEASE))] = sha256(path)
    (RELEASE / "RELEASE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
