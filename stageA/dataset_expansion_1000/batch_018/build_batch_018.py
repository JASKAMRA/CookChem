"""Controlled expansion batch 018: wild edible leaf primary-table evidence."""
from pathlib import Path
import hashlib, json
import pandas as pd

R=Path(__file__).resolve().parent; ROOT=R.parent; PARENT=ROOT/"batch_016"/"updated_master_dataset.csv"
base=pd.read_csv(PARENT)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def template(compound):
    h=base.loc[base.compound.astype(str).str.casefold().eq(compound.casefold())]
    assert len(h), compound
    return h.iloc[0]
def write(name,text): (R/name).write_text(text.strip()+"\n",encoding="utf-8")

# Fratianni et al. (2024), Tables 2 and 3; fresh-weight means (SD).
# The study reports separate raw, boiled and steamed sample means, each only once.
foods={
 "Sonchus oleraceus leaves": {"Lutein":(5.7,.6,6.0,.0,5.6,.3), "Beta-Carotene":(1.8,.1,1.8,.2,1.3,.0), "Gamma-Tocopherol":(.3,.0,.4,.0,.4,.0)},
 "Sonchus asper leaves": {"Lutein":(6.1,.1,5.5,.2,4.8,.2), "Beta-Carotene":(2.2,.1,2.4,.1,1.8,.0), "Gamma-Tocopherol":(.3,.0,.3,.0,.4,.0)},
 "Spinach leaves (Spinacia oleracea)": {"Lutein":(8.5,.4,7.2,.3,7.7,.5), "Beta-Carotene":(3.1,.6,2.6,.1,2.3,.1), "Gamma-Tocopherol":(.3,.0,.4,.0,.4,.0)},
 "Chicory leaves (Cichorium intybus)": {"Lutein":(6.1,.3,6.7,.2,6.2,.3), "Beta-Carotene":(4.7,.4,4.8,.1,4.0,.1), "Gamma-Tocopherol":(.9,.1,.9,.1,.8,.0)},
 "Chard leaves (Beta vulgaris var. cicla)": {"Lutein":(8.8,.4,9.5,.1,9.2,.1), "Beta-Carotene":(2.9,.0,2.6,.4,2.7,.2), "Gamma-Tocopherol":(.2,.0,.3,.0,.3,.0)},
}
treatments=(("Boiling","boiling","1:10 leaves/water, 100 g in 1 L boiling water",100), ("Steaming","steaming","100 g leaves on rack over boiling water in closed water bath",100))
rows=[]
for food, compounds in foods.items():
  for compound, (raw,raw_sd,boiled,boiled_sd,steamed,steamed_sd) in compounds.items():
    src=template(compound)
    for method,normalized,medium,temp in treatments:
      cooked,cooked_sd=(boiled,boiled_sd) if normalized=="boiling" else (steamed,steamed_sd)
      row={c:src[c] for c in base.columns}; ft=food.upper().replace(" ","_").replace("(","").replace(")","").replace(".","").replace("-","_")
      row.update({"observation_id":f"LIT-FRATIANNI2024-{ft}-{compound.upper().replace('-','_')}-{normalized.upper()}","original_record_id":"","doi":"10.3390/foods13030472","paper_id":"NEW_LITERATURE_FRATIANNI_2024","source_locator":"Table 2 or Table 3; Methods 2.2","compound":compound,"food_matrix":food,"cooking_method":method,"cooking_method_normalized":normalized,"cooking_medium":medium,"raw_concentration":raw,"raw_sd":raw_sd,"cooked_concentration":cooked,"cooked_sd":cooked_sd,"concentration_unit":"mg/100 g fresh weight","measurement_basis":"fresh weight (FW)","target_name":"apparent_concentration_ratio_percent","target_equation":"100 * C_cooked / C_raw","target_value_percent":100*cooked/raw,"target_semantics":"apparent concentration ratio; not total-mass retention","evidence_status":"VERIFIED_PRIMARY_TABLE","cooked_yield_status":"NOT_REPORTED","total_mass_retention_status":"NOT_ESTABLISHED","source_detail":"Fratianni et al. (2024), Tables 2/3: individual fresh-weight results expressed as mean (SD), n=3 treatment repetitions. Raw, boiled and steamed samples all freeze-dried only after treatment before analysis; values reported on original fresh-weight basis.","Temperature_C":temp,"Cooking_Time_min":10,"reported_replicate_design":"Three treatment repetitions per sample; reported means with SD, not expanded into replicate observations.","analytical_definition":"Individual HPLC analyte with authenticated standard; raw/cooked table mean on fresh-weight basis."})
      rows.append(row)
