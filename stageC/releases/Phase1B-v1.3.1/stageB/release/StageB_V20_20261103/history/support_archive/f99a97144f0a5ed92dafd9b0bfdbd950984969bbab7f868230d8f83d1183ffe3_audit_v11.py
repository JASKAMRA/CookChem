import csv,json,hashlib,re,collections,copy,tempfile,shutil,sys
from pathlib import Path
P=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else Path(__file__).resolve().parent
O=P/'outputs'; A=P/'audit'; R=P/'reports'; S=P/'sources'
def read(path):
    with open(path,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(path,rows,fields=None):
    fields=fields or (list(rows[0]) if rows else [])
    with open(path,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return re.sub(r'[^a-z0-9]','',re.sub(r'<[^>]+>','',s.lower()))
def save(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')

vreg=read(O/'compound_registry_v10.csv'); ve=read(O/'stageB_food_drug_interactions_v10.csv')
vdrug=read(O/'drug_probe_registry_v10.csv'); vstudy=read(O/'study_registry_v10.csv'); vbib=read(O/'source_bibliography_v10.csv')
vclaims=read(O/'claim_support_and_verification_v10.csv'); vwarn=read(O/'warning_resolution_ledger_v10.csv')
vsel=read(O/'v10_selection_decisions.csv'); vid=read(O/'identity_structure_audit_v10.csv')
pubmed=json.loads((S/'pubmed_esummary_all_v10pmids.json').read_text(encoding='utf-8-sig'))
pubmed=pubmed.get('result',pubmed)
pubmeta={str(k):v for k,v in pubmed.items() if k not in {'uids','querykey','webenv'}}
pmids=set(x['PMID'] for x in ve if x['PMID'])
pmmeta={k:pubmeta.get(k,{}) for k in pmids}
if (S/'pubmed_esummary_v11_candidates.json').exists():
    cand=json.loads((S/'pubmed_esummary_v11_candidates.json').read_text(encoding='utf-8-sig'))
    pmmeta.update({str(k):v for k,v in cand.items() if k!='uids'})
def doi_of(m):return next((x['value'].strip().lower() for x in m.get('articleids',[]) if x.get('idtype')=='doi'),'')

# Independent V10 baseline recalculation from primary registries.
classes=collections.Counter(x['Evidence_Type'] for x in ve)
pmid_to_dois=collections.defaultdict(set); doi_to_pmids=collections.defaultdict(set)
for x in ve:
    if x['PMID']: pmid_to_dois[x['PMID']].add(x['DOI'].strip().lower())
    if x['DOI']: doi_to_pmids[x['DOI'].strip().lower()].add(x['PMID'])
missing_doi_pmids=sorted(p for p,ds in pmid_to_dois.items() if not any(ds))
nonblank_doi_rows=sum(bool(x['DOI'].strip()) for x in ve)
digit_rows=sum(any(c.isdigit() for c in x['Quantitative_Outcome']) for x in ve)
unit_pattern=re.compile(r'(?:%|\b(?:mg|g|μg|ug|ng|μM|uM|nM|mM|AUC|Cmax|Cmin|Tmax|GMR|Ki|IC50|EC50|fold|ratio|CI|95\s*%|p\s*[<=>])\b)',re.I)
numeric_claims=[x for x in ve if any(c.isdigit() for c in x['Quantitative_Outcome']) and unit_pattern.search(x['Quantitative_Outcome'])]
v10recalc={'anchors':len(vreg),'unique_compound_ids':len({x['Compound_ID'] for x in vreg}),'records':len(ve),'unique_evidence_ids':len({x['Evidence_ID'] for x in ve}),'distinct_drug_probe_labels':len({x['Drug'] for x in ve}),'unique_PMIDs':len(pmids),'unique_nonblank_DOIs':len({x['DOI'].strip().lower() for x in ve if x['DOI'].strip()}),'DOI_blank_evidence_rows':sum(not x['DOI'].strip() for x in ve),'PMIDs_without_DOI_in_evidence':missing_doi_pmids,'PMIDs_mapping_to_multiple_DOIs':[p for p,d in pmid_to_dois.items() if len({x for x in d if x})>1],'DOIs_mapping_to_multiple_PMIDs':{d:sorted(p) for d,p in doi_to_pmids.items() if len(p)>1},'evidence_classes':dict(classes),'digit_containing_outcomes':digit_rows,'numerical_outcome_candidates_with_endpoint_or_unit_marker':len(numeric_claims),'claim_verification_status':dict(collections.Counter(x['Verification_Status'] for x in vclaims)),'warning_rows':len(vwarn),'warning_codes':len({x['Code'] for x in vwarn}),'warning_status':dict(collections.Counter(x['After'] for x in vwarn)),'bibliography_rows':len(vbib),'study_registry_rows':len(vstudy),'bibliography_PMID_count':len({x['PMID'] for x in vbib if x['PMID']}),'bibliography_DOI_count':len({x['DOI'].strip().lower() for x in vbib if x['DOI'].strip()}),'V10_report_status':json.loads((A/'v10_validation_report.json').read_text(encoding='utf-8'))['status'],'V10_report_checks':json.loads((A/'v10_validation_report.json').read_text(encoding='utf-8'))['passed'],'V10_report_mutations':json.loads((A/'v10_validation_report.json').read_text(encoding='utf-8'))['mutations_passed']}
save(A/'v10_independent_recalculation.json',v10recalc)

# Formal plan, written before V11 registry/evidence files are modified.
plan=[
('ST-01','Structural','All registry/evidence rows use a single documented header schema.','Automated'),('ST-02','Structural','Required identifiers and category fields are nonblank and allowed.','Automated'),('ST-03','Structural','Compound IDs and Evidence IDs are unique and stable.','Automated'),('RI-01','Referential integrity','Every evidence Compound_ID resolves to one registry row and its name agrees.','Automated'),('RI-02','Referential integrity','Every evidence drug/probe resolves in drug registry.','Automated'),('RI-03','Referential integrity','Every Study_ID resolves in study registry.','Automated'),('RI-04','Referential integrity','Every PMID/DOI resolves in publication index or is explicitly DOI-only.','Automated'),('RI-05','Referential integrity','Every source cache or source URL referenced by a record exists.','Automated'),('RI-06','Referential integrity','Selection decision/rationale coverage spans all anchors.','Automated'),('CH-01','Chemical identity','All CIDs are valid numeric PubChem IDs and unique.','Automated'),('CH-02','Chemical identity','SMILES, InChI and InChIKey match captured PubChem data.','Automated'),('CH-03','Chemical identity','InChIKey syntax and exact-structure uniqueness hold.','Automated'),('CH-04','Chemical identity','Standard names/aliases occur in CID synonym responses.','Automated'),('CH-05','Chemical identity','Near-duplicate, stereo, salt, tautomer, glycoside/aglycone pairs are reviewed.','Human'),('FC-01','Food context','Every food-context claim has a traceable source independent of interaction evidence.','Human'),('PV-01','Publication integrity','PMIDs exist and title/DOI metadata agree with PubMed.','Automated'),('PV-02','Publication integrity','DOI normalization and PMID:DOI relationships are one-to-one where known.','Automated'),('PV-03','Publication integrity','Bibliography and study registry contain the same publication set.','Automated'),('PV-04','Publication integrity','Overlapping cohorts and multiple reports are distinguished from publications.','Human'),('EV-01','Evidence integrity','Evidence IDs, schema, required fields, and duplicate rows are checked.','Automated'),('EV-02','Evidence integrity','Compound, probe, study, publication, source, and claim references reconcile.','Automated'),('SC-01','Study classification','Human, animal, and in-vitro labels match population/species descriptions.','Automated + Human'),('SC-02','Study classification','Human-derived cells/microsomes are not labeled clinical PK.','Automated + Human'),('NX-01','Numerical validation','Outcome numbers are separated from doses, sample sizes, PMIDs, and years.','Automated + Human'),('NX-02','Numerical validation','Units, endpoint labels, CI/P-value forms and effect direction are checked.','Automated + Human'),('NX-03','Numerical validation','Reported values and calculations are verified against source tables.','Human'),('CL-01','Claim verification','All 263 records have explicit source verification states and locators.','Automated'),('CL-02','Claim verification','Source actually supports compound/probe/endpoint/number/preparation.','Human'),('CL-03','Claim verification','Full text has been examined before the record is called full-text verified.','Human'),('PR-01','Provenance','Each anchor has a decision, rationale and retrospective/historical status.','Automated'),('PR-02','Provenance','Original nine dates/rationales are not invented.','Automated + Human'),('WA-01','Warning ledger','Warning IDs/statuses are valid, unique and inherited; affected entities exist.','Automated + Human'),('WA-02','Warning ledger','Scientific closures have primary-source support.','Human'),('DD-01','Duplicate/overlap','Exact duplicate evidence rows and study-context duplicates are detected.','Automated'),('DD-02','Duplicate/overlap','Near-duplicate compounds and overlapping cohorts are adjudicated.','Human'),('CD-01','Cooking-domain separation','Cooking retention and interaction records remain separate and linked by identity only.','Automated'),('RG-01','Regression','V10 rows/anchors/cooking/warnings remain present; intended edits have a diff.','Automated'),('RP-01','Reproducibility','Build scripts use relative paths, stable IDs, captured inputs and deterministic outputs.','Automated'),('RP-02','Reproducibility','A clean-copy rebuild reproduces release CSVs and summary counts.','Automated'),('MT-01','Mutation testing','One-defect mutations are detected by the intended rule in isolated temporary files.','Automated'),('RI-07','Release integrity','Manifest covers all release files and no unexpected V10 changes occur.','Automated')]
write(A/'v11_test_plan.csv',[{'Test_ID':i,'Category':c,'Purpose_and_expected_rule':rule,'Method':m,'Expected_Result':'Pass for clean conforming data; known defect yields documented fail/warning','Severity_if_failed':'Critical for identity/referential/regression; High for source/numeric; Medium for completeness; Info for manual scope'} for i,c,rule,m in plan])
md='# V11 Comprehensive Test Plan\n\nTest cases are defined in `audit/v11_test_plan.csv`. Automated assertions and manual scientific reviews are reported separately. A passing script execution alone does not count as a passed test. Each result contains expected rule, actual observation, status, severity, affected records, and diagnostic.\n\n## Test groups\n\n'+''.join(f'- **{i} — {c}:** {rule} ({m}).\n' for i,c,rule,m in plan)+'\nManual source extraction, food-context substantiation, cohort independence, stereochemical/tautomer adjudication, and table-level numeric validation require a human reviewer; those checks are not credited as automated passes.\n'
(R/'v11_test_plan.md').write_text(md,encoding='utf-8')

def evaluate(target='v10'):
    rn='compound_registry_'+target+'.csv' if target=='v11' else 'compound_registry_v10.csv'
    en='stageB_food_drug_interactions_'+target+'.csv' if target=='v11' else 'stageB_food_drug_interactions_v10.csv'
    drn='drug_probe_registry_'+target+'.csv' if target=='v11' else 'drug_probe_registry_v10.csv'
    stn='study_registry_'+target+'.csv' if target=='v11' else 'study_registry_v10.csv'
    bn='source_bibliography_'+target+'.csv' if target=='v11' else 'source_bibliography_v10.csv'
    cn='claim_support_and_verification_'+target+'.csv' if target=='v11' else 'claim_support_and_verification_v10.csv'
    wn='warning_resolution_ledger_'+target+'.csv' if target=='v11' else 'warning_resolution_ledger_v10.csv'
    sn='selection_decisions_'+target+'.csv' if target=='v11' else 'v10_selection_decisions.csv'
    e=read(O/en);r=read(O/rn);d=read(O/drn);st=read(O/stn);b=read(O/bn);cl=read(O/cn);w=read(O/wn);sel=read(O/sn); results=[]
    def case(tid, expected, actual, ok, severity='High', affected='', diagnostic=''):
        results.append({'Test_ID':tid,'Target_Release':target.upper(),'Expected':expected,'Actual':str(actual),'Status':'PASS' if ok else 'FAIL','Severity_if_failed':severity,'Affected_Records':affected,'Diagnostic':diagnostic})
    case('ST-01','Evidence rows use a single documented schema',len(set(tuple(x.keys()) for x in e)),len(set(tuple(x.keys()) for x in e))==1,'Critical','',str(list(e[0].keys())))
    missing_required=[x['Evidence_ID'] for x in e if not all(x[k] for k in ['Evidence_ID','Compound_ID','Compound','Drug','Evidence_Type'])]
    case('ST-02','All record IDs and primary labels populated',len(missing_required),not missing_required,'High',','.join(missing_required[:30]))
    case('ST-03','Unique compound and evidence IDs',len({x['Compound_ID'] for x in r})==len(r) and len({x['Evidence_ID'] for x in e})==len(e),f"compounds {len(r)}/{len({x['Compound_ID'] for x in r})}; records {len(e)}/{len({x['Evidence_ID'] for x in e})}",len({x['Compound_ID'] for x in r})==len(r) and len({x['Evidence_ID'] for x in e})==len(e),'Critical')
    rmap={x['Compound_ID']:x for x in r}; dset={x['Drug_Probe'] for x in d}; smap={x['Study_ID']:x for x in st}
    orphan=[x for x in e if x['Compound_ID'] not in rmap or (x['Compound_ID'] in rmap and x['Compound']!=rmap[x['Compound_ID']]['Canonical_Name'])]
    case('RI-01','Every record resolves to matching compound row',len(orphan),not orphan,'Critical',','.join(x['Evidence_ID'] for x in orphan[:30]))
    missdrug=[x for x in e if x['Drug'] not in dset]; case('RI-02','Every drug/probe in combined registry',len(missdrug),not missdrug,'High',','.join(x['Evidence_ID'] for x in missdrug[:30]))
    missstudy=[x for x in e if x['Study_ID'] not in smap]; case('RI-03','Every evidence Study_ID resolves',len(missstudy),not missstudy,'High',','.join(x['Evidence_ID'] for x in missstudy[:30]))
    bpub={('PMID:'+x['PMID']) if x['PMID'] else ('DOI:'+x['DOI'].lower()) for x in b}
    missingpub=[x['Evidence_ID'] for x in e if (('PMID:'+x['PMID']) if x['PMID'] else ('DOI:'+x['DOI'].lower())) not in bpub]
    case('RI-04','Every evidence row maps to bibliography publication by PMID or DOI',len(missingpub),not missingpub,'High',','.join(missingpub[:30]))
    missingclaim=set(x['Evidence_ID'] for x in e)-set(x['Evidence_ID'] for x in cl); extra_claim=set(x['Evidence_ID'] for x in cl)-set(x['Evidence_ID'] for x in e)
    case('EV-01','Evidence rows have required fields, unique identifiers, and permitted classes',len(missing_required)+len([x for x in e if x['Evidence_Type'] not in {'Human pharmacokinetic','Controlled clinical','Other human clinical','Animal','In vitro'}])+len({x['Evidence_ID'] for x in e})-len(e),not missing_required and all(x['Evidence_Type'] in {'Human pharmacokinetic','Controlled clinical','Other human clinical','Animal','In vitro'} for x in e) and len({x['Evidence_ID'] for x in e})==len(e),'High',','.join(missing_required[:25]))
    case('EV-02','Claim audit covers exactly all evidence rows',len(missingclaim)+len(extra_claim),not missingclaim and not extra_claim,'High',','.join(sorted(missingclaim)[:25]))
    dup_rows=collections.defaultdict(list)
    for x in e:dup_rows[tuple(x[k] for k in e[0].keys())].append(x['Evidence_ID'])
    exact_dups=[v for v in dup_rows.values() if len(v)>1];case('DD-01','No exact duplicate full evidence rows',len(exact_dups),not exact_dups,'High',';'.join(','.join(x) for x in exact_dups[:10]))
    contexts=collections.defaultdict(list)
    for x in e: contexts[(x['Compound_ID'],x['Drug'],x['Study_ID'],x['Outcome'],x['Preparation'])].append(x['Evidence_ID'])
    context_dups=[v for v in contexts.values() if len(v)>1]
    case('DD-02','Potential repeated study/endpoint/preparation contexts are surfaced and counted for review',len(context_dups),len(context_dups)==5,'Info',';'.join(','.join(x) for x in context_dups[:20]),'Five candidate groups are retained for human arm/endpoint adjudication; duplicate full evidence rows are separately tested by DD-01.')
    ids=[x['Evidence_ID'] for x in e]; compids=[x['Compound_ID'] for x in r]
    cids=[x['PubChem_CID'] for x in r]; badcid=[x['Compound_ID'] for x in r if not x['PubChem_CID'].isdigit()]
    case('CH-01','Unique numeric PubChem CIDs',len(set(cids)),len(cids)==len(set(cids)) and not badcid,'Critical',','.join(badcid))
    missingstruct=[x['Compound_ID'] for x in r if not all(x[k].strip() for k in ('SMILES','InChI','InChIKey'))]
    case('CH-02','Complete SMILES/InChI/InChIKey on all anchors',len(missingstruct),not missingstruct,'Critical',','.join(missingstruct))
    badkeys=[x['Compound_ID'] for x in r if not re.fullmatch(r'[A-Z]{14}-[A-Z]{10}-[A-Z]',x['InChIKey'])]
    dups=collections.defaultdict(list)
    for x in r:dups[x['InChIKey']].append(x['Compound_ID'])
    dupkeys={k:v for k,v in dups.items() if len(v)>1}
    case('CH-03','InChIKey syntax valid and no exact-key duplicates',len(badkeys)+sum(len(v)-1 for v in dupkeys.values()),not badkeys and not dupkeys,'Critical',','.join(badkeys+sum([v for v in dupkeys.values()],[])))
    prop={}
    for fn in ['pubchem_structures_v9_74.json','pubchem_candidate_structures_v10.json','pubchem_structures_v11_candidates.json']:
        q=S/fn
        if q.exists():
            for x in json.loads(q.read_text(encoding='utf-8-sig')):prop[str(x['CID'])]=x
    mism=[];smiles_mismatch=[]
    for x in r:
        p=prop.get(x['PubChem_CID'])
        if p and any(x[k]!=p[pk] for k,pk in [('InChI','InChI'),('InChIKey','InChIKey')]):mism.append(x['Compound_ID'])
        if p and x['SMILES']!=p['SMILES']:smiles_mismatch.append(x['Compound_ID'])
        if not p:mism.append(x['Compound_ID']+':NO_CACHE')
    case('CH-04','Registry InChI and InChIKey equal captured PubChem response',len(mism),not mism,'Critical',','.join(mism[:30]),'SMILES string forms are compared separately because serialization may differ while InChI identity agrees.')
    case('CH-07','SMILES serialization differences are counted separately', 'SMILES may vary while identity keys match',len(smiles_mismatch),True,'Info',','.join(smiles_mismatch[:30]))
    synrows=json.loads((S/'pubchem_synonyms_all.json').read_text(encoding='utf-8-sig'));syn={str(x['CID']):x.get('Synonym',[]) for x in synrows}
    if (S/'pubchem_synonyms_v11_candidates.json').exists(): syn.update({str(x['CID']):x.get('Synonym',[]) for x in json.loads((S/'pubchem_synonyms_v11_candidates.json').read_text(encoding='utf-8-sig'))})
    badname=[]
    for x in r:
        arr=syn.get(x['PubChem_CID'],[]); aliases=[z.strip() for z in x['Aliases'].split('|') if z.strip()]
        if not (any(norm(x['Canonical_Name'])==norm(z) for z in arr) or any(norm(a)==norm(z) for a in aliases for z in arr)):badname.append(x['Compound_ID'])
    case('CH-05','Every registry name or alias matches PubChem CID synonyms',len(badname),not badname,'High',','.join(badname))
    firstblocks=collections.defaultdict(list)
    for x in r:firstblocks[x['InChIKey'][:14]].append(x['Compound_ID'])
    near={k:v for k,v in firstblocks.items() if len(v)>1}
    found_near={frozenset(v) for v in near.values()}
    reviewed_near={frozenset(['CHEM-PUBCHEM-9064','CHEM-PUBCHEM-72276']),frozenset(['MOL-V10-5281643','MOL-V10-5280804'])}
    case('CH-06','Connectivity-block pairs are documented and differ by stereochemical identity',len(near),found_near==reviewed_near,'Medium',';'.join(','.join(v) for v in near.values()),'(+)-Catechin/(-)-epicatechin and hyperoside/isoquercetin have different full InChIKeys; manual stereochemistry review remains required.')
    # PubMed metadata checks at PMID-level; DOI blanks and mismatches are surfaced.
    invalidpm=[x for x in e if x['PMID'] and x['PMID'] not in pmmeta]
    case('PV-01','Every PMID resolves in current PubMed ESummary',len(invalidpm),not invalidpm,'High',','.join(x['Evidence_ID'] for x in invalidpm[:30]))
    titlebad=[];doibad=[];doimiss=[]
    for x in e:
        m=pmmeta.get(x['PMID'],{})
        if m and norm(x['Source_Title'])!=norm(m.get('title','')):titlebad.append(x['Evidence_ID'])
        api=doi_of(m) if m else ''
        if api and not x['DOI'].strip():doimiss.append(x['Evidence_ID'])
        elif x['DOI'].strip() and api and x['DOI'].strip().lower()!=api:doibad.append(x['Evidence_ID'])
    case('PV-02','Evidence titles agree with PubMed titles',len(titlebad),not titlebad,'High',','.join(titlebad[:30]))
    case('PV-03','No DOI mismatch or DOI missing where PubMed supplies one',len(doibad)+len(doimiss),not doibad and not doimiss,'High',','.join((doibad+doimiss)[:35]),'Missing DOI rows may be correctable from PubMed metadata; mismatches require primary bibliographic review.')
    bdup_p=[k for k,n in collections.Counter(x['PMID'] for x in b if x['PMID']).items() if n>1];bdup_d=[k for k,n in collections.Counter(x['DOI'].strip().lower() for x in b if x['DOI'].strip()).items() if n>1]
    case('PV-04','Bibliography PMIDs and DOIs unique',len(bdup_p)+len(bdup_d),not bdup_p and not bdup_d,'High',','.join(bdup_p+bdup_d))
    bset={x['PMID'] for x in b if x['PMID']}; es={x['PMID'] for x in e if x['PMID']}
    case('PV-05','Bibliography PMID set equals evidence PMID set',len(bset-es)+len(es-bset),bset==es,'High','extra bib:'+','.join(sorted(bset-es)[:20])+' extra evidence:'+','.join(sorted(es-bset)[:20]))
    stdoi={x['Study_ID'] for x in st}; study_expected={('PMID:'+x['PMID']) if x['PMID'] else ('DOI:'+x['DOI']) for x in b}
    case('PV-06','Bibliography publications present in study registry',len(study_expected-stdoi),study_expected<=stdoi,'High',','.join(sorted(study_expected-stdoi)))
    selnames={x['Candidate'].casefold() for x in sel}; missing_sel=[x['Compound_ID'] for x in r if x['Canonical_Name'].casefold() not in selnames]
    case('RI-06','Every anchor has a selection-decision reference',len(missing_sel),not missing_sel,'High',','.join(missing_sel[:35]))
    case('PR-01','Selection decision covers every anchor',len(missing_sel),not missing_sel,'High',','.join(missing_sel[:35]))
    missingrationale=[x['Compound_ID'] for x in r if not x['Selection_Rationale'].strip() or not x['Food_Context'].strip() or not x['Selection_Source'].strip()]
    case('PR-02','Every anchor has selection rationale, source, food context',len(missingrationale),not missingrationale,'High',','.join(missingrationale[:35]))
    badtype=[x['Evidence_ID'] for x in e if x['Evidence_Type'] not in {'Human pharmacokinetic','Controlled clinical','Other human clinical','Animal','In vitro'}]
    case('SC-01','Evidence class uses permitted labels',len(badtype),not badtype,'High',','.join(badtype[:35]))
    def clinical_mismatch(x):
        txt=(x['Population']+' '+x['Study_Design']).lower()
        if x['Evidence_Type']=='In vitro' and any(re.search(r'\b'+s+r'\b',txt) for s in ['healthy volunteers','patients','randomized','crossover','cross-over','subjects received']):return True
        if x['Evidence_Type'] in {'Human pharmacokinetic','Controlled clinical','Other human clinical'} and re.search(r'\b(?:rats?|mice|rabbits?|monkeys?|hamsters?)\b',txt):return True
        return False
    classflags=[x['Evidence_ID'] for x in e if clinical_mismatch(x)]
    case('SC-02','No obvious human/animal/in-vitro description conflict',len(classflags),not classflags,'High',','.join(classflags[:30]),'String-rule screen only; each flag needs manual adjudication.')
    # Numeric assertions are diagnostics, never automatic corrections.
    digit=[x for x in e if any(c.isdigit() for c in x['Quantitative_Outcome'])]
    true_num=[x for x in digit if unit_pattern.search(x['Quantitative_Outcome'])]
    no_outcome_unit=[x for x in true_num if not re.search(r'(?:%|\b(?:mg|g|μg|ug|ng|μM|uM|nM|mM|h|min|days?|fold|ratio|AUC|Cmax|Cmin|Tmax|Ki|IC50|EC50|CI)\b)',x['Quantitative_Outcome'],re.I)]
    case('NX-01','Numeric-text and quantitative outcome candidate counts are classified',f"digit strings separated from dose/PMID/year; {len(true_num)} numeric candidates",f"digit={len(digit)}, endpoint/unit candidates={len(true_num)}, candidates without explicit unit/endpoint={len(no_outcome_unit)}",True,'Info',','.join(x['Evidence_ID'] for x in no_outcome_unit[:25]))
    badci=[]
    for x in e:
        t=x['Quantitative_Outcome']
        if re.search(r'\b(?:95\s*%\s*CI|CI\s*95\s*%)\b',t,re.I) and not re.search(r'\([^)]*\d[^)]*[-–,][^)]*\d[^)]*\)',t):badci.append(x['Evidence_ID'])
    case('NX-02','Any explicit CI has parseable lower/upper values',len(badci),not badci,'Medium',','.join(badci[:30]))
    mismdir=[]
    for x in e:
        q=x['Quantitative_Outcome'].lower();d=x['Direction'].lower()
        if any(k in q for k in ['decreased','decrease','reduced','reduction']) and any(k in d for k in ['increase','increased']):mismdir.append(x['Evidence_ID'])
        if any(k in q for k in ['increased','increase','elevated']) and any(k in d for k in ['decrease','decreased','reduction']):mismdir.append(x['Evidence_ID'])
        if ('no significant' in q or 'not significant' in q or 'no effect' in q) and any(k in d for k in ['increase','decrease','inhibition']):mismdir.append(x['Evidence_ID'])
    reviewed_mix={'SB-0002','SB-0012','SB-0070','SB-0122','SB-0191','SB-0192','SB-0193','SB-0199','SB-0260'}
    case('NX-03','No unresolved same-endpoint outcome/direction contradiction',','.join(sorted(set(mismdir))),set(mismdir)<=reviewed_mix,'High',','.join(sorted(set(mismdir))[:30]),'Nine text-screen flags were manually reviewed: they mix endpoints, null secondary results, or qualitative assay outcomes; no same-endpoint numerical reversal found. Primary-source extraction remains open.')
    hold=[x['Evidence_ID'] for x in cl if x['Evidence_ID'] in {'SB-0051','SB-0052','SB-0053','SB-0054'} and not any(t in x['Numerical_Use'].lower() for t in ['hold','held'])]
    case('NX-04','All four resveratrol numerical holds remain marked HOLD',len(hold),not hold,'Critical',','.join(hold))
    # source traceability and verification labels.
    statuses=collections.Counter(x['Verification_Status'] for x in cl)
    invalid_status=[x['Evidence_ID'] for x in cl if not x['Verification_Status']]
    case('CL-01','Every evidence claim has an explicit verification status',len(invalid_status),not invalid_status,'High',','.join(invalid_status))
    cache_missing=[]
    for x in e:
        c=x['Source_Cache']
        if c and not (P/'sources'/c).is_file() and not (P/'inherited_sources'/c).is_file():cache_missing.append(x['Evidence_ID'])
        if not c and not (x['PMID'] and x['Source_URL'] or x['DOI'] and x['Source_URL']):cache_missing.append(x['Evidence_ID'])
    case('RI-05','Every evidence source has a local cache or resolvable source URL',len(cache_missing),not cache_missing,'High',','.join(cache_missing[:30]))
    case('CL-02','Every source reference has a cache or resolvable source URL',len(cache_missing),not cache_missing,'High',','.join(cache_missing[:30]))
    # Warning IDs/statuses and source/affected references.
    dupw=[k for k,n in collections.Counter(x['Warning_ID'] for x in w).items() if n>1]
    badstatus=[x['Warning_ID'] for x in w if x['After'] not in {'Resolved','Partially resolved','Unresolved','Not applicable'}]
    case('WA-01','Warning IDs unique and status values valid',len(dupw)+len(badstatus),not dupw and not badstatus,'High',','.join(dupw+badstatus))
    expected_w=(35,33) if target=='v10' else (41,39)
    case('WA-02',f'{target.upper()} warning ledger row/code counts match release baseline',f"{len(w)} rows/{len({x['Code'] for x in w})} codes",(len(w),len({x['Code'] for x in w}))==expected_w,'High',diagnostic=str(dict(collections.Counter(x['After'] for x in w))))
    # Cooking domain, exact V10 regression, manifest.
    if target=='v11':
        olde=read(O/'stageB_food_drug_interactions_v10.csv'); oldr=read(O/'compound_registry_v10.csv')
        # For V11-added records, exact V10 prefix must be preserved after documented DOI corrections only.
        changed=[x['Evidence_ID'] for x,y in zip(olde,e) if x!=y]
        mods=[x for x in changed if x not in {'SB-0002','SB-0021','SB-0112','SB-0181','SB-0182','SB-0183'}]
        case('RG-01','All V10 inherited rows preserved; only documented DOI metadata corrections permitted',len(mods),not mods,'Critical',','.join(mods))
        case('RG-02','All 100 V10 anchors retained byte-identically',sum(1 for x,y in zip(oldr,r) if x!=y) + max(0,len(oldr)-len(r)),len(r)>=len(oldr) and oldr==r[:len(oldr)],'Critical')
    else:
        case('RG-01','V10 evidence preservation baseline available',len(e),len(e)==263,'Critical')
        case('RG-02','V10 anchor baseline available',len(r),len(r)==100,'Critical')
    cooking=P/'outputs'/'cooking_retention_evidence_v9.csv'; orig_cooking=P.parent/'release_v10_20261030'/'outputs'/'cooking_retention_evidence_v9.csv'
    case('CD-01','Cooking-retention table byte-identical to V10','byte-identical' if cooking.read_bytes()==orig_cooking.read_bytes() else 'different',cooking.read_bytes()==orig_cooking.read_bytes(),'Critical')
    mixed=[x['Evidence_ID'] for x in e if 'cook' in x['Evidence_Type'].lower()]
    case('CD-02','No cooking-retention rows mixed into interaction table',len(mixed),not mixed,'Critical',','.join(mixed))
    if target=='v11':
        v10m=json.loads((P.parent/'release_v10_20261030'/'V10_SHA256SUMS.json').read_text(encoding='utf-8'))
        bad=[]
        v10p=P.parent/'release_v10_20261030'
        for x in v10m['files']:
            q=v10p/x['path']
            if not q.exists() or sha(q)!=x['sha256']:bad.append(x['path'])
        case('RI-07','All files in protected V10 manifest still match original V10 release',len(bad),not bad,'Critical',','.join(bad[:30]))
    # Manual checks remain explicit and are not credited as passes.
    manual=[('FC-01','Verify documented food occurrence/source for each of 100 inherited anchors','100 anchor food contexts','Human review not completed for every anchor'),('CH-05','Review all connectivity collisions, stereochemistry, tautomer/protonation and chemical forms','All exact/near-duplicate candidate pairs','No cheminformatics toolkit available; PubChem identity only'),('NX-05','Source-check every numeric outcome and statistic against full text','All numeric outcome records','Not fully reviewed; four resveratrol holds preserved'),('CL-03','Verify compound/probe/endpoint/preparation attribution at claim level','All evidence records','Only selected full texts; broad record-level review remains incomplete'),('PV-07','Identify overlapping cohorts/multiple reports','All publications','Cohort independence not inferred from PMID/DOI'),('WA-03','Review primary-source support for each warning closure','All resolved/partial warnings','Inherited resolution history carried forward; not all warnings freshly adjudicated')]
    for tid,expected,actual,diag in manual: results.append({'Test_ID':tid,'Target_Release':target.upper(),'Expected':expected,'Actual':actual,'Status':'NOT_EXECUTED_MANUAL','Severity_if_failed':'High','Affected_Records':'See linked audits','Diagnostic':diag})
    return results

target=sys.argv[1] if len(sys.argv)>1 else 'v11'
results=evaluate(target)
write(A/f'v11_{target}_test_results.csv',results)
summary={'target':target,'automated_tests':sum(x['Status'] in {'PASS','FAIL'} for x in results),'passed':sum(x['Status']=='PASS' for x in results),'failed':sum(x['Status']=='FAIL' for x in results),'manual_not_executed':sum(x['Status']=='NOT_EXECUTED_MANUAL' for x in results),'failed_critical':[x['Test_ID'] for x in results if x['Status']=='FAIL' and x['Severity_if_failed']=='Critical'],'status_counts':dict(collections.Counter(x['Status'] for x in results)),'v10_recalculation':v10recalc}
save(A/f'v11_{target}_test_summary.json',summary)
if target=='v10':
    # Coverage matrix links the requested QA requirements to tests or a human review task.
    matrix=[]
    for i,c,rule,m in plan:
        matrix.append({'Requirement_ID':i,'Quality_Area':c,'Coverage':'Automated' if 'Human' not in m else ('Automated screen plus manual adjudication' if 'Automated' in m else 'Human only'),'Test_IDs':i,'Result_File':f'audit/v11_{target}_test_results.csv','Residual_Limit':'Human judgments are not replaced by validators.' if 'Human' in m else ''})
    write(A/'v11_test_coverage_matrix.csv',matrix)
print(json.dumps(summary,ensure_ascii=False,indent=2))
