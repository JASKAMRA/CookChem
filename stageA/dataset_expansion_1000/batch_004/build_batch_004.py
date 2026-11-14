"""Controlled expansion batch 004: edible chestnut seeds, individual HPLC-MS/MS analytes."""
from pathlib import Path
import hashlib
import json
import pandas as pd

R = Path(__file__).resolve().parent
PARENT = R.parent / "batch_003" / "updated_master_dataset.csv"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name, text): (R / name).write_text(text.strip() + "\n", encoding="utf-8")

base = pd.read_csv(PARENT)
def template(name):
    found = base.loc[base.compound.astype(str).str.casefold().eq(name.casefold())]
    assert len(found), name
    return found.iloc[0]

# Table 2, seed columns only: raw mean/SD then four treatment means/SD.
# All omitted table analytes lack a pre-existing exact descriptor identity, have
# a stereochemical mismatch, are aggregate values, or are not edible seed data.
values = {
    "Chlorogenic Acid": (0.94, 0.07, [("Boiling", "boiling", 0.63, 0.02, 100, 15, "water, 1:2 w/v"), ("Microwave roasting", "microwave roasting", 0.16, 0.02, pd.NA, 4, "not reported"), ("Oven roasting", "oven roasting", 0.54, 0.03, 180, 25, "dry oven"), ("Pan frying", "pan frying", 0.66, 0.05, pd.NA, 10, "not reported")]),
    "Caffeic Acid": (3.15, 0.01, [("Boiling", "boiling", 1.50, 0.01, 100, 15, "water, 1:2 w/v"), ("Microwave roasting", "microwave roasting", 0.19, 0.01, pd.NA, 4, "not reported"), ("Oven roasting", "oven roasting", 3.28, 0.01, 180, 25, "dry oven"), ("Pan frying", "pan frying", 1.39, 0.01, pd.NA, 10, "not reported")]),
    "Syringic acid": (0.26, 0.01, [("Boiling", "boiling", 0.44, 0.01, 100, 15, "water, 1:2 w/v"), ("Microwave roasting", "microwave roasting", 0.35, 0.01, pd.NA, 4, "not reported"), ("Oven roasting", "oven roasting", 0.35, 0.01, 180, 25, "dry oven"), ("Pan frying", "pan frying", 0.35, 0.01, pd.NA, 10, "not reported")]),
    "P-Coumaric Acid": (6.73, 0.03, [("Boiling", "boiling", 2.28, 0.03, 100, 15, "water, 1:2 w/v"), ("Microwave roasting", "microwave roasting", 0.71, 0.01, pd.NA, 4, "not reported"), ("Oven roasting", "oven roasting", 4.78, 0.01, 180, 25, "dry oven"), ("Pan frying", "pan frying", 2.96, 0.01, pd.NA, 10, "not reported")]),
    "Ferulic Acid": (3.37, 0.01, [("Boiling", "boiling", 1.55, 0.01, 100, 15, "water, 1:2 w/v"), ("Microwave roasting", "microwave roasting", 0.25, 0.01, pd.NA, 4, "not reported"), ("Oven roasting", "oven roasting", 2.15, 0.01, 180, 25, "dry oven"), ("Pan frying", "pan frying", 9.36, 0.01, pd.NA, 10, "not reported")]),
    "Rutin": (1.59, 0.03, [("Boiling", "boiling", 1.65, 0.03, 100, 15, "water, 1:2 w/v"), ("Microwave roasting", "microwave roasting", 1.24, 0.02, pd.NA, 4, "not reported"), ("Oven roasting", "oven roasting", 2.05, 0.01, 180, 25, "dry oven"), ("Pan frying", "pan frying", 1.91, 0.01, pd.NA, 10, "not reported")]),
    "Isoquercitrin": (2.17, 0.01, [("Boiling", "boiling", 2.99, 0.01, 100, 15, "water, 1:2 w/v"), ("Microwave roasting", "microwave roasting", 0.83, 0.01, pd.NA, 4, "not reported"), ("Oven roasting", "oven roasting", 2.63, 0.05, 180, 25, "dry oven"), ("Pan frying", "pan frying", 1.75, 0.03, pd.NA, 10, "not reported")]),
    "Quercetin": (0.22, 0.01, [("Boiling", "boiling", 0.25, 0.005, 100, 15, "water, 1:2 w/v"), ("Microwave roasting", "microwave roasting", 0.06, 0.01, pd.NA, 4, "not reported"), ("Oven roasting", "oven roasting", 0.13, 0.004, 180, 25, "dry oven"), ("Pan frying", "pan frying", 0.10, 0.001, pd.NA, 10, "not reported")]),
    "Kaempferol": (0.98, 0.01, [("Boiling", "boiling", 1.11, 0.03, 100, 15, "water, 1:2 w/v"), ("Microwave roasting", "microwave roasting", 1.04, 0.01, pd.NA, 4, "not reported"), ("Oven roasting", "oven roasting", 1.18, 0.02, 180, 25, "dry oven"), ("Pan frying", "pan frying", 0.13, 0.01, pd.NA, 10, "not reported")]),
}

