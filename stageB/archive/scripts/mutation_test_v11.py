"""Isolated adversarial mutations for V11's core data-integrity rules."""
import csv, copy, json, tempfile, re, hashlib, shutil
from pathlib import Path

P=Path(__file__).resolve().parent
O=P/'outputs'; A=P/'audit'
V10=P.parent/'release_v10_20261030'
V11=P
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(p,rows):
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
base={'compound':read(O/'compound_registry_v11.csv'),'evidence':read(O/'stageB_food_drug_interactions_v11.csv'),'drug':read(O/'drug_probe_registry_v11.csv'),'study':read(O/'study_registry_v11.csv'),'claim':read(O/'claim_support_and_verification_v11.csv'),'selection':read(O/'selection_decisions_v11.csv'),'warning':read(O/'warning_resolution_ledger_v11.csv'),'cooking':read(O/'cooking_retention_evidence_v9.csv')}

def validate(x, root):
 out=set(); c,e,d,s,cl,sel,w=x['compound'],x['evidence'],x['drug'],x['study'],x['claim'],x['selection'],x['warning']
 if len({z['Compound_ID'] for z in c})<len(c):out.add('duplicate_compound_id')
 if len({z['Evidence_ID'] for z in e})<len(e):out.add('duplicate_evidence_id')
 if any(z['Compound_ID'] not in {a['Compound_ID'] for a in c} for z in e):out.add('orphan_compound')
 if any(z['Drug'] not in {a['Drug_Probe'] for a in d} for z in e):out.add('orphan_drug')
 if any(z['Study_ID'] not in {a['Study_ID'] for a in s} for z in e):out.add('orphan_study')
 if any(not z['PMID'] and not z['DOI'] for z in e):out.add('missing_publication')
 if any(z['DOI'] and not re.fullmatch(r'10\.\d{4,9}/\S+',z['DOI'],re.I) for z in e):out.add('invalid_doi')
 if any(z['InChIKey'] and not re.fullmatch(r'[A-Z]{14}-[A-Z]{10}-[A-Z]',z['InChIKey']) for z in c):out.add('bad_inchikey')
 if len({z['InChIKey'] for z in c if z['InChIKey']})<sum(bool(z['InChIKey']) for z in c):out.add('duplicate_structure')
 if any(('IC50' in z['Quantitative_Outcome'] or 'Ki =' in z['Quantitative_Outcome']) and not any(u in z['Quantitative_Outcome'] for u in ['μM','uM','nM','mM']) for z in e):out.add('missing_numeric_unit')
 if any('IC50 =' in z['Quantitative_Outcome'] and not re.search(r'IC50\s*=\s*\d+(?:\.\d+)?',z['Quantitative_Outcome']) for z in e):out.add('invalid_numeric')
 if any(('decreas' in z['Quantitative_Outcome'].lower() and 'increase' in z['Direction'].lower()) or ('increas' in z['Quantitative_Outcome'].lower() and 'decrease' in z['Direction'].lower()) for z in e):out.add('direction_conflict')
 if any((z['Evidence_Type']=='Human pharmacokinetic' and re.search(r'\b(?:in vitro|microsomes?|cell line|transfected cells?)\b',z['Study_Design']+' '+z['Population'],re.I)) or (z['Evidence_Type']=='In vitro' and re.search(r'\b(?:healthy volunteers|patients|randomized|crossover|cross-over|subjects received)\b',z['Study_Design']+' '+z['Population'],re.I)) for z in e):out.add('classification_conflict')
 if len({z['Evidence_ID'] for z in cl})!=len(e) or {z['Evidence_ID'] for z in cl}!={z['Evidence_ID'] for z in e}:out.add('claim_mapping')
 ctx=[(z['Compound_ID'],z['Drug'],z['Study_ID'],z['Outcome'],z['Preparation']) for z in e]
 if len(set(ctx))<len(ctx):out.add('duplicate_context')
 if any(not z['Interaction_Rationale'] or not z['Food_Context'] for z in sel):out.add('missing_selection')
 if any(z['After'] not in {'Resolved','Partially resolved','Unresolved','Not applicable'} for z in w):out.add('warning_status')
 if any('cook' in z.get('Evidence_Type','').lower() for z in e):out.add('cooking_contamination')
 if any(z['Evidence_Type'] in {'Human pharmacokinetic','Controlled clinical','Other human clinical'} and re.search(r'\b(?:in vitro|microsomes?|cell line|transfected cells?)\b',z['Study_Design']+' '+z['Population'],re.I) for z in e):out.add('clinical_class_conflict')
 old=read(V10/'outputs/stageB_food_drug_interactions_v10.csv'); by={z['Evidence_ID']:z for z in e}
 if any(by.get(z['Evidence_ID'])!=z for z in old):out.add('inherited_row_change')
 manifest=root/'V11_SHA256SUMS.json'
 if manifest.exists():
  m=json.loads(manifest.read_text(encoding='utf-8'));files={z['path'] for z in m['files']}
  if 'outputs/compound_registry_v11.csv' not in files:out.add('manifest_missing')
  oldm=json.loads((root/'v10'/'V10_SHA256SUMS.json').read_text(encoding='utf-8'))
  if any(not (root/'v10'/z['path']).exists() or hashlib.sha256((root/'v10'/z['path']).read_bytes()).hexdigest()!=z['sha256'] for z in oldm['files']):out.add('v10_manifest_hash')
 else:out.add('manifest_missing')
 if any(z['Source_Cache'] and not (root/'sources'/z['Source_Cache']).exists() for z in e):out.add('source_missing')
 return out

