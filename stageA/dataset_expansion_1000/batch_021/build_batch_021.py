"""Controlled expansion batch 021: Buratti et al. open primary tables."""
from pathlib import Path
import hashlib, json
import pandas as pd

R = Path(__file__).resolve().parent
ROOT = R.parent
PARENT = ROOT / "batch_020" / "updated_master_dataset.csv"
base = pd.read_csv(PARENT)

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name, text): (R / name).write_text(text.strip() + "\n", encoding="utf-8")
def template(compound):
    x = base.loc[base.compound.astype(str).str.casefold().eq(compound.casefold())]
    assert len(x), compound
    return x.iloc[0]

# Table 2, carrots. Each listed pair is Trial 1 / Trial 2. The source states
# cooking trials were run on different days to account for raw-material
# variability; reported values are the mean ± SD of triplicate HPLC analyses.
CARROT = {
    "boiling": [(5, (37,27), (67,65), (24,21), (41,48)), (10, (37,27), (69,87), (24,21), (49,60)), (15, (37,27), (81,97), (24,21), (60,65)), (20, (37,27), (125,107), (24,21), (79,70)), (30, (37,27), (86,109), (24,21), (59,74))],
    "steaming": [(7.5, (27,42), (39,37), (21,32), (30,29)), (15, (27,42), (57,60), (21,32), (43,39)), (22.5, (27,42), (59,61), (21,32), (42,41)), (30, (27,42), (57,63), (21,32), (40,42))],
    "microwaving": [(5, (37,42), (40,38), (24,32), (24,26)), (10, (37,42), (44,49), (24,32), (32,38)), (15, (37,42), (33,54), (24,32), (20,36)), (20, (37,42), (41,40), (24,32), (25,29))],
}
# Table 3, orange-fleshed sweet potatoes; beta-carotene only.
SWEET = {
    "boiling": [(4, (33,39), (46,51)), (8, (33,39), (45,51)), (12, (33,39), (47,47)), (16, (33,39), (44,46))],
    "steaming": [(4, (33,39), (42,38)), (8, (33,39), (32,37)), (12, (33,39), (38,37)), (16, (33,39), (26,33))],
    "microwaving": [(6, (33,39), (37,53)), (8, (33,39), (45,47)), (10, (33,39), (33,41)), (15, (33,39), (32,31)), (20, (33,39), (26,31))],
}
METHOD = {
    "boiling": ("Boiling", "boiling", "300 g vegetable in 2 L unsalted tap water", None),
    "steaming": ("Steaming", "steaming", "900 W electric steamer, preheated to full vapour", None),
    "microwaving": ("Microwaving", "microwaving", "500 W microwave; covered vegetable vessel with 100 mL tap water below perforated tray", None),
}
rows=[]
def add(food, compound, method_key, minute, raw_pair, cooked_pair, trial):
    src = template("Beta-Carotene")
    method, norm, medium, temp = METHOD[method_key]
    raw, cooked = raw_pair[trial-1], cooked_pair[trial-1]
    token = f"{food}_{compound}_{norm}_{str(minute).replace('.', '_')}_T{trial}".upper().replace(" ", "_").replace("-", "_")
    row = {c: src[c] for c in base.columns}
    row.update({
        "observation_id": f"LIT-BURATTI2020-{token}", "original_record_id": "",
        "doi": "10.3390/foods9050607", "paper_id": "NEW_LITERATURE_BURATTI_2020",
        "source_locator": "Open primary article, Table 2 (carrot) or Table 3 (sweet potato), exact method section 2.2",
        "compound": compound,
        "canonical_molecular_id": "MOL-" + hashlib.sha256(compound.encode()).hexdigest()[:16].upper() if compound == "Alpha-Carotene" else src["canonical_molecular_id"],
        "food_matrix": food, "cooking_method": method, "cooking_method_normalized": norm, "cooking_medium": medium,
        "raw_concentration": raw, "cooked_concentration": cooked, "raw_sd": None, "cooked_sd": None,
        "concentration_unit": "mg/100 g dry weight", "measurement_basis": "dry-weight basis (common stated basis)",
        "target_name": "apparent_concentration_ratio_percent", "target_equation": "100 * C_cooked / C_raw", "target_value_percent": 100*cooked/raw,
        "target_semantics": "apparent concentration ratio; not total-mass retention", "evidence_status": "VERIFIED_PRIMARY_TABLE",
        "cooked_yield_status": "NOT_REPORTED", "total_mass_retention_status": "NOT_ESTABLISHED",
        "source_detail": "Buratti et al. (2020) Tables 2/3. Direct individual HPLC beta- or alpha-carotene concentrations on dry-weight basis. Trial 1 and Trial 2 are distinct cooking trials on different days/raw-material lots; each value is a triplicate analytical mean.",
        "Temperature_C": temp, "Cooking_Time_min": minute,
        "reported_replicate_design": "Two independent cooking trials conducted on different days to account for raw-material variability; each trial's individual sample was analyzed in triplicate. One table mean per condition/trial is one observation; no technical replicate is expanded.",
        "analytical_definition": "Individual beta-carotene or alpha-carotene quantified by HPLC (454 nm) against pure standards; never an aggregate carotenoid endpoint.",
    })
    rows.append(row)

for method, entries in CARROT.items():
    for minute, rb, cb, ra, ca in entries:
        for trial in (1,2):
            add("Carrot", "Beta-Carotene", method, minute, rb, cb, trial)
            add("Carrot", "Alpha-Carotene", method, minute, ra, ca, trial)
for method, entries in SWEET.items():
    for minute, raw, cooked in entries:
        for trial in (1,2): add("Orange-fleshed Sweet Potato", "Beta-Carotene", method, minute, raw, cooked, trial)

