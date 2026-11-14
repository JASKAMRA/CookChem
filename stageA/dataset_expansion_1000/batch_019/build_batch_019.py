"""Controlled expansion batch 019: multi-matrix vegetable primary HPLC evidence."""
from pathlib import Path
import hashlib, json
import pandas as pd
R=Path(__file__).resolve().parent; ROOT=R.parent; PARENT=ROOT/"batch_018"/"updated_master_dataset.csv"
base=pd.read_csv(PARENT)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def template(compound):
    h=base.loc[base.compound.astype(str).str.casefold().eq(compound.casefold())]
    assert len(h),compound
    return h.iloc[0]
def write(n,t): (R/n).write_text(t.strip()+"\n",encoding="utf-8")

# Miglio et al. (2008), Tables 2, 4, and 5. Values are raw, boiled,
# steamed, fried: all are individual means ± SD, dry-weight basis.
V={
 "Carrot":{
  "Lutein":(11,.2,12.2,.1,7.2,.1,6.3,.1), "Beta-Carotene":(53.8,.2,54.6,.2,48.5,.4,41,1),
  "Chlorogenic Acid":(44,1.5,None,None,2.2,.3,3.1,0), "Caffeic acid":(18,.1,None,None,29.9,3.2,29.3,2.4),
  "p-Coumaric acid":(6.8,.8,None,None,7.6,.3,8.1,.8), "Vitamin C":(30.8,1.5,28.1,.5,19.2,.3,None,None)},
 "Courgette":{
  "Lutein":(45.4,.3,40.6,1.8,30.5,.5,25.8,0), "Beta-Carotene":(4.8,.1,5.7,.1,5.8,0,4.3,0),
  "Caffeic acid":(39.9,1.3,12.7,.3,27.3,2.3,17.7,2.1), "p-Coumaric acid":(9.6,.1,3.2,.4,8,.8,4.2,.6),
  "Vitamin C":(193.8,9.5,186.5,8.6,165.6,6.3,167,6.2)},
 "Broccoli":{
  "Lutein":(16.9,.2,22.2,.3,18.1,.5,4.8,.1), "Beta-Carotene":(5.7,.2,6.6,.2,6.7,0,2,.1),
  "Chlorogenic Acid":(35.7,1.5,12.6,2,14.8,2.4,9.8,.7), "Caffeic acid":(2.8,.6,2.9,.9,2.8,.8,3.1,.4),
  "Sinapic acid":(9.4,.8,4.3,.2,5.9,.4,6.1,.6), "Ferulic Acid":(8.9,1,1.4,0,2.7,.5,2.8,1.5),
  "Quercetin":(18.9,1.8,2.2,.2,11.7,1.3,5.3,.4), "Kaempferol":(24.1,1.6,3.7,.1,23.9,2.8,13.3,.2),
  "Vitamin C":(847,4.7,437.6,14.5,575.5,7.3,113.3,1.3)} }
methods=(("Boiling","boiling","boiling tap water, 1:5 food/water; drained 30 s",pd.NA),("Atmospheric steaming","steaming","Combi-Steal oven, atmospheric pressure",pd.NA),("Deep frying","deep_frying","peanut oil, 170 C; drained and blotted",170))
rows=[]
for food, compounds in V.items():
 for compound,x in compounds.items():
  raw,raw_sd=x[:2]; src=template(compound)
  for i,(method,norm,medium,temp) in enumerate(methods):
   cooked,cooked_sd=x[2+i*2:4+i*2]
   if cooked is None: continue
   row={c:src[c] for c in base.columns}; token=f"{food}_{compound}_{norm}".upper().replace(" ","_").replace("-","_")
   row.update({"observation_id":f"LIT-MIGLIO2008-{token}","original_record_id":"","doi":"10.1021/jf072304b","paper_id":"NEW_LITERATURE_MIGLIO_2008","source_locator":{"Carrot":"Table 2","Courgette":"Table 4","Broccoli":"Table 5"}[food]+"; Methods Cooking Treatments","compound":compound,"food_matrix":food,"cooking_method":method,"cooking_method_normalized":norm,"cooking_medium":medium,"raw_concentration":raw,"raw_sd":raw_sd,"cooked_concentration":cooked,"cooked_sd":cooked_sd,"concentration_unit":"mg/100 g dry weight","measurement_basis":"dry weight (DW)","target_name":"apparent_concentration_ratio_percent","target_equation":"100 * C_cooked / C_raw","target_value_percent":100*cooked/raw,"target_semantics":"apparent concentration ratio; not total-mass retention","evidence_status":"VERIFIED_PRIMARY_TABLE","cooked_yield_status":"NOT_REPORTED","total_mass_retention_status":"NOT_ESTABLISHED","source_detail":"Miglio et al. (2008), direct individual table mean ± SD (n=3), all values expressed as mg/100 g dry weight. Source supplies treatment procedures but only states each vegetable had an optimized minimum time; no duration is invented.","Temperature_C":temp,"Cooking_Time_min":pd.NA,"reported_replicate_design":"Three cooked-method replicates per vegetable; published mean ± SD retained as one condition row, never expanded.","analytical_definition":"Individual HPLC/HPLC-DAD analyte; identity verified against standards/retention time or UV-vis as reported."})
   rows.append(row)
