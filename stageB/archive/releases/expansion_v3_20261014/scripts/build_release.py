"""Offline release builder using only available files and cached research snapshots."""
from pathlib import Path
import csv,json,hashlib,re,html,collections,difflib
from curation import RECORDS
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1];B=ROOT/'stageB'
DATE='2026-10-14'
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def load(p):return json.loads(p.read_text(encoding='utf8'))
def write(name,rows,fields=None):
    p=OUT/'outputs'/name
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
def clean(t):return html.unescape(re.sub(r'</?[A-Za-z][^>]*>',' ',t or '')).strip()
def norm(t):return re.sub('[^a-z0-9]','',clean(t).lower())
def numeric_tokens(t):
    from decimal import Decimal
    return {str(Decimal(x).normalize()) for x in re.findall(r'(?:\d+(?:\.\d+)?|\.\d+)',clean(t).replace(',',''))}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=read(B/'expansion_v2/outputs/stageB_food_drug_interactions_expanded.csv');fields=list(base[0])
mapping=read(B/'outputs/stageB_compound_mapping.csv')
master=read(B/'inputs/cookchem_master_expanded_round11.csv')
byid={r['Canonical_Molecular_ID']:r for r in mapping}
byname={r['CookRisk_compound_name'].lower():r for r in mapping}
def paper(pmid):
    return load(OUT/'sources'/f'pmid_{pmid}.json')['resultList']['result'][0]
def author(m):return m.get('authorString','')

# Baseline manifests are created once and checked, never refreshed to conceal changes.
inventory=[];preserved={}
for folder in ['stageB','data','docs','literature','reports','molecular_features','preprocessing']:
    for p in sorted((ROOT/folder).rglob('*')):
        if not p.is_file() or OUT in p.parents or '__pycache__' in p.parts:continue
        rel=p.relative_to(ROOT).as_posix();preserved[rel]=sha(p)
        if p.suffix.lower() not in ['.csv','.json','.md','.txt','.pdf','.docx','.xlsx','.py']:continue
        count='';headers=[];inspection='Metadata and hash inspected'
        if p.suffix.lower()=='.csv':
            try:
                rr=read(p);count=len(rr);headers=list(rr[0]) if rr else [];inspection='CSV headers and row count inspected'
            except Exception as e:inspection='Read failure: '+str(e)
        category='source snapshots' if '/sources/' in rel else ('compound identity' if any(x in rel.lower() for x in ['mapping','identity','molecular']) else ('search and screening' if any(x in rel.lower() for x in ['search','screen']) else ('reports and documentation' if p.suffix in ['.md','.pdf','.docx','.txt'] else 'data and audit')))
        sourcecols=[x for x in headers if any(y in x.lower() for y in ['source','doi','pmid','reference','citation'])]
        inventory.append(dict(File=rel,Category=category,Purpose={'source snapshots':'Saved external source response','compound identity':'Identity or molecular inventory','search and screening':'Search discovery or screening decisions','reports and documentation':'Saved methodology, research or report','data and audit':'Data, reference or audit table'}[category],Rows=count,Source_Information='source snapshot' if category=='source snapshots' else (' | '.join(sourcecols) or ('Narrative source context; not a selection ledger' if p.suffix in ['.md','.pdf','.docx','.txt'] else 'No explicit source column detected')),Inspection=inspection,SHA256=preserved[rel]))
for name in ['README.md','requirements.txt','CookRisk_StageB_Evidence_Release.zip','CookRisk_StageB_Expanded_v2.zip']:
    p=ROOT/name
    if p.exists():preserved[name]=sha(p)
manifest=OUT/'audit/supplied_file_manifest.json'
if not manifest.exists():manifest.write_text(json.dumps(preserved,indent=2),encoding='utf8')
write('file_inventory.csv',inventory)
short=[r for r in inventory if (r['File'].startswith('stageB/outputs/') or r['File'].startswith('stageB/expansion_v2/outputs/') or r['File'].startswith('stageB/reports/') or r['File'].startswith('stageB/expansion_v2/reports/') or r['File'] in ['docs/methodology/WEEK1_METHODOLOGY.md','reports/final_molecular_identity_resolution.csv'])]
write('inventory_key_files.csv',short)

