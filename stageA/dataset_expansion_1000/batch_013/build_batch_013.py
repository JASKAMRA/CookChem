"""Controlled expansion batch 013: Loche squash primary table and supplementary methods."""
from pathlib import Path
import hashlib
import json
import pandas as pd

R = Path(__file__).resolve().parent
PARENT = R.parent / "batch_012" / "updated_master_dataset.csv"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(name, text):
    (R / name).write_text(text.strip() + "\n", encoding="utf-8")

base = pd.read_csv(PARENT)

def template(compound):
    hit = base.loc[base.compound.astype(str).str.casefold().eq(compound.casefold())]
    assert len(hit), compound
    return hit.iloc[0]

# Jimenez-Aspee et al. (2026), Table 1 (mg/100 g DW), with the boiling protocol
# in Supplementary Materials, Plant material. Each pair remains one source-table
# condition mean; the source's three technical portions are never expanded.
data = {
    "Beta-Carotene": (0.208, 0.023, 0.055, 0.007),
    "Lutein": (1.995, 0.181, 1.110, 0.313),
    "Alpha-Tocopherol (Vitamin E)": (2.346, 0.327, 0.274, 0.098),
    "Gamma-Tocopherol": (1.628, 0.101, 0.365, 0.031),
    "Protocatechuic Acid": (1147.4, 68.4, 80.3, 1.1),
    "Caffeic acid": (37.6, 0.5, 2.7, 0.5),
    "P-Coumaric Acid": (116.0, 14.2, 12.9, 1.1),
    "Ferulic Acid": (19.4, 0.1, 1.76, 0.01),
}
rows = []
for compound, (raw, raw_sd, cooked, cooked_sd) in data.items():
    src = template(compound)
    safe = compound.upper().replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "")
    row = {col: src[col] for col in base.columns}
    row.update({
        "observation_id": f"LIT-JIMENEZASPEE2026-LOCHE-{safe}-BOILED",
        "original_record_id": "",
        "doi": "10.1007/s11130-026-01551-8",
        "paper_id": "NEW_LITERATURE_JIMENEZ_ASPEE_2026",
        "source_locator": "Table 1; Supplementary Materials, Plant material",
        "compound": compound,
        "food_matrix": "Loche squash (Cucurbita moschata) pulp, composite of ten fruits",
        "cooking_method": "Boiling",
        "cooking_method_normalized": "boiling",
        "cooking_medium": "water, 1:5 w/v; traditional preparation",
        "raw_concentration": raw,
        "raw_sd": raw_sd,
        "cooked_concentration": cooked,
        "cooked_sd": cooked_sd,
        "concentration_unit": "mg/100 g dry weight",
        "measurement_basis": "dry weight (DW)",
        "target_name": "apparent_concentration_ratio_percent",
        "target_equation": "100 * C_cooked / C_raw",
        "target_value_percent": 100 * cooked / raw,
        "target_semantics": "apparent concentration ratio; not total-mass retention",
        "evidence_status": "VERIFIED_PRIMARY_TABLE_AND_SUPPLEMENT",
        "cooked_yield_status": "NOT_REPORTED",
        "total_mass_retention_status": "NOT_ESTABLISHED",
        "source_detail": "Jimenez-Aspee et al. (2026), Table 1: individual carotenoid, tocopherol and phenolic-acid raw/boiled concentrations; Supplementary Materials specifies three 1-kg portions boiled in water (1:5 w/v) for 20 min, then freeze-dried. Table mean ± SD retained without technical-row expansion.",
        "Temperature_C": pd.NA,
        "Cooking_Time_min": 20,
        "reported_replicate_design": "Three independently prepared 1-kg composite-pulp portions per condition, described by source as technical replicates; Table means ± SD retained as one condition row per analyte.",
        "analytical_definition": "Individual standard-quantified carotenoid/tocopherol or UPLC-DAD-MS2 phenolic acid; dry-weight result",
    })
    rows.append(row)

new = pd.DataFrame(rows, columns=base.columns)
master = pd.concat([base, new], ignore_index=True)
assert len(new) == 8 and len(master) == 757 and master.doi.nunique() == 26
assert new.canonical_molecular_id.notna().all() and not master.observation_id.duplicated().any()
assert (new.target_value_percent.round(8) == (100 * new.cooked_concentration / new.raw_concentration).round(8)).all()
master.to_csv(R / "updated_master_dataset.csv", index=False)
new.to_csv(R / "verified_observations.csv", index=False)
new.to_csv(R / "extracted_observations.csv", index=False)