rows = []
for compound, (raw, raw_sd, treatments) in values.items():
    src = template(compound)
    for method, normalized, cooked, cooked_sd, temp, minutes, medium in treatments:
        row = {column: src[column] for column in base.columns}
        row.update({
            "observation_id": f"LIT-MUSTAFA2021-CHESTNUT_SEED-{compound.upper().replace(' ', '_').replace('-', '_')}-{normalized.upper().replace(' ', '_')}",
            "original_record_id": "", "doi": "10.3390/plants10102192", "paper_id": "NEW_LITERATURE_MUSTAFA_2021",
            "source_locator": "Table 2, seed columns; Methods §§3.2–3.4",
            "compound": compound, "food_matrix": "Sweet chestnut edible seed (Castanea sativa)",
            "cooking_method": method, "cooking_method_normalized": normalized, "cooking_medium": medium,
            "raw_concentration": raw, "cooked_concentration": cooked, "concentration_unit": "mg/kg dry weight", "measurement_basis": "dry weight (DW)",
            "target_name": "apparent_concentration_ratio_percent", "target_equation": "100 * C_cooked / C_raw", "target_value_percent": 100 * cooked / raw,
            "target_semantics": "apparent concentration ratio; not total-mass retention", "evidence_status": "VERIFIED_PRIMARY_TABLE",
            "cooked_yield_status": "NOT_REPORTED", "total_mass_retention_status": "NOT_ESTABLISHED",
            "source_detail": "Mustafa et al. (2021), Table 2 seed values. Individual HPLC-MS/MS analyte, 70% ethanol:water extract, dry-weight basis; analysis performed twice and reported as mean ± SD.",
            "Temperature_C": temp, "Cooking_Time_min": minutes, "raw_sd": raw_sd, "cooked_sd": cooked_sd,
            "reported_replicate_design": "HPLC analysis performed twice; reported mean ± SD; one dataset row per cooking condition",
            "analytical_definition": "70% ethanol:water extract; individual HPLC-MS/MS analyte",
        })
        rows.append(row)

new = pd.DataFrame(rows, columns=base.columns)
master = pd.concat([base, new], ignore_index=True)
assert len(new) == 36 and len(master) == 524 and master.doi.nunique() == 15
assert new.canonical_molecular_id.notna().all()
assert (new.target_value_percent.round(9) == (100 * new.cooked_concentration / new.raw_concentration).round(9)).all()
master.to_csv(R / "updated_master_dataset.csv", index=False)
new.to_csv(R / "verified_observations.csv", index=False)
new.to_csv(R / "extracted_observations.csv", index=False)

