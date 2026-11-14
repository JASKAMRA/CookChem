"""Controlled expansion batch 020: Murador et al. author-deposited primary text."""
from pathlib import Path
import hashlib, json
import pandas as pd

R = Path(__file__).resolve().parent
ROOT = R.parent
PARENT = ROOT / "batch_019" / "updated_master_dataset.csv"
base = pd.read_csv(PARENT)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def template(compound):
    x = base.loc[base.compound.astype(str).str.casefold().eq(compound.casefold())]
    assert len(x), compound
    return x.iloc[0]

def write(name, text):
    (R / name).write_text(text.strip() + "\n", encoding="utf-8")

# Direct author-deposited thesis Chapter 3 (the published Food Chemistry paper):
# Table 1 and Table 4. Values are published means +/- SD (n=3), normalized to
# the raw sample; therefore every within-row ratio has an explicit common basis.
V = {
    "Kale": {
        "Lutein": (56.18, 2.90, 6.90, 0.54, 5.81, 1.14, 4.66, 1.81),
        "Beta-Carotene": (59.37, 4.67, 21.23, 3.82, 26.88, 2.83, 51.73, 11.32),
        "9-cis-Beta-Carotene": (14.08, 1.29, 3.63, 0.20, 4.31, 0.39, 5.89, 1.19),
        "Vitamin C": (122.9, 0.03, 359.1, 0.77, 790.0, 0.97, 257.4, 0.21),
    },
    "Red Cabbage": {
        "Lutein": (0.106, 0.018, 0.195, 0.014, 0.128, 0.028, 0.129, 0.008),
        "Beta-Carotene": (0.144, 0.048, 0.124, 0.019, 0.098, 0.036, 0.105, 0.014),
        "9-cis-Beta-Carotene": (0.038, 0.007, 0.040, 0.003, 0.032, 0.006, 0.027, 0.003),
        "Vitamin C": (113.7, 0.10, 107.8, 0.32, 187.6, 0.23, 152.4, 0.21),
    },
}

rows = []
for food, compounds in V.items():
    for compound, x in compounds.items():
        src = template("Beta-Carotene" if compound == "9-cis-Beta-Carotene" else compound)
        raw, raw_sd = x[:2]
        for i, (method, norm, medium, temp, minute) in enumerate((
            ("Boiling", "boiling", "covered stainless pot; tap water 1:5 food/water; drained 30 s", 98, 4),
            ("Steaming", "steaming", "covered pot; stainless steam basket above boiling water", 90, 5 if food == "Kale" else 15),
            ("Stir-frying", "stir_frying", "pre-heated wok; 4 mL soybean oil", 90, 4),
        )):
            cooked, cooked_sd = x[2 + 2*i : 4 + 2*i]
            row = {c: src[c] for c in base.columns}
            token = f"{food}_{compound}_{norm}".upper().replace(" ", "_").replace("-", "_")
            row.update({
                "observation_id": f"LIT-MURADOR2016-{token}",
                "original_record_id": "",
                "doi": "10.1016/j.foodchem.2015.10.037",
                "paper_id": "NEW_LITERATURE_MURADOR_2016",
                "source_locator": "Author-deposited thesis Chapter 3, Table 1 (carotenoids) or Table 4 (ascorbic acid); Methods Cooking Techniques",
                "compound": compound,
                "canonical_molecular_id": "MOL-" + hashlib.sha256(compound.encode()).hexdigest()[:16].upper() if compound == "9-cis-Beta-Carotene" else src["canonical_molecular_id"],
                "food_matrix": food,
                "cooking_method": method,
                "cooking_method_normalized": norm,
                "cooking_medium": medium,
                "raw_concentration": raw,
                "raw_sd": raw_sd,
                "cooked_concentration": cooked,
                "cooked_sd": cooked_sd,
                "concentration_unit": "µg/g raw sample" if compound != "Vitamin C" else "mg/100 g raw sample",
                "measurement_basis": "raw-sample reference basis (common raw mass)",
                "target_name": "apparent_concentration_ratio_percent",
                "target_equation": "100 * C_cooked / C_raw",
                "target_value_percent": 100 * cooked / raw,
                "target_semantics": "apparent concentration ratio; not total-mass retention",
                "evidence_status": "VERIFIED_PRIMARY_TABLE",
                "cooked_yield_status": "NOT_REPORTED",
                "total_mass_retention_status": "NOT_ESTABLISHED",
                "source_detail": "Murador et al. (2016) author-deposited primary Chapter 3, Tables 1/4; triplicate mean ± SD. Tables explicitly state per raw sample; methods state raw vegetable masses were used to calculate values to eliminate moisture gain/loss as a confounder.",
                "Temperature_C": temp,
                "Cooking_Time_min": minute,
                "reported_replicate_design": "Three batches per vegetable; cooked in triplicate. Published mean ± SD is one condition row and is never expanded into technical replicates.",
                "analytical_definition": "Individual HPLC-DAD-MS(n) carotenoid or HPLC-PDA ascorbic-acid analyte; 9-cis-beta-carotene is preserved as a distinct geometrical isomer, never collapsed into total beta-carotene.",
            })
            rows.append(row)

new = pd.DataFrame(rows, columns=base.columns)
master = pd.concat([base, new], ignore_index=True)
assert len(new) == 24 and len(master) == 938 and master.doi.nunique() == 31
assert not master.observation_id.duplicated().any()
assert new.canonical_molecular_id.notna().all()
assert (new.target_value_percent.round(8) == (100 * new.cooked_concentration / new.raw_concentration).round(8)).all()
assert new.loc[new.compound.eq("9-cis-Beta-Carotene"), "RDKit_LogP"].eq(template("Beta-Carotene")["RDKit_LogP"]).all()

