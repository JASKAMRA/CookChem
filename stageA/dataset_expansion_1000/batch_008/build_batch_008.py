"""Controlled expansion batch 008: red-potato HPLC-ESI-MS/MS primary table."""
from pathlib import Path
import hashlib,json
import pandas as pd
R=Path(__file__).resolve().parent;PARENT=R.parent/'batch_007'/'updated_master_dataset.csv'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,t):(R/n).write_text(t.strip()+'\n',encoding='utf-8')
base=pd.read_csv(PARENT)
def template(x):
 f=base.loc[base.compound.astype(str).str.casefold().eq(x.casefold())];assert len(f),x;return f.iloc[0]
rows=[]
# Acito et al. (2024) Table 1, values mg/kg FM.  Storage strata and commercial
# comparator are retained as explicit matrices; each mean condition is one row.
groups=[('PRC_T0','Patata Rossa di Colfiorito red-skinned potato (T0)',{'Catechin':(0.10,0.09,0.15),'Chlorogenic Acid':(139.48,238.77,173.72),'Caffeic acid':(2.19,22.11,18.81),'p-Coumaric acid':(0.09,0.36,0.23),'Ferulic Acid':(0.97,3.61,1.99),'Rutin':(1.07,12.48,4.03),'Isoquercitrin':(0.07,0.11,0.14)}),('PRC_T1','Patata Rossa di Colfiorito red-skinned potato (T1; 1 month storage)',{'Catechin':(0.07,None,0.04),'Chlorogenic Acid':(139.28,206.88,164.92),'Caffeic acid':(2.51,16.15,29.64),'p-Coumaric acid':(0.09,0.42,0.61),'Ferulic Acid':(1.69,3.15,3.74),'Rutin':(3.26,0.25,1.02)}),('Commercial_RSP','Commercial red-skinned potato (France)',{'Chlorogenic Acid':(21.47,99.12,180.19),'Caffeic acid':(0.44,19.90,28.76),'p-Coumaric acid':(0.07,0.10,0.32),'Ferulic Acid':(1.72,3.34,6.05),'Rutin':(0.12,0.02,0.80)})]
for group,food,data in groups:
 for compound,(raw,boiled,pressure) in data.items():
  for method,norm,cooked,mins in [('Boiling','boiling',boiled,40),('Pressure cooking','pressure cooking',pressure,20)]:
   if cooked is None:continue
   src=template(compound);safe=compound.upper().replace(' ','_').replace('-','_')
   row={c:src[c] for c in base.columns};row.update({'observation_id':f'LIT-ACITO2024-{group}-{safe}-{norm.upper().replace(" ","_")}', 'original_record_id':'','doi':'10.1016/j.jff.2024.106380','paper_id':'NEW_LITERATURE_ACITO_2024','source_locator':'Table 1; Methods §§2.2–2.3','compound':compound,'food_matrix':food,'cooking_method':method,'cooking_method_normalized':norm,'cooking_medium':'2 L tap water; unpeeled whole tubers','raw_concentration':raw,'cooked_concentration':cooked,'concentration_unit':'mg/kg fresh matter','measurement_basis':'fresh matter (FM)','target_name':'apparent_concentration_ratio_percent','target_equation':'100 * C_cooked / C_raw','target_value_percent':100*cooked/raw,'target_semantics':'apparent concentration ratio; not total-mass retention','evidence_status':'VERIFIED_PRIMARY_TABLE','cooked_yield_status':'NOT_REPORTED','total_mass_retention_status':'NOT_ESTABLISHED','source_detail':'Acito et al. (2024), Table 1. Individual HPLC-ESI-MS/MS analyte in raw, boiled, and pressure-cooked potato; table reports mg/kg fresh matter, with RSD range 2.26–7.87%.','Temperature_C':pd.NA,'Cooking_Time_min':mins,'raw_sd':pd.NA,'cooked_sd':pd.NA,'reported_replicate_design':'Two sacks/replicates; each sample pooled from three tubers (commercial: six tubers from two sacks); Table 1 reports no per-cell SD','analytical_definition':'Individual HPLC-ESI-MS/MS analyte; 70% methanol/0.1% HCl extract'})
   rows.append(row)