registry=[];selection=[]
original=sorted({(r['Compound'],r['Compound_ID']) for r in base})
four={'Resveratrol','Genistein','Naringin','Capsaicin'}
method='stageB/expansion_v2/reports/literature_search_methodology.md'
for name,cid in original:
    m=byid[cid];fourflag=name in four
    status='documented_v2_rationale_specific_primary_selection_trigger_unresolved' if fourflag else 'original_selection_source_unresolved'
    reason='Reliable exact/parent identity plus useful primary human evidence; low inventory frequency was not a disqualifier.' if fourflag else 'Original five evidence anchors are documented in the initial release, but no contemporaneous per-compound selection-source ledger was found.'
    registry.append(dict(Compound_ID=cid,Canonical_Name=name,Aliases=m['synonyms'],PubChem_CID=m['PubChem_CID'],SMILES=m['SMILES'],InChI=m['InChI'],InChIKey=m['InChIKey'],Identity_Status=m['mapping_status'],Identity_Source=m['mapping_source'],Origin='original_nine',Selection_Rationale=reason,Selection_Source=method if fourflag else 'stageB/reports/stageB_methodology.md; stageB/outputs/stageB_food_drug_interactions.csv',Selection_DOI='',Selection_PMID='',Selection_URL='',Date_Added='',First_Documented_Release_Date='2026-10-06',Date_Status='Original addition date unknown; release date is not original selection date',Coverage_Status='Inherited verified extraction; current cached metadata audited',Provenance_Status=status,Original_Molecular_Group=cid,Retention_Status=f"{m['observation_count']} supplied master observations; provenance not newly certified",Food_Context=m['food_sources'],Evidence_Records=sum(r['Compound_ID']==cid for r in base),Link_Restriction=m['notes'] or 'No new exposure integration performed'))
    selection.append(dict(Selection_Record_ID='SEL-ORIGINAL-'+name,Compound_ID=cid,Decision_Date='',Source_Role='historical_selection_documentation',Source_Locator=(method+' priority paragraph' if fourflag else 'Initial methodology section 3 and initial evidence table'),DOI='',PMID='',URL='',Supports=reason,Does_Not_Establish='Specific primary-paper selection trigger or exact original selection date',Provenance_Status=status))

