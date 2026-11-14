"""Controlled expansion batch 015: primary HPLC corn evidence."""
from pathlib import Path
import hashlib
import json
import pandas as pd

R = Path(__file__).resolve().parent
ROOT = R.parent
PARENT = ROOT / "batch_013" / "updated_master_dataset.csv"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, text):
    (R / name).write_text(text.strip() + "\n", encoding="utf-8")


base = pd.read_csv(PARENT)


def template(compound):
    hit = base.loc[base.compound.astype(str).str.casefold().eq(compound.casefold())]
    assert len(hit), compound
    return hit.iloc[0]


# Prasanthi et al. (2017), Tables 1, 4 and 5.  Values are direct means +/- SD
# from triplicate composite food samples.  One source-table condition is one row;
# the three composites are never expanded to observations.
phenolics = {
    "Baby corn": ("Steaming", "steaming", "water steam", 8, (2.34, 0.20, 1.15, 0.09), (11.66, 0.17, 8.19, 0.14), (1.25, 0.11, 0.34, 0.18), (10.34, 0.17, 2.47, 0.15)),
    "Sweet corn": ("Steaming", "steaming", "water steam", 10, (6.46, 0.11, 3.62, 0.05), (15.48, 0.12, 13.31, 0.23), (1.69, 0.39, 1.29, 0.06), (3.45, 0.25, 1.67, 0.47)),
    "Dent corn": ("Steaming", "steaming", "water steam", 10, (3.72, 0.10, 2.53, 0.16), (10.25, 0.09, 5.57, 0.09), (2.47, 0.09, 1.26, 0.11), (1.50, 0.06, 1.16, 0.13)),
    "Popcorn, groundnut oil": ("Popping", "popping", "groundnut oil (10 mL per 100 g kernel)", 6, (2.21, 0.21, 1.35, 0.03), (1.59, 0.28, 1.28, 0.09), (4.21, 0.08, 0.94, 0.08), (1.43, 0.05, 0.87, 0.07)),
    "Popcorn, no added oil": ("Popping", "popping", "none", 6, (1.39, 0.03, 1.25, 0.03), (1.43, 0.03, 1.10, 0.07), (3.83, 0.08, 0.50, 0.03), (1.15, 0.09, 0.61, 0.03)),
    "Corn grits": ("Boiling", "boiling", "water (500 mL per 100 g)", 8, (4.80, 0.13, 2.34, 0.14), (6.77, 0.18, 4.69, 0.28), (11.43, 0.08, 8.68, 0.27), (3.34, 0.24, 1.31, 0.04)),
    "Corn flour": ("Boiling", "boiling", "water (200 mL per 100 g)", 3, (2.32, 0.03, 0.78, 0.03), (10.41, 0.17, 8.39, 0.07), (1.32, 0.09, 1.16, 0.08), (1.23, 0.11, 0.47, 0.05)),
    "Corn flakes": ("Frying", "frying", "groundnut oil (100 mL per 100 g)", pd.NA, (3.49, 0.07, 1.87, 0.05), (15.38, 0.10, 6.72, 0.31), (1.45, 0.06, 0.37, 0.04), (1.45, 0.03, 1.13, 0.05)),
}
compound_values = ("Caffeic acid", "Syringic acid", "p-Coumaric acid", "Ferulic acid")
rows = []
for matrix, (method, normalized, medium, minutes, *values) in phenolics.items():
    for compound, (raw, raw_sd, cooked, cooked_sd) in zip(compound_values, values):
        src = template(compound)
        row = {col: src[col] for col in base.columns}
        safe = compound.upper().replace("-", "_").replace(" ", "_")
        row.update({
            "observation_id": f"LIT-PRASANTHI2017-{matrix.upper().replace(',', '').replace(' ', '_')}-{safe}-{normalized.upper()}",
            "original_record_id": "",
            "doi": "10.1007/s13197-017-2547-2",
            "paper_id": "NEW_LITERATURE_PRASANTHI_2017",
            "source_locator": "Tables 1 and 5",
            "compound": compound,
            "food_matrix": f"{matrix} (Zea mays), market composite",
            "cooking_method": method,
            "cooking_method_normalized": normalized,
            "cooking_medium": medium,
            "raw_concentration": raw,
            "raw_sd": raw_sd,
            "cooked_concentration": cooked,
            "cooked_sd": cooked_sd,
            "concentration_unit": "µg/100 g fresh weight",
            "measurement_basis": "fresh weight (FW)",
            "target_name": "apparent_concentration_ratio_percent",
            "target_equation": "100 * C_cooked / C_raw",
            "target_value_percent": 100 * cooked / raw,
            "target_semantics": "apparent concentration ratio; not total-mass retention",
            "evidence_status": "VERIFIED_PRIMARY_TABLE",
            "cooked_yield_status": "NOT_REPORTED",
            "total_mass_retention_status": "NOT_ESTABLISHED",
            "source_detail": "Prasanthi et al. (2017), Table 5 direct RPHPLC phenolic-acid means ± SD. Table 1 documents the matched raw/cooked protocol; Table 5 states fresh-weight basis and triplicate composite measurement.",
            "Temperature_C": pd.NA,
            "Cooking_Time_min": minutes,
            "reported_replicate_design": "Three composite samples per food product, each assembled from market subsamples; reported means ± SD. Not expanded into technical or composite-replicate rows.",
            "analytical_definition": "Individual RPHPLC-quantified phenolic acid; fresh-weight result",
        })
        rows.append(row)

