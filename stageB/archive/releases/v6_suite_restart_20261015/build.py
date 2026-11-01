from pathlib import Path
import csv,json,collections,shutil,html,re
from curation import ROWS
from collect import CANDIDATES,slug
O=Path(__file__).resolve().parent;B=O.parent;V=B/'release_v5_20261014'
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(n,rows,fields=None):
 with (O/'outputs'/n).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
def load(p):return json.loads(p.read_text(encoding='utf8'))
def primary(p):return load(O/'sources'/('pmid_'+p+'.json'))['resultList']['result'][0]
def clean(s):return html.unescape(re.sub(r'</?[A-Za-z][^>]*>','',s))
FOOD={
 '(+)-Catechin':('Tea, cocoa, apples and other foods','34836412'), '(-)-Epicatechin':('Tea, cocoa, apples and other foods','34836412'),
 'Morin':('Mulberry; named in primary mouse study','15885265'),
 'Hesperetin':('Citrus-related flavanone aglycone; glycoside metabolism distinguished','15351063'),
 'Diosmin':('Citrus fruit juices; glycoside distinct from diosmetin','12972089'),
 'Hesperidin':('Citrus fruit juices; glycoside distinct from hesperetin','12972089'),
 '6-Gingerol':('Ginger ingredient; not interchangeable with Sini Decoction mixture','28051355'),
 'Thymoquinone':('Nigella sativa seed oil','10755708'),
 'Eugenol':('Clove-derived ingredient; pure eugenol distinct from clove oil','33074419'),
 'Cinnamaldehyde':('Cinnamon','38958374'), 'Carvacrol':('Thyme essential-oil constituent','38958374'), 'Thymol':('Thyme essential-oil constituent','38958374'),
 'Diallyl sulfide':('Garlic constituent; source distinct from disulfide and trisulfide','12136947'),
 'Diallyl disulfide':('Garlic constituent','38148345'), 'Diallyl trisulfide':('Garlic constituent','21535728'),
 'Allicin':('Freshly crushed garlic; thiosulfinate distinct from diallyl sulfides','38411783'),
 'Bergapten':('Grapefruit and grapefruit juice; distinct from bergamottin','10812937'),
 'Glycyrrhizin':('Licorice-containing sweets, liqueurs and dietary ingredients','17875310')}
DEFER={
 'Baicalein':'Qualifying rat doxorubicin report located (19827298), but common dietary-ingredient scope not resolved; medicinal plant use alone does not certify food relevance.',
 'Rutin':'Historical apigenin/rutin paclitaxel attribution remains ambiguous (24871039); no independently curated qualifying isolated-rutin arm admitted in this release.',
 'Pterostilbene':'Recent formulation and sensitization candidates retrieved; exact preparation, qualifying combination and food-source attribution not fully curated.',
 'Ursolic acid':'Retrieved formulation, derivative and combination studies require separation of parent acid, modified carriers and actual drug co-treatment.',
 'Oleanolic acid':'Retrieved azole and formulation candidates require drug-specific arm extraction and food-matrix verification.',
 'Glycyrrhetinic acid':'Drug-probe microsome report located (22943175); metabolite-versus-dietary-parent scope and exact epimer not resolved. Not counted merely as a glycyrrhizin metabolite.'}
