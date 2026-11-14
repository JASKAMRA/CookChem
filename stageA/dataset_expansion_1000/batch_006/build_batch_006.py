"""Controlled expansion batch 006: white-cauliflower primary HPLC table."""
from pathlib import Path
import hashlib, json
import pandas as pd

R=Path(__file__).resolve().parent
PARENT=R.parent/'batch_005'/'updated_master_dataset.csv'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,t): (R/n).write_text(t.strip()+'\n',encoding='utf-8')
base=pd.read_csv(PARENT)
def template(name):
    found=base.loc[base.compound.astype(str).str.casefold().eq(name.casefold())]
    assert len(found),name
    return found.iloc[0]

# Ahmed & Ali (2013), primary Table 3.  Table values are individual HPLC
# analytes in mg/100 g DW.  It supplies no per-analyte SD, so SD is left
# missing rather than invented; the HPLC method says each sample was triplicate.
values={
 'Catechin':(1.91,[('Steam blanching','steam blanching',0.85,100,3,'steam above 1000 mL boiling water'),('Steam boiling','steam boiling',0.71,100,6.25,'steam above 1000 mL boiling water')]),
 'Protocatechuic Acid':(192.4,[('Steam blanching','steam blanching',78.78,100,3,'steam above 1000 mL boiling water'),('Water blanching','water blanching',37.23,100,3,'1000 mL water / 200 g florets'),('Steam boiling','steam boiling',66.10,100,6.25,'steam above 1000 mL boiling water'),('Water boiling','water boiling',23.04,100,6,'1000 mL water / 200 g florets'),('Microwaving','microwave',67.41,pd.NA,3.5,'10 mL water / 200 g florets; 1000 W'),('Stir-frying','stir-frying',52.38,140,4.5,'10 mL sunflower oil / 200 g florets')]),
 'Chlorogenic Acid':(25.83,[('Steam blanching','steam blanching',11.36,100,3,'steam above 1000 mL boiling water'),('Steam boiling','steam boiling',8.14,100,6.25,'steam above 1000 mL boiling water'),('Microwaving','microwave',12.36,pd.NA,3.5,'10 mL water / 200 g florets; 1000 W'),('Stir-frying','stir-frying',10.45,140,4.5,'10 mL sunflower oil / 200 g florets')]),
 'Rutin':(2.57,[('Steam blanching','steam blanching',0.24,100,3,'steam above 1000 mL boiling water'),('Water blanching','water blanching',0.01,100,3,'1000 mL water / 200 g florets'),('Steam boiling','steam boiling',0.01,100,6.25,'steam above 1000 mL boiling water'),('Microwaving','microwave',0.12,pd.NA,3.5,'10 mL water / 200 g florets; 1000 W')]),
 'Caffeic acid':(0.77,[('Steam blanching','steam blanching',0.44,100,3,'steam above 1000 mL boiling water'),('Water blanching','water blanching',0.21,100,3,'1000 mL water / 200 g florets'),('Stir-frying','stir-frying',1.644,140,4.5,'10 mL sunflower oil / 200 g florets')]),
 'Quercetin':(202.46,[('Steam blanching','steam blanching',85.20,100,3,'steam above 1000 mL boiling water'),('Water blanching','water blanching',45.13,100,3,'1000 mL water / 200 g florets'),('Steam boiling','steam boiling',54.19,100,6.25,'steam above 1000 mL boiling water'),('Water boiling','water boiling',22.35,100,6,'1000 mL water / 200 g florets'),('Microwaving','microwave',61.78,pd.NA,3.5,'10 mL water / 200 g florets; 1000 W'),('Stir-frying','stir-frying',58.74,140,4.5,'10 mL sunflower oil / 200 g florets')]),
 'Cinnamic acid':(3.10,[('Steam blanching','steam blanching',0.35,100,3,'steam above 1000 mL boiling water'),('Steam boiling','steam boiling',0.25,100,6.25,'steam above 1000 mL boiling water'),('Water boiling','water boiling',0.24,100,6,'1000 mL water / 200 g florets')]),
 'Kaempferol':(25.91,[('Steam blanching','steam blanching',15.12,100,3,'steam above 1000 mL boiling water'),('Water blanching','water blanching',10.91,100,3,'1000 mL water / 200 g florets'),('Steam boiling','steam boiling',9.21,100,6.25,'steam above 1000 mL boiling water'),('Water boiling','water boiling',7.34,100,6,'1000 mL water / 200 g florets'),('Microwaving','microwave',11.36,pd.NA,3.5,'10 mL water / 200 g florets; 1000 W'),('Stir-frying','stir-frying',11.84,140,4.5,'10 mL sunflower oil / 200 g florets')]),
}
rows=[]
for compound,(raw,treatments) in values.items():
  src=template(compound)
  for method,normalized,cooked,temp,minutes,medium in treatments:
    safe=compound.upper().replace(' ','_').replace('-','_')
    row={c:src[c] for c in base.columns}
    row.update({'observation_id':f'LIT-AHMED2013-CAULIFLOWER_FLORET-{safe}-{normalized.upper().replace(" ","_").replace("-","_")}', 'original_record_id':'', 'doi':'10.1155/2013/367819', 'paper_id':'NEW_LITERATURE_AHMED_2013', 'source_locator':'Table 3; Methods §§2.1–2.3.7', 'compound':compound, 'food_matrix':'White cauliflower edible floret (Brassica oleracea var. botrytis)', 'cooking_method':method, 'cooking_method_normalized':normalized, 'cooking_medium':medium, 'raw_concentration':raw, 'cooked_concentration':cooked, 'concentration_unit':'mg/100 g dry weight', 'measurement_basis':'dry weight (DW)', 'target_name':'apparent_concentration_ratio_percent', 'target_equation':'100 * C_cooked / C_raw', 'target_value_percent':100*cooked/raw, 'target_semantics':'apparent concentration ratio; not total-mass retention', 'evidence_status':'VERIFIED_PRIMARY_TABLE', 'cooked_yield_status':'NOT_REPORTED', 'total_mass_retention_status':'NOT_ESTABLISHED', 'source_detail':'Ahmed and Ali (2013), Table 3. Individual HPLC phenolic analyte, mg/100 g DW; each sample analysed in triplicate; Table 3 does not report per-analyte SD.', 'Temperature_C':temp, 'Cooking_Time_min':minutes, 'raw_sd':pd.NA, 'cooked_sd':pd.NA, 'reported_replicate_design':'Each HPLC sample analysed in triplicate; Table 3 reports one condition mean, no per-analyte SD', 'analytical_definition':'Individual HPLC UV (280 nm) analyte; primary table dry-weight result'})
    rows.append(row)
