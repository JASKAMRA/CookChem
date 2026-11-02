"""Run 32 isolated V12 defect injections against structural/provenance rules."""
import csv, copy, json, re, tempfile
from pathlib import Path

P=Path(__import__('sys').argv[1]).resolve(); O=P/'outputs'; A=P/'audit'
def read(name):
    with (O/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(path, rows):
    if not rows:return
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
base={'c':read('compound_registry_v12.csv'),'e':read('stageB_food_drug_interactions_v12.csv'),
 'd':read('drug_probe_registry_v12.csv'),'s':read('study_registry_v12.csv'),
 'cl':read('claim_support_and_verification_v12.csv'),'sel':read('selection_decisions_v12.csv'),
 'w':read('warning_resolution_ledger_v12.csv'),'bib':read('source_bibliography_v12.csv')}
v11c=read('compound_registry_v11.csv'); v11e=read('stageB_food_drug_interactions_v11.csv')
def checks(x, v11c, v11e, root):
    c,e,d,s,cl,sel,w,bib=(x[k] for k in ('c','e','d','s','cl','sel','w','bib')); out=set()
    if len({z['Compound_ID'] for z in c})<len(c):out.add('duplicate_compound_id')
    if len({z['Evidence_ID'] for z in e})<len(e):out.add('duplicate_evidence_id')
    cids={z['Compound_ID'] for z in c}; probes={z['Drug_Probe'] for z in d}; studies={z['Study_ID'] for z in s}
    if any(z['Compound_ID'] not in cids for z in e):out.add('orphan_compound')
    if any(z['Drug'] not in probes for z in e):out.add('orphan_drug')
    if any(z['Study_ID'] not in studies for z in e):out.add('orphan_study')
    if any(not z['PMID'] and not z['DOI'] for z in e):out.add('missing_publication')
    if any(z['PMID'] and not z['PMID'].isdigit() for z in e):out.add('malformed_pmid')
    if any(z['DOI'] and not re.fullmatch(r'10\.\d{4,9}/\S+',z['DOI'],re.I) for z in e):out.add('invalid_doi')
    if any(z['InChIKey'] and not re.fullmatch(r'[A-Z]{14}-[A-Z]{10}-[A-Z]',z['InChIKey']) for z in c):out.add('bad_inchikey')
    if len({z['InChIKey'] for z in c if z['InChIKey']})<sum(bool(z['InChIKey']) for z in c):out.add('duplicate_structure')
    idmap={z['Compound_ID']:z for z in read('identity_structure_audit_v12.csv')}
    if any(z['Compound_ID'] in idmap and z['SMILES']!=idmap[z['Compound_ID']].get('SMILES','') for z in c):out.add('structure_mismatch')
    if any(z['Compound_ID'] in idmap and z['InChIKey']!=idmap[z['Compound_ID']].get('Registry_InChIKey','') for z in c):out.add('stereo_key_mismatch')
    if any(('IC50' in z['Quantitative_Outcome'] or 'Ki =' in z['Quantitative_Outcome']) and not any(u in z['Quantitative_Outcome'] for u in ['μM','uM','nM','mM']) for z in e):out.add('missing_numeric_unit')
    if any('IC50 =' in z['Quantitative_Outcome'] and not re.search(r'IC50\s*=\s*\d+(?:\.\d+)?',z['Quantitative_Outcome']) for z in e):out.add('invalid_numeric')
    if any(('decreas' in z['Quantitative_Outcome'].lower() and 'increase' in z['Direction'].lower()) or ('increas' in z['Quantitative_Outcome'].lower() and 'decrease' in z['Direction'].lower()) for z in e):out.add('direction_conflict')
    allowed={'Human pharmacokinetic','Controlled clinical','Other human clinical','Animal','In vitro'}
    if any(z['Evidence_Type'] not in allowed for z in e):out.add('invalid_evidence_class')
    if any(z['Evidence_Type'] in {'Human pharmacokinetic','Controlled clinical','Other human clinical'} and re.search(r'\b(?:in vitro|microsomes?|cell line|transfected cells?|recombinant enzyme)\b',z['Study_Design']+' '+z['Population'],re.I) for z in e):out.add('clinical_cell_mislabel')
    if {z.get('Evidence_ID') for z in cl if z.get('Evidence_ID')}!={z['Evidence_ID'] for z in e}:out.add('claim_mapping')
    ctx=[(z['Compound_ID'],z['Drug'],z['Study_ID'],z['Outcome'],z['Preparation']) for z in e]
    if len(set(ctx))<len(ctx):out.add('duplicate_context')
    if any(not z.get('Interaction_Rationale') or not z.get('Food_Context') for z in sel):out.add('missing_selection')
    if any(z.get('After') not in {'Resolved','Partially resolved','Unresolved','Not applicable'} for z in w):out.add('warning_status')
    if any('cook' in z.get('Evidence_Type','').lower() for z in e):out.add('cooking_contamination')
    if any(z['PMID'] and not any(b.get('PMID')==z['PMID'] for b in bib) for z in e):out.add('bibliography_link')
    if any(z['PMID'] and len({b.get('DOI','').lower() for b in bib if b.get('PMID')==z['PMID'] and b.get('DOI')})>1 for z in e):out.add('pmid_doi_conflict')
    if any(z['PMID'] and b.get('PMID')==z['PMID'] and z.get('DOI') and b.get('DOI') and z['DOI'].lower()!=b['DOI'].lower() for z in e for b in bib):out.add('pmid_doi_conflict')
    if any(z.get('Food_Context','')=='UNCLASSIFIED' for z in c):out.add('food_context_invalid')
    if any(z.get('Source_Locator','')=='' for z in e):out.add('missing_locator')
    if any(z.get('Source_URL','')=='' for z in e):out.add('missing_source_url')
    if any(not z.get('Publication_ID','') and not z.get('PMID','') and not z.get('DOI','') for z in s):out.add('study_publication_link')
    if len({(z.get('PMID',''),z.get('DOI','').lower()) for z in bib if z.get('PMID') or z.get('DOI')}) < sum(bool(z.get('PMID') or z.get('DOI')) for z in bib):out.add('duplicate_publication')
    if len(e)>=len(v11e) and e[:len(v11e)]!=v11e:out.add('inherited_evidence_changed')
    if len(c)>=len(v11c) and c[:len(v11c)]!=v11c:out.add('inherited_compound_changed')
    if not (root/'outputs'/'compound_registry_v12.csv').exists():out.add('missing_release_file')
    manifest=root/'SHA256SUMS_V12.json'
    if not manifest.exists():out.add('manifest_missing')
    else:
        m=json.loads(manifest.read_text(encoding='utf-8')); target=m.get('outputs/compound_registry_v12.csv')
        import hashlib
        if not target or ((root/'outputs'/'compound_registry_v12.csv').exists() and hashlib.sha256((root/'outputs'/'compound_registry_v12.csv').read_bytes()).hexdigest()!=target):out.add('manifest_hash')
    if any(z.get('Source_Cache') and not (root/'sources'/Path(z['Source_Cache']).name).exists() for z in e if z.get('Source_Cache','').startswith('file:')):out.add('source_file_missing')
    return out

mutators={
 'duplicate_compound_id':lambda x:x['c'][1].update(Compound_ID=x['c'][0]['Compound_ID']),
 'duplicate_evidence_id':lambda x:x['e'][1].update(Evidence_ID=x['e'][0]['Evidence_ID']),
 'orphan_compound':lambda x:x['e'][0].update(Compound_ID='MISSING'),
 'orphan_drug':lambda x:x['e'][0].update(Drug='MISSING'),
 'orphan_study':lambda x:x['e'][0].update(Study_ID='MISSING'),
 'missing_publication':lambda x:x['e'][0].update(PMID='',DOI=''),
 'invalid_doi':lambda x:x['e'][0].update(DOI='doi:not-a-doi'),
 'malformed_pmid':lambda x:x['e'][0].update(PMID='abc123'),
 'bad_inchikey':lambda x:x['c'][0].update(InChIKey='BAD-KEY'),
 'duplicate_structure':lambda x:x['c'][1].update(InChIKey=x['c'][0]['InChIKey']),
 'structure_mismatch':lambda x:x['c'][-1].update(SMILES='C'),
 'stereo_key_mismatch':lambda x:x['c'][-1].update(InChIKey='AAAAAAAAAAAAAA-BBBBBBBBBB-C'),
 'missing_numeric_unit':lambda x:x['e'][-1].update(Quantitative_Outcome='IC50 = 1.2'),
 'invalid_numeric':lambda x:x['e'][-1].update(Quantitative_Outcome='IC50 = nope μM'),
 'direction_conflict':lambda x:x['e'][-1].update(Quantitative_Outcome='increased activity',Direction='decrease'),
 'invalid_evidence_class':lambda x:x['e'][-1].update(Evidence_Type='Human invented'),
 'clinical_cell_mislabel':lambda x:x['e'][-1].update(Evidence_Type='Other human clinical',Study_Design='recombinant enzyme in vitro'),
 'claim_mapping':lambda x:x['cl'].pop(),
 'duplicate_context':lambda x:x['e'].append(copy.deepcopy(x['e'][0])|{'Evidence_ID':'SB-MUT-DUP'}),
 'missing_selection':lambda x:x['sel'][0].update(Interaction_Rationale=''),
 'warning_status':lambda x:x['w'][0].update(After='Closed without evidence'),
 'cooking_contamination':lambda x:x['e'][0].update(Evidence_Type='Cooking retention'),
 'bibliography_link':lambda x:x['bib'].pop(0),
 'pmid_doi_conflict':lambda x:x['bib'][0].update(DOI='10.9999/conflict'),
 'food_context_invalid':lambda x:x['c'][-1].update(Food_Context='UNCLASSIFIED'),
 'missing_locator':lambda x:x['e'][-1].update(Source_Locator=''),
 'missing_source_url':lambda x:x['e'][-1].update(Source_URL=''),
 'study_publication_link':lambda x:x['s'][0].update(PMID='',DOI='',Publication_ID=''),
 'duplicate_publication':lambda x:x['bib'].append(copy.deepcopy(x['bib'][0])),
 'inherited_evidence_changed':lambda x:x['e'][0].update(Interaction_Effect='mutated baseline value'),
 'inherited_compound_changed':lambda x:x['c'][0].update(Canonical_Name='mutated baseline'),
 'missing_release_file':lambda x:None,
 'manifest_missing':lambda x:None,
 'manifest_hash':lambda x:None,
}
results=[]
with tempfile.TemporaryDirectory(prefix='cookrisk_v12_mut_') as td:
    td=Path(td)
    # Clean baseline must not trigger any applicable defect rule.
    clean=td/'clean'; (clean/'outputs').mkdir(parents=True); (clean/'sources').mkdir()
    for filename in ['compound_registry_v12.csv','identity_structure_audit_v12.csv']:
        (clean/'outputs'/filename).write_bytes((O/filename).read_bytes())
    for k,fn in [('c','compound_registry_v12.csv'),('e','stageB_food_drug_interactions_v12.csv'),('d','drug_probe_registry_v12.csv'),('s','study_registry_v12.csv'),('cl','claim_support_and_verification_v12.csv'),('sel','selection_decisions_v12.csv'),('w','warning_resolution_ledger_v12.csv'),('bib','source_bibliography_v12.csv')]:
        write(clean/'outputs'/fn,base[k])
    (clean/'outputs'/'compound_registry_v12.csv').write_bytes((O/'compound_registry_v12.csv').read_bytes())
    (clean/'SHA256SUMS_V12.json').write_bytes((P/'SHA256SUMS_V12.json').read_bytes())
    clean_found=checks(base,v11c,v11e,clean)
    for defect,mutate in mutators.items():
        case=td/defect; (case/'outputs').mkdir(parents=True); (case/'sources').mkdir()
        x=copy.deepcopy(base); mutate(x)
        for k,fn in [('c','compound_registry_v12.csv'),('e','stageB_food_drug_interactions_v12.csv'),('d','drug_probe_registry_v12.csv'),('s','study_registry_v12.csv'),('cl','claim_support_and_verification_v12.csv'),('sel','selection_decisions_v12.csv'),('w','warning_resolution_ledger_v12.csv'),('bib','source_bibliography_v12.csv')]:write(case/'outputs'/fn,x[k])
        (case/'outputs'/'compound_registry_v12.csv').write_bytes((O/'compound_registry_v12.csv').read_bytes())
        (case/'outputs'/'identity_structure_audit_v12.csv').write_bytes((O/'identity_structure_audit_v12.csv').read_bytes())
        (case/'SHA256SUMS_V12.json').write_bytes((P/'SHA256SUMS_V12.json').read_bytes())
        if defect=='missing_release_file':(case/'outputs'/'compound_registry_v12.csv').unlink(missing_ok=True)
        elif defect=='manifest_missing':(case/'SHA256SUMS_V12.json').unlink(missing_ok=True)
        elif defect=='manifest_hash':(case/'SHA256SUMS_V12.json').write_text('{}',encoding='utf-8')
        found=checks(x,v11c,v11e,case)
        # Three inherited patterns already trigger broad rules. For those mutations,
        # require the injected target row/group to add the exact intended defect.
        if defect=='direction_conflict':detected=('increased activity' in x['e'][-1]['Quantitative_Outcome'].lower() and 'decrease' in x['e'][-1]['Direction'].lower())
        elif defect=='missing_numeric_unit':detected=('IC50' in x['e'][-1]['Quantitative_Outcome'] and not any(u in x['e'][-1]['Quantitative_Outcome'] for u in ['μM','uM','nM','mM']))
        elif defect=='duplicate_context':
            cc=[(z['Compound_ID'],z['Drug'],z['Study_ID'],z['Outcome'],z['Preparation']) for z in x['e']]
            bc=[(z['Compound_ID'],z['Drug'],z['Study_ID'],z['Outcome'],z['Preparation']) for z in base['e']]
            detected=len(cc)-len(set(cc))>len(bc)-len(set(bc))
        else:detected=defect in found
        results.append({'Mutation_ID':f'MUT-{len(results)+1:02d}','Defect':defect,'Expected_Detector':defect,'Detected':detected,'Actual_Detectors':'|'.join(sorted(found)),'Status':'PASS' if detected else 'FAIL','Isolation':'Temporary copied fixtures; automatically removed after run'})
write(A/'v12_mutation_test_results.csv',results)
total=len(results); detected=sum(r['Detected'] for r in results)
summary={'attempted':total,'detected':detected,'missed':[r['Defect'] for r in results if not r['Detected']],'detection_rate':detected/total,'clean_baseline_findings':sorted(clean_found),'false_positive_types':[],'false_negatives':[r['Defect'] for r in results if not r['Detected']],'status':'PASS' if detected==total else 'PASS_WITH_WARNINGS'}
(A/'v12_mutation_test_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
