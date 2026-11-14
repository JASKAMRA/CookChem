"""Controlled expansion batch 017: Chaya primary HPLC evidence."""
from pathlib import Path
import hashlib, json
import pandas as pd

R = Path(__file__).resolve().parent
ROOT = R.parent
PARENT = ROOT / "batch_016" / "updated_master_dataset.csv"
base = pd.read_csv(PARENT)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def template(compound):
    hit = base.loc[base.compound.astype(str).str.casefold().eq(compound.casefold())]
    assert len(hit), compound
    return hit.iloc[0]
def write(name, text): (R / name).write_text(text.strip() + "\n", encoding="utf-8")

# Kongphapa et al. (2022), Table 4. Raw and cooked samples have the same
# explicit dry-weight basis; the source's triplicate means remain one row each.
values = {
    "Caffeic acid": (561.71, 27.66, 406.98, 16.55),
    "Chlorogenic Acid": (82.14, 4.61, 7.31, 1.64),
    "Ferulic Acid": (5.25, 2.58, 0.86, 0.02),
    "p-Coumaric acid": (3.86, 2.04, 6.75, 1.73),
    "Protocatechuic Acid": (67.98, 1.94, 20.25, 1.10),
    "Quercetin": (95.36, 3.11, 9.55, 0.34),
    "Rutin": (52.00, 0.06, 123.03, 6.99),
    "Sinapic acid": (784.50, 20.76, 112.50, 6.88),
    "Syringic acid": (70.71, 5.10, 225.00, 8.77),
}
rows=[]
for compound, (raw, raw_sd, cooked, cooked_sd) in values.items():
    src = template(compound)
    row = {c:src[c] for c in base.columns}
    token = compound.upper().replace(" ", "_").replace("-", "_")
    row.update({
        "observation_id": f"LIT-KONGPHAPA2022-CHAYA-{token}-BOILING",
        "original_record_id":"", "doi":"10.14456/apst.2022.5", "paper_id":"NEW_LITERATURE_KONGPHAPA_2022",
        "source_locator":"Table 4; Methods 2.1 and 2.6-2.7",
        "compound":compound, "food_matrix":"Chaya leaves (Cnidoscolus chayamansa)",
        "cooking_method":"Boiling then tray drying", "cooking_method_normalized":"boiling_then_drying",
        "cooking_medium":"boiling water; subsequently tray dried to constant weight",
        "raw_concentration":raw, "raw_sd":raw_sd, "cooked_concentration":cooked, "cooked_sd":cooked_sd,
        "concentration_unit":"mg/100 g dry weight", "measurement_basis":"dry weight (DW)",
        "target_name":"apparent_concentration_ratio_percent", "target_equation":"100 * C_cooked / C_raw",
        "target_value_percent":100*cooked/raw,
        "target_semantics":"apparent concentration ratio; not total-mass retention",
        "evidence_status":"VERIFIED_PRIMARY_TABLE", "cooked_yield_status":"NOT_REPORTED",
        "total_mass_retention_status":"NOT_ESTABLISHED",
        "source_detail":"Kongphapa et al. (2022), Table 4, individual HPLC-DAD phenolic acid/flavonoid means ± SD. Raw and cooked samples are both explicitly dry-weight measurements; cooked leaves were boiled at 100 C for 15 min and then tray dried at 60 C.",
        "Temperature_C":100, "Cooking_Time_min":15,
        "reported_replicate_design":"Triplicate measurement; source reports mean ± SD. Never expanded into replicate observations.",
        "analytical_definition":"Individual HPLC-DAD analyte identified by retention time and calibration-curve peak area",
    })
    rows.append(row)
new = pd.DataFrame(rows, columns=base.columns)
master = pd.concat([base, new], ignore_index=True)
assert len(new)==9 and len(master)==837 and master.doi.nunique()==29
assert not master.observation_id.duplicated().any() and new.canonical_molecular_id.notna().all()
assert (new.target_value_percent.round(8)==(100*new.cooked_concentration/new.raw_concentration).round(8)).all()
master.to_csv(R/"updated_master_dataset.csv", index=False)
new.to_csv(R/"verified_observations.csv", index=False)
new.to_csv(R/"extracted_observations.csv", index=False)

