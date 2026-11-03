"""Append Batch 102 accepted measurements after strict baseline and identity gates.

This is an intentionally one-shot, fail-closed continuation script. It preserves
the existing dataset byte-for-byte as a prefix and does not alter Stage B.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
STAGE = ROOT / "stageC"
PHASE1B = STAGE / "reports" / "phase1b"
BATCH = PHASE1B / "batches" / "batch_102_scientific_coverage"
FOOD = STAGE / "data" / "food_composition" / "food_composition.csv"
MAPPING = STAGE / "data" / "compound_food_mapping" / "compound_food_mapping.csv"
AUDIT = STAGE / "data" / "stage_b_snapshot_20261103" / "identity_structure_audit.csv"
COMPOUNDS = STAGE / "data" / "stage_b_snapshot_20261103" / "compound_registry.csv"
CHECKPOINT = PHASE1B / "CHECKPOINTS.json"

EXPECTED_FOOD_SHA = "616a62c3cce8426b058e8aee3c6e746438ee2eea49680f2da492e10101172115"
EXPECTED_MAPPING_SHA = "9774a96396107409a53f6bef5960daffacf5e40ae25d26e7ecaabbbc8c1d6bc1"
ACCEPTED = {
    "MOL-V17-CID-5280704": {
        "food_record_id": "APIGETRIN-FOODS2021-LAMBSLETTUCE-STANDARD",
        "food_name": "Lamb's lettuce (Valerianella locusta), edible leaves",
        "common_name": "Lamb's lettuce",
        "scientific_name": "Valerianella locusta",
        "food_database": "Primary analytical food-composition study",
        "food_database_record_id": "Table 3; Apigenin-7-O-glucoside, standard 1/2 Hoagland condition",
        "food_part": "Edible leaves",
        "raw_or_processed_state": "raw",
        "compound_id": "MOL-V17-CID-5280704",
        "compound_name": "Apigetrin",
        "food_use_classification": "ordinary food",
        "pubchem_cid": "5280704",
        "inchikey": "KMOUJOKENFFTPU-QNDFHXLGSA-N",
        "reported_concentration": "0.012",
        "reported_unit": "µg/g",
        "moisture_basis": "fresh weight (FW)",
        "analytical_method": "HPLC-DAD quantification; LC-MS/MS identification against the reference standard (m/z 431 [M-H]-; fragment 269)",
        "sample_size": "Treatment study used 2 blocks x 3 replicates per treatment/block, 50 plants/replicate; analyte-specific biological n not separately stated; analytical triplicate reported.",
        "source_title": "Phenolic and Carotenoid Profile of Lamb’s Lettuce and Improvement of the Bioactive Content by Preharvest Conditions",
        "doi": "10.3390/foods10010188",
        "database_reference": "Table 3; table heading explicitly gives µg/g fresh weight",
        "source_url": "https://www.mdpi.com/2304-8158/10/1/188",
        "publication_year": "2021",
        "source_classification": "Primary analytical measurement",
        "source_verification_status": "full-text verified",
        "extraction_notes": "The source directly reports apigenin-7-O-glucoside at 0.012 µg/g FW in lamb’s lettuce under the standard nutrient condition. The table value is retained as reported; no graph reconstruction or conversion across moisture basis was used.",
        "uncertainty_notes": "The paper describes treatment replication and analytical triplicates but does not separately state biological n for this Table 3 analyte value. Analyte-specific LOD/LOQ was not located."
    },
    "MOL-V17-CID-5281673": {
        "food_record_id": "MYRICITRIN-PLANTS2024-SPINACH",
        "food_name": "Spinach (Spinacia oleracea), edible leaves",
        "common_name": "Spinach",
        "scientific_name": "Spinacia oleracea",
        "food_database": "Primary analytical food-composition study",
        "food_database_record_id": "Results section 2.3; Supplementary Table S3; spinach row, myricitrin",
        "food_part": "Edible leaves",
        "raw_or_processed_state": "raw",
        "compound_id": "MOL-V17-CID-5281673",
        "compound_name": "Myricitrin",
        "food_use_classification": "ordinary food",
        "pubchem_cid": "5281673",
        "inchikey": "DCYOADKBABEMIQ-OWMUPTOHSA-N",
        "reported_concentration": "398.2",
        "reported_unit": "mg/kg",
        "moisture_basis": "as-analyzed homogenized food-sample mass; moisture state and correction not reported",
        "analytical_method": "HPLC-DAD against authentic Sigma-Aldrich standards; overlapping retention-time compounds checked across all four gradient systems",
        "extraction_method": "Pre-homogenized food sample (5 ± 0.3 g) extracted in methanol/water/formic acid (80:19:1), sonicated 24 h, centrifuged and filtered.",
        "sample_size": "Supermarket food sample; biological sample count not stated; analytical triplicate.",
        "quantification_limit": "30.83 µg/mL calibration-solution LOQ; not a matrix-specific LOQ",
        "source_title": "Investigation of Pharmacologically Important Polyphenolic Secondary Metabolites in Plant-based Food Samples Using HPLC-DAD",
        "doi": "10.3390/plants13101311",
        "pmid": "38864076",
        "database_reference": "Results section 2.3 gives spinach myricitrin 398.2 mg/kg; Table S3 is cited for quantified results",
        "source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11124887/",
        "publication_year": "2024",
        "source_classification": "Primary analytical measurement",
        "source_verification_status": "full-text verified",
        "extraction_notes": "The exact spinach value (398.2 mg/kg) is stated in the article’s Results, is tied to myricitrin, and the methods calculate concentration from sample mass. The mass basis is retained as analyzed; it is not relabelled fresh-weight or dry-weight.",
        "uncertainty_notes": "Moisture state/correction and biological n are not reported. The paper reports an analyte-specific calibration-solution LOQ; it is not treated as a matrix LOQ. Apple values have a separate textual conflict and were not ingested."
    }
}

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def append_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> bytes:
    before = path.read_bytes()
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\r\n")
    writer.writerows(rows)
    with path.open("ab") as f:
        f.write(stream.getvalue().encode("utf-8"))
    after = path.read_bytes()
    if not after.startswith(before):
        raise RuntimeError(f"Existing bytes were not preserved as a prefix: {path}")
    return before

def main() -> None:
    cp = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    if cp.get("checkpoint_id") != "Phase1B-2026-11-03-batch-101-final-continuation":
        raise RuntimeError("Expected Batch 101 checkpoint; stop and inspect current state.")
    food_bytes, mapping_bytes = FOOD.read_bytes(), MAPPING.read_bytes()
    if digest(food_bytes) != EXPECTED_FOOD_SHA or digest(mapping_bytes) != EXPECTED_MAPPING_SHA:
        raise RuntimeError("Active data hashes differ from verified Batch 101 baseline; no files changed.")
    foods, mappings = read_csv(FOOD), read_csv(MAPPING)
    if len(foods) != 539 or len(mappings) != 539:
        raise RuntimeError("Expected 539 food records and 539 mappings; no files changed.")

    audit = {r["Compound_ID"]: r for r in read_csv(AUDIT)}
    compounds = read_csv(COMPOUNDS)
    compound_by_id = {r["Compound_ID"]: r for r in compounds}
    for cid, record in ACCEPTED.items():
        a = audit.get(cid, {})
        c = compound_by_id.get(cid, {})
        if a.get("Status") != "Complete" or a.get("Exact_Key_Match") != "True":
            raise RuntimeError(f"Identity gate failed for {cid}; no files changed.")
        if a.get("PubChem_CID") != record["pubchem_cid"] or a.get("Registry_InChIKey") != record["inchikey"]:
            raise RuntimeError(f"CID/InChIKey mismatch for {cid}; no files changed.")
        if c.get("PubChem_CID") != record["pubchem_cid"] or c.get("InChIKey") != record["inchikey"]:
            raise RuntimeError(f"Snapshot registry mismatch for {cid}; no files changed.")
        if any(r["compound_id"] == cid for r in foods):
            raise RuntimeError(f"{cid} already has a food record; duplicate prevention stopped append.")

    sys.path.insert(0, str(STAGE / "src"))
    from stage_c.food_composition import FIELDS, normalize_record, validate_food_record
    from stage_c.compound_mapping import MAPPING_FIELDS, build_mappings
    new_foods = [normalize_record(r) for r in ACCEPTED.values()]
    for record in new_foods:
        errors = validate_food_record(record)
        if errors:
            raise RuntimeError(f"Food record validation failed for {record['food_record_id']}: {errors}")
    new_mappings = build_mappings(compounds, new_foods)
    if len(new_mappings) != 2 or any(r["mapping_status"] not in {"Exact identity match", "Verified synonym match", "Structure-supported match"} or r["quantitative_data_available"] != "true" for r in new_mappings):
        raise RuntimeError("Mapping eligibility failed; no files changed.")
    if any(r["mapping_id"] in {m["mapping_id"] for m in mappings} for r in new_mappings):
        raise RuntimeError("Duplicate mapping ID; no files changed.")
    if len({r["food_record_id"] for r in foods + new_foods}) != len(foods) + len(new_foods):
        raise RuntimeError("Duplicate food record ID; no files changed.")

    BATCH.mkdir(parents=True, exist_ok=True)
    (BATCH / "CHECKPOINTS_BATCH101_PRE_APPEND.json").write_bytes(CHECKPOINT.read_bytes())
    append_rows(FOOD, FIELDS, new_foods)
    append_rows(MAPPING, MAPPING_FIELDS, new_mappings)
    with (BATCH / "accepted_rows.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(new_foods)
    with (BATCH / "accepted_mappings.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MAPPING_FIELDS); w.writeheader(); w.writerows(new_mappings)

    after_food, after_mapping = read_csv(FOOD), read_csv(MAPPING)
    if len(after_food) != 541 or len(after_mapping) != 541:
        raise RuntimeError("Post-append row count failed; review durable prefix-preserving append.")
    if not FOOD.read_bytes().startswith(food_bytes) or not MAPPING.read_bytes().startswith(mapping_bytes):
        raise RuntimeError("Post-append integrity check failed.")
    print(json.dumps({"status":"APPEND_PASS","accepted_records":2,"accepted_mappings":2,"food_records":len(after_food),"mapping_rows":len(after_mapping),"food_sha256":digest(FOOD.read_bytes()),"mapping_sha256":digest(MAPPING.read_bytes()),"mapping_statuses":[r["mapping_status"] for r in new_mappings]},indent=2))

if __name__ == "__main__":
    main()
