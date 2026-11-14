"""Controlled expansion batch 009: Croatian garlic HPLC primary table."""
from pathlib import Path
import hashlib, json
import pandas as pd

R = Path(__file__).resolve().parent
PARENT = R.parent / 'batch_008' / 'updated_master_dataset.csv'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name, text): (R / name).write_text(text.strip() + '\n', encoding='utf-8')

base = pd.read_csv(PARENT)
def template(compound):
    found = base.loc[base.compound.astype(str).str.casefold().eq(compound.casefold())]
    assert len(found), compound
    return found.iloc[0]

# Pedišić et al. Table 1: all values are mean +/- SD mg/100 g fresh mass.
# Only exactly identity-mapped individual compounds already supported by the
# master are retained. The paper's gallic and p-hydroxybenzoic acids are not
# mapped by inference into this existing descriptor schema.
data = {
 'Protocatechuic Acid': (5.30, 0.02, {'Blanching': [(2,4.03,.04),(5,3.68,.01),(8,3.41,.01),(10,3.39,.03)], 'Frying': [(2,3.10,.03),(5,2.61,.01),(8,2.09,.02),(10,1.20,.01)]}),
 'Caffeic acid': (9.50, 0.04, {'Blanching': [(2,6.72,.04),(5,6.36,.02),(8,5.93,.04),(10,5.50,.03)], 'Frying': [(2,6.18,.03),(5,4.73,.02),(8,4.30,.01),(10,4.08,.03)]}),
 'p-Coumaric acid': (10.79, 0.03, {'Blanching': [(2,7.70,.04),(5,7.23,.03),(8,6.87,.01),(10,6.27,.02)], 'Frying': [(2,7.03,.02),(5,5.40,.03),(8,4.91,.02),(10,4.65,.02)]}),
 'Ferulic Acid': (2.06, 0.09, {'Blanching': [(2,1.53,.01),(5,1.60,.03),(8,1.59,.02),(10,1.55,.04)], 'Frying': [(2,1.70,.02),(5,1.67,.01),(8,1.67,.01),(10,1.22,.00)]}),
}

rows=[]
for compound,(raw,raw_sd,processes) in data.items():
    for process,cells in processes.items():
        method = 'Water blanching' if process == 'Blanching' else 'Dry frying'
        normalized = 'blanching' if process == 'Blanching' else 'frying'
        temperature = 100 if process == 'Blanching' else 120
        medium = 'water bath' if process == 'Blanching' else 'without fat, covered double fry pan'
        for mins,cooked,cooked_sd in cells:
            src=template(compound); safe=compound.upper().replace(' ','_').replace('-','_')
            row={c:src[c] for c in base.columns}
            row.update({'observation_id':f'LIT-PEDISIC2018-GARLIC-{safe}-{normalized.upper()}-{mins}MIN',
                'original_record_id':'','doi':'10.17113/ftb.56.04.18.5709','paper_id':'NEW_LITERATURE_PEDISIC_2018',
                'source_locator':'Table 1; Methods Sample preparation and processing; HPLC analysis of polyphenolic compounds',
                'compound':compound,'food_matrix':'Croatian domestic garlic cloves (Allium sativum L.)',
                'cooking_method':method,'cooking_method_normalized':normalized,'cooking_medium':medium,
                'raw_concentration':raw,'raw_sd':raw_sd,'cooked_concentration':cooked,'cooked_sd':cooked_sd,
                'concentration_unit':'mg/100 g fresh mass','measurement_basis':'fresh mass (FM)',
                'target_name':'apparent_concentration_ratio_percent','target_equation':'100 * C_cooked / C_raw',
                'target_value_percent':100*cooked/raw,'target_semantics':'apparent concentration ratio; not total-mass retention',
                'evidence_status':'VERIFIED_PRIMARY_TABLE','cooked_yield_status':'NOT_REPORTED','total_mass_retention_status':'NOT_ESTABLISHED',
                'source_detail':'Pedišić et al. (2018), Table 1: individual HPLC-UV/Vis-PDA phenolic acids, mean ± SD on fresh-mass basis. Raw is the immediately analysed crushed fresh control; cooked samples are uncrushed garlic blanched at 100 °C or fried without fat at 120 °C.',
                'Temperature_C':temperature,'Cooking_Time_min':mins,
                'reported_replicate_design':'Treatments done in two runs using 100 g garlic; paper reports measurements in triplicate and Table 1 mean ± SD. One condition mean per row; technical measurements are not expanded.',
                'analytical_definition':'Individual HPLC-UV/Vis-PDA phenolic acid; fresh-mass concentration'})
            rows.append(row)