mutators={
 'duplicate_compound_id':lambda x:x['compound'][1].update(Compound_ID=x['compound'][0]['Compound_ID']),
 'duplicate_evidence_id':lambda x:x['evidence'][1].update(Evidence_ID=x['evidence'][0]['Evidence_ID']),
 'orphan_compound':lambda x:x['evidence'][0].update(Compound_ID='MISSING'),
 'orphan_drug':lambda x:x['evidence'][0].update(Drug='MISSING'),
 'orphan_study':lambda x:x['evidence'][0].update(Study_ID='MISSING'),
 'missing_publication':lambda x:x['evidence'][0].update(PMID='',DOI=''),
 'invalid_doi':lambda x:x['evidence'][0].update(DOI='doi:not-a-doi'),
 'bad_inchikey':lambda x:x['compound'][0].update(InChIKey='BAD-KEY'),
 'duplicate_structure':lambda x:x['compound'][1].update(InChIKey=x['compound'][0]['InChIKey']),
 'missing_numeric_unit':lambda x:x['evidence'][-1].update(Quantitative_Outcome='IC50 = 1.2'),
 'invalid_numeric':lambda x:x['evidence'][-1].update(Quantitative_Outcome='IC50 = not-a-number μM'),
 'direction_conflict':lambda x:x['evidence'][-1].update(Quantitative_Outcome='Increased activity',Direction='decrease'),
 'classification_conflict':lambda x:x['evidence'][0].update(Evidence_Type='In vitro',Study_Design='Human volunteers randomized'),
 'claim_mapping':lambda x:x['claim'].pop(),
 'duplicate_context':lambda x:x['evidence'].append(copy.deepcopy(x['evidence'][0])|{'Evidence_ID':'SB-9999'}),
 'missing_selection':lambda x:x['selection'][0].update(Interaction_Rationale=''),
 'warning_status':lambda x:x['warning'][0].update(After='Closed without evidence'),
 'cooking_contamination':lambda x:x['evidence'][0].update(Evidence_Type='Cooking retention'),
 'clinical_class_conflict':lambda x:x['evidence'][0].update(Evidence_Type='Human pharmacokinetic',Study_Design='In-vitro microsomes'),
 'inherited_row_change':lambda x:x['evidence'][0].update(Interaction_Effect='mutated inherited value'),
 'manifest_missing':lambda x:None,
 'v10_manifest_hash':lambda x:None,
 'source_missing':lambda x:x['evidence'][-1].update(Source_Cache='absent-cache.json'),
}
results=[]
with tempfile.TemporaryDirectory(prefix='cookrisk_v11_mut_') as td:
 for tid,mutate in mutators.items():
  t=Path(td)/tid;t.mkdir();x=copy.deepcopy(base);mutate(x)
  (t/'outputs').mkdir();(t/'sources').mkdir();(t/'v10').mkdir()
  if (V11/'V11_SHA256SUMS.json').exists(): shutil.copy2(V11/'V11_SHA256SUMS.json',t/'V11_SHA256SUMS.json')
  for sf in {z['Source_Cache'] for z in base['evidence'] if z['Source_Cache']}:
   if (V11/'sources'/sf).exists():shutil.copy2(V11/'sources'/sf,t/'sources'/sf)
  oldm=json.loads((V10/'V10_SHA256SUMS.json').read_text(encoding='utf-8'));oldm['files']=[z for z in oldm['files'] if z['path']=='outputs/stageB_food_drug_interactions_v10.csv']
  (t/'v10'/'V10_SHA256SUMS.json').write_text(json.dumps(oldm),encoding='utf-8')
  shutil.copy2(V10/'outputs/stageB_food_drug_interactions_v10.csv',t/'v10'/'stageB_food_drug_interactions_v10.csv')
  if tid=='manifest_missing':(t/'V11_SHA256SUMS.json').unlink(missing_ok=True)
  if tid=='v10_manifest_hash':(t/'v10'/'stageB_food_drug_interactions_v10.csv').write_text('corrupted',encoding='utf-8')
  for key,file in [('compound','compound_registry_v11.csv'),('evidence','stageB_food_drug_interactions_v11.csv'),('drug','drug_probe_registry_v11.csv'),('study','study_registry_v11.csv'),('claim','claim_support_and_verification_v11.csv'),('selection','selection_decisions_v11.csv'),('warning','warning_resolution_ledger_v11.csv'),('cooking','cooking_retention_evidence_v9.csv')]:write(t/file,x[key])
  x={key:read(t/file) for key,file in [('compound','compound_registry_v11.csv'),('evidence','stageB_food_drug_interactions_v11.csv'),('drug','drug_probe_registry_v11.csv'),('study','study_registry_v11.csv'),('claim','claim_support_and_verification_v11.csv'),('selection','selection_decisions_v11.csv'),('warning','warning_resolution_ledger_v11.csv'),('cooking','cooking_retention_evidence_v9.csv')]}
  found=validate(x,t);results.append({'Mutation_ID':'MT-'+str(len(results)+1).zfill(2),'Defect':tid,'Expected_Detector':tid,'Detected':tid in found,'Actual_Detectors':'|'.join(sorted(found)),'Status':'PASS' if tid in found else 'FAIL','Isolation':'Temporary fixture copy mutated and validated; auto-cleaned'})
with (A/'v11_mutation_test_results.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
summary={'attempted':len(results),'detected':sum(x['Detected'] for x in results),'missed':[x['Mutation_ID'] for x in results if not x['Detected']],'detection_rate':sum(x['Detected'] for x in results)/len(results),'status':'PASS' if all(x['Detected'] for x in results) else 'FAIL'}
(A/'v11_mutation_test_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