pd.DataFrame([{
    "doi": "10.1007/s11130-026-01551-8",
    "title": "Loche Squash (Cucurbita moschata): Phytochemical Profile and Bioaccessibility of Carotenoids, Tocopherols, and (poly)Phenols",
    "year": 2026,
    "admitted_rows": 8,
    "status": "VERIFIED_PARTIAL",
    "basis": "mg/100 g dry weight",
    "reason": "Primary Table 1 directly provides individual raw/boiled values. Open publisher supplement verifies water ratio and 20-minute boiling procedure."
}]).to_csv(R / "literature_candidate_registry.csv", index=False)
pd.DataFrame([{
    "category": "EXCLUDED_TABLE_VALUES",
    "doi": "10.1007/s11130-026-01551-8",
    "reason": "Alpha-carotene, beta-cryptoxanthin, zeaxanthin, beta- and delta-tocopherol, salicylic acid and all digested-matrix outputs lack exact established descriptor identities in the current master or are outside the raw/cooked contract. Lycopene is cooked ND. No technical replicate is expanded."
}]).to_csv(R / "excluded_candidates.csv", index=False)

prior = pd.read_csv(R.parent / "batch_012" / "source_verification_ledger.csv")
extra = pd.DataFrame([{
    "doi": "10.1007/s11130-026-01551-8",
    "paper_title": "Loche Squash (Cucurbita moschata): Phytochemical Profile and Bioaccessibility of Carotenoids, Tocopherols, and (poly)Phenols",
    "source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC13380564/",
    "locator": "Table 1; Supplementary Materials, Plant material",
    "rows_admitted": 8,
    "compound": "Beta-carotene; lutein; alpha- and gamma-tocopherol; protocatechuic, caffeic, p-coumaric and ferulic acids",
    "basis": "mg/100 g dry weight",
    "analytical_method": "Individual carotenoids/tocopherols and UPLC-DAD-MS2 phenolic acids",
    "admission_status": "VERIFIED_PARTIAL",
    "rationale": "Direct raw/boiled Table-1 means ± SD, backed by publisher supplementary method confirming 1:5 water ratio and 20-minute boiling."
}])
pd.concat([prior, extra], ignore_index=True, sort=False).to_csv(R / "source_verification_ledger.csv", index=False)
master.groupby("doi").agg(observations=("observation_id", "size"), compounds=("compound", "nunique"), foods=("food_matrix", "nunique"), methods=("cooking_method_normalized", "nunique"), bases=("measurement_basis", lambda x: "; ".join(sorted(x.dropna().unique())))).reset_index().to_csv(R / "source_coverage_analysis.csv", index=False)

write("dataset_expansion_report.md", f"""# Scientific dataset expansion — controlled batch 013

The controlled master becomes **{len(master)} verified observations from {master.doi.nunique()} DOI families**. Batch 013 adds eight primary-table pairs from Jimenez-Aspee et al. (2026), DOI `10.1007/s11130-026-01551-8`, and preserves all 749 parent rows.

Table 1 directly reports individual raw/boiled Loche-squash-pulp concentrations. The open publisher supplement supplies the missing cooking protocol: ten-fruit composite pulp, three separate 1-kg portions, water at 1:5 w/v, 20-minute boiling and freeze-drying. Values remain mg/100 g dry weight. A condition mean is one observation, never three technical rows. Only exact existing identities with positive raw and cooked values are retained; digested samples, nondetects, aggregates and unmapped identities are excluded. No model is retrained; 243 observations remain to the 1,000 target.
""")
write("reproduction_instructions.md", """# Reproduction
Run `python build_batch_013.py`, then `python validate_batch_013.py`. It reads only Batch 012 and writes only this package; no historical package, Git, or Stage B/C/D file is changed.
""")
manifest = {"package": "StageA_DatasetExpansion1000_Batch013_2026-11-10", "parent_rows": 749, "parent_sha256": sha(PARENT), "new_rows": 8, "total_rows": len(master), "new_doi_families": 1, "strict_cross_source_replications_created": 0, "target_1000_reached": False, "stage_c_integration_authorized": False}
(R / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
(R / "SHA256SUMS.txt").write_text("\n".join(f"{sha(p)}  {p.name}" for p in sorted(R.iterdir()) if p.is_file() and p.name != "SHA256SUMS.txt") + "\n", encoding="utf-8")
print(json.dumps(manifest, indent=2))