new=pd.DataFrame(rows,columns=base.columns)
master=pd.concat([base,new],ignore_index=True)
assert len(new)==32 and len(master)==667 and master.doi.nunique()==22
assert new.canonical_molecular_id.notna().all() and not master.observation_id.duplicated().any()
assert (new.target_value_percent.round(8)==(100*new.cooked_concentration/new.raw_concentration).round(8)).all()
master.to_csv(R/'updated_master_dataset.csv',index=False)
new.to_csv(R/'verified_observations.csv',index=False)
new.to_csv(R/'extracted_observations.csv',index=False)

pd.DataFrame([{'doi':'10.17113/ftb.56.04.18.5709','title':'Retention of Bioactive Compounds During Domestic Processing of Croatian Domestic Garlic (Allium sativum L.)','year':2018,'admitted_rows':32,'status':'VERIFIED_PARTIAL','basis':'mg/100 g fresh mass','reason':'Table 1 gives traceable raw/cooked individual HPLC-UV/Vis-PDA values. Blanching and frying rows are admitted; non-cooking crushed samples and unmapped identities are excluded.'}]).to_csv(R/'literature_candidate_registry.csv',index=False)
pd.DataFrame([{'category':'EXCLUDED_TABLE_VALUES','doi':'10.17113/ftb.56.04.18.5709','reason':'Crushed-at-room-temperature rows are not cooking treatments. Gallic acid and p-hydroxybenzoic acid lack exact established descriptor identities in the current master and are not inferred; total phenolics, trace quercetin, organosulfur analytes and aggregate assays are also excluded.'},{'category':'EXCLUDED_CANDIDATE','doi':'10.1016/j.foodchem.2019.01.148','reason':'Open-access record located, but primary numerical full text/supplement could not be retrieved through an auditable route in this batch; no search-snippet values admitted.'}]).to_csv(R/'excluded_candidates.csv',index=False)
prior=pd.read_csv(R.parent/'batch_008'/'source_verification_ledger.csv')
extra=pd.DataFrame([{'doi':'10.17113/ftb.56.04.18.5709','paper_title':'Retention of Bioactive Compounds During Domestic Processing of Croatian Domestic Garlic (Allium sativum L.)','source_url':'https://hrcak.srce.hr/file/314303','locator':'Table 1; Methods Sample preparation and processing; HPLC analysis of polyphenolic compounds','rows_admitted':32,'compound':'Protocatechuic, caffeic, p-coumaric and ferulic acids','basis':'mg/100 g fresh mass','analytical_method':'Individual HPLC-UV/Vis-PDA','admission_status':'VERIFIED_PARTIAL','rationale':'Direct raw/control and timed blanching/frying values with explicitly stated fresh-mass basis; mean conditions only, no technical-replicate expansion.'}])
pd.concat([prior,extra],ignore_index=True,sort=False).to_csv(R/'source_verification_ledger.csv',index=False)
master.groupby('doi').agg(observations=('observation_id','size'),compounds=('compound','nunique'),foods=('food_matrix','nunique'),methods=('cooking_method_normalized','nunique'),bases=('measurement_basis',lambda x:'; '.join(sorted(x.dropna().unique())))).reset_index().to_csv(R/'source_coverage_analysis.csv',index=False)
write('dataset_expansion_report.md',f'''# Scientific dataset expansion — controlled batch 009

The controlled master becomes **{len(master)} verified observations from {master.doi.nunique()} DOI families**. Batch 009 adds 32 primary-table apparent-concentration pairs from Pedišić et al. (2018), DOI `10.17113/ftb.56.04.18.5709`, while preserving all 635 parent rows.

Table 1 directly reports four identity-mapped individual phenolic acids as mean ± SD in mg/100 g fresh mass. The 32 admitted pairs are raw versus water-blanched (100 °C) or dry-fried (120 °C) garlic at 2, 5, 8 and 10 min. The paper's gallic and p-hydroxybenzoic acids do not have exact established descriptor identities in the current master and are not inferred. Non-cooking crushed samples, total endpoints, trace-only quercetin, organosulfur compounds and all aggregate assays are excluded. One reported condition mean remains one row; technical measurements are never expanded. No model is retrained; 333 observations remain to the 1,000 target.
''')
write('reproduction_instructions.md','''# Reproduction
Run `python build_batch_009.py`, then `python validate_batch_009.py`. It reads only Batch 008 and writes only this package; no historical package, Git, or Stage B/C/D file is changed.
''')
m={'package':'StageA_DatasetExpansion1000_Batch009_2026-11-10','parent_rows':635,'parent_sha256':sha(PARENT),'new_rows':32,'total_rows':len(master),'new_doi_families':1,'strict_cross_source_replications_created':0,'target_1000_reached':False,'stage_c_integration_authorized':False}
(R/'manifest.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
(R/'SHA256SUMS.txt').write_text('\n'.join(f'{sha(p)}  {p.name}' for p in sorted(R.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt')+'\n',encoding='utf-8')
print(json.dumps(m,indent=2))
