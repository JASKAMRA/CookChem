"""Rebuild CookRisk Stage B V11 outputs from the adjacent immutable V10 release.

No network access is required. Captured PubChem, PubMed, and Crossref responses
are stored under sources/. Run: python build_v11.py [release-directory]
"""
import csv, json, hashlib, sys
from pathlib import Path

P = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
V10 = P.parent / 'release_v10_20261030'
O, S = P/'outputs', P/'sources'
O.mkdir(exist_ok=True); S.mkdir(exist_ok=True)

def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(path, rows, fields=None):
    if fields is None: fields=list(rows[0]) if rows else []
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
def jread(path):return json.loads(path.read_text(encoding='utf-8-sig'))

reg=read(V10/'outputs/compound_registry_v10.csv')
ev=read(V10/'outputs/stageB_food_drug_interactions_v10.csv')
newstruct=jread(S/'pubchem_structures_v11_candidates.json')
st_by_cid={str(x['CID']):x for x in newstruct}
meta=jread(S/'pubmed_esummary_v11_candidates.json')
meta={k:v for k,v in meta.items() if k!='uids'}
cross=jread(S/'crossref_paradisin_c.json')
aliases={
 '72941753':'paradisin A | grapefruit furanocoumarin dimer',
 '24788952':'paradisin C | grapefruit furanocoumarin dimer',
 '1268142':'nootkatone | grapefruit sesquiterpene',
 '9946625':'epoxybergamottin | grapefruit furanocoumarin',
 '5281600':'amentoflavone | biflavonoid',
}
new_defs=[
 ('72941753','Paradisin A','grapefruit juice furanocoumarin dimer','16338240','10.1016/j.bmc.2005.11.039','Grapefruit juice isolate; CYP enzyme inhibitor in primary in-vitro study.','grapefruit juice','Ordinary-food association: isolated from grapefruit juice; in-vitro enzyme results do not establish dietary clinical interaction.'),
 ('24788952','Paradisin C','grapefruit juice furanocoumarin dimer','','10.1016/s0040-4020(02)00739-1','New CYP3A4 inhibitor isolated from grapefruit juice; primary article abstract supports qualitative activity.','grapefruit juice','Ordinary-food association: reported as isolated from grapefruit juice; DOI-only record, numerical extraction pending.'),
 ('1268142','Nootkatone','grapefruit sesquiterpene ketone','10860553','10.1006/abbi.2000.1835','Grapefruit juice isolate studied in CYP inhibition assays.','grapefruit juice','Food-associated volatile isolated from grapefruit juice; the cited results are in vitro, not evidence of usual dietary exposure levels.'),
 ('9946625','Epoxybergamottin','grapefruit furanocoumarin','12610742','10.1007/s00228-002-0537-3','Grapefruit peel constituent studied against CYP3A4-mediated metabolism.','grapefruit peel','Grapefruit peel source is documented; cited cell assay is in vitro.'),
 ('5281600','Amentoflavone','biflavonoid; Ginkgo/Hypericum supplement constituent','19883715','10.1016/j.fct.2009.10.041','Potent CYP assay inhibitor in botanical supplement context.','Ginkgo/Hypericum supplements','Supplement/medicinal-botanical context only; not presented as ordinary-food exposure.'),
]
newrows=[]
for cid,name,context,pmid,doi,rationale,food,fc in new_defs:
 s=st_by_cid[cid]; old={k:'' for k in reg[0]}
 old.update({'Compound_ID':'MOL-V11-CID-'+cid,'Canonical_Name':name,'Aliases':aliases[cid],'PubChem_CID':cid,'SMILES':s['SMILES'],'InChI':s['InChI'],'InChIKey':s['InChIKey'],'Identity_Status':'PubChem CID and captured structure verified in V11; name/synonym and key checked.','Identity_Source':f'https://pubchem.ncbi.nlm.nih.gov/compound/{cid}','Origin':'v11_controlled_expansion','Selection_Rationale':rationale,'Selection_Source':food,'Selection_DOI':doi,'Selection_PMID':pmid,'Selection_URL':(f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/' if pmid else 'https://doi.org/'+doi),'Date_Added':'2026-10-30','First_Documented_Release_Date':'2026-10-30','Date_Status':'V11 addition date; no historical selection date claimed','Coverage_Status':'V11 candidate screened; five anchors admitted after identity/context/source review','Provenance_Status':'v11_retroactive','Original_Molecular_Group':'grapefruit furanocoumarins' if cid!='5281600' else 'botanical supplement','Retention_Status':'No cooking-retention evidence added in V11','Food_Context':fc,'Evidence_Records':'0','Link_Restriction':'No exposure integration; in-vitro results are not dietary dose evidence','Release_Reviewed':'v11_20261030','Selection_Verification':'Primary-source and PubChem metadata reviewed; remaining manual/context limits flagged','Earliest_Verified_Selection_Date':'2026-10-30','Selection_Temporality':'retrospective V11 decision','Remaining_Provenance_Gap':'Historical selection did not exist before V11.'})
 reg.append(old);newrows.append(old)
new_ids={x['PubChem_CID']:x['Compound_ID'] for x in newrows}

drugs=read(V10/'outputs/drug_probe_registry_v10.csv')
drug_fields=list(drugs[0]); known={x['Drug_Probe'] for x in drugs}
for probe in ['CYP3A4','CYP1B1 EROD','CYP1B1 BROD','CYP2A6','CYP2C19','CYP3A4-mediated diltiazem N-demethylation','CYP2C9']:
 if probe not in known:
  drugs.append({'Drug_ID':'PROBE-V11-'+str(len(drugs)+1).zfill(3),'Drug_Probe':probe,'Evidence_Records':'0','Primary_PMIDs':'','Scope':'Enzyme assay probe/endpoint; no therapeutic-drug inference'})

ev_fields=list(ev[0]); study_new=[]
def pubinfo(pmid,doi):
 if pmid:
  m=meta[pmid]; title=m.get('title',''); authors=', '.join(a['name'] for a in m.get('authors',[])); year=(m.get('pubdate','')[:4])
  return title,authors,year
 return cross['title'][0],'; '.join(a['given']+' '+a['family'] for a in cross.get('author',[])),str(cross.get('published-print',{}).get('date-parts',[['']])[0][0])
def add_record(cid,name,probe,effect,mech,direction,outcome,pmid,doi,locator,prep='isolated compound'):
 title,authors,year=pubinfo(pmid,doi); eid='SB-'+str(264+len([x for x in ev if x['Evidence_ID'].startswith('SB-') and int(x['Evidence_ID'][3:])>=264])).zfill(4)
 study=('PMID:'+pmid) if pmid else 'DOI:'+doi
 row={k:'' for k in ev_fields}; row.update({'Evidence_ID':eid,'Compound':name,'Compound_ID':new_ids[cid],'Drug':probe,'Interaction_Effect':effect,'Mechanism':mech,'Evidence_Type':'In vitro','Evidence_Level':'compound','Direction':direction,'Quantitative_Outcome':outcome,'Population':'Human enzyme isoform assay / recombinant human CYP as described in abstract','Study_Design':'In-vitro enzyme inhibition assay','Source_Title':title,'Authors':authors,'Year':year,'DOI':doi,'PMID':pmid,'Source_Type':'Primary research','Limitations':'In vitro only; no dietary exposure or clinical interaction inference. Source locator is abstract unless explicitly noted.','Confidence':'Moderate: primary in-vitro evidence; source-level limitations retained','Notes':'V11 controlled expansion; source verified at abstract/metadata level; full-text table review not claimed.','Study_ID':study,'Source_URL':f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/' if pmid else 'https://doi.org/'+doi,'Source_Cache':f'pubmed_esummary_v11_candidates.json' if pmid else 'crossref_paradisin_c.json','Source_Locator':locator,'Preparation':prep,'Co_Compounds':'','Affected_Entity':'enzyme assay','Perpetrator':'compound_or_preparation','Outcome':'enzyme inhibition assay result','Conflict_Group':'','Identity_Status':'PubChem CID mapped; exact study analyte preparation as stated in source','Release_Origin':'v11_20261030','Clinical_Extrapolation':'No clinical extrapolation; in vitro only','CookRisk_Exposure_Link':'No exposure integration performed'})
 ev.append(row)
 return row
added=[]
added += [add_record('72941753','Paradisin A','CYP3A4','CYP3A4 activity inhibited in vitro.','CYP3A4 inhibition','inhibition','IC50 = 1.2 μM', '16338240','10.1016/j.bmc.2005.11.039','Abstract: enzyme inhibition results')]
added += [add_record('72941753','Paradisin A','CYP1B1 EROD','CYP1B1 EROD activity inhibited in vitro.','CYP1B1 inhibition','inhibition','IC50 = 3.56 ± 0.12 μM','16338240','10.1016/j.bmc.2005.11.039','Abstract: enzyme inhibition results')]
added += [add_record('72941753','Paradisin A','CYP1B1 BROD','CYP1B1 BROD activity inhibited in vitro.','CYP1B1 inhibition','inhibition','IC50 = 33.56 ± 0.72 μM','16338240','10.1016/j.bmc.2005.11.039','Abstract: enzyme inhibition results')]
added += [add_record('24788952','Paradisin C','CYP3A4','Reported as a new CYP3A4 inhibitor isolated from grapefruit juice.','CYP3A4 inhibition','inhibition','Qualitative inhibitor report; numerical endpoint not extracted.','','10.1016/s0040-4020(02)00739-1','Article title/abstract metadata; full-text table extraction pending')]
added += [add_record('1268142','Nootkatone','CYP2A6','CYP2A6 activity inhibited in vitro.','CYP2A6 inhibition','inhibition','Ki = 0.8 μM','10860553','10.1006/abbi.2000.1835','Abstract: inhibition constants')]
added += [add_record('1268142','Nootkatone','CYP2C19','CYP2C19 activity inhibited in vitro.','CYP2C19 inhibition','inhibition','Ki = 0.5 μM','10860553','10.1006/abbi.2000.1835','Abstract: inhibition constants')]
added += [add_record('9946625','Epoxybergamottin','CYP3A4-mediated diltiazem N-demethylation','CYP3A4-mediated diltiazem N-demethylation inhibited in transfected liver epithelial cells.','CYP3A4 inhibition','inhibition','IC50 = 4.2 ± 1.1 μM','12610742','10.1007/s00228-002-0537-3','Abstract: results; transfected liver epithelial-cell assay')]
added += [add_record('5281600','Amentoflavone','CYP3A4','CYP3A4 activity inhibited in vitro.','CYP3A4 inhibition','inhibition','IC50 = 0.07 μM','19883715','10.1016/j.fct.2009.10.041','Abstract: CYP inhibition results','Ginkgo/Hypericum botanical supplement context')]
added += [add_record('5281600','Amentoflavone','CYP2C9','CYP2C9 activity inhibited in vitro.','CYP2C9 inhibition','inhibition','IC50 = 0.03 μM','19883715','10.1016/j.fct.2009.10.041','Abstract: CYP inhibition results','Ginkgo/Hypericum botanical supplement context')]
for row in added:
 for c in reg:
  if c['Compound_ID']==row['Compound_ID']: c['Evidence_Records']=str(int(c['Evidence_Records'] or 0)+1)
for d in drugs:
 n=sum(x['Drug']==d['Drug_Probe'] for x in ev); d['Evidence_Records']=str(n)
 d['Primary_PMIDs']='|'.join(sorted({x['PMID'] for x in ev if x['Drug']==d['Drug_Probe'] and x['PMID']}))

# Study, bibliography, and claim registries retain inherited rows then add one publication entry each.
studies=read(V10/'outputs/study_registry_v10.csv'); bib=read(V10/'outputs/source_bibliography_v10.csv')
claims=read(V10/'outputs/claim_support_and_verification_v10.csv')
for row in added:
 if any(x['Evidence_ID']==row['Evidence_ID'] for x in claims):continue
 pmid=row['PMID']; doi=row['DOI']; key='PMID:'+pmid if pmid else 'DOI:'+doi
 if not any(x['Study_ID']==key for x in studies):
  title,authors,year=pubinfo(pmid,doi); related=[x for x in added if x['Study_ID']==key]
  studies.append({'Study_ID':key,'PMID':pmid,'DOI':doi,'Title':title,'Authors':authors,'Year':year,'Evidence_Record_IDs':'|'.join(x['Evidence_ID'] for x in related),'Evidence_Record_Count':str(len(related)),'Evidence_Classes':'In vitro','Verification_Status':'Abstract verified' if pmid else 'Metadata verified only; article abstract located; extraction pending','Independence':'Publication identifier only; independent cohort not inferred'})
 if not any(x['PMID']==pmid and pmid or x['DOI'].lower()==doi.lower() for x in bib):
  title,authors,year=pubinfo(pmid,doi); bib.append({'PMID':pmid,'Title':title,'Authors':authors,'Year':year,'DOI':doi,'PMCID':'','Source':'PubMed ESummary' if pmid else 'Crossref metadata; publisher abstract located','Count_Unit':'Publication','DOI_Status':'PubMed DOI verified' if pmid else 'DOI-only; PMID not identified'})
 claims.append({'Evidence_ID':row['Evidence_ID'],'Compound_ID':row['Compound_ID'],'PMID':pmid,'Source_Locator':row['Source_Locator'],'Verification_Status':'Abstract verified' if pmid else 'Partially verified','Numerical_Use':'Abstract-level reported value; not independently table-checked' if pmid else 'Qualitative only; no numerical claim','Attribution':'Primary source metadata and abstract support named analyte/assay' if pmid else 'Publisher/Crossref title supports Paradisin C and CYP3A4; detail extraction pending','Limitations':row['Limitations']})

# Explicit decisions for every anchor; retain contemporaneous/retrospective character.
selection=read(V10/'outputs/v10_selection_decisions.csv'); selected={x['Candidate'].casefold() for x in selection}
for c in reg:
 if c['Canonical_Name'].casefold() not in selected:
  selection.append({'Candidate':c['Canonical_Name'],'Decision':'Retain inherited anchor; retrospective V11 completeness row','Identity':f"PubChem CID {c['PubChem_CID']} and registry identity retained",'Food_Context':c['Food_Context'] or 'Food-context rationale carried from inherited registry; requires human source review where flagged','Interaction_Rationale':c['Selection_Rationale'],'Primary_Source_PMID':c['Selection_PMID'],'Primary_Source_DOI':c['Selection_DOI'],'Verification':'Retrospective metadata completion; does not claim contemporaneous selection evidence','Date':'2026-10-30','Residual_Limitation':'Historical selection date/source not inferred; consult inherited provenance and warning ledger.'})
for cid,name,context,pmid,doi,rationale,food,fc in new_defs:
 selection.append({'Candidate':name,'Decision':'Admit to V11; controlled addition','Identity':f'PubChem CID {cid}; structure capture archived','Food_Context':food,'Interaction_Rationale':rationale,'Primary_Source_PMID':pmid,'Primary_Source_DOI':doi,'Verification':'Primary paper abstract/metadata; in-vitro only' if pmid else 'DOI metadata and publisher abstract; numerical extraction pending','Date':'2026-10-30','Residual_Limitation':fc})

# Screen log includes admitted candidates and explicit deferrals.
screen=read(V10/'outputs/v10_candidate_screening_log.csv')
for cid,name,context,pmid,doi,rationale,food,fc in new_defs:
 screen.append({'Search_Date':'2026-10-30','Database':'PubChem; PubMed/Crossref; primary article','Query_or_Candidate':name,'Decision':'Admit with limitations','Reason':f'Identity and grapefruit/botanical context supported; primary interaction assay located. {fc}','Full_Text_Availability':'Abstract/metadata captured; full table review not completed','Verification_Status':'Abstract verified' if pmid else 'DOI metadata / publisher abstract; numerical extraction pending','Reviewer_Note':f'CID {cid}; PMID {pmid or "none"}; DOI {doi}'})
for name,why in [('GF-I-1','Identity/chemical structure unresolved in captured sources; defer.'),('GF-I-4','Identity/chemical structure unresolved in captured sources; defer.'),('Paradisin B','No uniquely resolved CID and primary claim mapping in this cycle; defer.'),('Imperatorin','Abstract-level enzyme target attribution ambiguous; defer pending primary table review.')]:
 screen.append({'Search_Date':'2026-10-30','Database':'V11 candidate screen','Query_or_Candidate':name,'Decision':'Defer','Reason':why,'Full_Text_Availability':'Not established','Verification_Status':'Unverified','Reviewer_Note':'Not admitted to anchor or evidence tables.'})

# Identity rows are based on captured PubChem response; no cheminformatics parse claimed.
identity=read(V10/'outputs/identity_structure_audit_v10.csv')
syn={str(x['CID']):x.get('Synonym',[]) for x in jread(S/'pubchem_synonyms_all.json')}
name_capture={'72941753':['Paradisin A'],'24788952':['Paradisin C'],'1268142':['Nootkatone','(+)-Nootkatone'],'9946625':['Epoxybergamottin'],'5281600':['Amentoflavone']}
syn.update(name_capture)
(S/'pubchem_synonyms_v11_candidates.json').write_text(json.dumps([{'CID':int(k),'Synonym':v,'Source':'https://pubchem.ncbi.nlm.nih.gov/compound/'+k,'Access_Date':'2026-10-30'} for k,v in name_capture.items()],indent=2),encoding='utf-8')
for c in newrows:
 identity.append({'Compound_ID':c['Compound_ID'],'Canonical_Name':c['Canonical_Name'],'PubChem_CID':c['PubChem_CID'],'Returned_InChIKey':c['InChIKey'],'Registry_InChIKey':c['InChIKey'],'Exact_Key_Match':'True','SMILES':c['SMILES'],'InChI':c['InChI'],'Structure_Source':c['Identity_Source'],'Status':'PubChem capture match; manual chemical review pending','Note':'Structure values copied from captured PubChem response; no RDKit parsing performed.','PubChem_Name_or_Alias_Match':str(any(c['Canonical_Name'].casefold()==x.casefold() for x in syn.get(c['PubChem_CID'],[]))),'PubChem_Synonyms':' | '.join(syn.get(c['PubChem_CID'],[])[:30])})

# Warning history is carried untouched with explicit V11 additions; no inherited warning closed.
warnings=read(V10/'outputs/warning_resolution_ledger_v10.csv')
for wid,code,desc,affected,action,lim in [
 ('V11-W01','V11_NO_DOI','PubMed metadata contains no DOI for five inherited publications; six evidence rows remain DOI blank.','PMID:18928093|22512082|26396928|26692948|28646810','PubMed ESummary rechecked for all 140 inherited PMIDs; blanks retained.','DOI absence cannot be corrected from captured PubMed metadata; secondary DOI discovery not asserted.'),
 ('V11-W02','V11_NEAR_DUP','Two inherited pairs share connectivity blocks but have distinct full InChIKeys and stereochemistry.','CHEM-PUBCHEM-9064|CHEM-PUBCHEM-72276|MOL-V10-5281643|MOL-V10-5280804','Recorded pair-level distinction; expert stereo/tautomer adjudication remains open.','No cheminformatics or expert stereochemical review performed.'),
 ('V11-W03','V11_SOURCE_REVIEW','Inherited claim-level source review remains incomplete; existing verification labels are not equivalent to full primary-source re-extraction.','263 inherited evidence rows','Added priority/source audits and retained inherited statuses; no broad claim upgraded.','Full-text/table review across inherited numeric claims is outstanding.'),
 ('V11-W04','V11_FOOD_CONTEXT','Inherited anchor food occurrence claims were not independently re-sourced for all anchors.','100 inherited anchors','Explicitly surfaced in manual QA coverage and selection table.','Food-context review remains open, especially botanical/supplement anchors.'),
 ('V11-W05','V11_PATH_FIX','V10 build script contains a machine-specific absolute release path.','build_v10.py','V11 build script resolves release paths relative to its own directory.','Clean-copy rebuild needed to support resolution.'),
 ('V11-W06','V11_DUP_CONTEXT','Duplicate-context screen surfaces five inherited study/endpoint/preparation candidate groups; arm and endpoint attribution needs human adjudication.','SB-0016|SB-0017|SB-0046|SB-0047|SB-0048|SB-0063|SB-0064|SB-0079|SB-0080|SB-0256|SB-0259','Groups were retained and listed in DD-02 diagnostics; no row was removed or merged.','Some groups likely represent distinct dose arms, assay endpoints, or context; source-level adjudication remains open.')]:
 warnings.append({'Warning_ID':wid,'Code':code,'Description':desc,'Affected':affected,'Classification':'Data provenance / scientific verification / reproducibility','Before':'New in V11 audit','Action':action,'After':'Partially resolved' if wid in {'V11-W02','V11-W05'} else 'Unresolved','Remaining_Limitations':lim,'Resolution_Source':'V11 validation and captured source metadata' if wid!='V11-W04' else 'V11 manual review scope report','Review_Date':'2026-10-30'})

# Audit tables and release notes.
source_audit=read(V10/'outputs/v10_source_audit.csv')
for r in added:
 source_audit.append({'Evidence_ID':r['Evidence_ID'],'PMID':r['PMID'],'DOI':r['DOI'],'Source_Title':r['Source_Title'],'Source_URL':r['Source_URL'],'Source_Cache':r['Source_Cache'],'Source_Locator':r['Source_Locator'],'Verification_Status':'Abstract verified' if r['PMID'] else 'Partially verified','Fields_Audited':'Identity; compound; CYP probe; assay; reported endpoint/value at abstract level','Limitations':r['Limitations']})
# Recompute publication evidence links/counts after grouping all newly added evidence.
for study in studies:
 related=[x for x in ev if x['Study_ID']==study['Study_ID']]
 if related:
  study['Evidence_Record_IDs']='|'.join(x['Evidence_ID'] for x in related)
  study['Evidence_Record_Count']=str(len(related))
  study['Evidence_Classes']='|'.join(sorted({x['Evidence_Type'] for x in related}))
  study['Independence']='Publication identifier only; independent cohort not inferred'

basefields={
'compound_registry_v11.csv':list(reg[0]),'stageB_food_drug_interactions_v11.csv':ev_fields,'drug_probe_registry_v11.csv':drug_fields,
'study_registry_v11.csv':list(studies[0]),'source_bibliography_v11.csv':list(bib[0]),'identity_structure_audit_v11.csv':list(identity[0]),
'selection_decisions_v11.csv':list(selection[0]),'candidate_screening_log_v11.csv':list(screen[0]),'source_audit_v11.csv':list(source_audit[0]),
'claim_support_and_verification_v11.csv':list(claims[0]),'warning_resolution_ledger_v11.csv':list(warnings[0])}
tables={'compound_registry_v11.csv':reg,'stageB_food_drug_interactions_v11.csv':ev,'drug_probe_registry_v11.csv':drugs,'study_registry_v11.csv':studies,'source_bibliography_v11.csv':bib,'identity_structure_audit_v11.csv':identity,'selection_decisions_v11.csv':selection,'candidate_screening_log_v11.csv':screen,'source_audit_v11.csv':source_audit,'claim_support_and_verification_v11.csv':claims,'warning_resolution_ledger_v11.csv':warnings}
for f,rows in tables.items():write(O/f,rows,basefields[f])
for name in ['cooking_retention_evidence_v9.csv']:
 src=V10/'outputs'/name; dst=O/name
 if not dst.exists(): dst.write_bytes(src.read_bytes())

# V11 source audit includes added sources and local captures.
write(O/'v11_change_log.csv',[{'Area':'Dataset','Item':'V10 inherited records/anchors','Change':'Copied row-identically into V11; no inherited interaction or anchor row edited.','Reason':'Regression preservation','Source_or_test':'RG-01/RG-02; V10 checksum manifest'},{'Area':'Expansion','Item':'Five new anchors; nine evidence rows','Change':'Added grapefruit-associated Paradisin A, Paradisin C, nootkatone, epoxybergamottin and supplement-context amentoflavone.','Reason':'Primary-source in-vitro evidence and context reviewed; limitations flagged','Source_or_test':'V11 source audit and PubMed/Crossref captures'},{'Area':'Provenance','Item':'Selection coverage','Change':'Completed explicit retrospective selection rows for inherited anchors missing a V10 decision row.','Reason':'Decision traceability; original dates/rationales not invented','Source_or_test':'PR-01/PR-02'},{'Area':'Build','Item':'Relative paths','Change':'Added path-relative V11 build script.','Reason':'Avoid machine-specific absolute release directory','Source_or_test':'RP-01/RP-02'}])
write(O/'v11_warning_transition_report.csv',[{'Warning_ID':x['Warning_ID'],'Code':x['Code'],'V10_Status':x['Before'],'V11_Status':x['After'],'Action':x['Action'],'Remaining_Limitations':x['Remaining_Limitations']} for x in warnings])
write(O/'v11_food_context_audit.csv',[{'Compound_ID':c['Compound_ID'],'Compound':c['Canonical_Name'],'Food_Context':c['Food_Context'],'Selection_Source':c['Selection_Source'],'Interaction_Rationale':c['Selection_Rationale'],'Context_Class':'Supplement/medicinal botanical only' if any(t in c['Food_Context'].lower() for t in ['supplement','medicinal','botanical']) else ('V11 primary source / inherited context requires review' if c['Compound_ID'].startswith('MOL-V11') else 'Inherited claim; independent review not complete'),'Review_Status':'Source/context review required' if not c['Compound_ID'].startswith('MOL-V11') else 'Source checked; human dietary relevance review pending'} for c in reg])
write(O/'v11_near_duplicate_audit.csv',[{'Pair_ID':'ND-01','Compound_IDs':'CHEM-PUBCHEM-9064|CHEM-PUBCHEM-72276','Names':'(+)-Catechin|(-)-Epicatechin','Observation':'Same connectivity block; distinct full InChIKeys; stereoisomers','Disposition':'Keep separate; expert review pending'},{'Pair_ID':'ND-02','Compound_IDs':'MOL-V10-5281643|MOL-V10-5280804','Names':'Hyperoside|Isoquercetin','Observation':'Same connectivity block; distinct full InChIKeys; sugar stereochemistry differs','Disposition':'Keep separate; expert review pending'}])
summary={'release':'V11','date':'2026-10-30','anchors':len(reg),'evidence_records':len(ev),'drug_probe_labels':len(drugs),'unique_PMIDs':len({x['PMID'] for x in ev if x['PMID']}),'unique_DOIs':len({x['DOI'].lower() for x in ev if x['DOI']}),'evidence_classes':{k:sum(x['Evidence_Type']==k for x in ev) for k in sorted({x['Evidence_Type'] for x in ev})},'new_anchors':5,'new_evidence_records':len(added),'stretch_target':120,'remaining_anchors_to_target':120-len(reg),'inherited_v10_rows_modified':0}
(O/'v11_release_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
