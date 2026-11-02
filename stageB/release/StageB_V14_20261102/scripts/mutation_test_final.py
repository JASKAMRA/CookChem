"""Isolated mutation checks for StageB_Final; all changed files live in temp dirs."""
import csv, json, shutil, sys, tempfile
from pathlib import Path
sys.dont_write_bytecode=True
from validate_final import inspect

def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(p,rows):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else []);w.writeheader();w.writerows(rows)
def main(root):
    root=Path(root).resolve(); cases=[]
    def case(name,rel,mutator,expected,record=''):
        temp_root=root/'validation'
        temp_root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='stageb_final_mutation_',dir=temp_root) as td:
            cp=Path(td)/'final';cp.mkdir()
            required=['data/compound_registry.csv','data/interaction_evidence.csv','data/drug_probe_registry.csv',
              'data/study_registry.csv','data/publication_bibliography.csv','data/warning_ledger.csv',
              'data/cooking_retention_evidence.csv','identity/identity_structure_audit.csv',
              'provenance/selection_decisions.csv','provenance/source_audit.csv',
              'provenance/claim_support_and_verification.csv']
            for req_rel in required:
                dest=cp/req_rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/req_rel,dest)
            p=cp/rel;rows=read(p);mutator(rows);write(p,rows)
            errors,warnings,_=inspect(cp);hits=[e for e in errors+warnings if e['Code']==expected and (not record or e['Record_ID']==record)]
            cases.append({'Mutation':name,'Expected_Code':expected,'Target_Record':record,'Detected':bool(hits),'Observed_Matching_Diagnostics':len(hits)})
    compounds='data/compound_registry.csv'; evidence='data/interaction_evidence.csv'
    ev0=read(root/evidence); cp0=read(root/compounds); cid=cp0[0]['Compound_ID']; eid=ev0[0]['Evidence_ID']
    case('duplicate compound ID',compounds,lambda r:r.__setitem__(1,{**r[1],'Compound_ID':r[0]['Compound_ID']}),'CMP_ID_DUP',cid)
    case('duplicate evidence ID',evidence,lambda r:r.__setitem__(1,{**r[1],'Evidence_ID':r[0]['Evidence_ID']}),'EVI_ID_DUP',eid)
    case('orphan compound reference',evidence,lambda r:r.__setitem__(0,{**r[0],'Compound_ID':'MUTATION-NO-COMPOUND'}),'FK_COMPOUND',eid)
    case('orphan drug reference',evidence,lambda r:r.__setitem__(0,{**r[0],'Drug':'MUTATION-NO-DRUG'}),'FK_DRUG',eid)
    case('missing study reference',evidence,lambda r:r.__setitem__(0,{**r[0],'Study_ID':''}),'FK_STUDY',eid)
    case('invalid evidence class',evidence,lambda r:r.__setitem__(0,{**r[0],'Evidence_Type':'human microsome'}),'EVIDENCE_CLASS',eid)
    case('invalid PMID',evidence,lambda r:r.__setitem__(0,{**r[0],'PMID':'PMID-ABC'}),'PMID_FORMAT',eid)
    keyfile='identity/identity_structure_audit.csv'; ir=read(root/keyfile); iid=ir[1]['Compound_ID']
    case('duplicate InChIKey',keyfile,lambda rows:rows[1].update({'Registry_InChIKey':rows[0].get('Registry_InChIKey','')}),'IDENTITY_DUP_KEY',ir[0]['Registry_InChIKey'])
    claimfile='provenance/claim_support_and_verification.csv'; claimrows=read(root/claimfile); target=next((x['Evidence_ID'] for x in ev0 if any(c.get('Evidence_ID')==x['Evidence_ID'] for c in claimrows)),'')
    case('missing source claim',claimfile,lambda r:r.__setitem__(slice(None),[x for x in r if x.get('Evidence_ID')!=target]),'CLAIM_MISSING',target)
    new_anchor=next(x for x in cp0 if x.get('Origin','')=='v12_controlled_expansion')
    case('missing selection rationale',compounds,lambda rows:rows.__setitem__(rows.index(next(x for x in rows if x.get('Compound_ID')==new_anchor['Compound_ID'])),{**next(x for x in rows if x.get('Compound_ID')==new_anchor['Compound_ID']),'Selection_Rationale':''}),'SELECTION_MISSING',new_anchor['Compound_ID'])
    warningfile='data/warning_ledger.csv'; wr=read(root/warningfile); wid=wr[0]['Warning_ID']
    case('duplicate warning ID',warningfile,lambda r:r.__setitem__(1,{**r[1],'Warning_ID':r[0]['Warning_ID']}),'WARNING_ID_DUP',wid)
    cookfile='data/cooking_retention_evidence.csv'; cr=read(root/cookfile)
    def collide(rows):
        rows[0]['Evidence_ID']=eid
    case('cooking/interactions domain collision',cookfile,collide,'DOMAIN_ID_COLLISION',eid)
    out={'attempted':len(cases),'detected':sum(x['Detected'] for x in cases),'missed':[x for x in cases if not x['Detected']],
      'detection_rate':sum(x['Detected'] for x in cases)/len(cases) if cases else 0,'temporary_copies_removed':True,'cases':cases,
      'status':'PASS' if all(x['Detected'] for x in cases) else 'FAIL'}
    p=root/'validation/final_mutation_test_results.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2),encoding='utf-8')
    with (root/'validation/final_mutation_test_results.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Mutation','Expected_Code','Target_Record','Detected','Observed_Matching_Diagnostics']);w.writeheader();w.writerows(cases)
    print(json.dumps({'status':out['status'],'attempted':out['attempted'],'detected':out['detected'],'missed':len(out['missed'])},indent=2))
    return 0 if out['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main(sys.argv[1] if len(sys.argv)>1 else '.'))