new=pd.DataFrame(rows, columns=base.columns)
master=pd.concat([base,new],ignore_index=True)
assert len(new)==78 and len(master)==1016 and master.doi.nunique()==32
assert not master.observation_id.duplicated().any() and new.canonical_molecular_id.notna().all()
assert (new.target_value_percent.round(8)==(100*new.cooked_concentration/new.raw_concentration).round(8)).all()
assert new.cooking_method_normalized.nunique()==3
master.to_csv(R/"updated_master_dataset.csv",index=False); new.to_csv(R/"verified_observations.csv",index=False); new.to_csv(R/"extracted_observations.csv",index=False)
reg=pd.read_csv(ROOT/"literature_candidate_registry.csv")
pd.concat([reg,pd.DataFrame([{"doi":"10.3390/foods9050607","title":"Influence of Cooking Conditions on Nutritional Properties and Sensory Characteristics Interpreted by E-Senses: Case-Study on Selected Vegetables","year":2020,"compound":"beta-carotene; alpha-carotene","food_matrix":"carrot; orange-fleshed sweet potato","cooking_method":"boiling; steaming; microwaving","measurement_technique":"HPLC, 454 nm, pure-standard calibration","measurement_basis":"dry-weight basis","raw_values":"Tables 2–3","cooked_values":"Tables 2–3","extractable_observations":78,"verification_status":"VERIFIED","rejection_reason":""}])],ignore_index=True,sort=False).to_csv(R/"literature_candidate_registry.csv",index=False)
exc=pd.read_csv(ROOT/"excluded_candidates.csv")
pd.concat([exc,pd.DataFrame([{"doi":"10.3390/foods9050607","title":"Influence of Cooking Conditions on Nutritional Properties and Sensory Characteristics Interpreted by E-Senses: Case-Study on Selected Vegetables","year":2020,"compound":"ascorbic acid; total phenolics; antioxidant activity; non-detects","food_matrix":"cauliflower; carrot; sweet potato","cooking_method":"boiling; steaming; microwaving","measurement_technique":"HPLC and non-specific assays","measurement_basis":"dry-weight basis","raw_values":"Tables 1–3","cooked_values":"Tables 1–3","extractable_observations":0,"verification_status":"PARTIAL_EXCLUSION","rejection_reason":"Only direct individual carotenoid analytes with positive raw/cooked values are admitted. Aggregate Folin/DPPH endpoints, non-detects and cauliflower ascorbate with unsuitable raw baseline are excluded."}])],ignore_index=True,sort=False).to_csv(R/"excluded_candidates.csv",index=False)
prior=pd.read_csv(ROOT/"batch_020"/"source_verification_ledger.csv")
pd.concat([prior,pd.DataFrame([{"doi":"10.3390/foods9050607","paper_title":"Influence of Cooking Conditions on Nutritional Properties and Sensory Characteristics Interpreted by E-Senses: Case-Study on Selected Vegetables","source_url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC7278733/","locator":"Methods 2.2; Tables 2–3; method 2.4 carotenoid HPLC; table footnotes","rows_admitted":78,"compound":"beta-carotene; alpha-carotene","basis":"mg/100 g dry weight","analytical_method":"HPLC 454 nm, pure standards","admission_status":"VERIFIED_PARTIAL","rationale":"Open primary tables report individual positive raw/cooked carotenoid values on one stated dry-weight basis, methods and cooking conditions. Two reported trials are genuinely separate cooking days/raw-material lots, not technical assay replicates."}])],ignore_index=True,sort=False).to_csv(R/"source_verification_ledger.csv",index=False)
master.groupby("doi").agg(observations=("observation_id","size"),compounds=("compound","nunique"),foods=("food_matrix","nunique"),methods=("cooking_method_normalized","nunique"),bases=("measurement_basis",lambda x:"; ".join(sorted(x.dropna().unique())))).reset_index().to_csv(R/"source_coverage_analysis.csv",index=False)
write("dataset_expansion_report.md",f"""# Scientific dataset expansion — controlled batch 021

The controlled master becomes **{len(master)} verified observations from {master.doi.nunique()} DOI families**, exceeding the 1,000-observation expansion threshold. Batch 021 adds 78 direct primary-table pairs from Buratti et al. (2020), DOI `10.3390/foods9050607`, preserving all 938 Batch-020 rows.

Tables 2–3 report individual HPLC beta-carotene and alpha-carotene concentrations in carrots and orange-fleshed sweet potatoes across boiling, steaming and microwaving times. All admitted values are on the stated dry-weight basis; the resulting target remains an apparent concentration ratio, never total-mass retention. The two cooking trials were performed on different days to account for raw-material variability, so they are preserved as separate experimental lots; within-trial triplicate assays are not expanded. Non-detects, aggregate assays and unsuitable cauliflower ascorbate baseline values remain excluded.
""")
write("reproduction_instructions.md","Run `python build_batch_021.py`, then `python validate_batch_021.py`. It reads Batch 020/current ledgers and writes only this package; it does not modify historical packages, Git, or Stage B/C/D.")
manifest={"package":"StageA_DatasetExpansion1000_Batch021_2026-11-11","parent_rows":938,"parent_sha256":sha(PARENT),"new_rows":78,"total_rows":len(master),"new_doi_families":1,"strict_cross_source_replications_created":0,"target_1000_reached":True,"stage_c_integration_authorized":False}
(R/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
(R/"SHA256SUMS.txt").write_text("\n".join(f"{sha(p)}  {p.name}" for p in sorted(R.iterdir()) if p.is_file() and p.name!="SHA256SUMS.txt")+"\n",encoding="utf-8")
print(json.dumps(manifest,indent=2))