new=pd.DataFrame(rows,columns=base.columns);master=pd.concat([base,new],ignore_index=True)
assert len(new)==35 and len(master)==635 and master.doi.nunique()==21
assert new.canonical_molecular_id.notna().all() and not master.observation_id.duplicated().any();assert (new.target_value_percent.round(8)==(100*new.cooked_concentration/new.raw_concentration).round(8)).all()
master.to_csv(R/'updated_master_dataset.csv',index=False);new.to_csv(R/'verified_observations.csv',index=False);new.to_csv(R/'extracted_observations.csv',index=False)
pd.DataFrame([{'doi':'10.1016/j.jff.2024.106380','title':'Patata Rossa di Colfiorito IGP (Solanum tuberosum, L.) and health-promoting potentialities: Do cooking techniques and storage affect chemical profile and antioxidant activity?','year':2024,'admitted_rows':35,'status':'VERIFIED_PARTIAL','basis':'mg/kg fresh matter','reason':'Table 1 gives direct individual HPLC-ESI-MS/MS raw/cooked values. Only positive raw/cooked pairs with exact current descriptor identities are admitted; T0, T1 storage and commercial matrices retained separately.'}]).to_csv(R/'literature_candidate_registry.csv',index=False)
pd.DataFrame([{'category':'EXCLUDED_TABLE_VALUES','doi':'10.1016/j.jff.2024.106380','reason':'All non-detect cells excluded. Gallic, neochlorogenic, hydroxybenzoic, anthocyanin, hyperoside, phloridzin and other molecules without exact established descriptor identities are not inferred.'}]).to_csv(R/'excluded_candidates.csv',index=False)
prior=pd.read_csv(R.parent/'batch_007'/'source_verification_ledger.csv');extra=pd.DataFrame([{'doi':'10.1016/j.jff.2024.106380','paper_title':'Patata Rossa di Colfiorito IGP and health-promoting potentialities: Do cooking techniques and storage affect chemical profile and antioxidant activity?','source_url':'https://pubblicazioni.unicam.it/bitstream/11581/487507/1/Patata%20Rossa%20di%20Colfiorito%20IGP.pdf','locator':'Table 1; Methods §§2.2–2.3','rows_admitted':35,'compound':'Catechin; chlorogenic, caffeic, p-coumaric and ferulic acids; rutin; isoquercitrin','basis':'mg/kg fresh matter','analytical_method':'Individual HPLC-ESI-MS/MS','admission_status':'VERIFIED_PARTIAL','rationale':'Direct raw/boiled/pressure-cooked individual values with fresh-matter table basis and explicit cooking protocol.'}]);pd.concat([prior,extra],ignore_index=True,sort=False).to_csv(R/'source_verification_ledger.csv',index=False)
master.groupby('doi').agg(observations=('observation_id','size'),compounds=('compound','nunique'),foods=('food_matrix','nunique'),methods=('cooking_method_normalized','nunique'),bases=('measurement_basis',lambda x:'; '.join(sorted(x.dropna().unique())))).reset_index().to_csv(R/'source_coverage_analysis.csv',index=False)
write('dataset_expansion_report.md',f'''# Scientific dataset expansion — controlled batch 008

The controlled master becomes **{len(master)} verified observations from {master.doi.nunique()} DOI families**. Batch 008 adds 35 primary-table raw/cooked pairs from Acito et al. (2024), DOI `10.1016/j.jff.2024.106380`, and preserves all 600 parent rows.

Table 1 reports individual HPLC-ESI-MS/MS values in mg/kg fresh matter for raw, boiled (40 min), and pressure-cooked (20 min) red-skinned potatoes. The explicit matrices retain cultivar/commercial provenance and T0/T1 storage status; no technical replicate is turned into a data row. Only positive raw/cooked values with existing exact molecular identities are included; all non-detects and unmapped identities remain excluded. No model is retrained; 365 observations remain to the 1,000 target.
''')
write('reproduction_instructions.md','''# Reproduction
Run `python build_batch_008.py`, then `python validate_batch_008.py`. It reads only Batch 007 and writes only this package; no historical package, Git, or Stage B/C/D file is changed.
''')
m={'package':'StageA_DatasetExpansion1000_Batch008_2026-11-10','parent_rows':600,'parent_sha256':sha(PARENT),'new_rows':35,'total_rows':len(master),'new_doi_families':1,'strict_cross_source_replications_created':0,'target_1000_reached':False,'stage_c_integration_authorized':False};(R/'manifest.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8');(R/'SHA256SUMS.txt').write_text('\n'.join(f'{sha(p)}  {p.name}' for p in sorted(R.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt')+'\n',encoding='utf-8');print(json.dumps(m,indent=2))
