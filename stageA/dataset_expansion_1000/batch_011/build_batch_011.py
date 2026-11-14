"""Controlled expansion batch 011: solid-state microwave primary measurements."""
from pathlib import Path
import hashlib,json
import pandas as pd
R=Path(__file__).resolve().parent; PARENT=R.parent/'batch_010'/'updated_master_dataset.csv'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,t): (R/n).write_text(t.strip()+'\n',encoding='utf-8')
base=pd.read_csv(PARENT)
def template(x):
 f=base.loc[base.compound.astype(str).str.casefold().eq(x.casefold())]; assert len(f),x; return f.iloc[0]
methods=[('Conventional oven cooking','oven cooking',180,'14–15 min broccoli; 8–10 min pepper; 15–16 min carrot'),('Microwave cooking','microwave cooking',pd.NA,'2450 MHz, 350 W; 6–7 min broccoli; 3–4 min pepper; 8–10 min carrot'),('Solid-state microwave cooking','solid-state microwave cooking',pd.NA,'910 MHz within 902–928 MHz, 350 W; 9–11 min broccoli; 6–7 min pepper; 11–12 min carrot')]
vitamin={'Broccoli florets (Brassica oleracea var. italica)':(372.99,31.86,[(202.08,54.60),(300.11,50.00),(213.29,27.25)]),'Red pepper pieces (Capsicum annuum L. cv. Kapya)':(522.11,33.32,[(278.68,67.92),(409.59,59.96),(381.63,38.40)]),'Carrot slices (Daucus carota subsp. sativus)':(66.52,9.12,[(9.17,3.57),(28.43,5.88),(45.19,6.86)])}
beta_raw=(757.65,67.99); beta_cooked=[(647.52,46.72),(866.43,59.76),(868.69,31.61)]
rows=[]
def add(compound,food,raw,raw_sd,method,norm,temp,detail,cooked,cooked_sd):
 src=template(compound); safe=compound.upper().replace(' ','_').replace('-','_')
 row={c:src[c] for c in base.columns}; row.update({'observation_id':f'LIT-KAPLAN2024-{food.split(" ")[0].upper()}-{safe}-{norm.upper().replace(" ","_")}', 'original_record_id':'','doi':'10.3390/foods13213459','paper_id':'NEW_LITERATURE_KAPLAN_2024','source_locator':'Table 6 (Vitamin C) or Table 7 (β-carotene); Methods §§2.3–2.5','compound':compound,'food_matrix':food,'cooking_method':method,'cooking_method_normalized':norm,'cooking_medium':'dry heating; 100 g portion; target internal temperature 75 °C; '+detail,'raw_concentration':raw,'raw_sd':raw_sd,'cooked_concentration':cooked,'cooked_sd':cooked_sd,'concentration_unit':'mg/100 g dry basis','measurement_basis':'dry basis (as reported)','target_name':'apparent_concentration_ratio_percent','target_equation':'100 * C_cooked / C_raw','target_value_percent':100*cooked/raw,'target_semantics':'apparent concentration ratio; not total-mass retention','evidence_status':'VERIFIED_PRIMARY_TABLE','cooked_yield_status':'weight loss reported separately; not used for target','total_mass_retention_status':'NOT_ESTABLISHED','source_detail':'Kaplan and Fıratlıgil (2024). Vitamin C is individually quantified with HPLC-PAD against ascorbic-acid standard; β-carotene is directly quantified by UV/Vis absorbance. Means ± SD retained as reported.','Temperature_C':temp,'Cooking_Time_min':pd.NA,'reported_replicate_design':'Reported as mean ± SD; Table values are one condition mean, not expanded into technical rows.','analytical_definition':'Individual ascorbic acid by HPLC-PAD or directly quantified beta-carotene by specified UV/Vis method'})
 rows.append(row)
for food,(raw,sd,cells) in vitamin.items():
 for (method,norm,temp,detail),(cooked,cooked_sd) in zip(methods,cells): add('Vitamin C',food,raw,sd,method,norm,temp,detail,cooked,cooked_sd)
