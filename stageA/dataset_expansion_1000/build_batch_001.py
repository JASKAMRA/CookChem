"""Controlled expansion batch 001: one primary-table admission, no inferred values."""
from pathlib import Path
import hashlib, json, shutil
import pandas as pd

R=Path(__file__).resolve().parent; P=R.parent/'recovery_v1_0_0_2026_11_10'; DATA=P/'expanded_clean_stageA_dataset.csv'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def md(name,text): (R/name).write_text(text.strip()+'\n',encoding='utf-8')
R.mkdir(exist_ok=True); base=pd.read_csv(DATA)
# The HPLC/PDA Table 2 values are condition means ± SD of triplicate experiments.
# Each raw/cooked treatment pair is one observation; triplicates are explicitly not expanded.
value={
 'Oven cooking':[(170,11.64,.25),(180,12.32,.40),(190,11.93,.19),(200,11.70,.60)],
 'Air frying':[(170,12.95,.09),(180,13.67,.14),(190,13.45,.28),(200,13.22,.17)],
 'Infrared grilling':[(170,11.54,.18),(180,12.53,.23),(190,12.60,.16),(200,12.43,.21)],
}
v=base[base.compound.eq('Vitamin C')].iloc[0]
rows=[]
for method,vals in value.items():
 for temp,cooked,csd in vals:
  x={c:v[c] for c in base.columns}
  x.update({'observation_id':f'LIT-ZHAO2024-RED_BELL_PEPPER-VITAMIN_C-{method.upper().replace(" ","_")}-{temp}C','original_record_id':'','doi':'10.1007/s10068-024-01623-y','paper_id':'NEW_LITERATURE_ZHAO_2024','source_locator':'Table 2 (ascorbic acid); Materials and methods, pp. 2325–2327','compound':'Vitamin C','canonical_molecular_id':v.canonical_molecular_id,'compound_class':'Vitamin','food_matrix':'Red bell pepper','cooking_method':method,'cooking_method_normalized':method.casefold(),'cooking_medium':'dry hot-air treatment; pepper pieces, no added water reported','raw_concentration':19.38,'cooked_concentration':cooked,'concentration_unit':'mg/g dry weight','measurement_basis':'dry weight (DW)','target_name':'apparent_concentration_ratio_percent','target_equation':'100 * C_cooked / C_raw','target_value_percent':100*cooked/19.38,'target_semantics':'apparent concentration ratio; not total-mass retention','evidence_status':'VERIFIED_PRIMARY_TABLE','cooked_yield_status':'NOT_REPORTED','total_mass_retention_status':'NOT_ESTABLISHED','source_detail':'Zhao et al. (2024), Table 2. HPLC-PDA (254 nm); values are mean ± SD of triplicate experiments. Red bell peppers freeze-dried after cooking before dry-weight analysis.','Temperature_C':temp,'Cooking_Time_min':15})
  rows.append(x)
new=pd.DataFrame(rows)
new['raw_sd']=1.48;new['cooked_sd']=[z[2] for vals in value.values() for z in vals];new['reported_replicate_design']='triplicate condition mean ± SD; one dataset row per cooking condition'
base['raw_sd']=pd.NA;base['cooked_sd']=pd.NA;base['reported_replicate_design']=pd.NA
master=pd.concat([base,new],ignore_index=True)
assert len(new)==12 and len(master)==451 and master.doi.nunique()==11
assert (new.target_value_percent.round(10)==(100*new.cooked_concentration/new.raw_concentration).round(10)).all()
master.to_csv(R/'updated_master_dataset.csv',index=False);new.to_csv(R/'extracted_observations.csv',index=False);new.to_csv(R/'verified_observations.csv',index=False)

