"""Build v0.3 verified apparent-concentration-ratio dataset from primary-table families."""
from __future__ import annotations
import csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
MASTER=ROOT/'data/reviewed/cookchem_molecular_retention_master.csv'; PAIRS=ROOT/'stageC/phase2/data/observed_cooking_pairs.csv'
APPROVED={
 '10.3390/foods12163086':('Zagórska et al. (2023), Table 1','Primary Phase 2 pair audit; mg/g plant material.'),
 '10.3390/molecules31162740':('Stryjecka et al. (2026), Tables 2–3','Primary Phase 2 pair audit; dry-weight concentration.'),
 '10.1016/j.fochx.2022.100339':('Fang et al. (2022), Table 2','Potato phenolic acids, mg/100 g DW.'),
 '10.3390/molecules26175171':('Wu et al. (2021), Table 3','Red-cabbage glucosinolates, µmol/g DW.'),
 '10.3390/plants13101283':('AlJuhaimi et al. (2024), Table 2','Broccoli phenolic compounds, mg/100 g.'),
 '10.3390/foods10050960':("Fratianni et al. (2021), Table 1",'Leafy-vegetable lipophilic compounds, mg/100 g dry matter.'),
}
NUM=['Temperature_C','Cooking_Time_min','RDKit_Molecular_Weight','RDKit_LogP','RDKit_TPSA','RDKit_HBond_Donors','RDKit_HBond_Acceptors','RDKit_Rotatable_Bonds','RDKit_Aromatic_Rings','RDKit_Hydroxyl_Groups']
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(p,rows,fields):
 with p.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def method(x):return ' '.join(x.casefold().replace('-',' ').split())
def n(x):
 try:return float(x)
 except (ValueError,TypeError):return None
def main():
 phase={x['source_stagea_record_id']:x for x in read(PAIRS)}; rows=[]; excluded=[]; seen=set()
 for x in read(MASTER):
  doi=x['DOI'].strip().lower()
  if doi not in APPROVED:continue
  pair=phase.get(x['Record_ID'])
  raw=n(pair['raw_mean_value']) if pair else n(x['Initial_Concentration'])
  cooked=n(pair['cooked_mean_value']) if pair else n(x['Final_Concentration'])
  unit=pair['measurement_unit'] if pair else x['Initial_Unit']
  units_compatible=True if pair else x['Initial_Unit']==x['Final_Unit']
  if raw is None or cooked is None or raw<=0 or not units_compatible:
   excluded.append({'record_id':x['Record_ID'],'doi':doi,'reason':'Missing/nonpositive concentration or incompatible stored units'});continue
  k=(doi,x['Canonical_Molecular_ID'],x['Food_Name'],method(x['Cooking_Method']),x['Temperature_C'],x['Cooking_Time_min'],raw,cooked)
  if k in seen:
   excluded.append({'record_id':x['Record_ID'],'doi':doi,'reason':'Exact duplicate source observation'});continue
  seen.add(k); locator,detail=APPROVED[doi]
  target=n(pair['concentration_ratio_percent']) if pair else 100*cooked/raw
  row={'observation_id':'REC-'+x['Record_ID'],'original_record_id':x['Record_ID'],'doi':doi,'paper_id':x['Paper_ID'],'source_locator':pair['source_locator'] if pair else locator,'compound':x['Canonical_Compound_Name'],'canonical_molecular_id':x['Canonical_Molecular_ID'],'compound_class':x['Compound_Class_Standardized'],'food_matrix':x['Food_Name'],'cooking_method':x['Cooking_Method'],'cooking_method_normalized':method(x['Cooking_Method']),'cooking_medium':x['Cooking_Medium'],'raw_concentration':raw,'cooked_concentration':cooked,'concentration_unit':unit,'measurement_basis':unit,'target_name':'apparent_concentration_ratio_percent','target_equation':'100 * C_cooked / C_raw','target_value_percent':f'{target:.12g}','target_semantics':'apparent concentration ratio; not total-mass retention','evidence_status':'VERIFIED_PRIMARY_TABLE','cooked_yield_status':'NOT_REPORTED_OR_NOT_COMPATIBLE','total_mass_retention_status':'NOT_ESTABLISHED','source_detail':detail}
  for c in NUM:row[c]=x[c]
  rows.append(row)
 rows.sort(key=lambda x:x['observation_id']); fields=list(rows[0]); write(OUT/'expanded_clean_stageA_dataset.csv',rows,fields);write(OUT/'recovered_observations.csv',rows,fields);write(OUT/'new_literature_observations.csv',[],fields);write(OUT/'dataset_exclusion_log.csv',excluded,['record_id','doi','reason'])
 ledger=[{k:r[k] for k in ['observation_id','original_record_id','doi','paper_id','source_locator','compound','food_matrix','cooking_method','raw_concentration','cooked_concentration','concentration_unit','target_value_percent','evidence_status','source_detail']} for r in rows];write(OUT/'source_verification_ledger.csv',ledger,list(ledger[0]))
 counts={d:sum(r['doi']==d for r in rows) for d in APPROVED};manifest={'package':'StageA_Expansion_v0.3.0_2026-11-10','generated_at_utc':datetime.now(timezone.utc).isoformat(),'input_hashes':{str(MASTER.relative_to(ROOT)):sha(MASTER),str(PAIRS.relative_to(ROOT)):sha(PAIRS)},'target_contract':'apparent concentration ratio only','rows':len(rows),'source_counts':counts,'deployment_authorized':False};(OUT/'dataset_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
 (OUT/'target_definition_contract.md').write_text('# v0.3 target contract\n\n`apparent_concentration_ratio_percent = 100 * C_cooked / C_raw`, only where a primary paper table reports compatible raw and cooked concentration units/bases. It is not total-mass retention; cooking yield, moisture reconciliation, and liquid disposition are not sufficient for mass-retention calculations in this dataset.\n',encoding='utf-8')
 (OUT/'dataset_expansion_report.md').write_text('# Dataset expansion report\n\n'+f'- v0.2 verified rows: 117\n- v0.3 admitted rows: {len(rows)}\n- Recovered historical rows added: {len(rows)-117}\n- New literature rows: 0\n- Independent primary DOI families: {len(set(r["doi"] for r in rows))}\n- Compound groups: {len(set(r["canonical_molecular_id"] for r in rows))}\n- Food matrices: {len(set(r["food_matrix"] for r in rows))}\n- Cooking methods: {len(set(r["cooking_method_normalized"] for r in rows))}\n\nAll admissions are primary-table apparent concentration ratios. None is total-mass retention.\n\n## Family counts\n\n'+'\n'.join(f'- `{d}`: {c}' for d,c in counts.items()),encoding='utf-8')
if __name__=='__main__':main()