new=pd.DataFrame(rows,columns=base.columns); master=pd.concat([base,new],ignore_index=True)
assert len(new)==30 and len(master)==858 and master.doi.nunique()==29
assert not master.observation_id.duplicated().any() and new.canonical_molecular_id.notna().all()
assert (new.target_value_percent.round(8)==(100*new.cooked_concentration/new.raw_concentration).round(8)).all()
master.to_csv(R/"updated_master_dataset.csv",index=False); new.to_csv(R/"verified_observations.csv",index=False); new.to_csv(R/"extracted_observations.csv",index=False)
reg=pd.read_csv(ROOT/"literature_candidate_registry.csv")
pd.concat([reg,pd.DataFrame([{"doi":"10.3390/foods13030472","title":"Evaluation of the Content of Minerals, B-Group Vitamins, Tocols, and Carotenoids in Raw and In-House Cooked Wild Edible Plants","year":2024,"compound":"lutein; beta-carotene; gamma-tocopherol","food_matrix":"five leafy vegetable matrices","cooking_method":"boiling; steaming","measurement_technique":"HPLC","measurement_basis":"fresh weight","raw_values":"Tables 2-3","cooked_values":"Tables 2-3","extractable_observations":30,"verification_status":"VERIFIED","rejection_reason":""}])],ignore_index=True,sort=False).to_csv(R/"literature_candidate_registry.csv",index=False)
exc=pd.read_csv(ROOT/"excluded_candidates.csv")
pd.concat([exc,pd.DataFrame([{"doi":"10.3390/foods13030472","title":"Evaluation of the Content of Minerals, B-Group Vitamins, Tocols, and Carotenoids in Raw and In-House Cooked Wild Edible Plants","year":2024,"compound":"other carotenoids, alpha/beta tocopherol, thiamine, riboflavin, total endpoints","food_matrix":"five leafy vegetable matrices","cooking_method":"boiling; steaming","measurement_technique":"HPLC and other methods","measurement_basis":"fresh weight","raw_values":"Tables 2-3","cooked_values":"Tables 2-3","extractable_observations":0,"verification_status":"PARTIAL_EXCLUSION","rejection_reason":"Only exact established canonical individual identities are admitted; isomers, unregistered identities, minerals, and aggregate endpoints are excluded."}])],ignore_index=True,sort=False).to_csv(R/"excluded_candidates.csv",index=False)
prior=pd.read_csv(ROOT/"batch_016"/"source_verification_ledger.csv")
pd.concat([prior,pd.DataFrame([{"doi":"10.3390/foods13030472","paper_title":"Evaluation of the Content of Minerals, B-Group Vitamins, Tocols, and Carotenoids in Raw and In-House Cooked Wild Edible Plants","source_url":"https://www.mdpi.com/2304-8158/13/3/472/pdf?version=1706847114","locator":"Tables 2-3; Methods 2.2","rows_admitted":30,"compound":"Lutein; beta-carotene; gamma-tocopherol","basis":"mg/100 g fresh weight","analytical_method":"HPLC","admission_status":"VERIFIED_PARTIAL","rationale":"Direct raw/boiled/steamed numerical tables use explicit fresh-weight basis; methods specify 10-min boiling or steaming and n=3 treatment repetitions. Only exact current canonical identities retained."}])],ignore_index=True,sort=False).to_csv(R/"source_verification_ledger.csv",index=False)
master.groupby("doi").agg(observations=("observation_id","size"),compounds=("compound","nunique"),foods=("food_matrix","nunique"),methods=("cooking_method_normalized","nunique"),bases=("measurement_basis",lambda x:"; ".join(sorted(x.dropna().unique())))).reset_index().to_csv(R/"source_coverage_analysis.csv",index=False)
write("dataset_expansion_report.md",f"""# Scientific dataset expansion — controlled batch 018

The controlled master becomes **{len(master)} verified observations from {master.doi.nunique()} DOI families**. Batch 018 adds 30 pairs from Fratianni et al. (2024), DOI `10.3390/foods13030472`, preserving every 828 parent row.

Tables 2–3 give direct individual fresh-weight means (SD) for lutein, beta-carotene and gamma-tocopherol in five leafy matrices before and after boiling or steaming. Methods retain 100 g leaves, a 1:10 boiling-water ratio or rack steaming over boiling water, and 10-min duration. The source reports three treatment repetitions; each condition mean remains one row. Unregistered identities, isomers and aggregate/non-target endpoints are excluded. No model is retrained; 142 observations remain to the target.
""")
write("reproduction_instructions.md","Run `python build_batch_018.py`, then `python validate_batch_018.py`. It reads Batch 016/current ledgers and writes only this package; it does not modify historical packages, Git, or Stage B/C/D.")
manifest={"package":"StageA_DatasetExpansion1000_Batch018_2026-11-10","parent_rows":828,"parent_sha256":sha(PARENT),"new_rows":30,"total_rows":len(master),"new_doi_families":1,"strict_cross_source_replications_created":0,"target_1000_reached":False,"stage_c_integration_authorized":False}
(R/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
(R/"SHA256SUMS.txt").write_text("\n".join(f"{sha(p)}  {p.name}" for p in sorted(R.iterdir()) if p.is_file() and p.name!="SHA256SUMS.txt")+"\n",encoding="utf-8")
print(json.dumps(manifest,indent=2))