# Table 4 identifies lutein separately and explicitly states a fresh-weight basis.
lutein = {
    "Baby corn": ("Steaming", "steaming", "water steam", 8, 224.58, 0.90, 233.49, 43.06),
    "Sweet corn": ("Steaming", "steaming", "water steam", 10, 136.76, 9.57, 128.92, 3.45),
    "Dent corn": ("Steaming", "steaming", "water steam", 10, 394.38, 2.75, 313.66, 36.22),
    "Popcorn, groundnut oil": ("Popping", "popping", "groundnut oil (10 mL per 100 g kernel)", 6, 114.20, 2.52, 109.30, 0.70),
    "Popcorn, no added oil": ("Popping", "popping", "none", 6, 247.19, 20.25, 225.01, 1.21),
    "Corn grits": ("Boiling", "boiling", "water (500 mL per 100 g)", 8, 177.54, 29.22, 138.61, 3.97),
    "Corn flakes": ("Frying", "frying", "groundnut oil (100 mL per 100 g)", pd.NA, 87.28, 8.39, 71.32, 2.33),
}
for matrix, (method, normalized, medium, minutes, raw, raw_sd, cooked, cooked_sd) in lutein.items():
    src = template("Lutein")
    row = {col: src[col] for col in base.columns}
    row.update({
        "observation_id": f"LIT-PRASANTHI2017-{matrix.upper().replace(',', '').replace(' ', '_')}-LUTEIN-{normalized.upper()}",
        "original_record_id": "",
        "doi": "10.1007/s13197-017-2547-2",
        "paper_id": "NEW_LITERATURE_PRASANTHI_2017",
        "source_locator": "Tables 1 and 4",
        "compound": "Lutein",
        "food_matrix": f"{matrix} (Zea mays), market composite",
        "cooking_method": method,
        "cooking_method_normalized": normalized,
        "cooking_medium": medium,
        "raw_concentration": raw,
        "raw_sd": raw_sd,
        "cooked_concentration": cooked,
        "cooked_sd": cooked_sd,
        "concentration_unit": "µg/100 g fresh weight",
        "measurement_basis": "fresh weight (FW)",
        "target_name": "apparent_concentration_ratio_percent",
        "target_equation": "100 * C_cooked / C_raw",
        "target_value_percent": 100 * cooked / raw,
        "target_semantics": "apparent concentration ratio; not total-mass retention",
        "evidence_status": "VERIFIED_PRIMARY_TABLE",
        "cooked_yield_status": "NOT_REPORTED",
        "total_mass_retention_status": "NOT_ESTABLISHED",
        "source_detail": "Prasanthi et al. (2017), Table 4 direct lutein means ± SD. Table 1 documents the matched raw/cooked protocol; Table 4 states fresh-weight basis and triplicate composite measurement.",
        "Temperature_C": pd.NA,
        "Cooking_Time_min": minutes,
        "reported_replicate_design": "Three composite samples per food product, each assembled from market subsamples; reported means ± SD. Not expanded into technical or composite-replicate rows.",
        "analytical_definition": "Individual HPLC-quantified lutein; fresh-weight result",
    })
    rows.append(row)

new = pd.DataFrame(rows, columns=base.columns)
master = pd.concat([base, new], ignore_index=True)
assert len(new) == 39 and len(master) == 796 and master.doi.nunique() == 27
assert new.canonical_molecular_id.notna().all() and not master.observation_id.duplicated().any()
assert (new.target_value_percent.round(8) == (100 * new.cooked_concentration / new.raw_concentration).round(8)).all()
master.to_csv(R / "updated_master_dataset.csv", index=False)
new.to_csv(R / "verified_observations.csv", index=False)
new.to_csv(R / "extracted_observations.csv", index=False)

