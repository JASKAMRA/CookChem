"""Create a narrow, primary-traceable concentration-ratio dataset.

This does not alter v0.1, historical data, or any deployed artifact.  The
target is explicitly an apparent concentration ratio and is never labelled
total-mass retention.
"""
from __future__ import annotations
import csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
MASTER = ROOT / "data/reviewed/cookchem_molecular_retention_master.csv"
PAIRS = ROOT / "stageC/phase2/data/observed_cooking_pairs.csv"

NUMERIC = ["Temperature_C", "Cooking_Time_min", "RDKit_Molecular_Weight", "RDKit_LogP", "RDKit_TPSA", "RDKit_HBond_Donors", "RDKit_HBond_Acceptors", "RDKit_Rotatable_Bonds", "RDKit_Aromatic_Rings", "RDKit_Hydroxyl_Groups"]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f: return list(csv.DictReader(f))

def write(path: Path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(rows)

def method(value: str) -> str:
    return " ".join(value.casefold().replace("-", " ").split())

def main():
    master = {r["Record_ID"]: r for r in read(MASTER)}
    pairs = read(PAIRS)
    rows, ledger, exclusions = [], [], []
    seen = set()
    for pair in pairs:
        rid = pair["source_stagea_record_id"]
        source = master.get(rid)
        if source is None:
            exclusions.append({"record_id": rid, "reason": "Phase 2 pointer absent from reviewed master"}); continue
        if pair["ratio_semantics"] not in {"concentration_ratio_not_mass_retention", "apparent_concentration_ratio_not_total_mass_retention"}:
            exclusions.append({"record_id": rid, "reason": "Phase 2 semantics are not approved concentration-ratio evidence"}); continue
        key = (source["DOI"], source["Canonical_Molecular_ID"], source["Food_Name"], method(source["Cooking_Method"]), source["Temperature_C"], source["Cooking_Time_min"])
        if key in seen:
            exclusions.append({"record_id": rid, "reason": "Exact duplicate source/compound/matrix/condition key"}); continue
        seen.add(key)
        row = {
            "record_id": rid, "doi": source["DOI"], "paper_id": source["Paper_ID"],
            "source_locator": pair["source_locator"], "compound": source["Canonical_Compound_Name"],
            "canonical_molecular_id": source["Canonical_Molecular_ID"], "compound_class": source["Compound_Class_Standardized"],
            "food_matrix": source["Food_Name"], "cooking_method": source["Cooking_Method"], "cooking_method_normalized": method(source["Cooking_Method"]),
            "cooking_medium": source["Cooking_Medium"], "raw_concentration": pair["raw_mean_value"], "cooked_concentration": pair["cooked_mean_value"],
            "concentration_unit": pair["measurement_unit"], "measurement_basis": pair["measurement_unit"],
            "target_name": "apparent_concentration_ratio_percent", "target_equation": "100 * C_cooked / C_raw",
            "target_value_percent": pair["concentration_ratio_percent"], "target_semantics": pair["ratio_semantics"],
            "evidence_status": "VERIFIED", "cooked_yield_status": "NOT_REPORTED", "total_mass_retention_status": "NOT_ESTABLISHED",
        }
        for col in NUMERIC: row[col] = source[col]
        rows.append(row)
        ledger.append({"record_id": rid, "doi": source["DOI"], "source_locator": pair["source_locator"], "evidence_status": "VERIFIED", "target_classification": "VERIFIED_APPARENT_RATIO", "basis": pair["measurement_unit"], "explanation": pair["limitations"]})
    fields = list(rows[0])
    write(OUT / "recovered_observations.csv", rows, fields)
    write(OUT / "clean_stageA_dataset.csv", rows, fields)
    write(OUT / "source_verification_ledger.csv", ledger, list(ledger[0]))
    write(OUT / "dataset_exclusion_log.csv", exclusions, ["record_id", "reason"])
    write(OUT / "new_literature_observations.csv", [], fields)
    manifest = {"package": "StageA_Recovery_v0.2.0_2026-11-10", "generated_at_utc": datetime.now(timezone.utc).isoformat(), "inputs": {str(MASTER.relative_to(ROOT)): digest(MASTER), str(PAIRS.relative_to(ROOT)): digest(PAIRS)}, "target": "100 * C_cooked / C_raw", "target_semantics": "apparent concentration ratio, not total-mass retention", "admitted_rows": len(rows), "excluded_duplicate_rows": len(exclusions), "model_deployment_authorized": False}
    (OUT / "dataset_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (OUT / "target_definition_contract.md").write_text("""# Experimental target contract\n\n## Target\n\n`apparent_concentration_ratio_percent = 100 × C_cooked / C_raw`\n\nBoth concentrations must use the same reported basis within an observed source pair. This target describes measured concentration change, including possible concentration effects of water/solid loss and extraction changes. It is **not** total analyte-mass retention.\n\n## Exclusions\n\nNo cooking yield, raw/cooked mass, moisture correction, or cooking-liquid disposition was available for the admitted observations. Therefore no total-mass target is calculated, no value is converted into an analyte-mass multiplier, and no Stage C cooked-exposure integration is authorized.\n""", encoding="utf-8")
    (OUT / "dataset_quality_report.md").write_text(f"""# Dataset quality report\n\n- Verified source-pair observations admitted: **{len(rows)}**\n- Exact duplicate condition records excluded: **{len(exclusions)}**\n- Unique molecular groups: **{len({r['canonical_molecular_id'] for r in rows})}**\n- Source DOI families: **{len({r['doi'] for r in rows})}**\n- Food matrices: **{len({r['food_matrix'] for r in rows})}**\n\nThis is a narrow experimental concentration-ratio dataset. Its two DOI families and two food matrices prohibit claims of source- or food-matrix-generalisation.\n""", encoding="utf-8")

if __name__ == "__main__": main()