registry=pd.DataFrame([
 {'doi':'10.1007/s10068-024-01623-y','title':'Effects of cooking methods on antioxidant activity and acrylamide formation in red bell pepper','year':2024,'compound':'Ascorbic acid (Vitamin C)','food_matrix':'Red bell pepper','cooking_method':'oven cooking; air frying; infrared grilling','measurement_technique':'HPLC-PDA, 254 nm','measurement_basis':'mg/g dry weight','raw_values':'Table 2: 19.38 ± 1.48','cooked_values':'12 tabled condition means ± SD','extractable_observations':12,'verification_status':'VERIFIED','rejection_reason':''},
 {'doi':'10.3390/molecules26175171','title':'Analysis of Processing Effects on Glucosinolate Profiles in Red Cabbage','year':2021,'compound':'individual glucosinolates','food_matrix':'Red cabbage','cooking_method':'boiling; steaming; microwave; frying; stir-frying','measurement_technique':'LC-MS/MS','measurement_basis':'see existing admitted record','raw_values':'primary table','cooked_values':'primary table','extractable_observations':'already represented','verification_status':'DUPLICATE','rejection_reason':'DOI already represented in the 439-row parent; no duplicate extraction.'},
 {'doi':'10.1016/j.fochx.2022.100339','title':'Cooking methods affected phytochemicals and antioxidant activities of potato','year':2022,'compound':'phenolic acids','food_matrix':'Potato','cooking_method':'multiple','measurement_technique':'primary table','measurement_basis':'dry weight','raw_values':'primary table','cooked_values':'primary table','extractable_observations':'already represented','verification_status':'DUPLICATE','rejection_reason':'DOI already represented in the 439-row parent; no duplicate extraction.'},
 {'doi':'10.1002/fsn3.1805','title':'Effects of cooking methods on total isothiocyanate yield from cruciferous vegetables','year':2020,'compound':'total isothiocyanate yield','food_matrix':'broccoli/cabbage/cauliflower/kale','cooking_method':'multiple','measurement_technique':'HPLC cyclocondensation','measurement_basis':'wet weight','raw_values':'Table 3','cooked_values':'Table 3','extractable_observations':23,'verification_status':'TARGET_UNRESOLVED','rejection_reason':'Total isothiocyanate yield is an assay-defined aggregate, not one verified canonical molecular entity compatible with the descriptor schema.'},
 {'doi':'10.1108/NFS-12-2012-0126','title':'Vitamin retention in vegetables submitted to heat treatment','year':2013,'compound':'Ascorbic acid','food_matrix':'Carrot','cooking_method':'boiling; steaming; microwaving','measurement_technique':'HPLC-UV','measurement_basis':'wet basis','raw_values':'Table I','cooked_values':'Table I','extractable_observations':3,'verification_status':'BASIS_UNCLEAR','rejection_reason':'Wet basis is not silently relabelled fresh weight under the project contract; already logged in v1 candidate audit.'}
])
registry.to_csv(R/'literature_candidate_registry.csv',index=False)
registry[registry.verification_status.ne('VERIFIED')].to_csv(R/'excluded_candidates.csv',index=False)
ledger=pd.read_csv(P/'source_verification_ledger.csv')
extra=pd.DataFrame([{'doi':'10.1007/s10068-024-01623-y','paper_title':'Effects of cooking methods on antioxidant activity and acrylamide formation in red bell pepper (Capsicum annuum L.)','source_url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC11319575/','locator':'Table 2; Materials and methods pp. 2325–2327','rows_admitted':12,'compound':'Vitamin C','basis':'mg/g dry weight','analytical_method':'HPLC-PDA, 254 nm','admission_status':'VERIFIED','rationale':'Raw and cooked means, explicit DW basis, conditions and HPLC method are directly traceable.'}])
pd.concat([ledger,extra],ignore_index=True,sort=False).to_csv(R/'source_verification_ledger.csv',index=False)
coverage=master.groupby('doi').agg(observations=('observation_id','size'),compounds=('compound','nunique'),foods=('food_matrix','nunique'),methods=('cooking_method_normalized','nunique'),bases=('measurement_basis',lambda x:'; '.join(sorted(x.dropna().unique())))).reset_index();coverage.to_csv(R/'source_coverage_analysis.csv',index=False)
md('schema_migration.md','''# Schema migration

`updated_master_dataset.csv` preserves every parent column and appends `raw_sd`, `cooked_sd`, and `reported_replicate_design`. Parent rows are null in these extensions because their original source tables did not uniformly provide a retained SD field. The 12 Zhao rows preserve reported condition-level SDs; they are not expanded into artificial replicates.
''')
md('dataset_expansion_report.md',f'''# Scientific dataset expansion — controlled batch 001

## Result

The target of 1,000–1,200 is **not reached in this batch**. The defensible master dataset is **{len(master)} observations** from **{master.doi.nunique()} DOI families**: 12 verified additions from one independent primary paper. The 439-row v1 parent is preserved verbatim.

## Admission

Zhao et al. (2024), DOI `10.1007/s10068-024-01623-y`, Table 2, provides raw and cooked HPLC-PDA ascorbic-acid concentrations in `mg/g dry weight` for red bell pepper. There are three methods × four temperatures, each 15 minutes: 12 condition means. The raw value is 19.38 ± 1.48 mg/g DW; cooked means and SDs are retained in `verified_observations.csv`. These are apparent concentration ratios only and not total-mass retention.

## Deliberate exclusions

Already-admitted DOI families were not duplicated. Total-isothiocyanate yield was excluded because it is an aggregate assay outcome without a single canonical molecular identity for descriptor-dependent modelling. Wet-basis carrot data remain separate rather than being silently relabelled FW.

## Evidence effect

The batch adds one food matrix, three method labels, one independent DOI family, and a new dry-weight Vitamin-C protocol cluster. It creates **zero strict cross-source protocol-identical replications**. It increases source diversity, but does not yet justify rerunning the frozen final prototype or claiming improved source generalisation.
''')
md('reproduction_instructions.md','''# Reproduction

Run `python build_batch_001.py`. The script reads only the frozen v1 parent dataset, creates a new master copy, and uses explicitly transcribed Table 2 values documented in the candidate registry. It makes no remote, Git, or historical-package change.
''')
manifest={'package':'StageA_DatasetExpansion1000_Batch001_2026-11-10','parent_rows':439,'parent_sha256':sha(DATA),'new_rows':12,'total_rows':len(master),'new_doi_families':1,'strict_cross_source_replications_created':0,'target_1000_reached':False,'stage_c_integration_authorized':False}
(R/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
(R/'SHA256SUMS.txt').write_text('\n'.join(f'{sha(p)}  {p.name}' for p in sorted(R.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt')+'\n',encoding='utf-8')
print(json.dumps(manifest,indent=2))