new=pd.DataFrame(rows,columns=base.columns)
master=pd.concat([base,new],ignore_index=True)
assert len(new)==34 and len(master)==573 and master.doi.nunique()==18
assert new.canonical_molecular_id.notna().all() and not master.observation_id.duplicated().any()
assert (new.target_value_percent.round(9)==(100*new.cooked_concentration/new.raw_concentration).round(9)).all()
master.to_csv(R/'updated_master_dataset.csv',index=False);new.to_csv(R/'verified_observations.csv',index=False);new.to_csv(R/'extracted_observations.csv',index=False)
pd.DataFrame([{'doi':'10.1155/2013/367819','title':'Bioactive Compounds and Antioxidant Activity of Fresh and Processed White Cauliflower','year':2013,'admitted_rows':34,'status':'VERIFIED_PARTIAL','basis':'mg/100 g dry weight','reason':'Table 3 provides individual HPLC raw/cooked values; only detected compounds with exact pre-existing verified descriptor identities are included.'},{'doi':'10.3390/plants13101283','title':'Quantitative Determination of Biogenic Element Contents and Phytochemicals of Broccoli','year':2024,'admitted_rows':0,'status':'EXCLUDED_DUPLICATE_DOI','basis':'not used','reason':'Already contained in parent data; its table is not re-admitted.'}]).to_csv(R/'literature_candidate_registry.csv',index=False)
pd.DataFrame([{'category':'EXCLUDED_TABLE_VALUES','doi':'10.1155/2013/367819','reason':'ND cells are excluded. Gallic, pyrogallol, catechol, rosmarinic, vanillic and naringenin lack exact existing descriptor identities; generic Coumaric acid is not silently mapped to p-Coumaric acid.'},{'category':'EXCLUDED_SOURCE','doi':'10.3390/plants13101283','reason':'Duplicate DOI family already represented in the parent dataset.'}]).to_csv(R/'excluded_candidates.csv',index=False)
prior=pd.read_csv(R.parent/'batch_005'/'source_verification_ledger.csv')
extra=pd.DataFrame([{'doi':'10.1155/2013/367819','paper_title':'Bioactive Compounds and Antioxidant Activity of Fresh and Processed White Cauliflower','source_url':'https://downloads.hindawi.com/journals/bmri/2013/367819.pdf','locator':'Table 3; Methods §§2.1–2.3.7','rows_admitted':34,'compound':'Catechin; protocatechuic, chlorogenic, caffeic and cinnamic acids; rutin; quercetin; kaempferol','basis':'mg/100 g dry weight','analytical_method':'Individual HPLC UV (280 nm)','admission_status':'VERIFIED_PARTIAL','rationale':'Table 3 direct values; raw/cooked DW basis; methods directly specify all cooking conditions. Non-detects and identity-schema gaps excluded.'}])
pd.concat([prior,extra],ignore_index=True,sort=False).to_csv(R/'source_verification_ledger.csv',index=False)
coverage=master.groupby('doi').agg(observations=('observation_id','size'),compounds=('compound','nunique'),foods=('food_matrix','nunique'),methods=('cooking_method_normalized','nunique'),bases=('measurement_basis',lambda x:'; '.join(sorted(x.dropna().unique())))).reset_index();coverage.to_csv(R/'source_coverage_analysis.csv',index=False)
write('dataset_expansion_report.md',f'''# Scientific dataset expansion — controlled batch 006

The controlled master becomes **{len(master)} verified observations from {master.doi.nunique()} DOI families**. Batch 006 adds 34 direct raw/cooked, individual-analyte pairs from Ahmed and Ali (2013), DOI `10.1155/2013/367819`, while preserving the 539 parent records.

Primary Table 3 reports HPLC individual phenolics in white-cauliflower florets on a dry-weight basis after steam/water blanching, steam/water boiling, microwave cooking, and stir-frying. Methods document material, temperatures, durations and media. It says each HPLC sample was analysed in triplicate; because the table gives no per-analyte SD, no SD is inferred. ND cells, generic/ambiguous `Coumaric acid`, and molecules absent from the established exact-identity descriptor schema remain excluded.

No model is retrained. Stage C remains untouched and unauthorized; 427 observations are still required to reach 1,000.
''')
write('reproduction_instructions.md','''# Reproduction

Run `python build_batch_006.py`, then `python validate_batch_006.py`. The script reads Batch 005 only and writes only this package. It performs no remote, Git, historical-package, or Stage-B/C/D change.
''')
manifest={'package':'StageA_DatasetExpansion1000_Batch006_2026-11-10','parent_rows':539,'parent_sha256':sha(PARENT),'new_rows':34,'total_rows':len(master),'new_doi_families':1,'strict_cross_source_replications_created':0,'target_1000_reached':False,'stage_c_integration_authorized':False}
(R/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
(R/'SHA256SUMS.txt').write_text('\n'.join(f'{sha(p)}  {p.name}' for p in sorted(R.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt')+'\n',encoding='utf-8')
print(json.dumps(manifest,indent=2))
