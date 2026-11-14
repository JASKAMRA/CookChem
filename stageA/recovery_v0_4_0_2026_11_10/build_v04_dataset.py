"""Build v0.4: v0.3 plus independently sourced fresh-weight concentration pairs.

No temperature is inferred for the Heliyon study: it was not reported.
"""
from __future__ import annotations
import csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

OUT=Path(__file__).resolve().parent
V03=OUT.parent/'recovery_v0_3_0_2026_11_10'/'expanded_clean_stageA_dataset.csv'
NUM=['Temperature_C','Cooking_Time_min','RDKit_Molecular_Weight','RDKit_LogP','RDKit_TPSA','RDKit_HBond_Donors','RDKit_HBond_Acceptors','RDKit_Rotatable_Bonds','RDKit_Aromatic_Rings','RDKit_Hydroxyl_Groups']
DESCRIPTORS={
 'Beta-Carotene':('MOL-4211365770E800E7','Carotenoid',536.888,12.6058,0,0,0,10,0,0),
 'Vitamin C':('MOL-CF1446AA0DE93D24','Vitamin',176.124,-1.4074,107.22,4,6,2,0,4),
}
# Table 3 means; all values are mg/100 g fresh weight.  Treatment durations and
# water quantities are Table 1.  A blank temperature is deliberate evidence,
# not an imputed process setting.
VALUES={
 'Carrot':{'Beta-Carotene':(8.02,{'Boiling':7.41,'Steaming':7.2,'Microwave':7.56}),'Vitamin C':(5.9,{'Boiling':5.32,'Steaming':5.67,'Microwave':5.88})},
 'Pumpkin':{'Beta-Carotene':(2.27,{'Boiling':2.1,'Steaming':2.42,'Microwave':2.11}),'Vitamin C':(30.91,{'Boiling':16.97,'Steaming':25.87,'Microwave':29.45})},
 'Pea':{'Beta-Carotene':(3.08,{'Boiling':2.86,'Steaming':3.13,'Microwave':2.77}),'Vitamin C':(41.21,{'Boiling':27.98,'Steaming':35.64,'Microwave':38.6})},
 'Spinach':{'Beta-Carotene':(4.9,{'Boiling':3.32,'Steaming':5.33,'Microwave':3.17}),'Vitamin C':(76.54,{'Boiling':22.29,'Steaming':30.33,'Microwave':70.55})},
 'Sathkora':{'Beta-Carotene':(1.74,{'Boiling':1.28,'Steaming':1.87,'Microwave':1.68}),'Vitamin C':(60.26,{'Boiling':35.88,'Steaming':49.92,'Microwave':59.33})},
 'Green pepper':{'Beta-Carotene':(1.82,{'Boiling':1.12,'Steaming':1.93,'Microwave':1.09}),'Vitamin C':(87.75,{'Boiling':65.13,'Steaming':49.43,'Microwave':84.23})},
}
PROTOCOL={'Boiling':(6,'water; 150 mL per 100 g'),'Steaming':(8,'steam; water amount not reported'),'Microwave':(1,'microwave; 900 W, 6 mL water per 100 g')}
DOI='10.1016/j.heliyon.2023.e21709'

