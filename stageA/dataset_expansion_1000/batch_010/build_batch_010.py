"""Controlled expansion batch 010: cauliflower HPLC-PDA primary table."""
from pathlib import Path
import hashlib,json
import pandas as pd
R=Path(__file__).resolve().parent; PARENT=R.parent/'batch_009'/'updated_master_dataset.csv'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,t): (R/n).write_text(t.strip()+'\n',encoding='utf-8')
base=pd.read_csv(PARENT)
def template(x):
    f=base.loc[base.compound.astype(str).str.casefold().eq(x.casefold())]; assert len(f),x; return f.iloc[0]

# AlJuhaimi et al. (2024), Table 2. Each tuple is mean, SD on mg/100 g DW.
conditions=[
 ('Pressure cooking','pressure cooking',120,6,'500 mL water per 1 kg florets',
  {'Catechin':(482.03,18.03),'Caffeic acid':(39.30,.79),'Syringic acid':(20.56,.35),'Rutin':(71.74,2.83),'p-Coumaric acid':(4.78,.13),'Ferulic Acid':(5.20,.07),'Resveratrol':(3.96,.05),'Quercetin':(2.91,.02),'Cinnamic acid':(1.73,.01),'Kaempferol':(5.04,.06)}),
 ('Conventional boiling','boiling',100,13,'water, 1:1 w/v florets:water',
  {'Catechin':(443.91,17.43),'Caffeic acid':(36.84,.34),'Syringic acid':(20.32,.22),'Rutin':(40.86,.20),'p-Coumaric acid':(1.52,.02),'Ferulic Acid':(3.84,.07),'Resveratrol':(2.99,.02),'Quercetin':(6.48,.04),'Cinnamic acid':(.80,.01),'Kaempferol':(7.36,.15)}),
 ('Oven heating','oven heating',120,35,'florets in a single layer on Teflon tray',
  {'Catechin':(79.75,5.51),'Caffeic acid':(3.73,.36),'Syringic acid':(6.43,.94),'Rutin':(19.53,1.05),'p-Coumaric acid':(2.20,.34),'Ferulic Acid':(2.20,.11),'Resveratrol':(.96,.06),'Quercetin':(.63,.07),'Cinnamic acid':(.39,.01),'Kaempferol':(.53,.05)}),
 ('Microwave heating','microwave heating',900,12,'0.5 kg florets in a single layer; turned intermittently',
  {'Catechin':(94.05,7.57),'Caffeic acid':(15.05,.25),'Syringic acid':(20.75,3.38),'Rutin':(31.73,2.59),'p-Coumaric acid':(6.35,.68),'Ferulic Acid':(7.34,.74),'Resveratrol':(3.09,.22),'Quercetin':(4.44,.47),'Cinnamic acid':(.07,.01),'Kaempferol':(.41,.07)})]
raw={'Catechin':(147.52,15.02),'Caffeic acid':(46.87,3.31),'Syringic acid':(66.84,2.16),'Rutin':(148.72,13.62),'p-Coumaric acid':(12.35,.25),'Ferulic Acid':(19.85,.35),'Resveratrol':(1.27,.01),'Quercetin':(6.95,.17),'Cinnamic acid':(.79,.02),'Kaempferol':(3.86,.05)}
rows=[]
for method,norm,temp,mins,medium,cells in conditions:
  for compound,(cooked,cooked_sd) in cells.items():
    raw_value,raw_sd=raw[compound]; src=template(compound); safe=compound.upper().replace(' ','_').replace('-','_')
    row={c:src[c] for c in base.columns}; row.update({'observation_id':f'LIT-ALJUHAIMI2024-CAULIFLOWER-{safe}-{norm.upper().replace(" ","_")}', 'original_record_id':'','doi':'10.3390/pr12102114','paper_id':'NEW_LITERATURE_ALJUHAIMI_2024','source_locator':'Table 2; Methods §§2.1–2.2.8','compound':compound,'food_matrix':'Cauliflower florets (Brassica oleracea var. botrytis)','cooking_method':method,'cooking_method_normalized':norm,'cooking_medium':medium,'raw_concentration':raw_value,'raw_sd':raw_sd,'cooked_concentration':cooked,'cooked_sd':cooked_sd,'concentration_unit':'mg/100 g dry weight','measurement_basis':'dry weight (DW)','target_name':'apparent_concentration_ratio_percent','target_equation':'100 * C_cooked / C_raw','target_value_percent':100*cooked/raw_value,'target_semantics':'apparent concentration ratio; not total-mass retention','evidence_status':'VERIFIED_PRIMARY_TABLE','cooked_yield_status':'NOT_REPORTED','total_mass_retention_status':'NOT_ESTABLISHED','source_detail':'AlJuhaimi et al. (2024), Table 2: individual HPLC-PDA analyte, mean ± SD, dry-weight basis. Identity was based on standards, retention time and spectral comparison; one independent experiment mean per condition is recorded.','Temperature_C':temp,'Cooking_Time_min':mins,'reported_replicate_design':'Three independent experiments, each analytically triplicated; Table 2 reports mean ± SD. No technical replicates expanded.','analytical_definition':'Individual HPLC-PDA phenolic compound; 80:20 methanol:water extraction'})
    rows.append(row)