for (method,norm,temp,detail),(cooked,cooked_sd) in zip(methods,beta_cooked): add('Beta-Carotene','Carrot slices (Daucus carota subsp. sativus)',beta_raw[0],beta_raw[1],method,norm,temp,detail,cooked,cooked_sd)
new=pd.DataFrame(rows,columns=base.columns); master=pd.concat([base,new],ignore_index=True)
assert len(new)==12 and len(master)==719 and master.doi.nunique()==24
assert new.canonical_molecular_id.notna().all() and not master.observation_id.duplicated().any() and (new.target_value_percent.round(8)==(100*new.cooked_concentration/new.raw_concentration).round(8)).all()
master.to_csv(R/'updated_master_dataset.csv',index=False);new.to_csv(R/'verified_observations.csv',index=False);new.to_csv(R/'extracted_observations.csv',index=False)
pd.DataFrame([{'doi':'10.3390/foods13213459','title':'Effects of 910 MHz Solid-State Microwave Cooking on the Quality Properties of Broccoli, Carrots, and Red Peppers','year':2024,'admitted_rows':12,'status':'VERIFIED_PARTIAL','basis':'mg/100 g dry basis','reason':'Tables 6–7 give direct raw/cooked values with standard deviations, specified cooking conditions and individual Vitamin C / beta-carotene measurements.'}]).to_csv(R/'literature_candidate_registry.csv',index=False)
pd.DataFrame([{'category':'EXCLUDED_TABLE_VALUES','doi':'10.3390/foods13213459','reason':'Total phenolic content is an aggregate GAE assay; chlorophyll is aggregate; lycopene is outside the current exact descriptor set. These are not inferred or admitted.'}]).to_csv(R/'excluded_candidates.csv',index=False)
prior=pd.read_csv(R.parent/'batch_010'/'source_verification_ledger.csv');extra=pd.DataFrame([{'doi':'10.3390/foods13213459','paper_title':'Effects of 910 MHz Solid-State Microwave Cooking on the Quality Properties of Broccoli, Carrots, and Red Peppers','source_url':'https://pdfs.semanticscholar.org/6edf/5e0e22002c7df87718c23540a9d4790152ec.pdf','locator':'Tables 6–7; Methods §§2.3–2.5','rows_admitted':12,'compound':'Vitamin C; beta-carotene','basis':'mg/100 g dry basis','analytical_method':'Vitamin C HPLC-PAD; beta-carotene specified direct UV/Vis measurement','admission_status':'VERIFIED_PARTIAL','rationale':'Direct raw/cooked condition means ± SD, explicit cooking protocol, individual molecular targets; no technical-repeat expansion.'}]);pd.concat([prior,extra],ignore_index=True,sort=False).to_csv(R/'source_verification_ledger.csv',index=False)
master.groupby('doi').agg(observations=('observation_id','size'),compounds=('compound','nunique'),foods=('food_matrix','nunique'),methods=('cooking_method_normalized','nunique'),bases=('measurement_basis',lambda x:'; '.join(sorted(x.dropna().unique())))).reset_index().to_csv(R/'source_coverage_analysis.csv',index=False)
write('dataset_expansion_report.md',f'''# Scientific dataset expansion — controlled batch 011

The controlled master becomes **{len(master)} verified observations from {master.doi.nunique()} DOI families**. Batch 011 adds 12 primary-table pairs from Kaplan and Fıratlıgil (2024), DOI `10.3390/foods13213459`, preserving all 707 parent rows.

The source provides individual HPLC-PAD vitamin-C measurements for broccoli, red pepper and carrot plus direct beta-carotene measurements for carrot, all in mg/100 g dry basis. Cooking conditions are conventionally oven-cooked, 2450-MHz microwave cooked and 910-MHz solid-state microwave cooked, with a common 75 °C target internal temperature and reported method-specific time ranges. No interval midpoint is invented in the numeric time field. Aggregate total phenolics/chlorophyll and out-of-schema lycopene remain excluded. No model is retrained; 281 observations remain to the 1,000 target.
''')
write('reproduction_instructions.md','''# Reproduction
Run `python build_batch_011.py`, then `python validate_batch_011.py`. It reads only Batch 010 and writes only this package; no historical package, Git, or Stage B/C/D file is changed.
''')
m={'package':'StageA_DatasetExpansion1000_Batch011_2026-11-10','parent_rows':707,'parent_sha256':sha(PARENT),'new_rows':12,'total_rows':len(master),'new_doi_families':1,'strict_cross_source_replications_created':0,'target_1000_reached':False,'stage_c_integration_authorized':False};(R/'manifest.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8');(R/'SHA256SUMS.txt').write_text('\n'.join(f'{sha(p)}  {p.name}' for p in sorted(R.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt')+'\n',encoding='utf-8');print(json.dumps(m,indent=2))