registry = pd.DataFrame([{
    "doi":"10.3390/plants10102192", "title":"Effect of Roasting, Boiling, and Frying Processing on 29 Polyphenolics and Antioxidant Activity in Seeds and Shells of Sweet Chestnut", "year":2021,
    "admitted_rows":36, "status":"VERIFIED_PARTIAL", "basis":"mg/kg dry weight", "reason":"Table 2 and methods directly support 36 edible-seed individual-analyte pairs. Shell matrices are excluded; aggregates, non-detects, stereochemically mismatched catechin, and molecules without existing verified descriptor identities are excluded."
}])
registry.to_csv(R / "literature_candidate_registry.csv", index=False)
pd.DataFrame([{"category":"EXCLUDED_TABLE_VALUES", "reason":"Shell matrices excluded as non-edible food material; total rows excluded as aggregates; non-detects excluded; (+)-catechin excluded because the parent generic Catechin identity does not prove the required enantiomer; other no-template analytes not inferred.", "doi":"10.3390/plants10102192"}]).to_csv(R / "excluded_candidates.csv", index=False)
prior = pd.read_csv(R.parent / "batch_003" / "source_verification_ledger.csv")
extra = pd.DataFrame([{"doi":"10.3390/plants10102192", "paper_title":"Effect of Roasting, Boiling, and Frying Processing on 29 Polyphenolics and Antioxidant Activity in Seeds and Shells of Sweet Chestnut", "source_url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC8537430/", "locator":"Table 2 seed columns; Methods §§3.2–3.4", "rows_admitted":36, "compound":"Chlorogenic, caffeic, syringic, p-coumaric, ferulic acids; rutin, isoquercitrin, quercetin, kaempferol", "basis":"mg/kg dry weight", "analytical_method":"HPLC-MS/MS; individual analytes", "admission_status":"VERIFIED_PARTIAL", "rationale":"Only directly tabled edible-seed pairs that map to existing verified descriptor identities are admitted."}])
pd.concat([prior, extra], ignore_index=True, sort=False).to_csv(R / "source_verification_ledger.csv", index=False)
coverage = master.groupby("doi").agg(observations=("observation_id","size"), compounds=("compound","nunique"), foods=("food_matrix","nunique"), methods=("cooking_method_normalized","nunique"), bases=("measurement_basis",lambda x:"; ".join(sorted(x.dropna().unique())))).reset_index()
coverage.to_csv(R / "source_coverage_analysis.csv", index=False)
write("dataset_expansion_report.md", f"""
# Scientific dataset expansion — controlled batch 004

The controlled master becomes **{len(master)} observations from {master.doi.nunique()} DOI families**. The 1,000 target remains unreached. Batch 004 adds 36 direct raw/cooked pairs from one independent study while preserving all 488 parent rows.

Mustafa et al. (2021), DOI `10.3390/plants10102192`, Table 2 and Methods, measures 25 individual HPLC-MS/MS phenolics in chestnut seed and shell matrices after boiling, microwave roasting, oven roasting, and pan frying. This package admits only edible chestnut seed pairs for nine analytes with exact existing verified descriptor identities, preserving the mg/kg dry-weight basis and condition protocol. Shell matrices, all aggregate rows, non-detects, (+)-catechin (stereochemical identity mismatch), and analytes with no existing verified identity are explicitly excluded.

The additions expand compound and method coverage but are one source cluster and do not establish source-held-out generalisation. No model is retrained and Stage C remains untouched.
""")
write("reproduction_instructions.md", """
# Reproduction

Run `python build_batch_004.py`, then `python validate_batch_004.py`. The build reads Batch 003 only and writes only this new package. It performs no remote, Git, historical-package, or Stage-B/C/D change.
""")
manifest = {"package":"StageA_DatasetExpansion1000_Batch004_2026-11-10", "parent_rows":488, "parent_sha256":sha(PARENT), "new_rows":36, "total_rows":len(master), "new_doi_families":1, "strict_cross_source_replications_created":0, "target_1000_reached":False, "stage_c_integration_authorized":False}
(R / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
(R / "SHA256SUMS.txt").write_text("\n".join(f"{sha(p)}  {p.name}" for p in sorted(R.iterdir()) if p.is_file() and p.name != "SHA256SUMS.txt") + "\n", encoding="utf-8")
print(json.dumps(manifest, indent=2))