new=pd.DataFrame(rows,columns=base.columns); master=pd.concat([base,new],ignore_index=True)
assert len(new)==40 and len(master)==707 and master.doi.nunique()==23
assert new.canonical_molecular_id.notna().all() and not master.observation_id.duplicated().any()
assert (new.target_value_percent.round(8)==(100*new.cooked_concentration/new.raw_concentration).round(8)).all()
master.to_csv(R/'updated_master_dataset.csv',index=False); new.to_csv(R/'verified_observations.csv',index=False); new.to_csv(R/'extracted_observations.csv',index=False)
pd.DataFrame([{'doi':'10.3390/pr12102114','title':'The Effects of Different Cooking Systems on Changes in the Bioactive Compounds, Polyphenol Profiles, Biogenic Elements, and Protein Contents of Cauliflower Florets','year':2024,'admitted_rows':40,'status':'VERIFIED_PARTIAL','basis':'mg/100 g dry weight','reason':'Table 2 supplies direct raw/cooked individual HPLC-PDA data for 10 exactly mapped compounds across four specified methods.'}]).to_csv(R/'literature_candidate_registry.csv',index=False)
pd.DataFrame([{'category':'EXCLUDED_TABLE_VALUES','doi':'10.3390/pr12102114','reason':'Gallic acid and 3,4-dihydroxybenzoic acid lack exact established descriptor identities in the current master and are not inferred. Total phenolics, total flavonoids, antioxidant and mineral endpoints are not individual molecular measurements.'}]).to_csv(R/'excluded_candidates.csv',index=False)
prior=pd.read_csv(R.parent/'batch_009'/'source_verification_ledger.csv'); extra=pd.DataFrame([{'doi':'10.3390/pr12102114','paper_title':'The Effects of Different Cooking Systems on Changes in the Bioactive Compounds, Polyphenol Profiles, Biogenic Elements, and Protein Contents of Cauliflower Florets','source_url':'https://www.mdpi.com/2227-9717/12/10/2114','locator':'Table 2; Methods §§2.1–2.2.8','rows_admitted':40,'compound':'Catechin; caffeic, syringic, p-coumaric, ferulic and cinnamic acids; rutin; resveratrol; quercetin; kaempferol','basis':'mg/100 g dry weight','analytical_method':'Individual HPLC-PDA','admission_status':'VERIFIED_PARTIAL','rationale':'Direct raw/cooked means ± SD, explicit cooking protocols and individual standard-supported identities; technical replicates not expanded.'}]); pd.concat([prior,extra],ignore_index=True,sort=False).to_csv(R/'source_verification_ledger.csv',index=False)
master.groupby('doi').agg(observations=('observation_id','size'),compounds=('compound','nunique'),foods=('food_matrix','nunique'),methods=('cooking_method_normalized','nunique'),bases=('measurement_basis',lambda x:'; '.join(sorted(x.dropna().unique())))).reset_index().to_csv(R/'source_coverage_analysis.csv',index=False)
write('dataset_expansion_report.md',f'''# Scientific dataset expansion — controlled batch 010

The controlled master becomes **{len(master)} verified observations from {master.doi.nunique()} DOI families**. Batch 010 adds 40 primary-table apparent-concentration pairs from AlJuhaimi et al. (2024), DOI `10.3390/pr12102114`, preserving all 667 parent rows.

Table 2 reports individual HPLC-PDA values as mean ± SD in mg/100 g dry weight for fresh cauliflower florets and pressure-cooked, conventionally boiled, oven-heated and microwave-heated conditions. All ten admitted compound identities already have verified master descriptors. The source's gallic and 3,4-dihydroxybenzoic acids are excluded because exact established descriptor identities are absent, and all aggregate assays remain excluded. The three independent experiment means remain one row per condition; analytical replicates are never expanded. No model is retrained; 293 observations remain to the 1,000 target.
''')
write('reproduction_instructions.md','''# Reproduction
Run `python build_batch_010.py`, then `python validate_batch_010.py`. It reads only Batch 009 and writes only this package; no historical package, Git, or Stage B/C/D file is changed.
''')
m={'package':'StageA_DatasetExpansion1000_Batch010_2026-11-10','parent_rows':667,'parent_sha256':sha(PARENT),'new_rows':40,'total_rows':len(master),'new_doi_families':1,'strict_cross_source_replications_created':0,'target_1000_reached':False,'stage_c_integration_authorized':False}; (R/'manifest.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8'); (R/'SHA256SUMS.txt').write_text('\n'.join(f'{sha(p)}  {p.name}' for p in sorted(R.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt')+'\n',encoding='utf-8'); print(json.dumps(m,indent=2))