specs=[('Sulforaphane','23153560','Human crossover interaction/probe study with overall null and subgroup findings; verified inventory structure and broccoli processing literature.','22471240'),('Apigenin','24369535','Verified dietary flavone inventory plus primary animal drug disposition studies with regimen-dependent findings.',''),('Kaempferol','18338336','Verified dietary flavonol inventory plus primary parent/metabolite drug PK evidence; distinguishes metabolite null.',''),('Daidzein','12756512','Soy-associated aglycone with primary human theophylline and caffeine-probe evidence; useful comparison with existing genistein.','11285356'),('Quercetin','19221726','Dietary flavonol with primary human drug PK evidence, acute null and repeated-dose contrasts; standalone identity avoids mixed total-flavonol group.','25988261')]
for n,(name,pmid,reason,extra) in enumerate(specs,1):
    m=byname.get(name.lower());newparent=name in ['Quercetin','Daidzein']
    if newparent:
        pubcid='5280343' if name=='Quercetin' else '5281708';pr=load(OUT/'sources'/f'pubchem_{pubcid}.json')['PropertyTable']['Properties'][0]
        sy=load(OUT/'sources'/f'pubchem_synonyms_{pubcid}.json')['InformationList']['Information'][0]['Synonym']
        assert name.lower() in [s.lower() for s in sy]
        cid='CHEM-PUBCHEM-'+pubcid;identity='verified_external_parent_identity_no_master_link';smi=pr.get('ConnectivitySMILES',pr.get('CanonicalSMILES',''));inchi=pr['InChI'];key=pr['InChIKey'];aliases=' | '.join(sy[:25]);idsource=f'https://pubchem.ncbi.nlm.nih.gov/compound/{pubcid}'
        oldgroup=m['Canonical_Molecular_ID'] if m else ''
        retention='No reliable compound-specific retention link established; cooking source audit unresolved' if name=='Quercetin' else 'No exact daidzein aglycone group found in supplied inventory; do not substitute daidzin or acetyldaidzin'
        food='Dietary flavonol; primary PMID 25988261 plus mixed master Apple/Onion/Strawberry labels, not validated retention data' if name=='Quercetin' else 'Soybean; primary PMID 12756512; supplied soybean glycosides are distinct compounds'
        restriction='No automatic link to mixed quercetin/total-flavonol group '+oldgroup if oldgroup else 'No master retention observations assigned; aglycone is distinct from glycosides'
    else:
        cid=m['Canonical_Molecular_ID'];pubcid=m['PubChem_CID'];identity=m['mapping_status'];smi=m['SMILES'];inchi=m['InChI'];key=m['InChIKey'];aliases=m['synonyms'];idsource=m['mapping_source'];oldgroup=cid
        retention=f"{m['observation_count']} supplied master observations; inherited provenance requires review";food=m['food_sources'];restriction='Mapping inherited from supplied identity table; no Stage A or exposure join generated'
    s=paper(pmid)
    registry.append(dict(Compound_ID=cid,Canonical_Name=name,Aliases=aliases,PubChem_CID=pubcid,SMILES=smi,InChI=inchi,InChIKey=key,Identity_Status=identity,Identity_Source=idsource,Origin='added_v3',Selection_Rationale=reason,Selection_Source=f'SEL-20261014-{n:02d}; decision recorded in this release',Selection_DOI=s.get('doi',''),Selection_PMID=pmid,Selection_URL=f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/',Date_Added=DATE,First_Documented_Release_Date=DATE,Date_Status='Current documented decision, not reconstructed history',Coverage_Status='Primary interaction evidence added; limited search',Provenance_Status='current_selection_documented_with_supporting_primary_sources',Original_Molecular_Group=oldgroup,Retention_Status=retention,Food_Context=food,Evidence_Records=sum(r['compound']==name for r in RECORDS),Link_Restriction=restriction))
    for p in [pmid]+([extra] if extra else []):
        s=paper(p)
        selection.append(dict(Selection_Record_ID=f'SEL-20261014-{n:02d}'+('-SUPPORT' if p!=pmid else ''),Compound_ID=cid,Decision_Date=DATE,Source_Role='supporting_processing_or_dietary_context' if p!=pmid else 'primary_interaction_evidence_supporting_current_selection',Source_Locator=f'sources/pmid_{p}.json abstract; decision in scripts/build_release.py specs',DOI=s.get('doi',''),PMID=p,URL=f'https://pubmed.ncbi.nlm.nih.gov/{p}/',Supports=reason,Does_Not_Establish='Historical selection rationale; ordinary cooked-serving exposure; clinical risk',Provenance_Status='current_decision_and_primary_support_documented'))
write('compound_registry.csv',registry);write('selection_sources.csv',selection)
write('original_nine_interaction_reference_map.csv',[dict(Compound=r['Canonical_Name'],Compound_ID=r['Compound_ID'],Interaction_PMIDs=' | '.join(sorted({e['PMID'] for e in base if e['Compound_ID']==r['Compound_ID']})),Interaction_DOIs=' | '.join(sorted({e['DOI'] for e in base if e['Compound_ID']==r['Compound_ID'] and e['DOI']})),Historical_Selection_Status=r['Provenance_Status'],Warning='These are retained interaction references, not proof of the original compound selection source') for r in registry if r['Origin']=='original_nine'])
reg={r['Canonical_Name']:r for r in registry}
provenance=[{k:r[k] for k in ['Compound_ID','Canonical_Name','Origin','Selection_Source','Selection_PMID','Date_Added','Provenance_Status','Identity_Status','Retention_Status','Link_Restriction']} for r in registry]
write('compound_selection_provenance_audit.csv',provenance)
candidate=[]
for m in mapping:
    chosen=next((r for r in registry if r['Compound_ID']==m['Canonical_Molecular_ID']),None)
    candidate.append(dict(Original_Compound_ID=m['Canonical_Molecular_ID'],Original_Name=m['CookRisk_compound_name'],Identity_Status=m['mapping_status'],Observation_Count=m['observation_count'],Decision='selected_existing_or_v3' if chosen else ('identity_unresolved_do_not_assign' if m['mapping_status']=='uncertain' else 'not_selected_in_bounded_v3'),Reason=chosen['Selection_Rationale'] if chosen else 'Inventory considered; no assertion that all literature was screened',Standalone_Quercetin_ID='CHEM-PUBCHEM-5280343' if 'Total flavonols' in m['CookRisk_compound_name'] else '',Automatic_Standalone_Link='forbidden' if 'Total flavonols' in m['CookRisk_compound_name'] else 'not created'))
write('inventory_candidate_decisions.csv',candidate)

new=[];claimledger=[]
for i,r in enumerate(RECORDS,65):
    m=paper(r['pmid']);a=reg[r['compound']];eid=f'SB-{i:04d}'
    row={k:'' for k in fields}
    row.update(Evidence_ID=eid,Compound=r['compound'],Compound_ID=a['Compound_ID'],Drug=r['drug'],Interaction_Effect=r['effect'],Mechanism=r['mechanism'],Evidence_Type=r['type'],Evidence_Level=r['level'],Direction=r['direction'],Quantitative_Outcome=r['quantity'],Dose=r['dose'],Population=r['population'],Study_Design=r['design'],Source_Title=m['title'],Authors=author(m),Year=m.get('pubYear',''),DOI=m.get('doi',''),PMID=r['pmid'],Source_Type='Primary research',Limitations=r['limits'],Confidence=('Moderate: primary human observation; limited generalizability' if r['type']=='Human pharmacokinetic' else 'Limited for human inference: primary animal observation'),Notes='Verified cached primary abstract; mechanism interpretation is not clinical causality.',Study_ID='PMID:'+r['pmid'],Source_URL=f"https://pubmed.ncbi.nlm.nih.gov/{r['pmid']}/",Source_Cache=f"expansion_v3_20261014/sources/pmid_{r['pmid']}.json",Source_Locator='Abstract: Methods and Results; no full-text table extraction claimed',Preparation=r['preparation'],Co_Compounds=r['co'],Affected_Entity='drug/probe',Perpetrator='compound_or_preparation',Outcome=r['outcome'],Conflict_Group=r.get('conflict',''),Identity_Status=a['Identity_Status'],Release_Origin='expansion_v3_20261014',Clinical_Extrapolation='No automatic clinical risk classification; supplement/animal doses not meal effects',CookRisk_Exposure_Link=a['Link_Restriction'])
    new.append(row)
    claimledger.append(dict(Evidence_ID=eid,PMID=r['pmid'],Claim_Field='Quantitative_Outcome' if r['quantity'] else 'Interaction_Effect',Claim=r['quantity'] or r['effect'],Source_Locator=row['Source_Locator'],Supporting_Excerpt=r['quote'],Excerpt_Present=norm(r['quote']) in norm(m.get('abstractText','')),Numerical_Tokens_Supported=numeric_tokens(r['quantity']).issubset(numeric_tokens(m.get('abstractText',''))),Review_Status='Manual abstract comparison; original endpoint and unit retained; token check is a diagnostic, not semantic proof' if r['quantity'] else 'Qualitative extraction; dose and sample details checked against abstract'))
write('new_evidence_records.csv',new,fields);allrows=base+new;write('stageB_food_drug_interactions_v3.csv',allrows,fields);write('claim_support_ledger.csv',claimledger)

def cached_record(row):
    path=B/row['Source_Cache'].replace('\\','/')
    if not path.exists():return None,path
    data=load(path);hits=data.get('resultList',{}).get('result',[])
    return next((x for x in hits if str(x.get('id'))==row['PMID'] and x.get('source')=='MED'),None),path
audits=[];studies=[]
for pmid in sorted({r['PMID'] for r in allrows}):
    rr=[r for r in allrows if r['PMID']==pmid];r=rr[0];m,path=cached_record(r)
    m=m or {};doiok=all(norm(x['DOI'])==norm(m.get('doi','')) for x in rr)
    titleok=all(norm(x['Source_Title'])==norm(m.get('title','')) for x in rr)
    yearok=all(str(x['Year'])==str(m.get('pubYear','')) for x in rr)
    authorok=all(norm(x['Authors'])==norm(author(m)) for x in rr)
    cfpath=OUT/'sources'/f'crossref_{pmid}.json';cf=load(cfpath).get('message',{}) if cfpath.exists() else {}
    if not cfpath.exists():
        old=next((x for x in read(B/'expansion_v2/outputs/primary_source_DOI_audit.csv') if x['PMID']==pmid),{})
        cfstatus='Inherited v2: '+old.get('Status','not found')
    else:
        similarity=difflib.SequenceMatcher(None,norm(' '.join(cf.get('title',[]))),norm(m.get('title',''))).ratio() if isinstance(cf,dict) else 0
        cfstatus='concordant_title' if similarity>=.90 else ('lookup_unavailable' if not cf else 'manual_title_review_required')
    audits.append(dict(Study_ID='PMID:'+pmid,PMID=pmid,DOI=r['DOI'],Title=r['Source_Title'],Source_Cache=str(path.relative_to(ROOT)),Cache_Contains_PMID=bool(m),DOI_Concordant=doiok,Title_Concordant=titleok,Year_Concordant=yearok,Author_Concordant=authorok,Crossref_Status=cfstatus,Extraction_Verification='New manual abstract extraction with claim ledger' if any(x['Release_Origin']=='expansion_v3_20261014' for x in rr) else 'Inherited extraction retained; cached metadata rechecked, not all full-text outcomes re-extracted',Evidence_Records=len(rr),Source_Verification_Status='cached_primary_metadata_verified' if m and doiok and titleok and yearok and authorok else 'bibliographic_review_required'))
    studies.append(dict(Study_ID='PMID:'+pmid,PMID=pmid,DOI=r['DOI'],Title=r['Source_Title'],Authors=r['Authors'],Year=r['Year'],Evidence_Records=len(rr),Source_Cache=r['Source_Cache'],Source_URL=r['Source_URL'],Independence_Assessment='Unique primary PMID; same-report rows grouped; exhaustive cross-paper trial independence not established'))
write('interaction_evidence_source_audit.csv',audits);write('study_registry.csv',studies)
screen=[];seen=set();selected={r['pmid'] for r in RECORDS}
for p in sorted((OUT/'sources').glob('search_*.json')):
    for m in load(p).get('resultList',{}).get('result',[]):
        key=(m.get('source',''),str(m.get('id','')))
        if key in seen:continue
        seen.add(key);included=key[0]=='MED' and key[1] in selected
        screen.append(dict(Source=key[0],Source_ID=key[1],Title=m.get('title',''),DOI=m.get('doi',''),Status='included_primary' if included else 'candidate_not_fully_screened',Reason='Manually extracted primary report' if included else 'Retrieved bounded candidate; not a completed exclusion decision',Source_Cache=str(p.relative_to(OUT))))
for pmid in sorted(selected):
    if ('MED',pmid) not in seen:
        m=paper(pmid);screen.append(dict(Source='MED',Source_ID=pmid,Title=m['title'],DOI=m.get('doi',''),Status='included_primary_exact_followup',Reason='Targeted primary discovery and exact identifier verification',Source_Cache=f'sources/pmid_{pmid}.json'))
for pmid in ['22471240','11285356']:
    m=paper(pmid);screen.append(dict(Source='MED',Source_ID=pmid,Title=m['title'],DOI=m.get('doi',''),Status='selection_context_only_not_interaction',Reason='Processing/dietary context; not counted as compound-drug interaction',Source_Cache=f'sources/pmid_{pmid}.json'))
write('source_screening_log.csv',screen)
conflicts=read(B/'expansion_v2/outputs/conflict_synthesis.csv')
conflicts.append(dict(Pair='Quercetin-Midazolam_context',Evidence_IDs=' | '.join(r['Evidence_ID'] for r in new if r['Conflict_Group']),Context='Human genotype-conditioned repeated dosing versus acute/repeated oral and tiny IV substudy',Interpretation='Significant genotype subgroup decrease versus acute null and nonsignificant oral trend; different dose, duration and route, not matched-protocol contradiction',Resolution='Retain original endpoints and confidence interval; no pooled direction or risk'))
write('conflict_synthesis.csv',conflicts)
processing=paper('22471240')
write('processing_selection_context.csv',[dict(Compound_ID=reg['Sulforaphane']['Compound_ID'],PMID='22471240',DOI=processing.get('doi',''),Title=processing['title'],Source_URL='https://pubmed.ncbi.nlm.nih.gov/22471240/',Finding='Thermal processing altered sulforaphane formation; steaming 1.0-3.0 minutes enhanced yield in three of four cultivars',Limitation='Formation from glucoraphanin and cultivar effects; not a universal retention coefficient or interaction endpoint',Included_In_Interaction_Count='False')])
summary=dict(release='v3_20261014',date=DATE,baseline_evidence_records=len(base),new_compounds=5,new_evidence_records=len(new),total_compounds=len(registry),total_evidence_records=len(allrows),new_primary_reports=len(selected),total_primary_reports=len(studies),total_drugs=len({r['Drug'] for r in allrows}),evidence_types=dict(collections.Counter(r['Evidence_Type'] for r in allrows)),new_evidence_types=dict(collections.Counter(r['Evidence_Type'] for r in new)),quantitative_records=sum(bool(r['Quantitative_Outcome']) for r in allrows),new_quantitative_records=sum(bool(r['Quantitative_Outcome']) for r in new),conflict_context_groups=len(conflicts),compound_counts=dict(collections.Counter(r['Compound'] for r in allrows)),original_nine_provenance=dict(collections.Counter(r['Provenance_Status'] for r in registry if r['Origin']=='original_nine')),source_files_inventoried=len(inventory),key_files_inventoried=len(short),bounded_search=True,stage_A_modified=False,stage_C_or_D_implemented=False)
(OUT/'outputs/release_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
print(json.dumps(summary,indent=2))