prior_registry = pd.read_csv(ROOT / "literature_candidate_registry.csv")
candidate = pd.DataFrame([{
    "doi": "10.1007/s13197-017-2547-2",
    "title": "Compositional variability of nutrients and phytochemicals in corn after processing",
    "year": 2017,
    "compound": "caffeic, syringic, p-coumaric and ferulic acids; lutein",
    "food_matrix": "eight corn matrices/products",
    "cooking_method": "steaming; boiling; popping; frying",
    "measurement_technique": "RPHPLC phenolic acids; HPLC xanthophylls",
    "measurement_basis": "fresh weight",
    "raw_values": "Tables 4-5",
    "cooked_values": "Tables 4-5",
    "extractable_observations": 39,
    "verification_status": "VERIFIED",
    "rejection_reason": "",
}])
pd.concat([prior_registry, candidate], ignore_index=True, sort=False).to_csv(R / "literature_candidate_registry.csv", index=False)
prior_excluded = pd.read_csv(ROOT / "excluded_candidates.csv")
exclusion = pd.DataFrame([{
    "doi": "10.1007/s13197-017-2547-2",
    "title": "Compositional variability of nutrients and phytochemicals in corn after processing",
    "year": 2017,
    "compound": "4-OH benzoic acid, vanillic acid, o-coumaric acid, zeaxanthin, alpha- and beta-cryptoxanthin, total carotenoids/polyphenols",
    "food_matrix": "corn matrices/products",
    "cooking_method": "as reported",
    "measurement_technique": "HPLC and aggregate assays",
    "measurement_basis": "fresh weight",
    "raw_values": "Tables 4-5",
    "cooked_values": "Tables 4-5",
    "extractable_observations": 0,
    "verification_status": "PARTIAL_EXCLUSION",
    "rejection_reason": "No exact established canonical descriptor for the named individual compounds; total endpoints are not individual molecular identities. Corn flour lutein is raw/cooked ND.",
}])
pd.concat([prior_excluded, exclusion], ignore_index=True, sort=False).to_csv(R / "excluded_candidates.csv", index=False)

prior = pd.read_csv(ROOT / "batch_013" / "source_verification_ledger.csv")
extra = pd.DataFrame([{
    "doi": "10.1007/s13197-017-2547-2",
    "paper_title": "Compositional variability of nutrients and phytochemicals in corn after processing",
    "source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC5380630/",
    "locator": "Tables 1, 4 and 5",
    "rows_admitted": 39,
    "compound": "Caffeic, syringic, p-coumaric and ferulic acids; lutein",
    "basis": "fresh weight",
    "analytical_method": "RPHPLC phenolic acids; HPLC xanthophylls",
    "admission_status": "VERIFIED_PARTIAL",
    "rationale": "Direct raw/cooked numerical tables, declared fresh-weight basis, documented cooking durations/media and three composite means per product. Only exact established identities with positive raw and cooked values retained.",
}])
pd.concat([prior, extra], ignore_index=True, sort=False).to_csv(R / "source_verification_ledger.csv", index=False)
master.groupby("doi").agg(observations=("observation_id", "size"), compounds=("compound", "nunique"), foods=("food_matrix", "nunique"), methods=("cooking_method_normalized", "nunique"), bases=("measurement_basis", lambda x: "; ".join(sorted(x.dropna().unique())))).reset_index().to_csv(R / "source_coverage_analysis.csv", index=False)

write("dataset_expansion_report.md", f"""# Scientific dataset expansion — controlled batch 015

The controlled master becomes **{len(master)} verified observations from {master.doi.nunique()} DOI families**. Batch 015 adds 39 primary-table pairs from Prasanthi et al. (2017), DOI `10.1007/s13197-017-2547-2`, and preserves all 757 parent rows.

Tables 4 and 5 report individual HPLC xanthophyll and RPHPLC phenolic-acid values for matched raw/cooked corn matrices. Table 1 documents the food-specific protocols: steaming (8–10 min), water boiling (3–8 min), pressure-cooker popping (6 min, with or without 10 mL groundnut oil per 100 g kernel), and corn-flake frying in 100 mL groundnut oil per 100 g. Tables 4–5 explicitly label the results fresh-weight basis. Each reported mean ± SD from three composite food samples is one observation, never three rows.

Only exact established descriptor identities with positive raw and cooked values are retained: caffeic, syringic, p-coumaric and ferulic acids, and lutein. Total endpoints, non-detects, and source identities without an established exact canonical record are excluded. No model is retrained; 204 observations remain to the 1,000 target.
""")
write("reproduction_instructions.md", """# Reproduction
Run `python build_batch_015.py`, then `python validate_batch_015.py`. It reads only Batch 013 and the current candidate/exclusion ledgers, and writes only this package; no historical package, Git, or Stage B/C/D file is changed.
""")
manifest = {"package": "StageA_DatasetExpansion1000_Batch015_2026-11-10", "parent_rows": 757, "parent_sha256": sha(PARENT), "new_rows": 39, "total_rows": len(master), "new_doi_families": 1, "strict_cross_source_replications_created": 0, "target_1000_reached": False, "stage_c_integration_authorized": False}
(R / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
(R / "SHA256SUMS.txt").write_text("\n".join(f"{sha(p)}  {p.name}" for p in sorted(R.iterdir()) if p.is_file() and p.name != "SHA256SUMS.txt") + "\n", encoding="utf-8")
print(json.dumps(manifest, indent=2))