def read(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def write(p,rows,fields):
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rows=read(V03)
 for food,compounds in VALUES.items():
  for compound,(raw,cooked_by_method) in compounds.items():
   mid,clazz,*desc=DESCRIPTORS[compound]
   for cooking_method,cooked in cooked_by_method.items():
    time,medium=PROTOCOL[cooking_method]
    row={'observation_id':f'LIT-HELIYON2023-{food.upper().replace(" ","_")}-{compound.upper().replace(" ","_").replace("-","")}-{cooking_method.upper()}',
      'original_record_id':'','doi':DOI,'paper_id':'NEW_LITERATURE_HELIYON_2023','source_locator':'Table 3 (concentration means); Table 1 (treatment protocol)',
      'compound':compound,'canonical_molecular_id':mid,'compound_class':clazz,'food_matrix':food,'cooking_method':cooking_method,
      'cooking_method_normalized':cooking_method.casefold(),'cooking_medium':medium,'raw_concentration':raw,'cooked_concentration':cooked,
      'concentration_unit':'mg/100 g fresh weight','measurement_basis':'fresh weight (FW)','target_name':'apparent_concentration_ratio_percent',
      'target_equation':'100 * C_cooked / C_raw','target_value_percent':f'{100*cooked/raw:.12g}',
      'target_semantics':'apparent concentration ratio; not total-mass retention','evidence_status':'VERIFIED_PRIMARY_TABLE',
      'cooked_yield_status':'NOT_REPORTED','total_mass_retention_status':'NOT_ESTABLISHED',
      'source_detail':'Hossain et al. (2023), Heliyon Table 3; Table 1. Triplicate mean ± SD; FW stated in table caption.'}
    row['Temperature_C']='';row['Cooking_Time_min']=time
    for k,v in zip(NUM[2:],desc):row[k]=v
    rows.append(row)
 rows.sort(key=lambda r:r['observation_id']); fields=list(rows[0]); write(OUT/'expanded_clean_stageA_dataset.csv',rows,fields)
 write(OUT/'recovered_observations.csv',[r for r in rows if r['doi']!=DOI],fields);write(OUT/'new_literature_observations.csv',[r for r in rows if r['doi']==DOI],fields)
 ledger_fields=['observation_id','original_record_id','doi','paper_id','source_locator','compound','food_matrix','cooking_method','raw_concentration','cooked_concentration','concentration_unit','measurement_basis','target_value_percent','evidence_status','source_detail']
 write(OUT/'source_verification_ledger.csv',[{k:r[k] for k in ledger_fields} for r in rows],ledger_fields)
 counts={d:sum(r['doi']==d for r in rows) for d in sorted(set(r['doi'] for r in rows))}
 manifest={'package':'StageA_Expansion_v0.4.0_2026-11-10','generated_at_utc':datetime.now(timezone.utc).isoformat(),'parent_dataset':'stageA/recovery_v0_3_0_2026_11_10/expanded_clean_stageA_dataset.csv','parent_dataset_sha256':sha(V03),'rows':len(rows),'source_counts':counts,'target_contract':'apparent concentration ratio only','deployment_authorized':False}
 (OUT/'dataset_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
 (OUT/'target_definition_contract.md').write_text('# v0.4 target contract\n\n`apparent_concentration_ratio_percent = 100 * C_cooked / C_raw`, where a primary paper table reports matching raw and cooked concentration measurements with an explicit common basis. It is not total-mass retention: no cooked yield or full moisture/mass reconciliation is available.\n',encoding='utf-8')
 (OUT/'source_admission_report.md').write_text('# v0.4 source admission\n\n## Admitted independent source\n\nHossain et al. (2023), *Effect of cooking methods on the nutritional quality of selected vegetables at Sylhet City*, DOI `10.1016/j.heliyon.2023.e21709`, reports Table 3 means for beta-carotene and ascorbic acid in mg/100 g FW and states FW in the caption. Table 1 reports 100 g sample, boiling 6 min/150 mL water, steaming 8 min, and 900 W microwave 1 min/6 mL water. This adds 36 experiment-level apparent-ratio observations: 6 matrices × 2 compounds × 3 methods. Temperature is not reported and remains missing.\n\n## Excluded candidate\n\nOmbra et al. (2016), DOI `10.1155/2016/1398298`, was inspected at Table 4. Although raw/cooked pairs and a pressure-cooker protocol are reported, the table caption does not state a raw/cooked common dry- or fresh-weight basis, while rehydration/cooking alters mass. Its 26 historical ratios remain excluded rather than being silently treated as compatible concentration data.\n',encoding='utf-8')
 (OUT/'dataset_expansion_report.md').write_text('# Dataset expansion report\n\n'+f'- v0.3 parent rows: {len(rows)-36}\n- v0.4 admitted rows: {len(rows)}\n- New independently sourced rows: 36\n- DOI families: {len(counts)}\n- Compound groups: {len(set(r["canonical_molecular_id"] for r in rows))}\n- Food matrices: {len(set(r["food_matrix"] for r in rows))}\n\nAll rows are apparent concentration ratios only; none is total-mass retention.\n',encoding='utf-8')
if __name__=='__main__':main()