master.to_csv(R / "updated_master_dataset.csv", index=False)
new.to_csv(R / "verified_observations.csv", index=False)
new.to_csv(R / "extracted_observations.csv", index=False)
reg = pd.read_csv(ROOT / "literature_candidate_registry.csv")
pd.concat([reg, pd.DataFrame([{
    "doi": "10.1016/j.foodchem.2015.10.037", "title": "Cooking techniques improve the levels of bioactive compounds and antioxidant activity in kale and red cabbage", "year": 2016,
    "compound": "all-trans lutein; all-trans beta-carotene; 9-cis-beta-carotene; ascorbic acid", "food_matrix": "kale; red cabbage", "cooking_method": "boiling; steaming; stir-frying", "measurement_technique": "HPLC-DAD-MS(n); HPLC-PDA", "measurement_basis": "raw-sample reference basis", "raw_values": "Chapter 3 Tables 1 and 4", "cooked_values": "Chapter 3 Tables 1 and 4", "extractable_observations": 24, "verification_status": "VERIFIED", "rejection_reason": ""
}])], ignore_index=True, sort=False).to_csv(R / "literature_candidate_registry.csv", index=False)
exc = pd.read_csv(ROOT / "excluded_candidates.csv")
pd.concat([exc, pd.DataFrame([{
    "doi": "10.1016/j.foodchem.2015.10.037", "title": "Cooking techniques improve the levels of bioactive compounds and antioxidant activity in kale and red cabbage", "year": 2016,
    "compound": "one-sample detections; non-detects; total carotenoids; total anthocyanins; total phenolics; antioxidant endpoints; ambiguous/analyte-mixture entries", "food_matrix": "kale; red cabbage", "cooking_method": "boiling; steaming; stir-frying", "measurement_technique": "HPLC-DAD-MS(n); HPLC-PDA", "measurement_basis": "raw-sample reference basis", "raw_values": "Chapter 3 Tables 1–5", "cooked_values": "Chapter 3 Tables 1–5", "extractable_observations": 0, "verification_status": "PARTIAL_EXCLUSION", "rejection_reason": "Only direct individual analytes with non-missing published mean ± SD in raw and cooked conditions are admitted. One-sample detections, non-detects, totals, activity assays, and ambiguous mixture/identity rows remain excluded."
}])], ignore_index=True, sort=False).to_csv(R / "excluded_candidates.csv", index=False)
prior = pd.read_csv(ROOT / "batch_019" / "source_verification_ledger.csv")
pd.concat([prior, pd.DataFrame([{
    "doi": "10.1016/j.foodchem.2015.10.037", "paper_title": "Cooking techniques improve the levels of bioactive compounds and antioxidant activity in kale and red cabbage", "source_url": "https://repositorio.unifesp.br/bitstreams/f4cccbdf-c9b9-4540-9ece-9684f3adce8b/download", "locator": "Author thesis Chapter 3 pp. 80–84 (methods), Table 1 pp. 87–88, Table 4 p. 92", "rows_admitted": 24, "compound": "lutein; beta-carotene; 9-cis-beta-carotene; ascorbic acid", "basis": "raw-sample reference basis; units as table-stated", "analytical_method": "HPLC-DAD-MS(n); HPLC-PDA", "admission_status": "VERIFIED_PARTIAL", "rationale": "Direct primary author-deposited tables provide raw/cooked mean ± SD, with cooking conditions and common raw-sample basis. Only unambiguous, triplicate analytes with positive raw and cooked values admitted."
}])], ignore_index=True, sort=False).to_csv(R / "source_verification_ledger.csv", index=False)
master.groupby("doi").agg(observations=("observation_id", "size"), compounds=("compound", "nunique"), foods=("food_matrix", "nunique"), methods=("cooking_method_normalized", "nunique"), bases=("measurement_basis", lambda x: "; ".join(sorted(x.dropna().unique())))).reset_index().to_csv(R / "source_coverage_analysis.csv", index=False)
write("dataset_expansion_report.md", f"""# Scientific dataset expansion — controlled batch 020

The controlled master becomes **{len(master)} verified observations from {master.doi.nunique()} DOI families**. Batch 020 adds 24 direct primary-table raw/cooked pairs from Murador, Mercadante and de Rosso (2016), DOI `10.1016/j.foodchem.2015.10.037`, preserving every 914 parent row.

The author-deposited thesis contains the published primary Chapter 3. Table 1 reports individual carotenoids and Table 4 reports ascorbic acid; methods establish 1:5 boiling, steaming, and soybean-oil stir-frying, with time and endpoint temperature. Values are deliberately normalized to the same raw-sample reference mass, explicitly avoiding moisture-gain/loss confounding. One-sample detections, non-detects, totals and ambiguous identity/mixture rows are excluded. No model is retrained; 62 observations remain to the target.
""")
write("reproduction_instructions.md", "Run `python build_batch_020.py`, then `python validate_batch_020.py`. It reads Batch 019/current ledgers and writes only this package; it does not modify historical packages, Git, or Stage B/C/D.")
manifest = {"package": "StageA_DatasetExpansion1000_Batch020_2026-11-11", "parent_rows": 914, "parent_sha256": sha(PARENT), "new_rows": 24, "total_rows": len(master), "new_doi_families": 1, "strict_cross_source_replications_created": 0, "target_1000_reached": False, "stage_c_integration_authorized": False}
(R / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
(R / "SHA256SUMS.txt").write_text("\n".join(f"{sha(p)}  {p.name}" for p in sorted(R.iterdir()) if p.is_file() and p.name != "SHA256SUMS.txt") + "\n", encoding="utf-8")
print(json.dumps(manifest, indent=2))
