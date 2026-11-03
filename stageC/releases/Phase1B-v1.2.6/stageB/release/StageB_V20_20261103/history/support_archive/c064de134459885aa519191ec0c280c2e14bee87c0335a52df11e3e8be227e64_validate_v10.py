import csv,json,hashlib,copy,collections,re
from pathlib import Path
P=Path(r'C:\Users\dakshant\Documents\CookChem\stageB\release_v10_20261030'); O=P/'outputs'; A=P/'audit'
def rd(n):
    with open(O/n,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def assess(e,r,ids,sel,warn,claims):
    checks={}
    checks['100_distinct_anchors']=len(r)==100 and len({x['Compound_ID'] for x in r})==100
    checks['263_unique_evidence_ids']=len(e)==263 and len({x['Evidence_ID'] for x in e})==263
    old=rd('stageB_food_drug_interactions_v9.csv')
    checks['all_v9_evidence_preserved_exactly']=e[:len(old)]==old
    rb={x['Compound_ID']:x for x in r}
    checks['all_evidence_compound_references_valid']=all(x['Compound_ID'] in rb and x['Compound']==rb[x['Compound_ID']]['Canonical_Name'] for x in e)
    checks['all_structures_complete']=len(ids)==100 and all(x['Status']=='Complete' and x['SMILES'] and x['InChI'] and x['Returned_InChIKey'] for x in ids)
    keys=[x['Returned_InChIKey'] for x in ids]
    checks['unique_exact_structures']=len(keys)==100 and len(set(keys))==100
    cids=[x['PubChem_CID'] for x in r]
    checks['unique_pubchem_cids']=len(cids)==100 and len(set(cids))==100
    checks['selection_coverage']=len({x['Candidate'] for x in sel})==40 and all(x.get('Food_Context') and x.get('Interaction_Rationale') for x in sel)
    checks['claims_cover_new_records']=len(claims)==len(e) and {x['Evidence_ID'] for x in claims}=={x['Evidence_ID'] for x in e}
    checks['all_new_sources_linked']=all((P/'sources'/x['Source_Cache']).is_file() if x['Source_Cache'] else bool(x['DOI'] and x['Source_URL']) for x in e[len(old):])
    checks['valid_new_identifiers']=all((x['PMID'].isdigit() and (not x['DOI'] or x['DOI'].startswith('10.'))) or (not x['PMID'] and x['DOI'].startswith('10.')) for x in e[len(old):])
    checks['warning_inheritance']=set(x['Warning_ID'] for x in rd('warning_resolution_ledger_v9.csv'))<=set(x['Warning_ID'] for x in warn)
    checks['cooking_table_preserved']= (O/'cooking_retention_evidence_v9.csv').read_bytes()==(P.parent/'release_v9_20261029'/'outputs'/'cooking_retention_evidence_v9.csv').read_bytes()
    checks['no_cooking_records_in_interaction_table']=all('cook' not in x['Evidence_Type'].lower() for x in e)
    checks['no_duplicate_warning_ids']=len(warn)==len({x['Warning_ID'] for x in warn})
    checks['drug_registry_covers_records']= {x['Drug'] for x in e} <= {x['Drug_Probe'] for x in rd('drug_probe_registry_v10.csv')}
    checks['study_registry_covers_new_records']= {x['Study_ID'] for x in e[len(old):]} <= {x['Study_ID'] for x in rd('study_registry_v10.csv')}
    bib=rd('source_bibliography_v10.csv')
    checks['bibliography_identifier_reconciliation']=len(bib)==141 and len({x['PMID'] for x in bib if x['PMID']})==140 and len({x['DOI'].lower() for x in bib if x['DOI']})==136 and sum(not x['PMID'] for x in bib)==1
    return checks

e=rd('stageB_food_drug_interactions_v10.csv');r=rd('compound_registry_v10.csv');ids=rd('identity_structure_audit_v10.csv');sel=rd('v10_selection_decisions.csv');warn=rd('warning_resolution_ledger_v10.csv');claims=rd('claim_support_and_verification_v10.csv')
synrows=json.loads((P/'sources/pubchem_synonyms_all.json').read_text(encoding='utf-8-sig'))
synmap={str(x['CID']):x.get('Synonym',[]) for x in synrows}
def norm(s):return re.sub(r'[^a-z0-9]','',s.lower())
regby={x['Compound_ID']:x for x in r}
for x in ids:
    rr=regby[x['Compound_ID']]; synonyms=synmap.get(x['PubChem_CID'],[])
    aliases=[z.strip() for z in rr['Aliases'].split('|') if z.strip()]
    hit=any(norm(rr['Canonical_Name'])==norm(z) for z in synonyms) or any(norm(a)==norm(z) for a in aliases for z in synonyms)
    x['PubChem_Name_or_Alias_Match']=str(hit)
    x['PubChem_Synonyms']=' | '.join(synonyms[:20])
with open(O/'identity_structure_audit_v10.csv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(ids[0]));w.writeheader();w.writerows(ids)
checks=assess(e,r,ids,sel,warn,claims)
checks['100_name_or_alias_to_cid_matches']=all(x['PubChem_Name_or_Alias_Match']=='True' for x in ids)
mutations=[]
for name,kind in [('duplicate_compound_id','cid'),('duplicate_evidence_id','eid'),('orphan_compound','orphan'),('missing_inchikey','key'),('duplicate_structure','structure'),('bad_pmid','pmid'),('missing_source_claim','claim'),('missing_selection','selection'),('missing_warning','warning'),('mix_cooking_domain','cooking')]:
    ee,rr,ii,ss,ww,cc=copy.deepcopy(e),copy.deepcopy(r),copy.deepcopy(ids),copy.deepcopy(sel),copy.deepcopy(warn),copy.deepcopy(claims)
    if kind=='cid':rr[-1]['Compound_ID']=rr[0]['Compound_ID']
    elif kind=='eid':ee[-1]['Evidence_ID']=ee[0]['Evidence_ID']
    elif kind=='orphan':ee[-1]['Compound_ID']='NO-SUCH-COMPOUND'
    elif kind=='key':ii[-1]['Returned_InChIKey']=''
    elif kind=='structure':ii[-1]['Returned_InChIKey']=ii[0]['Returned_InChIKey']
    elif kind=='pmid':ee[-1]['PMID']='bad'
    elif kind=='claim':cc.pop()
    elif kind=='selection':ss.pop()
    elif kind=='warning':ww.pop(0)
    elif kind=='cooking':ee[-1]['Evidence_Type']='Cooking retention'
    try: caught=not all(assess(ee,rr,ii,ss,ww,cc).values())
    except Exception:caught=True
    mutations.append({'Mutation':name,'Detected':caught})

# Independent V9 baseline reconciliation; verified V9 paths must byte-match the separate baseline release.
hashes=json.loads((A/'v10_inherited_v9_hashes.json').read_text(encoding='utf-8'))
v9=P.parent/'release_v9_20261029'; mismatch=[]
for rel,h in hashes.items():
    if not (v9/rel).is_file() or sha(v9/rel)!=h:mismatch.append(rel)
checks['v9_unchanged_hashes_match']=not mismatch
full_manifest=json.loads((P/'V9_SHA256SUMS.json').read_text(encoding='utf-8-sig'))
full_mismatch=[]
for rel,expected in full_manifest.items():
    q=v9/rel
    if not q.is_file() or sha(q)!=expected: full_mismatch.append(rel)
checks['full_v9_release_manifest_matches']=bool(full_manifest) and not full_mismatch
summary={'status':'PASS' if all(checks.values()) and all(x['Detected'] for x in mutations) else 'FAIL','checks':checks,'passed':sum(checks.values()),'total_checks':len(checks),'errors':[k for k,v in checks.items() if not v],'mutation_tests':mutations,'mutations_passed':sum(x['Detected'] for x in mutations),'mutations_total':len(mutations),'v9_hash_mismatches':mismatch,'full_v9_manifest_files_checked':len(full_manifest),'full_v9_manifest_mismatches':full_mismatch,'anchors':len(r),'records':len(e),'new_anchors':len(r)-74,'new_records':len(e)-210,'unique_PMIDs':len({x['PMID'] for x in e if x['PMID']}),'unique_DOIs':len({x['DOI'].lower() for x in e if x['DOI']})}
(A/'v10_validation_report.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
# Source audit file for each V10 addition.
with open(O/'v10_source_audit.csv','w',encoding='utf-8-sig',newline='') as f:
    fields=['Evidence_ID','PMID','DOI','Source_Title','Source_URL','Source_Cache','Source_Locator','Verification_Status','Fields_Audited','Limitations']
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    cl={x['Evidence_ID']:x for x in claims}
    for x in e[210:]:w.writerow({'Evidence_ID':x['Evidence_ID'],'PMID':x['PMID'],'DOI':x['DOI'],'Source_Title':x['Source_Title'],'Source_URL':x['Source_URL'],'Source_Cache':x['Source_Cache'],'Source_Locator':x['Source_Locator'],'Verification_Status':cl[x['Evidence_ID']]['Verification_Status'],'Fields_Audited':'identity; assay; probe; outcome as stated in abstract/article locator','Limitations':x['Limitations']})
print(json.dumps(summary,ensure_ascii=False,indent=2))
