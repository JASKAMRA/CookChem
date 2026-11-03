from collect import O,CANDIDATES,slug
from curation import ROWS
from pathlib import Path
import csv,json,shutil,collections,re,html,itertools,xml.etree.ElementTree as ET
B=O.parent;V=B/'release_v6_20261014'
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def load(p):return json.loads(p.read_text(encoding='utf8'))
def write(n,rows):
 with (O/'outputs'/n).open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def primary(p):return load(O/'sources'/('pmid_'+p+'.json'))['resultList']['result'][0]
def clean(s):return html.unescape(re.sub(r'</?[A-Za-z][^>]*>','',s))
FOODS={
 'Diosmetin':('Citrus fruits','ChEBI description through PubChem','sources/description_diosmetin.json'),
 'Rutin':('Citrus peel; distinct quercetin rutinoside','PMID:31252064','sources/pmid_31252064.json'),
 'Pterostilbene':('Small berries','PMID:30976185','sources/pmid_30976185.json'),
 'Ursolic acid':('Apple peel','PMID:35766779','sources/pmid_35766779.json'),
 'Oleanolic acid':('Apple peel; distinct oleanane structure','PMID:35766779','sources/pmid_35766779.json'),
 'Sesamin':('Sesame seeds','PMID:30902268','sources/pmid_30902268.json'),
 'Nobiletin':('Citrus fruits','PMID:23441616','sources/pmid_23441616.json'),
 'Tangeretin':('Clementine/citrus flavonoid','PMID:32187570','sources/pmid_32187570.json'),
 'Ascorbic acid':('Vitamin C in fruits, vegetables and dietary ingredients','NIH ODS Vitamin C; food sources and introduction','sources/nih_food_context_retrieval.json'),
 'Folic acid':('Oxidized monoglutamate in fortified foods and supplements; not total natural food folate','NIH ODS Folate; introduction and fortified-food section','sources/nih_food_context_retrieval.json'),
 'Phylloquinone':('Vitamin K1 in green leafy vegetables and oils; not generic vitamin K','NIH ODS Vitamin K; introduction and food sources','sources/nih_food_context_retrieval.json'),
 'Vanillin':('Dietary flavouring ingredient','ChEBI description through PubChem','sources/description_vanillin.json'),
 'Oleuropein':('Olive cultivars and olive-derived dietary ingredients','ChEBI description through PubChem; PMID:28646810','sources/description_oleuropein.json'),
 'Allyl isothiocyanate':('Mustard and horseradish extracts used as food additives','PMID:34219099','sources/pmid_34219099.json'),
 'Zeaxanthin':('Corn, orange pepper, oranges and tangerines','PMID:27529203 Introduction','sources/PMC6272861.xml'),
 'Lutein':('Leafy vegetables, corn and egg yolks','PMID:27529203 Introduction','sources/PMC6272861.xml')}
