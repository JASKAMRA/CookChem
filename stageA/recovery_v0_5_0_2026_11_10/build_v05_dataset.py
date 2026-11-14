"""Build v0.5 from immutable v0.4 plus an independently verified potato study."""
from __future__ import annotations
import csv,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parent;PARENT=R.parent/'recovery_v0_4_0_2026_11_10'/'expanded_clean_stageA_dataset.csv'
NUM=['Temperature_C','Cooking_Time_min','RDKit_Molecular_Weight','RDKit_LogP','RDKit_TPSA','RDKit_HBond_Donors','RDKit_HBond_Acceptors','RDKit_Rotatable_Bonds','RDKit_Aromatic_Rings','RDKit_Hydroxyl_Groups']
PROTOCOL=[('Boiling','',35,'water; 5:1 water:raw material'),('Steaming','',50,'steam; perforated insert'),('Combi steaming',103,40,'steam; convection-steam oven'),('Microwave','',7,'microwave; 750 W'),('Grilling',250,45,'dry electric grill')]
COOKED=[43.79,56.35,62.34,68.83,60.01]
def read(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def write(p,rows,fields):
 with p.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rows=read(PARENT);raw=76.42
 for i,((method,temp,time,medium),cooked) in enumerate(zip(PROTOCOL,COOKED),1):
  row={'observation_id':f'LIT-NARWOJSZ2020-POTATO-VITAMIN_C-{i:02d}','original_record_id':'','doi':'10.1007/s11130-020-00808-0','paper_id':'NEW_LITERATURE_NARWOJSZ_2020','source_locator':'Table 2 (Vitamin C); Materials and Methods (thermal treatments)','compound':'Vitamin C','canonical_molecular_id':'MOL-CF1446AA0DE93D24','compound_class':'Vitamin','food_matrix':'Potato (Lord cultivar)','cooking_method':method,'cooking_method_normalized':method.casefold(),'cooking_medium':medium,'raw_concentration':raw,'cooked_concentration':cooked,'concentration_unit':'mg/100 g dry weight','measurement_basis':'dry weight (DW)','target_name':'apparent_concentration_ratio_percent','target_equation':'100 * C_cooked / C_raw','target_value_percent':f'{100*cooked/raw:.12g}','target_semantics':'apparent concentration ratio; not total-mass retention','evidence_status':'VERIFIED_PRIMARY_TABLE','cooked_yield_status':'NOT_REPORTED','total_mass_retention_status':'NOT_ESTABLISHED','source_detail':'Narwojsz et al. (2020), Table 2; HPLC vitamin C, mg/100 g DW. Raw and five thermal treatments.'}
  row['Temperature_C']=temp;row['Cooking_Time_min']=time
  for k,v in zip(NUM[2:],[176.124,-1.4074,107.22,4,6,2,0,4]):row[k]=v
  rows.append(row)
 rows.sort(key=lambda r:r['observation_id']);fields=list(rows[0]);write(R/'expanded_clean_stageA_dataset.csv',rows,fields);write(R/'recovered_observations.csv',[x for x in rows if x['doi']!='10.1007/s11130-020-00808-0'],fields);write(R/'new_literature_observations.csv',[x for x in rows if x['doi']=='10.1007/s11130-020-00808-0'],fields)
 lf=['observation_id','original_record_id','doi','paper_id','source_locator','compound','food_matrix','cooking_method','raw_concentration','cooked_concentration','concentration_unit','measurement_basis','target_value_percent','evidence_status','source_detail'];write(R/'source_verification_ledger.csv',[{k:x[k] for k in lf} for x in rows],lf)
 excluded=[{'doi':'10.1007/s10068-017-0281-1','status':'PENDING_PRIMARY_RETRIEVAL','reason':'Publisher page confirms publication but full primary table/method access has not been obtained; search snippets are not evidence.'},{'doi':'10.3389/fnut.2020.580550','status':'EXCLUDED_BASIS_AMBIGUOUS','reason':'Tables 1A/B state mg/kg but do not state whether this is fresh or dry basis, while analyses use freeze-dried samples.'}];write(R/'dataset_exclusion_log.csv',excluded,list(excluded[0]))
 counts={d:sum(x['doi']==d for x in rows) for d in sorted({x['doi'] for x in rows})};m={'package':'StageA_Expansion_v0.5.0_2026-11-10','parent_dataset':'stageA/recovery_v0_4_0_2026_11_10/expanded_clean_stageA_dataset.csv','parent_sha256':sha(PARENT),'rows':len(rows),'source_counts':counts,'target_contract':'apparent concentration ratio only','generated_at_utc':datetime.now(timezone.utc).isoformat(),'deployment_authorized':False};(R/'dataset_manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 (R/'source_admission_report.md').write_text('# v0.5 source admission\n\n## Admitted\n\nNarwojsz et al. (2020), DOI `10.1007/s11130-020-00808-0`, Table 2 reports HPLC vitamin C in compatible mg/100 g DW for raw Lord-cultivar potato and five treatments. Methods state: boiling 35 min (5:1 water:raw), steaming 50 min, 103 °C combi steaming 40 min, 750 W microwave 7 min, and 250 °C grilling 45 min. Five apparent-ratio rows are admitted; missing temperatures are deliberately blank.\n\n## Excluded/pending\n\nThe Frontiers phenolic study (DOI `10.3389/fnut.2020.580550`) gives mg/kg but does not state fresh/dry basis in the table; it is excluded. Lee et al. (DOI `10.1007/s10068-017-0281-1`) remains pending primary-table retrieval.\n')
 (R/'primary_source_bibliography.md').write_text('# Primary-source bibliography\n\n- Narwojsz A, Borowska EJ, Polak-Sliwinska M, Danowska-Oziewicz M. 2020. *Effect of Different Methods of Thermal Treatment on Starch and Bioactive Compounds of Potato*. Plant Foods for Human Nutrition 75:298-304. DOI: `10.1007/s11130-020-00808-0`.\n- Hossain et al. 2023. *Effect of cooking methods on the nutritional quality of selected vegetables at Sylhet City*. Heliyon. DOI: `10.1016/j.heliyon.2023.e21709`. Retained from v0.4 parent.\n',encoding='utf-8')
 (R/'target_definition_contract.md').write_text('# v0.5 target contract\n\n`100 * C_cooked / C_raw` from compatible raw/cooked concentration pairs with the same reported basis. It is an apparent concentration ratio only; it is not total-mass retention.\n')
if __name__=='__main__':main()
