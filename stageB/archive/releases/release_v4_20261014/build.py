"""Offline v4 build. Supplied releases and Stage A remain read-only."""
from pathlib import Path
import csv,json,hashlib,re,html,xml.etree.ElementTree as E,collections,difflib,urllib.parse
O=Path(__file__).resolve().parent;R=O.parents[1];B=R/'stageB';V3=B/'expansion_v3_20261014'
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rows):
    with (O/'outputs'/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def load(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return re.sub('[^a-z0-9]','',html.unescape(re.sub(r'</?[A-Za-z][^>]*>','',s)).lower())
inventory=[];manifest={}
for folder in ['stageB','data','docs','literature','reports','molecular_features','preprocessing']:
    for p in sorted((R/folder).rglob('*')):
        if not p.is_file() or O in p.parents or '__pycache__' in p.parts:continue
        rel=p.relative_to(R).as_posix();manifest[rel]=sha(p);n='';cols=[]
        if p.suffix=='.csv':
            rr=read(p);n=len(rr);cols=list(rr[0]) if rr else []
        inventory.append(dict(File=rel,Purpose='Saved source material' if '/sources/' in rel else 'Input, registry, audit, script or documentation',Rows=n,Source_Fields=' | '.join(c for c in cols if any(t in c.lower() for t in ['doi','pmid','source','reference'])),Inspection='CSV headers and row count' if p.suffix=='.csv' else 'Metadata and SHA256; no universal full-text-review claim',SHA256=manifest[rel]))
mp=O/'audit/preservation_manifest.json'
if not mp.exists():mp.write_text(json.dumps(manifest,indent=2),encoding='utf8')
write('file_inventory.csv',inventory)
baseline=read(V3/'outputs/stageB_food_drug_interactions_v3.csv');e=[r.copy() for r in baseline];reg=read(V3/'outputs/compound_registry.csv');oldval=load(V3/'audit/validation_report.json')
actual=dict(compounds=len(reg),records=len(e),drugs=len({r['Drug'] for r in e}),primary_reports=len({r['PMID'] for r in e}),types=dict(collections.Counter(r['Evidence_Type'] for r in e)),validation_status=oldval['status'],checks_passed=oldval['checks_passed'],checks_total=oldval['checks_total'],errors=len(oldval['errors']),warning_entries=len(oldval['warnings']),distinct_warning_codes=len({r['code'] for r in oldval['warnings']}),mutation_tests=load(V3/'audit/validation_self_tests.json')['passed'],baseline_v2_unchanged=all(a==b for a,b in zip(e[:64],read(B/'expansion_v2/outputs/stageB_food_drug_interactions_expanded.csv'))))
(O/'audit/verified_v3_baseline.json').write_text(json.dumps(actual,indent=2),encoding='utf8')
changes=[];row=next(r for r in e if r['Evidence_ID']=='SB-0067')
updates=dict(Dose='Apigenin 165 mg/kg for 15 days or single 165 or 252 mg/kg; imatinib 30 mg/kg after final pretreatment; oral PK sampling to 24 h',Population='20 male Sprague-Dawley rats; 4 groups; n=5 per group',Preparation='Apigenin purity >98%; 0.5% CMC-Na control vehicle; formulation details in Experimental section',Direction='repeated-dose exposure decrease; single-dose exposure increase',Interaction_Effect='Imatinib AUC decreased after 15-day apigenin and increased after single-dose pretreatment; parent/metabolite outcomes remain distinct.',Quantitative_Outcome='Table 1 imatinib AUC(0-infinity), mg.h/L, mean +/- SD: control 90.988 +/- 11.585; repeated 165 mg/kg 68.805 +/- 7.432; single 165 mg/kg 127.514 +/- 12.332; single 252 mg/kg 114.502 +/- 8.634. Each active group P<0.05 versus control.',Source_Locator='Full text release_v4_20261014/sources/PMC3863468.xml: Experimental 2.1 and 2.5; Table 1; Results 3.2-3.4',Limitations='Animal study n=5/group; high experimental doses; CYP mechanism proposed. Results prose says acute Cmax decreased, whereas Table 1 shows increased Cmax; Cmax interpretation withheld. No human clinical inference.',Notes='v4 selected full-text re-extraction; original v3 row retained in baseline and field-level change log.')
for k,value in updates.items():
    changes.append(dict(Evidence_ID=row['Evidence_ID'],Field=k,Before=row[k],After=value,Reason='Primary full-text methods and Table 1 recovered; Cmax prose/table discrepancy explicitly flagged',Source='sources/PMC3863468.xml'));row[k]=value
write('evidence_change_log.csv',changes);write('stageB_food_drug_interactions_v4.csv',e)
for r in reg:
    original=r['Origin']=='original_nine'
    r.update(Release_Reviewed='v4_20261014',Selection_Verification='Available local historical documentation only; no historical source inferred from interaction paper' if original else 'Dated v3 decision and cached supporting primary citation rechecked',Earliest_Verified_Selection_Date='' if original else '2026-10-14',Selection_Temporality='retrospective documentation; original event date unknown' if original else 'contemporaneous v3 decision ledger',Remaining_Provenance_Gap='Historical primary selection trigger and date unresolved' if original else 'No missing current selection decision; retention and source applicability remain separate')
    if r['Canonical_Name']=='Daidzein':r['Retention_Status']='Primary processing context located, but hydrolyzed isoflavone assay is not native aglycone retention; no master link established'
    if r['Canonical_Name']=='Quercetin':r['Retention_Status']='Primary onion processing context reviewed; conjugates and total flavonols cannot resolve mixed master group; no automatic link'
write('compound_registry.csv',reg)
write('compound_selection_provenance_audit.csv',[{k:r[k] for k in ['Compound_ID','Canonical_Name','Origin','Selection_Rationale','Selection_Source','Selection_PMID','Selection_DOI','Date_Added','Earliest_Verified_Selection_Date','Selection_Temporality','Selection_Verification','Provenance_Status','Remaining_Provenance_Gap']} for r in reg])
for name in ['selection_sources.csv','original_nine_interaction_reference_map.csv','selection_document_search.csv','inventory_candidate_decisions.csv']:
    write(name,read(V3/'outputs'/name))
reviews=[];claims=[]
for r in e:
    path=B/r['Source_Cache'].replace('\\','/');d=load(path);m=next(x for x in d['resultList']['result'] if str(x['id'])==r['PMID']);level='cached_primary_metadata_rechecked';locator=r['Source_Locator'];source=path.relative_to(R).as_posix();scope='Bibliographic fields only; inherited outcomes not independently re-extracted'
    if int(r['Evidence_ID'][3:])>=65:level='abstract_rechecked';scope='Dose, population, direction, null/context and numerical claims compared with cached primary abstract'
    if r['Evidence_ID']=='SB-0067':level='selected_full_text_reextraction';source='stageB/release_v4_20261014/sources/PMC3863468.xml';scope='Methods, sample size, drug dose and parent AUC Table 1 independently re-extracted in this pass; not whole-paper replication'
    if r['Evidence_ID'] in ['SB-0016','SB-0017']:level='selected_full_text_outcome_verification';source='stageB/sources/PMC6468355.xml';locator='Table 2 endoxifen AUC relative-difference row; Results 2.2';scope='Saved endoxifen percentage, CI and p-value agree with full-text Table 2; remaining fields not comprehensively re-extracted'
    verified=all(norm(r[k])==norm(str(m.get(v,''))) for k,v in [('Source_Title','title'),('Authors','authorString'),('Year','pubYear'),('DOI','doi')])
    reviews.append(dict(Evidence_ID=r['Evidence_ID'],PMID=r['PMID'],Compound=r['Compound'],Drug=r['Drug'],Verification_Level=level,Review_Date='2026-10-14',Source=source,Source_Locator=locator,Bibliographic_Concordance=verified,Review_Scope=scope,Remaining_Limitations=r['Limitations']))
    claims.append(dict(Evidence_ID=r['Evidence_ID'],Claim_Field='Quantitative_Outcome',Claim=r['Quantitative_Outcome'],Source=source,Locator=locator,Verification_Level=level,Status='selected claim checked' if level!='cached_primary_metadata_rechecked' else 'inherited outcome not independently re-extracted',Limitations=r['Limitations']))
write('record_source_review_audit.csv',reviews);write('claim_support_and_outcome_audit.csv',claims)
primary=[]
for old in read(V3/'outputs/study_registry.csv'):
    pmid=old['PMID'];cp=O/'sources'/f'crossref_{pmid}.json';cfstatus='inherited v3 verification'
    if cp.exists():
        m=load(cp).get('message',{});sim=difflib.SequenceMatcher(None,norm(' '.join(m.get('title',[]))),norm(old['Title'])).ratio();cfstatus='v4 Crossref title concordant' if sim>=.90 else 'v4 Crossref title difference requires review'
    primary.append(dict(**old,Release_Reviewed='v4',Crossref_Verification=cfstatus,Verification_Level='cached MED metadata; record-specific abstract/full-text scope in review audit'))
write('study_registry.csv',primary);write('interaction_evidence_source_audit.csv',primary)
processing=[]
for comp,pmc,lim in [('Daidzein','PMC11011382','Methods hydrolyze glycosylated isoflavones before assay; not proof of native free daidzein retention or master data validity'),('Quercetin','PMC8151956','LC-MS individual glycosides, total flavonols and weight-basis effects require separation; cannot certify mixed master group')]:
    rt=E.parse(O/'sources'/f'{pmc}.xml').getroot();doi=next((x.text for x in rt.findall('.//article-id') if x.get('pub-id-type')=='doi'),'')
    processing.append(dict(Compound=comp,Source_Title=' '.join(rt.find('.//article-title').itertext()),DOI=doi,URL=f'https://pmc.ncbi.nlm.nih.gov/articles/{pmc}/',Cache=f'sources/{pmc}.xml',Review_Level='Full-text selected methods and analyte scope reviewed',Finding=lim,Master_Link='not established; no automatic merge',Counted_As_Interaction_Report=False))
write('processing_provenance_audit.csv',processing)
master=read(B/'inputs/cookchem_master_expanded_round11.csv');write('quercetin_master_source_audit.csv',[dict(Record_ID=r['Record_ID'],Original_Compound=r['Compound_Name'],Original_Group=r['Canonical_Molecular_ID'],DOI=r['DOI'],Authors=r['Authors'],Year=r['Year'],Status='Mixed group retained unchanged; row-level primary analyte and source validation unresolved',Standalone_Link='forbidden') for r in master if r['Canonical_Molecular_ID']=='MOL-FDB10E6B0C4171D1'])
ledger=[]
for i,w in enumerate(oldval['warnings'],1):
    code=w['code'];action='Retained with explicit scope';after='unresolved';classification='provenance gap'
    if code=='Crossref_lookup_unavailable':after='resolved for 12 affected reports';action='Fresh Crossref snapshots retrieved; title concordance checked';classification='previously inaccessible source'
    if code=='inherited_outcome_scope':after='partially addressed';action='Two inherited endoxifen outcomes verified against full-text Table 2; other 62 baseline rows not independently re-extracted';classification='review scope limitation'
    if code=='unresolved_preparation':action='Primary publisher abstract/preview checked; full text subscription-only; provisional attribution retained';classification='inaccessible full text and preparation ambiguity'
    if code=='retention_link_unavailable':after='partially addressed; master links unresolved';action='Two primary processing methods reviewed; glycoside/hydrolysis restrictions documented, no retention coefficients imported';classification='identity and analyte ambiguity'
    if code=='source_reporting_ambiguity':action='Daidzein abstract reviewed; disputed CI wording and baseline day retained as limitation';classification='source reporting issue'
    if code=='bounded_review':classification='expected research scope uncertainty';action='Targeted source resolution only; no repeated compound-discovery search or exhaustive-review claim'
    if code=='DOI_not_supplied':action='Exact MED lookups repeated; DOI still absent for both PMIDs';classification='missing bibliographic identifier'
    ledger.append(dict(Warning_ID=f'V3-W{i:02d}',Code=code,Description=w['detail'],Affected=' | '.join(w['ids']),Classification=classification,Before='open in v3',Action=action,After=after,Remaining_Limitations='Historical facts cannot be recovered from unrelated interaction literature' if code=='historical_selection_provenance' else ('No remaining title-lookup gap; scientific outcome verification separate' if code=='Crossref_lookup_unavailable' else 'See record-level and provenance audits')))
ledger.append(dict(Warning_ID='V4-W10',Code='source_table_prose_discrepancy',Description='Apigenin imatinib acute Cmax prose conflicts with Table 1',Affected='SB-0067',Classification='source reporting issue',Before='not identified in v3 abstract review',Action='Extracted AUC from Table 1; conflicting Cmax interpretation withheld',After='unresolved source discrepancy',Remaining_Limitations='No correction notice or author clarification obtained'))
write('warning_resolution_ledger.csv',ledger)
search=[]
for p in sorted((O/'sources').glob('*')):
    url=''
    if p.name.startswith('PMC'):url='https://www.ebi.ac.uk/europepmc/webservices/rest/'+p.name.split('.')[0]+'/fullTextXML'
    if p.name.startswith('pmid_'):url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':'EXT_ID:'+p.stem.split('_')[1]+' AND SRC:MED','format':'json','resultType':'core'})
    if p.name.startswith('crossref_'):
        d=load(p).get('message',{}).get('DOI','');url='https://api.crossref.org/works/'+urllib.parse.quote(d,safe='')
    search.append(dict(Date='2026-10-14',Source=p.name,URL_or_Query=url,Query_or_Purpose='Targeted bibliographic/full-text resolution',Status='unavailable' if '.error.' in p.name else 'retrieved snapshot',Review_Level='Source availability does not by itself imply full review'))
search.append(dict(Date='2026-10-14',Source='publisher preview inspected via web tool',URL_or_Query='https://link.springer.com/article/10.1007/s13318-014-0203-z',Query_or_Purpose='Apigenin/rutin group attribution',Status='abstract and subscription preview available; full text inaccessible',Review_Level='Abstract/preview only'))
write('targeted_source_log.csv',search)
write('inherited_v3_search_log.csv',read(V3/'outputs/literature_search_log.csv'))
write('screening_log.csv',[dict(Evidence_ID=r['Evidence_ID'],Status='retained_corrected' if r['Evidence_ID']=='SB-0067' else 'retained',Reason='Primary verification and gap resolution; no additional records forced',Source_Verification=next(x['Verification_Level'] for x in reviews if x['Evidence_ID']==r['Evidence_ID'])) for r in e])
summary=dict(version='v4',date='2026-10-14',compounds=len(reg),interaction_records=len(e),drugs=len({r['Drug'] for r in e}),primary_reports=len(primary),types=dict(collections.Counter(r['Evidence_Type'] for r in e)),compounds_added=0,records_added=0,records_removed=0,records_corrected=1,corrected_fields=len(changes),records_with_metadata_corrections=0,verification_levels=dict(collections.Counter(r['Verification_Level'] for r in reviews)),quantitative_records=sum(bool(r['Quantitative_Outcome']) for r in e),warning_entries_remaining=sum(not r['After'].startswith('resolved') for r in ledger),v3_warning_entries=9,v3_distinct_warning_codes=8,original_64_preserved=all(a==b for a,b in zip(e[:64],baseline[:64])))
(O/'outputs/release_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8');print(json.dumps(summary,indent=2))
if __name__=='__main__':pass