def main():
 for n in ['compound_registry.csv','stageB_food_drug_interactions_v6.csv','warning_resolution_ledger.csv','cooking_retention_evidence.csv','processing_provenance_audit.csv']:
  dst=O/'inputs'/n
  if not dst.exists():shutil.copy2(V/'outputs'/n,dst)
 e=read(O/'inputs/stageB_food_drug_interactions_v6.csv');r=read(O/'inputs/compound_registry.csv');ef=list(e[0]);rf=list(r[0]);by={x['Canonical_Name']:x for x in r};decisions=[];food=[]
 for n in CANDIDATES:
  if n not in FOODS:
   reason='Not admitted: capped discovery not fully arm-reviewed; replace with stronger traceable candidate rather than count an uncertain entity.'
   if n in ['Isothiocyanate','Chlorophyllin']:reason='Excluded as a non-specific chemical class or formulation/mixture name; not a single uniquely defined anchor.'
   if n in ['Epigallocatechin','Catechin gallate','Epicatechin gallate','Gallocatechin']:reason='Deferred: retrieved results dominated by related catechins/mixtures; isolated exact-form evidence not independently curated.'
   decisions.append(dict(Candidate=n,Decision='excluded' if n in ['Isothiocyanate','Chlorophyllin'] else 'deferred',Reason=reason,Selection_Date='2026-10-15',Primary_PMIDs=''));continue
  qs=[a for a in ROWS if a['c']==n];p=load(O/'sources'/('identity_'+slug(n)+'.json'))['PropertyTable']['Properties'][0];s=primary(qs[0]['p']);f,fs,fc=FOODS[n];cid=str(p['CID']);rr={k:'' for k in rf}
  reason=f'{f}; '+('human controlled/PK primary evidence' if any(a['t'] in ['Controlled clinical','Human pharmacokinetic'] for a in qs) else 'traceable named-drug/probe experimental evidence, with null/context-specific results retained')+'. Distinct reference structure; no food-exposure equivalence inferred.'
  rr.update(Compound_ID='CHEM-PUBCHEM-'+cid,Canonical_Name=n,Aliases=n,PubChem_CID=cid,SMILES=p.get('ConnectivitySMILES',''),InChI=p['InChI'],InChIKey=p['InChIKey'],Identity_Status='external_reference_identity; tested isomer/purity scope not universally certified',Identity_Source=f'https://pubchem.ncbi.nlm.nih.gov/compound/{cid}',Origin='added_v7',Selection_Rationale=reason,Selection_Source=s['title'],Selection_DOI=s.get('doi',''),Selection_PMID=qs[0]['p'],Selection_URL=f'https://pubmed.ncbi.nlm.nih.gov/{qs[0]["p"]}/',Date_Added='2026-10-15',First_Documented_Release_Date='2026-10-15',Date_Status='Current v7 decision, not an inferred historical date',Coverage_Status='Bounded manual primary-source extraction',Provenance_Status='Selection and food-context sources recorded separately',Retention_Status='No cooking-retention coefficient imported',Food_Context=f,Evidence_Records=str(len(qs)),Link_Restriction='Standalone reference anchor; no automatic master measurement link. SMILES are connectivity-only; reference InChI carries stereochemical scope.',Release_Reviewed='v7_20261015_clean',Selection_Verification='Primary interaction source and independent food-context source reviewed',Earliest_Verified_Selection_Date='2026-10-15',Selection_Temporality='Current documented selection',Remaining_Provenance_Gap='Study-tested stereochemical purity may be unspecified; diet-to-experimental-dose equivalence not established')
  r.append(rr);by[n]=rr;decisions.append(dict(Candidate=n,Decision='selected',Reason=reason,Selection_Date='2026-10-15',Primary_PMIDs=' | '.join(sorted({a['p'] for a in qs}))));foodurl=('https://pubmed.ncbi.nlm.nih.gov/'+re.search(r'PMID:(\d+)',fs).group(1)+'/') if 'PMID:' in fs else 'https://ods.od.nih.gov/factsheets/'+{'Ascorbic acid':'VitaminC','Folic acid':'Folate','Phylloquinone':'VitaminK'}[n]+'-HealthProfessional/' if n in ['Ascorbic acid','Folic acid','Phylloquinone'] else rr['Identity_Source'];food.append(dict(Compound=n,Food_Context=f,Source=fs,Source_URL=foodurl,Cache=fc,Domain='Food association only; not an interaction outcome or retention coefficient',Selection_Rationale=reason))
 claims=[];changes=[];reviews=read(O/'inputs/baseline_review_levels.csv')
 for i,a in enumerate(ROWS,148):
  s=primary(a['p']);rr=by[a['c']];eid=f'SB-{i:04d}';x={k:'' for k in ef};level='full_text_selected' if a['full'] else 'abstract';source='sources/'+a['full'] if a['full'] else 'sources/pmid_'+a['p']+'.json'
  x.update(Evidence_ID=eid,Compound=a['c'],Compound_ID=rr['Compound_ID'],Drug=a['d'],Interaction_Effect=a['e'],Mechanism=a['mech'] or 'Mechanism not established by extracted claim; author proposals not treated as clinical proof',Evidence_Type=a['t'],Evidence_Level='compound',Direction=a['out'],Quantitative_Outcome=a['q'],Dose=a['dose'] or 'Not extracted/not supplied in reviewed source passage',Population=a['pop'],Study_Design='Randomized double-blind placebo-controlled clinical trial' if a['t']=='Controlled clinical' else 'Human PK investigation; design specified in preparation/limitations' if a['t']=='Human pharmacokinetic' else 'Experimental '+a['t'].lower()+' study',Source_Title=s['title'],Authors=s.get('authorString',''),Year=s['pubYear'],DOI=s.get('doi',''),PMID=a['p'],Source_Type='Primary research',Limitations=('Selected full-text passage verification; not whole-paper adjudication. ' if a['full'] else 'Abstract-only extraction; exact dose, n or preparation may be incomplete. ')+a['note']+' No experimental-dose equivalence to food intake.',Confidence='Primary-source scoped finding; no independent second reviewer',Notes='No calculated endpoint values; source precision and reported units retained.',Study_ID='PMID:'+a['p'],Source_URL=f'https://pubmed.ncbi.nlm.nih.gov/{a["p"]}/',Source_Cache=O.name+'/sources/pmid_'+a['p']+'.json',Source_Locator=a['loc'],Preparation=a['prep'],Affected_Entity='drug/probe' if a['t']!='Controlled clinical' else 'drug-associated clinical endpoint',Perpetrator='compound_or_preparation',Outcome=a['out'],Conflict_Group=a['c']+'-'+a['d']+'-context-dependent',Identity_Status=rr['Identity_Status'],Release_Origin='v7_20261015_clean',Clinical_Extrapolation='No clinical risk score or diet/exposure equivalence inferred',CookRisk_Exposure_Link='Not linked to master cooking-retention measurements')
  e.append(x);support=' '.join(ET.parse(O/source).getroot().itertext()) if a['full'] else clean(s.get('abstractText',''))
  claims.append(dict(Evidence_ID=eid,PMID=a['p'],Claim=a['q'],Qualitative_Claim=a['e'],Outcome=a['out'],Verification_Level=level,Source=source,Locator=a['loc'],Supporting_Text=support,Limitations=x['Limitations']))
  changes.append(dict(Evidence_ID=eid,Action='added',Field='all',Before='',After=a['e'],Source=source,Reason='Qualifying new primary experimental context'))
  reviews.append(dict(Evidence_ID=eid,Verification_Level=level,Detail=source+'; '+a['loc'],Scope='New v7 primary-source extraction'))
 # Six inherited claims rechecked; values remain exactly preserved.
 for x in e[:147]:
  if x['Evidence_ID'] not in ['SB-0001','SB-0003','SB-0004','SB-0005'] and not (x['Compound']=='Bergapten' and x['PMID']=='37492094'):continue
  full=x['Compound']=='Bergapten';source='sources/PMC10363979.xml' if full else 'inherited_sources/'+x['Source_Cache'];loc='Table 3; Results microsome inhibition; Methods animal and inhibition experiments' if full else 'Primary abstract Methods and Results; exact existing endpoint reviewed'
  level='full_text_selected' if full else 'abstract'
  next(v for v in reviews if v['Evidence_ID']==x['Evidence_ID']).update(Verification_Level=level,Detail=source+'; '+loc,Scope='Inherited claim reverified in v7; data fields unchanged')
  changes.append(dict(Evidence_ID=x['Evidence_ID'],Action='verification_upgrade',Field='external review ledger only',Before='V6 documented review scope',After=level,Source=source,Reason='Outcome and experimental context manually rechecked; inherited evidence row unchanged'))
  support=' '.join(ET.parse(O/source).getroot().itertext()) if full else ''
  if not full:
   d=load(O/source);support=next(h.get('abstractText','') for h in d['resultList']['result'] if str(h.get('id'))==x['PMID'])
  claims.append(dict(Evidence_ID=x['Evidence_ID'],PMID=x['PMID'],Claim=x['Quantitative_Outcome'],Qualitative_Claim=x['Interaction_Effect'],Outcome=x['Outcome'],Verification_Level=level,Source=source,Locator=loc,Supporting_Text=clean(support),Limitations='Selected claim re-verification only; no inherited field correction required'))
 registrychanges=[]
 old={x['Compound_ID']:x for x in read(O/'inputs/compound_registry.csv')}
 for rr in r:
  count=str(sum(x['Compound_ID']==rr['Compound_ID'] for x in e));before=rr['Evidence_Records'];rr['Evidence_Records']=count
  if rr['Origin']=='added_v7':registrychanges.append(dict(Compound_ID=rr['Compound_ID'],Action='added',Field='all',Before='',After=rr['Canonical_Name'],Reason=rr['Selection_Rationale']))
  elif before!=count:registrychanges.append(dict(Compound_ID=rr['Compound_ID'],Action='derived_count_update',Field='Evidence_Records',Before=before,After=count,Reason='New evidence for existing anchor'))
 write('stageB_food_drug_interactions_v7.csv',e);write('compound_registry.csv',r);write('new_evidence_records.csv',e[147:]);write('candidate_selection.csv',decisions);write('selection_provenance_ledger.csv',[x for x in r if x['Origin']=='added_v7']);write('food_context_source_audit.csv',food);write('claim_support_and_outcome_audit.csv',claims);write('all_record_review_audit.csv',reviews);write('evidence_change_log.csv',changes);write('registry_change_log.csv',registrychanges)
 write('identity_structure_audit.csv',[{k:x[k] for k in ['Compound_ID','Canonical_Name','PubChem_CID','InChI','InChIKey','Identity_Status','Identity_Source','Original_Molecular_Group','Link_Restriction']} for x in r])
 pairs=[dict(Compound_A=a['Canonical_Name'],Compound_B=b['Canonical_Name'],InChIKey_A=a['InChIKey'],InChIKey_B=b['InChIKey'],Decision='Distinct stereochemical reference entities; inherited anchors preserved',Basis='Same connectivity block, different full InChIKeys') for a,b in itertools.combinations(r,2) if a['InChIKey'][:14]==b['InChIKey'][:14]]
 if pairs:write('near_duplicate_identity_audit.csv',pairs)
 for n in ['cooking_retention_evidence.csv','processing_provenance_audit.csv']:write(n,read(O/'inputs'/n))
 warnings=read(O/'inputs/warning_resolution_ledger.csv')
 for w in warnings:
  w['Before']=w['After'];w['Action']='V7 inspection: '+w['Action']
  if w['Code']=='v6_anchor_target_gap':w['After']='Not applicable after inspection';w['Action']='Prior 50-anchor goal superseded; V7 reaches 60. Prior deferred candidates not all admitted: unused candidates remain deferred.'
  if w['Code'] in ['inherited_outcome_scope','v6_abstract_scope']:w['After']='Partially resolved';w['Action']='Four older berberine outcomes abstract-reverified and two V6 bergapten outcomes selected-full-text reverified; remaining inherited gaps retained.'
  if w['Code']=='new_bibliographic_gaps':w['Affected']+='; V7 PMID 26396928 and 28646810 DOI absent';w['Action']+=' Exact primary MED records for the two new reports supply no DOI; PMID retained without invention.'
 for code,desc in [('v7_identity_scope','Reference natural forms are not universal certification of experimental isomer/purity; ascorbic acid and folic acid remain unlinked to mixed master analytes.'),('v7_source_scope','New abstract-only records retain missing-dose/sample/preparation gaps; selected full-text review is not whole-paper adjudication.'),('v7_source_discrepancies','Pterostilbene abstract no-inhibition wording versus bounded full-text results; pioglitazone prose 17.9 vs Table 3 18.0 microM not imported; sesamin prior 0.2 microM result not attributed to current experiment.'),('v7_unequal_dose_comparator','Oleuropein/doxorubicin combination uses 1.5 mg/kg doxorubicin versus 2.5 mg/kg alone; no equal-dose synergy magnitude calculated.')]:
  warnings.append(dict(Warning_ID=code,Code=code,Description=desc,Affected='See primary claim ledger',Classification='Research scope or source reporting limitation',Before='New in v7',Action='Explicit limitation retained; no clinical or exposure inference',After='Unresolved',Remaining_Limitations=desc))
 write('warning_resolution_ledger.csv',warnings)
 studies=[]
 for p in sorted({x['PMID'] for x in e}):
  q=[x for x in e if x['PMID']==p];x=q[0];cp=O/'sources'/('crossref_'+p+'.json');d=load(cp) if cp.exists() else {};title=' '.join(d.get('message',{}).get('title',[]));norm=lambda s:re.sub('[^a-z0-9]','',clean(s).lower());status='Crossref title concordant' if title and norm(title)==norm(x['Source_Title']) else 'MED checked; Crossref unavailable/not repeated' if not title else 'Crossref mismatch requires review'
  if p=='1828561':status='Manually adjudicated: Crossref omits MED subtitle; DOI and main title agree'
  if p=='688723':status='Manually adjudicated: Crossref title has OCR-like c/e substitutions; DOI and citation checked against MED'
  studies.append(dict(PMID=p,DOI=x['DOI'],Title=x['Source_Title'],Authors=x['Authors'],Year=x['Year'],Evidence_Records=len(q),Verification=status,Independence='Unique publication, not inferred independent cohort'))
 write('study_registry.csv',studies);write('interaction_evidence_source_audit.csv',studies)
 write('bibliographic_discrepancy_audit.csv',[dict(PMID=p,MED_Title=primary(p)['title'],DOI=primary(p)['doi'],Crossref_Title=' | '.join(load(O/'sources'/('crossref_'+p+'.json')).get('message',{}).get('title',[])),Decision=next(x['Verification'] for x in studies if x['PMID']==p),Status='Resolved with supporting source; source metadata differences preserved') for p in ['1828561','688723']])
 write('drug_probe_registry.csv',[dict(Drug_ID=f'DRUG-{i:04d}',Drug_Probe=n,Evidence_Records=sum(x['Drug']==n for x in e),Primary_PMIDs=' | '.join(sorted({x['PMID'] for x in e if x['Drug']==n})),Scope='Named study drug/probe; salt and stereoselective scope retained in evidence') for i,n in enumerate(sorted({x['Drug'] for x in e}),1)])
 screened=[]
 included={x['p'] for x in ROWS}
 for p in sorted((O/'sources').glob('broad_*.json'))+sorted((O/'sources').glob('historical_*.json')):
  for h in load(p).get('resultList',{}).get('result',[]):screened.append(dict(Search_Cache=p.relative_to(O).as_posix(),PMID=h.get('id',''),Title=h.get('title',''),Status='included-source; curated claims only' if h.get('id') in included else 'candidate_not_fully_screened'))
 write('screening_log.csv',screened)
 s=dict(version='v7',anchors=len(r),records=len(e),drugs=len({x['Drug'] for x in e}),publications=len(studies),unique_nonempty_doi=len({x['DOI'].lower() for x in e if x['DOI']}),numerical_records=sum(bool(x['Quantitative_Outcome']) for x in e),classes=dict(collections.Counter(x['Evidence_Type'] for x in e)),verification=dict(collections.Counter(x['Verification_Level'] for x in reviews)),new_anchors=len(FOODS),new_records=len(ROWS),new_publications=len(included-{x['PMID'] for x in e[:147]}),new_verification=dict(collections.Counter(x['Verification_Level'] for x in reviews[147:])),inherited_review_upgrades=6,target=60,target_gap=60-len(r),warning_entries=sum(x['After'] in ['Unresolved','Partially resolved'] for x in warnings),distinct_warning_codes=len({x['Code'] for x in warnings if x['After'] in ['Unresolved','Partially resolved']}),issue_status_counts=dict(collections.Counter(x['After'] for x in warnings)),discovery_occurrences=len(screened),new_classes=dict(collections.Counter(x['Evidence_Type'] for x in e[147:])))
 (O/'outputs/release_summary.json').write_text(json.dumps(s,indent=2),encoding='utf8');print(json.dumps(s,indent=2))
if __name__=='__main__':main()