def main():
 (O/'inputs').mkdir(exist_ok=True)
 for file in ['stageB_food_drug_interactions_v5.csv','compound_registry.csv','warning_resolution_ledger.csv','processing_provenance_audit.csv']:
  dst=O/'inputs'/file
  if not dst.exists():shutil.copy2(V/'outputs'/file,dst)
 if not (O/'inputs/stageB_processing_evidence.csv').exists():shutil.copy2(B/'outputs/stageB_processing_evidence.csv',O/'inputs/stageB_processing_evidence.csv')
 evidence=read(O/'inputs/stageB_food_drug_interactions_v5.csv');registry=read(O/'inputs/compound_registry.csv');fields=list(evidence[0]);regfields=list(registry[0]);byname={r['Canonical_Name']:r for r in registry}
 selection=[];provenance=[]
 for name in CANDIDATES:
  if name not in FOOD:
   selection.append(dict(Candidate=name,Decision='deferred',Rationale=DEFER[name],Selection_PMID='',Interaction_PMIDs='',Date='2026-10-14'));continue
  prop=load(O/'sources'/('identity_'+slug(name)+'.json'))['PropertyTable']['Properties'][0];food,spmid=FOOD[name];s=primary(spmid);cid=str(prop['CID']);q=[x for x in ROWS if x['compound']==name];pmids=sorted({x['pmid'] for x in q})
  rationale=f'{food}. Admitted for traceable '+('human drug PK' if any(x['type']=='Human pharmacokinetic' for x in q) else 'preclinical named-drug/probe findings, including model-specific nulls where available')+'; no food-dose equivalence inferred.'
  row={k:'' for k in regfields};row.update(Compound_ID='CHEM-PUBCHEM-'+cid,Canonical_Name=name,Aliases=name,PubChem_CID=cid,SMILES=prop.get('ConnectivitySMILES',''),InChI=prop['InChI'],InChIKey=prop['InChIKey'],Identity_Status='external_reference_identity; tested stereochemistry not certified' if name in ['Hesperetin','Hesperidin','6-Gingerol','Cinnamaldehyde'] else 'external_reference_identity',Identity_Source=f'https://pubchem.ncbi.nlm.nih.gov/compound/{cid}',Origin='added_v6',Selection_Rationale=rationale,Selection_Source=s['title'],Selection_DOI=s.get('doi',''),Selection_PMID=spmid,Selection_URL=f'https://pubmed.ncbi.nlm.nih.gov/{spmid}/',Date_Added='2026-10-14',First_Documented_Release_Date='2026-10-14',Date_Status='New v6 selection date documented',Coverage_Status='Bounded primary-abstract review',Provenance_Status='Current selection documented; separate from experimental source',Retention_Status='No compound-specific cooking retention imported',Food_Context=food,Evidence_Records=str(len(q)),Link_Restriction='Standalone literature anchor; no automatic master measurement link. Connectivity SMILES; InChI carries reference stereochemistry.',Release_Reviewed='v6_20261014',Selection_Verification='Primary source metadata and abstract inspected; food-context source separate from outcome support',Earliest_Verified_Selection_Date='2026-10-14',Selection_Temporality='Current documented decision',Remaining_Provenance_Gap='Food exposure equivalence not established; source-tested stereochemical purity may be unspecified')
  registry.append(row);byname[name]=row
  selection.append(dict(Candidate=name,Decision='selected',Rationale=rationale,Selection_PMID=spmid,Interaction_PMIDs=' | '.join(pmids),Date='2026-10-14'))
  provenance.append(dict(Compound_ID=row['Compound_ID'],Compound=name,Selection_Rationale=rationale,Food_Context_PMID=spmid,Food_Context_Source=s['title'],Experimental_PMIDs=' | '.join(pmids),Date='2026-10-14',Status='Current selection documented; not historical provenance repair'))
 claims=[];changes=[];reviews=[]
 for i,a in enumerate(ROWS,119):
  s=primary(a['pmid']);r=byname[a['compound']];eid=f'SB-{i:04d}';row={k:'' for k in fields}
  row.update(Evidence_ID=eid,Compound=a['compound'],Compound_ID=r['Compound_ID'],Drug=a['drug'],Interaction_Effect=a['effect'],Mechanism=a['mechanism'] or 'Not established by extracted abstract',Evidence_Type=a['type'],Evidence_Level='compound',Direction=a['outcome'],Quantitative_Outcome=a['quantity'],Dose=a['dose'] or 'Not reported in reviewed abstract',Population=a['population'] or 'Not extracted',Study_Design='Open-label before/after or sequential PK investigation' if a['type']=='Human pharmacokinetic' else 'Experimental '+a['type'].lower()+' study; details limited to abstract',Source_Title=s['title'],Authors=s.get('authorString',''),Year=s['pubYear'],DOI=s.get('doi',''),PMID=a['pmid'],Source_Type='Primary research',Limitations='Abstract-only claim extraction; full methods, sample sizes or exact formulation may be incomplete. Preclinical results do not establish human food-drug effects. '+a['note'],Confidence='Primary abstract supports scoped claim; not independently adjudicated',Notes='No calculated values; separate compound and preparation attribution retained.',Study_ID='PMID:'+a['pmid'],Source_URL=f'https://pubmed.ncbi.nlm.nih.gov/{a["pmid"]}/',Source_Cache=f'release_v6_20261014/sources/pmid_{a["pmid"]}.json',Source_Locator='Primary abstract: Methods and Results; exact quoted support in v6 claim ledger',Preparation=a['preparation'],Affected_Entity=a['affected'],Perpetrator=a['perpetrator'],Outcome=a['outcome'],Conflict_Group='Thymoquinone-Doxorubicin-context-dependent' if a['compound']=='Thymoquinone' else '',Identity_Status=r['Identity_Status'],Release_Origin='v6_20261014',Clinical_Extrapolation='No clinical risk classification or food-exposure equivalence',CookRisk_Exposure_Link='Not linked to master retention observations')
  evidence.append(row)
  if a['outcome']=='observed effect':
   row['Direction']={'Hesperetin':'decreased drug metabolism','Diosmin':'increased parent drug exposure','Hesperidin':'increased parent drug exposure','6-Gingerol':'increased drug Cmax','Bergapten':'increased parent drug exposure','Thymoquinone':'cell-line-dependent enhanced drug response','Diallyl sulfide':'increased parent drug exposure'}[a['compound']]
  claims.append(dict(Evidence_ID=eid,PMID=a['pmid'],Claim=a['quantity'],Qualitative_Claim=a['effect'],Outcome=a['outcome'],Review_Level='Abstract-only',Source='sources/pmid_'+a['pmid']+'.json',Locator='Abstract Methods/Results',Supporting_Abstract=clean(s.get('abstractText','')),Missing_Details=a['note'] or 'Full methods not independently extracted'))
  changes.append(dict(Evidence_ID=eid,Action='added',Reason='New qualifying primary-source context',PMID=a['pmid'],Inherited_Change='None'))
  reviews.append(dict(Evidence_ID=eid,PMID=a['pmid'],Review_Level='Abstract-only',Source=row['Source_Cache'],Limitation=row['Limitations']))
 for r in registry:r['Evidence_Records']=str(sum(e['Compound_ID']==r['Compound_ID'] for e in evidence))
 write('stageB_food_drug_interactions_v6.csv',evidence);write('compound_registry.csv',registry);write('new_evidence_records.csv',evidence[118:]);write('candidate_selection.csv',selection);write('compound_selection_provenance_audit.csv',provenance);write('claim_support_and_outcome_audit.csv',claims);write('evidence_change_log.csv',changes)
 inherited=read(O/'inputs/stageB_food_drug_interactions_v5.csv');write('all_record_review_audit.csv',[dict(Evidence_ID=x['Evidence_ID'],PMID=x['PMID'],Review_Level='Inherited v5; prior extraction status retained, not newly full-text verified',Source=x['Source_Cache'],Limitation=x['Limitations']) for x in inherited]+reviews)
 write('identity_structure_audit.csv',[{k:r[k] for k in ['Compound_ID','Canonical_Name','PubChem_CID','InChIKey','Identity_Status','Identity_Source','Original_Molecular_Group','Link_Restriction']} for r in registry])
 write('cooking_retention_evidence.csv',read(O/'inputs/stageB_processing_evidence.csv'));write('processing_provenance_audit.csv',read(O/'inputs/processing_provenance_audit.csv'))
 warnings=read(O/'inputs/warning_resolution_ledger.csv')
 for w in warnings:
  old=w['After'];w['Before']=old
  w['After']='Resolved with supporting source' if old.startswith('resolved') else 'Partially resolved' if old.startswith('partially') else 'Not applicable after inspection' if w['Code']=='target_not_fully_reached' else 'Unresolved'
  w['Action']='Inspected v5 ledger and cited prior audit/cache; no new inherited correction. '+w['Action']
  if w['Code']=='target_not_fully_reached':w['Action']='V6 explicitly has no fixed evidence-row quota; old 150-row aspiration is not a v6 acceptance criterion.'
 for code,desc,affected in [('v6_anchor_target_gap','44/50 anchors admitted; six candidates deferred pending substantive scope/arm/source review','Six deferred candidates'),('v6_abstract_scope','All new interaction claims abstract-verified; available XML is not automatically full-text claim verification','New v6 records'),('v6_reference_stereochemistry','Reference structure does not certify study-tested enantiomer/geometric purity','Hesperetin; Hesperidin; 6-Gingerol; Cinnamaldehyde')]:
  warnings.append(dict(Warning_ID='V6-'+code,Code=code,Description=desc,Affected=affected,Classification='Research scope limitation',Before='New in v6',Action='Documented explicitly; no imputation',After='Unresolved',Remaining_Limitations=desc))
 write('warning_resolution_ledger.csv',warnings)
 registrychanges=[dict(Compound_ID=r['Compound_ID'],Action='added',Field='all',Before='',After=r['Canonical_Name'],Reason=r['Selection_Rationale']) for r in registry if r['Origin']=='added_v6'];write('registry_change_log.csv',registrychanges)
 studies=[]
 for p in sorted({x['PMID'] for x in evidence}):
  rs=[x for x in evidence if x['PMID']==p];r=rs[0];cp=O/'sources'/('crossref_'+p+'.json');d=load(cp) if cp.exists() else {};msg=d.get('message',{});title=' '.join(msg.get('title',[]));normalize=lambda t:re.sub('[^a-z0-9]','',clean(t).lower())
  verification='Crossref title concordant' if title and normalize(title)==normalize(r['Source_Title']) else 'Crossref unavailable/not repeated; MED verified' if not title else 'Crossref title requires review'
  studies.append(dict(PMID=p,DOI=r['DOI'],Title=r['Source_Title'],Evidence_Records=len(rs),Review_Level='New abstract-verified' if any(x['Release_Origin']=='v6_20261014' for x in rs) else 'Inherited v5 review retained',Verification=verification,Independent_Trial_Count='Not inferred; repeated/overlapping cohorts possible'))
 write('study_registry.csv',studies);write('interaction_evidence_source_audit.csv',studies)
 screening=[];seen=set()
 for p in sorted((O/'sources').glob('*search*.json'))+sorted((O/'sources').glob('target_*.json')):
  for h in load(p).get('resultList',{}).get('result',[]):
   key=(p.name,h.get('id'))
   if key in seen:continue
   seen.add(key);screening.append(dict(Cache='sources/'+p.name,ID=h.get('id',''),Title=h.get('title',''),Status='included primary context; see evidence ledger' if h.get('id') in {x['pmid'] for x in ROWS} else 'candidate_not_fully_screened',Source=h.get('source','')))
 write('screening_log.csv',screening)
 summary=dict(version='v6',anchors=len(registry),records=len(evidence),drugs=len({x['Drug'] for x in evidence}),publications=len(studies),numerical_records=sum(bool(x['Quantitative_Outcome']) for x in evidence),classes=dict(collections.Counter(x['Evidence_Type'] for x in evidence)),new_anchors=len(FOOD),new_records=len(ROWS),new_publications=len({x['pmid'] for x in ROWS}-{x['PMID'] for x in inherited}),target=50,target_gap=50-len(registry),new_abstract_records=len(ROWS),new_full_text_verified_records=0,warning_entries=sum(w['After'] in ['Unresolved','Partially resolved'] for w in warnings),distinct_warning_codes=len({w['Code'] for w in warnings if w['After'] in ['Unresolved','Partially resolved']}),issue_status_counts=dict(collections.Counter(w['After'] for w in warnings)),discovery_occurrences=len(screening))
 (O/'outputs/release_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