reg = pd.read_csv(ROOT/"literature_candidate_registry.csv")
pd.concat([reg,pd.DataFrame([{"doi":"10.14456/apst.2022.5","title":"Nutritional and phytochemical properties of Chaya leaves (Cnidoscolus chayamansa Mc Vaugh) planted in Northeastern Thailand","year":2022,"compound":"nine existing individual phenolic acids/flavonoids","food_matrix":"Chaya leaves","cooking_method":"boiling then tray drying","measurement_technique":"HPLC-DAD","measurement_basis":"dry weight","raw_values":"Table 4","cooked_values":"Table 4","extractable_observations":9,"verification_status":"VERIFIED","rejection_reason":""}])],ignore_index=True,sort=False).to_csv(R/"literature_candidate_registry.csv",index=False)
exc = pd.read_csv(ROOT/"excluded_candidates.csv")
pd.concat([exc,pd.DataFrame([{"doi":"10.14456/apst.2022.5","title":"Nutritional and phytochemical properties of Chaya leaves (Cnidoscolus chayamansa Mc Vaugh) planted in Northeastern Thailand","year":2022,"compound":"gallic, p-hydroxybenzoic and apigenin plus aggregate/nutrient endpoints","food_matrix":"Chaya leaves","cooking_method":"boiling then tray drying","measurement_technique":"HPLC-DAD and other methods","measurement_basis":"dry weight","raw_values":"Table 4 and other tables","cooked_values":"Table 4 and other tables","extractable_observations":0,"verification_status":"PARTIAL_EXCLUSION","rejection_reason":"Only exact established canonical compounds were admitted. Compounds missing from the current canonical molecular registry and all aggregate/non-target endpoints remain excluded."}])],ignore_index=True,sort=False).to_csv(R/"excluded_candidates.csv",index=False)
prior = pd.read_csv(ROOT/"batch_016"/"source_verification_ledger.csv")
pd.concat([prior,pd.DataFrame([{"doi":"10.14456/apst.2022.5","paper_title":"Nutritional and phytochemical properties of Chaya leaves (Cnidoscolus chayamansa Mc Vaugh) planted in Northeastern Thailand","source_url":"https://doi.nrct.go.th/ListDoi/Download/607362?Resolve_DOI=10.14456%2Fapst.2022.5","locator":"Table 4; Methods 2.1 and 2.6-2.7","rows_admitted":9,"compound":"Caffeic acid; chlorogenic acid; ferulic acid; p-coumaric acid; protocatechuic acid; quercetin; rutin; sinapic acid; syringic acid","basis":"mg/100 g dry weight","analytical_method":"HPLC-DAD","admission_status":"VERIFIED_PARTIAL","rationale":"Direct raw/cooked numerical table, identical explicit dry-weight basis, documented boiling (100 C, 15 min) and drying treatment, HPLC-DAD identity/quantification. One mean per compound, never technical replicates."}])],ignore_index=True,sort=False).to_csv(R/"source_verification_ledger.csv",index=False)
master.groupby("doi").agg(observations=("observation_id","size"),compounds=("compound","nunique"),foods=("food_matrix","nunique"),methods=("cooking_method_normalized","nunique"),bases=("measurement_basis",lambda x:"; ".join(sorted(x.dropna().unique())))).reset_index().to_csv(R/"source_coverage_analysis.csv",index=False)
write("dataset_expansion_report.md", f"""# Scientific dataset expansion — controlled batch 017

The controlled master becomes **{len(master)} verified observations from {master.doi.nunique()} DOI families**. Batch 017 adds nine independently sourced, primary-table raw/cooked pairs from Kongphapa et al. (2022), DOI `10.14456/apst.2022.5`, preserving all 828 parent rows.

Table 4 provides individual HPLC-DAD analytes in raw and boiled-then-dried Chaya leaves, expressed consistently as mg/100 g dry weight. Methods state boiling at 100 °C for 15 minutes, followed by tray drying at 60 °C. Only nine values matched pre-existing canonical molecular records; unregistered identities and aggregate endpoints are explicitly excluded. The source reports triplicate means ± SD; no technical replicate expansion occurred. No model is retrained; 163 observations remain to the target.
""")
write("reproduction_instructions.md", "Run `python build_batch_017.py`, then `python validate_batch_017.py`. It reads Batch 016/current ledgers and writes only this package; it does not modify historical packages, Git, or Stage B/C/D.")
manifest={"package":"StageA_DatasetExpansion1000_Batch017_2026-11-10","parent_rows":828,"parent_sha256":sha(PARENT),"new_rows":9,"total_rows":len(master),"new_doi_families":1,"strict_cross_source_replications_created":0,"target_1000_reached":False,"stage_c_integration_authorized":False}
(R/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
(R/"SHA256SUMS.txt").write_text("\n".join(f"{sha(p)}  {p.name}" for p in sorted(R.iterdir()) if p.is_file() and p.name!="SHA256SUMS.txt")+"\n",encoding="utf-8")
print(json.dumps(manifest,indent=2))