new=pd.DataFrame(rows,columns=base.columns); master=pd.concat([base,new],ignore_index=True)
assert len(new)==56 and len(master)==914 and master.doi.nunique()==30
assert not master.observation_id.duplicated().any() and new.canonical_molecular_id.notna().all()
assert (new.target_value_percent.round(8)==(100*new.cooked_concentration/new.raw_concentration).round(8)).all()
master.to_csv(R/"updated_master_dataset.csv",index=False); new.to_csv(R/"verified_observations.csv",index=False); new.to_csv(R/"extracted_observations.csv",index=False)
reg=pd.read_csv(ROOT/"literature_candidate_registry.csv")
pd.concat([reg,pd.DataFrame([{"doi":"10.1021/jf072304b","title":"Effects of Different Cooking Methods on Nutritional and Physicochemical Characteristics of Selected Vegetables","year":2008,"compound":"ten established individual compounds","food_matrix":"carrot; courgette; broccoli","cooking_method":"boiling; atmospheric steaming; deep frying","measurement_technique":"HPLC; HPLC-DAD","measurement_basis":"dry weight","raw_values":"Tables 2, 4, 5","cooked_values":"Tables 2, 4, 5","extractable_observations":56,"verification_status":"VERIFIED","rejection_reason":""}])],ignore_index=True,sort=False).to_csv(R/"literature_candidate_registry.csv",index=False)
exc=pd.read_csv(ROOT/"excluded_candidates.csv")
pd.concat([exc,pd.DataFrame([{"doi":"10.1021/jf072304b","title":"Effects of Different Cooking Methods on Nutritional and Physicochemical Characteristics of Selected Vegetables","year":2008,"compound":"alpha-carotene; cis-carotene; phytoene; phytofluene; beta-cryptoxanthin; total endpoints; raw/cooked nondetect cells","food_matrix":"carrot; courgette; broccoli","cooking_method":"boiling; atmospheric steaming; deep frying","measurement_technique":"HPLC; HPLC-DAD","measurement_basis":"dry weight","raw_values":"Tables 2, 4, 5","cooked_values":"Tables 2, 4, 5","extractable_observations":0,"verification_status":"PARTIAL_EXCLUSION","rejection_reason":"Only exact current canonical identities with positive raw and cooked values are admitted; unmapped or aggregate values and nondetect cells are excluded."}])],ignore_index=True,sort=False).to_csv(R/"excluded_candidates.csv",index=False)
prior=pd.read_csv(ROOT/"batch_018"/"source_verification_ledger.csv")
pd.concat([prior,pd.DataFrame([{"doi":"10.1021/jf072304b","paper_title":"Effects of Different Cooking Methods on Nutritional and Physicochemical Characteristics of Selected Vegetables","source_url":"https://www.greenme.com.br/wp-content/uploads/2015/05/Physicochemical-and-nutritional-qualities-of-vegetables-are-deeply-modified-by-domestic-cooking.pdf","locator":"Tables 2, 4, 5; Methods Cooking Treatments","rows_admitted":56,"compound":"Lutein; beta-carotene; chlorogenic, caffeic, p-coumaric, sinapic and ferulic acids; quercetin; kaempferol; Vitamin C","basis":"mg/100 g dry weight","analytical_method":"HPLC; HPLC-DAD","admission_status":"VERIFIED_PARTIAL","rationale":"Direct raw/cooked individual values with explicit common dry-weight basis and n=3. Conditions include 1:5 boiling, atmospheric steaming, and 170 C frying; duration deliberately missing because source reports optimized vegetable-specific duration without values."}])],ignore_index=True,sort=False).to_csv(R/"source_verification_ledger.csv",index=False)
master.groupby("doi").agg(observations=("observation_id","size"),compounds=("compound","nunique"),foods=("food_matrix","nunique"),methods=("cooking_method_normalized","nunique"),bases=("measurement_basis",lambda x:"; ".join(sorted(x.dropna().unique())))).reset_index().to_csv(R/"source_coverage_analysis.csv",index=False)
write("dataset_expansion_report.md",f"""# Scientific dataset expansion — controlled batch 019

The controlled master becomes **{len(master)} verified observations from {master.doi.nunique()} DOI families**. Batch 019 adds 56 direct primary-table pairs from Miglio et al. (2008), DOI `10.1021/jf072304b`, preserving every 858 parent row.

Tables 2, 4 and 5 contain individual compounds in carrot, courgette and broccoli on a shared dry-weight basis. Methods document 1:5 boiling-water treatment, atmospheric oven steaming, and peanut-oil frying at 170 °C. The authors report optimized vegetable-specific minimum times but do not give them, so time is retained missing. Only exact existing individual identities and positive raw/cooked pairs are admitted. No model is retrained; 86 observations remain to the target.
""")
write("reproduction_instructions.md","Run `python build_batch_019.py`, then `python validate_batch_019.py`. It reads Batch 018/current ledgers and writes only this package; it does not modify historical packages, Git, or Stage B/C/D.")
manifest={"package":"StageA_DatasetExpansion1000_Batch019_2026-11-10","parent_rows":858,"parent_sha256":sha(PARENT),"new_rows":56,"total_rows":len(master),"new_doi_families":1,"strict_cross_source_replications_created":0,"target_1000_reached":False,"stage_c_integration_authorized":False}
(R/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
(R/"SHA256SUMS.txt").write_text("\n".join(f"{sha(p)}  {p.name}" for p in sorted(R.iterdir()) if p.is_file() and p.name!="SHA256SUMS.txt")+"\n",encoding="utf-8")
print(json.dumps(manifest,indent=2))
