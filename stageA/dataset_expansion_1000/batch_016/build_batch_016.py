"""Controlled expansion batch 016: primary Brassica HPLC carotenoid evidence."""
from pathlib import Path
import hashlib, json
import pandas as pd

R = Path(__file__).resolve().parent
ROOT = R.parent
PARENT = ROOT / "batch_015" / "updated_master_dataset.csv"
base = pd.read_csv(PARENT)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def template(compound):
    h = base.loc[base.compound.astype(str).str.casefold().eq(compound.casefold())]
    assert len(h), compound
    return h.iloc[0]
def write(name, text): (R / name).write_text(text.strip() + "\n", encoding="utf-8")

# Pellegrini et al. (2010), Tables 2, 3, 5 and 6.  Table footnotes state
# mean +/- SD (n=3), dry-weight basis and identification by pure standards.
# The nested values follow the source's four treatment order: boil, microwave,
# basket steam, oven steam.  Each published condition mean remains one row.
groups = {
    "Fresh broccoli florets": {"times": (8,30,15,13), "Lutein": (8.4,.4, [(5.6,1.1),(5.5,0.0),(8.8,1.3),(10.5,1.1)]), "Beta-Carotene": (5.0,.4, [(4.1,1.2),(2.0,.2),(4.8,.7),(5.5,.6)])},
    "Frozen broccoli florets/stems": {"times": (15,13,14,12), "Lutein": (12.3,.4, [(8.8,.2),(6.0,.5),(6.9,.2),(5.8,.5)]), "Beta-Carotene": (9.4,.3, [(6.5,.6),(3.8,.5),(3.8,.2),(3.7,.1)])},
    "Fresh Brussels sprouts": {"times": (10,18,18,17), "Lutein": (.9,.1, [(2.1,.1),(1.1,.1),(.9,.1),(.8,0.0)]), "Beta-Carotene": (1.7,.1, [(1.5,.1),(1.0,.1),(.7,.2),(.5,0.0)])},
    "Frozen Brussels sprouts": {"times": (7,6,10,12), "Lutein": (1.6,.1, [(1.7,.2),(1.6,0.0),(1.7,.1),(1.4,.1)]), "Beta-Carotene": (1.1,0.0, [(1.0,.1),(1.3,.1),(1.0,0.0),(1.1,0.0)])},
}
treatments = (
    ("Boiling", "boiling", "boiling tap water, 1:5 food/water", 100),
    ("Microwave", "microwave", "no added water; 300 W, 2450 MHz", pd.NA),
    ("Basket steaming", "steaming", "steam basket above boiling water", 100),
    ("Oven steaming", "oven_steaming", "air/steam impingement oven", 100),
)
rows=[]
for food, info in groups.items():
    for compound in ("Lutein", "Beta-Carotene"):
        raw, raw_sd, cooked_values = info[compound]
        src = template(compound)
        for i, ((method, normalized, medium, temp), (cooked, cooked_sd)) in enumerate(zip(treatments, cooked_values)):
            row={c:src[c] for c in base.columns}
            food_id=food.upper().replace(" ","_").replace("/","_")
            row.update({
                "observation_id": f"LIT-PELLEGRINI2010-{food_id}-{compound.upper().replace('-','_')}-{normalized.upper()}",
                "original_record_id":"", "doi":"10.1021/jf904306r", "paper_id":"NEW_LITERATURE_PELLEGRINI_2010",
                "source_locator": {"Fresh broccoli florets":"Table 2", "Frozen broccoli florets/stems":"Table 3", "Fresh Brussels sprouts":"Table 5", "Frozen Brussels sprouts":"Table 6"}[food] + "; Methods, Cooking Treatments",
                "compound":compound, "food_matrix":food, "cooking_method":method, "cooking_method_normalized":normalized, "cooking_medium":medium,
                "raw_concentration":raw,"raw_sd":raw_sd,"cooked_concentration":cooked,"cooked_sd":cooked_sd,
                "concentration_unit":"mg/100 g dry weight","measurement_basis":"dry weight (DW)",
                "target_name":"apparent_concentration_ratio_percent","target_equation":"100 * C_cooked / C_raw","target_value_percent":100*cooked/raw,
                "target_semantics":"apparent concentration ratio; not total-mass retention","evidence_status":"VERIFIED_PRIMARY_TABLE",
                "cooked_yield_status":"NOT_REPORTED","total_mass_retention_status":"NOT_ESTABLISHED",
                "source_detail":"Pellegrini et al. (2010), direct individual HPLC-DAD carotenoid table mean ± SD (n=3); source footnote states dry-weight basis and pure-standard identification. Matched raw/cooked portions retained without replicate expansion.",
                "Temperature_C":temp,"Cooking_Time_min":info["times"][i],
                "reported_replicate_design":"Three cooking trials per condition; source reports mean ± SD (n=3). Never expanded into replicate observations.",
                "analytical_definition":"Individual HPLC-DAD lutein or beta-carotene, dry-weight result",
            })
            rows.append(row)
new=pd.DataFrame(rows, columns=base.columns)
master=pd.concat([base,new], ignore_index=True)
assert len(new)==32 and len(master)==828 and master.doi.nunique()==28
assert not master.observation_id.duplicated().any() and new.canonical_molecular_id.notna().all()
assert (new.target_value_percent.round(8)==(100*new.cooked_concentration/new.raw_concentration).round(8)).all()
master.to_csv(R/"updated_master_dataset.csv",index=False); new.to_csv(R/"verified_observations.csv",index=False); new.to_csv(R/"extracted_observations.csv",index=False)

reg=pd.read_csv(ROOT/"literature_candidate_registry.csv")
pd.concat([reg,pd.DataFrame([{"doi":"10.1021/jf904306r","title":"Effect of Different Cooking Methods on Color, Phytochemical Concentration, and Antioxidant Capacity of Raw and Frozen Brassica Vegetables","year":2010,"compound":"lutein; beta-carotene","food_matrix":"fresh/frozen broccoli; fresh/frozen Brussels sprouts","cooking_method":"boiling; microwave; basket steam; oven steam","measurement_technique":"HPLC-DAD","measurement_basis":"dry weight","raw_values":"Tables 2, 3, 5, 6","cooked_values":"Tables 2, 3, 5, 6","extractable_observations":32,"verification_status":"VERIFIED","rejection_reason":""}])],ignore_index=True,sort=False).to_csv(R/"literature_candidate_registry.csv",index=False)
exc=pd.read_csv(ROOT/"excluded_candidates.csv")
pd.concat([exc,pd.DataFrame([{"doi":"10.1021/jf904306r","title":"Effect of Different Cooking Methods on Color, Phytochemical Concentration, and Antioxidant Capacity of Raw and Frozen Brassica Vegetables","year":2010,"compound":"total endpoints, chlorophylls, glucosinolates and non-carotenoid analytes","food_matrix":"Brassica vegetables","cooking_method":"as reported","measurement_technique":"HPLC-DAD/LC-MS and aggregate assays","measurement_basis":"dry weight","raw_values":"Tables 2-8","cooked_values":"Tables 2-8","extractable_observations":0,"verification_status":"PARTIAL_EXCLUSION","rejection_reason":"This batch deliberately retains only exact established carotenoid identities; aggregate and out-of-scope endpoints are not admitted."}])],ignore_index=True,sort=False).to_csv(R/"excluded_candidates.csv",index=False)
prior=pd.read_csv(ROOT/"batch_015"/"source_verification_ledger.csv")
pd.concat([prior,pd.DataFrame([{"doi":"10.1021/jf904306r","paper_title":"Effect of Different Cooking Methods on Color, Phytochemical Concentration, and Antioxidant Capacity of Raw and Frozen Brassica Vegetables","source_url":"https://electronicsandbooks.com/edt/manual/Magazine/J/Journal%20of%20Agricultural%20and%20Food%20Chemistry/2010_58/07/4310-4321.pdf","locator":"Tables 2, 3, 5 and 6; Cooking Treatments","rows_admitted":32,"compound":"Lutein; beta-carotene","basis":"mg/100 g dry weight","analytical_method":"HPLC-DAD, pure standards","admission_status":"VERIFIED_PARTIAL","rationale":"Direct raw/cooked values, explicit dry-weight basis, documented four cooking protocols and n=3 means ± SD; only exact existing individual carotenoids retained."}])],ignore_index=True,sort=False).to_csv(R/"source_verification_ledger.csv",index=False)
master.groupby("doi").agg(observations=("observation_id","size"),compounds=("compound","nunique"),foods=("food_matrix","nunique"),methods=("cooking_method_normalized","nunique"),bases=("measurement_basis",lambda x:"; ".join(sorted(x.dropna().unique())))).reset_index().to_csv(R/"source_coverage_analysis.csv",index=False)
write("dataset_expansion_report.md",f"""# Scientific dataset expansion — controlled batch 016

The controlled master becomes **{len(master)} verified observations from {master.doi.nunique()} DOI families**. Batch 016 adds 32 primary-table pairs from Pellegrini et al. (2010), DOI `10.1021/jf904306r`, preserving all 796 parent rows.

Tables 2, 3, 5 and 6 directly report HPLC-DAD lutein and beta-carotene values for fresh/frozen broccoli and Brussels sprouts on dry-weight basis. The source Methods document boiling (1:5 food/water), 300-W no-water microwave, basket steaming and 100 °C oven steaming, with food-specific times retained in the records. Source values are mean ± SD (n=3); no replicate expansion occurs. Other endpoints are excluded. No model is retrained; 172 observations remain to the target.
""")
write("reproduction_instructions.md","Run `python build_batch_016.py`, then `python validate_batch_016.py`. It reads only Batch 015/current ledgers and writes only this package; it does not modify historical packages, Git, or Stage B/C/D.\n")
manifest={"package":"StageA_DatasetExpansion1000_Batch016_2026-11-10","parent_rows":796,"parent_sha256":sha(PARENT),"new_rows":32,"total_rows":len(master),"new_doi_families":1,"strict_cross_source_replications_created":0,"target_1000_reached":False,"stage_c_integration_authorized":False}
(R/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
(R/"SHA256SUMS.txt").write_text("\n".join(f"{sha(p)}  {p.name}" for p in sorted(R.iterdir()) if p.is_file() and p.name!="SHA256SUMS.txt")+"\n",encoding="utf-8")
print(json.dumps(manifest,indent=2))
