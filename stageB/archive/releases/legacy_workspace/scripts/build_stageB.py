"""Offline deterministic Stage B build from immutable inputs and curated source caches."""
import csv,json,re,hashlib,html
from pathlib import Path
from collections import Counter,defaultdict
from curated_evidence import E
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'outputs'; REPORT=ROOT/'reports'; REPORT.mkdir(exist_ok=True)
D=(ROOT/'inputs') if (ROOT/'inputs'/'cookchem_master_expanded_round11.csv').exists() else Path('C:/Users/dakshant/Downloads')
def read(p): return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def write(name,rows,fields=None):
    if fields is None: fields=list(rows[0])
    with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='raise'); w.writeheader(); w.writerows(rows)
def md(name,text): (REPORT/name).write_text(text.strip()+'\n',encoding='utf-8')
def table(headers,rows): return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(str(v).replace('|',';').replace('\n',' ') for v in r)+' |' for r in rows)
data=read(D/'cookchem_master_expanded_round11.csv'); raw_oof=read(D/'stageA_oof_predictions.csv'); oof=[r for r in raw_oof if r['Model']=='ExtraTrees_reference']; by_record={r['Record_ID']:r for r in data}
mapping=read(OUT/'stageB_compound_mapping.csv'); maps={r['Canonical_Molecular_ID']:r for r in mapping}; groups=defaultdict(list)
for r in data:
    if r['Canonical_Molecular_ID']: groups[r['Canonical_Molecular_ID']].append(r)
source_by_id={}; source_paths={}
for p in sorted((ROOT/'sources').glob('selected_*.json')):
    for r in json.loads(p.read_text(encoding='utf-8')).get('resultList',{}).get('result',[]): source_by_id[r['id']]=r; source_paths[r['id']]=p.relative_to(ROOT).as_posix()
def metadata(sid):
    s=source_by_id[sid]; url=f'https://pubmed.ncbi.nlm.nih.gov/{s["id"]}/' if s['source']=='MED' else 'https://doi.org/'+s['doi']
    return {'source_title':s['title'],'authors':s.get('authorString',''),'journal':s.get('journalInfo',{}).get('journal',{}).get('title',''),'year':s.get('pubYear',''),'doi':s.get('doi',''),'source_url':url,'citation':f'{s.get("authorString","")} ({s.get("pubYear","")}). {s["title"]} {s.get("journalInfo",{}).get("journal",{}).get("title","")}.','source_id':sid,'source_cache':source_paths[sid]}
names={}
for k,r in maps.items():
    for n in r['CookRisk_compound_name'].split(' | '): names.setdefault(n,[]).append(k)
compounds=['Berberine','Piperine','Curcumin','EGCG','Caffeine']
for n in compounds:
    assert len(names[n])==1 and maps[names[n][0]]['mapping_status'].startswith('verified'),(n,names[n])
drugnames=sorted({r['drug'] for r in E}); drugids={n:f'DRUG-{i:03}' for i,n in enumerate(drugnames,1)}
foodrows=[]; foodids={}
for i,n in enumerate(sorted({r['Food_Name'] for r in data if r['Food_Name']}),1): foodids[n]=f'FOOD-{i:03}'; foodrows.append({'food_id':foodids[n],'food_name':n,'food_scope':'CookRisk dataset label','source':'Supplied modelling master; original food names retained'})
for n in sorted({r.get('food_name','') for r in E if r.get('food_name')}):
    if n not in foodids: foodids[n]=f'FOOD-{len(foodids)+1:03}'; foodrows.append({'food_id':foodids[n],'food_name':n,'food_scope':'Literature-studied preparation/extract','source':'Interaction source; not asserted equivalent to a CookRisk food label'})
fields='interaction_id food_id food_name Canonical_Molecular_ID compound_id compound_name standardized_compound_name compound_identifier compound_synonyms drug_id drug_name drug_identifier drug_class interaction_type mechanism mechanism_category effect_direction effect_description enzyme_or_transporter pathway dose concentration duration frequency AUC_change Cmax_change Tmax_change clearance_change half_life_change study_type evidence_type species_or_population sample_size clinical_relevance source_title authors journal year doi source_url citation processing_relevance processing_effect_description stageA_link_available limitations notes source_id source_cache source_locator evidence_level compound_form co_compounds affected_entity perpetrator_entity record_outcome quantitative_result conflict_group identity_resolution_scope'.split()
interactions=[]; oofgroups={r['Canonical_Molecular_ID'] for r in oof}
for i,e in enumerate(E,1):
    key=names[e['compound']][0]; m=maps[key]; r={f:'' for f in fields}
    for f in fields:
        if f in e: r[f]=e[f]
    r.update(metadata(e['source']))
    r.update(interaction_id=f'SB-{i:04}',Canonical_Molecular_ID=key,compound_id=key,compound_name=e['compound'],standardized_compound_name=m['standardized_compound_name'],compound_identifier='PubChem CID:'+m['PubChem_CID'],compound_synonyms=m['synonyms'],drug_id=drugids[e['drug']],drug_name=e['drug'],interaction_type='Pharmacodynamic | Pharmacokinetic' if e['evidence_type']=='Controlled clinical' else ('Pharmacodynamic' if e['drug']=='Bortezomib' else 'Pharmacokinetic'),stageA_link_available=str(key in oofgroups).lower(),evidence_level=e.get('evidence_level','compound'),compound_form=e.get('compound_form',e['compound']+' as named by study; precise preparation not extracted'),affected_entity=e.get('affected_entity','drug'),perpetrator_entity=e.get('perpetrator_entity','compound_or_preparation'),record_outcome=e.get('record_outcome','observed_effect'),identity_resolution_scope=m['mapping_status'])
    r['clinical_relevance']='Clinical relevance not established' if e['evidence_type'] in ['Animal','In vitro'] else ('No meaningful PK effect observed under tested conditions' if r['record_outcome']=='null_finding' else ('pharmacodynamic effect observed' if e['evidence_type']=='Controlled clinical' else 'pharmacokinetic effect observed'))
    if r['food_name']: r['food_id']=foodids[r['food_name']]
    if e['compound']=='Piperine': r.update(processing_relevance='Separate processing evidence available',processing_effect_description='Boiling/pressure cooking affected piperine in black pepper (Suresh et al. 2007; DOI 10.1016/j.jfca.2006.10.002). No interaction-exposure conversion.')
    elif e['compound']=='Curcumin': r.update(processing_relevance='Separate processing evidence available',processing_effect_description='Cooking altered curcumin in turmeric (Suresh et al. 2007; DOI 10.1016/j.jfca.2006.10.002). Separate from Stage A and supplement intervention.')
    elif e['compound']=='EGCG': r.update(processing_relevance='Separate processing evidence available',processing_effect_description='Green-tea brewing changes extraction/epimerization (Jin et al. 2019; DOI 10.3390/molecules24091735). No derived interaction magnitude.')
    if m['mapping_status']=='verified_connectivity': r['limitations']+=' CookRisk name/CID/connectivity match; input SMILES stereochemistry incomplete. Link is to named parent identity, not a verified stereochemical exposure.'
    interactions.append(r)
write('stageB_food_drug_interactions.csv',interactions,fields)
drugs=[{'drug_id':drugids[n],'drug_name':n,'drug_identifier':'','drug_class':'','identifier_status':'Local database key; external identifier not independently resolved','supporting_source_ids':' | '.join(sorted({r['source_id'] for r in interactions if r['drug_name']==n}))} for n in drugnames]
write('stageB_drugs.csv',drugs); write('stageB_foods.csv',foodrows)
evidence=[{'interaction_id':r['interaction_id'],'compound':r['compound_name'],'drug':r['drug_name'],'study_type':r['study_type'],'evidence_type':r['evidence_type'],'population':r['species_or_population'],'effect':r['effect_description'],'mechanism':r['mechanism'],'quantitative_result':r['quantitative_result'],'source_title':r['source_title'],'authors':r['authors'],'year':r['year'],'doi':r['doi'],'source_url':r['source_url'],'limitations':r['limitations'],'source_id':r['source_id'],'source_cache':r['source_cache'],'source_locator':r['source_locator'],'record_outcome':r['record_outcome']} for r in interactions]
write('stageB_literature_evidence.csv',evidence)
rel=[]
for r in interactions:
    rel.append({'interaction_id':r['interaction_id'],'Canonical_Molecular_ID':r['Canonical_Molecular_ID'],'role':'anchor_named_identity'})
    for n in r['co_compounds'].split(' | '):
        if n and len(names.get(n,[]))==1 and maps[names[n][0]]['mapping_status'].startswith('verified'): rel.append({'interaction_id':r['interaction_id'],'Canonical_Molecular_ID':names[n][0],'role':'co_intervention_not_independently_attributable'})
write('stageB_interaction_compounds.csv',rel)
obslinks=[]
for o in oof:
    d=by_record[o['Record_ID']]; assert d['Canonical_Molecular_ID']==o['Canonical_Molecular_ID']; assert abs(float(d['Retention_Final'])-float(o['actual']))<1e-6
    obslinks.append({'Record_ID':o['Record_ID'],'Canonical_Molecular_ID':o['Canonical_Molecular_ID'],'Food_Name':d['Food_Name'],'Cooking_Method':d['Cooking_Method'],'Temperature_C':d['Temperature_C'],'Cooking_Time_min':d['Cooking_Time_min'],'Initial_Concentration':d['Initial_Concentration'],'Initial_Unit':d['Initial_Unit'],'stageA_model':o['Model'],'OOF_actual_retention_percent':o['actual'],'OOF_predicted_retention_percent':o['predicted'],'OOF_fold':o['fold'],'OOF_source_row':raw_oof.index(o)+2,'OOF_source_path':str(D/'stageA_oof_predictions.csv'),'interpretation':'OOF validation output only. Concentration, consumed amount and bioavailability are separate; no clinical risk inference.'})
write('stageB_stageA_observation_links.csv',obslinks)
fc=[]
for key,rs in groups.items():
    for food in sorted({r['Food_Name'] for r in rs if r['Food_Name']}): fc.append({'food_id':foodids[food],'food_name':food,'Canonical_Molecular_ID':key,'Record_IDs':' | '.join(r['Record_ID'] for r in rs if r['Food_Name']==food),'mapping_status':maps[key]['mapping_status'],'claim_scope':'Recorded food-compound association in supplied CookRisk master; source concentration not revalidated'})
write('stageB_food_compounds.csv',fc)
link=[]
for key,m in maps.items():
    ir={r['interaction_id'] for r in rel if r['Canonical_Molecular_ID']==key}; relevant=[r for r in interactions if r['interaction_id'] in ir]
    m['interaction_evidence_status']='Qualifying evidence retained' if ir else ('Identity uncertain; no interaction assigned' if m['mapping_status']=='uncertain' else 'No qualifying evidence retained in this limited search release')
    link.append({'Canonical_Molecular_ID':key,'compound_name':m['CookRisk_compound_name'],'standardized_compound_name':m['standardized_compound_name'],'observation_count':len(groups[key]),'stageA_prediction_available':str(key in oofgroups).lower(),'OOF_observation_count':sum(r['Canonical_Molecular_ID']==key for r in oof),'stageA_model':'ExtraTrees_reference' if key in oofgroups else '', 'food_count':len({r['Food_Name'] for r in groups[key] if r['Food_Name']}),'interaction_record_count':len(ir),'drug_count':len({r['drug_name'] for r in relevant}),'mapping_status':m['mapping_status'],'notes':'Interaction count includes explicit co-interventions. Uncertain groups not assigned. No group-level retention value generated.'})
write('stageB_compound_mapping.csv',mapping); write('stageB_stageA_linkage.csv',link)
processing=[]
for name,source,food,effect,quant,conditions in [('Piperine','IND43886445','Black pepper','Cooking-associated loss','16-34% piperine loss','Boiling 10 or 20 min; pressure cooking 10 min'),('Curcumin','IND43886445','Turmeric','Cooking-associated loss; matrix matters','27-53% loss; 12-30% with tamarind','Boiling 10 or 20 min; pressure cooking 10 min'),('EGCG','31060206','Green tea infusion','Extraction and epimerization change with brewing; total catechin peak is not isolated EGCG retention','Total catechins peaked at 95 C, 10 min','60 C or 95 C; 5-300 min')]:
    processing.append({'processing_id':f'PROC-{len(processing)+1:03}','Canonical_Molecular_ID':names[name][0],'compound_name':name,'food_name':food,'processing_conditions':conditions,'effect_description':effect,'quantitative_result':quant,**metadata(source),'limitations':'Original processing result; not a drug-interaction experiment, Stage A output, or universal retention coefficient.'})
write('stageB_processing_evidence.csv',processing)
excluded=[{'compound':'Quercetin','candidate_source_id':sid,'reason':'MOL-FDB10E6B0C4171D1 mixes Quercetin and total flavonols; identity uncertain at group level. Retain candidate without assigning interaction.'} for sid in ['19221726','21680781','25988261']]
excluded.append({'compound':'Vitamin C / ascorbic acid','candidate_source_id':'21400028','reason':'CookRisk group includes total L-AA+DHAA; do not equate total vitamin C with isolated ascorbic acid.'})
write('stageB_exclusions.csv',excluded)
search=read(ROOT/'sources/search_log.csv'); search=[r for r in search if r['Canonical_Molecular_ID']]
for r in search: r['screening_status']='targeted_selected_sources_screened' if r['Canonical_Molecular_ID'] in {names[n][0] for n in compounds} else 'candidate_retrieval_only_not_exhaustively_screened'
write('stageB_search_log.csv',search)
catalog=[]
for s in search:
    p=ROOT/'sources'/(s['Canonical_Molecular_ID'].replace(':','_')+'_search.json')
    for r in json.loads(p.read_text(encoding='utf-8')).get('resultList',{}).get('result',[]): catalog.append({'Canonical_Molecular_ID':s['Canonical_Molecular_ID'],'source_id':r['id'],'source_database':r['source'],'title':r['title'],'year':r.get('pubYear',''),'doi':r.get('doi',''),'screening_status':'selected_source_reviewed' if r['id'] in source_by_id else 'not_manually_screened','cache':p.relative_to(ROOT).as_posix()})
write('stageB_search_candidates.csv',catalog)
conflicts=[{'conflict_group':k,'interaction_ids':' | '.join(r['interaction_id'] for r in interactions if r['conflict_group']==k),'synthesis':v} for k,v in {
 'Piperine-Carbamazepine':'Human single-dose piperine increased exposure; repeated rat co-treatment decreased exposure despite metabolic inhibition. Species/regimen/context differ. Microsomal inhibition is a separate assay result; no common effect coefficient.',
 'Piperine-Midazolam':'Isolated piperine study reported longer sedation/lower clearance; short-term curcuminoid/piperine mixture showed no meaningful parent-midazolam PK change. Different preparation/regimen; not a pure same-intervention replication.',
 'Curcumin-Tamoxifen':'Rat oral exposure increased; human tamoxifen exposure decreased with curcumin with/without piperine. Different species and metabolites; curcumin-only human endoxifen contrast p=0.07.',
 'EGCG-Bortezomib':'Cell assays showed antagonism; xenografts showed concentration dependence and no antagonism at 11-16 uM, but antagonism above 200 uM. No human clinical interaction established.'}.items()]
write('stageB_conflict_synthesis.csv',conflicts)
source_audit=read(OUT/'stageB_dataset_source_audit.csv') if (OUT/'stageB_dataset_source_audit.csv').exists() else []
source_status={r['DOI']:r['status'] for r in source_audit}
for r in obslinks:
    d=by_record[r['Record_ID']]
    r['dataset_DOI']=d['DOI']; r['dataset_source_metadata_status']=source_status.get(d['DOI'].lower(),'not_audited')
    r['master_eligibility_flag']=d['Final_Preprocessing_Eligible']
    r['measurement_source_verification_status']='Original measurements not independently verified; metadata match alone insufficient'
write('stageB_stageA_observation_links.csv',obslinks)
for r in fc:
    records=[by_record[x] for x in r['Record_IDs'].split(' | ')]
    r['dataset_source_metadata_status']=' | '.join(sorted({source_status.get(d['DOI'].lower(),'not_audited') for d in records}))
write('stageB_food_compounds.csv',fc)
cidgroups=defaultdict(list)
for r in mapping:
    if r['PubChem_CID']: cidgroups[r['PubChem_CID']].append(r)
collisions=[{'PubChem_CID':cid,'Canonical_Molecular_IDs':' | '.join(r['Canonical_Molecular_ID'] for r in rs),'names':' | '.join(r['CookRisk_compound_name'] for r in rs),'decision':'Original groups preserved; no merge. Molecular model grouping may require separate historical audit.'} for cid,rs in cidgroups.items() if len(rs)>1]
write('stageB_duplicate_standardized_identities.csv',collisions,['PubChem_CID','Canonical_Molecular_IDs','names','decision'])
counts={'molecular_groups':len(mapping),'observations':len(data),'unassigned_observations':sum(not r['Canonical_Molecular_ID'] for r in data),'unique_compound_names':len({r['Compound_Name'] for r in data}),'food_names':len({r['Food_Name'] for r in data if r['Food_Name']}),'food_categories':None,'standardized_mapping_rows':sum(r['mapping_status'].startswith('verified') for r in mapping),'distinct_standardized_compounds':len({r['PubChem_CID'] for r in mapping if r['PubChem_CID']}),'verified_exact':sum(r['mapping_status']=='verified_exact' for r in mapping),'verified_connectivity':sum(r['mapping_status']=='verified_connectivity' for r in mapping),'uncertain_identity':sum(r['mapping_status']=='uncertain' for r in mapping),'compounds_searched':len(search),'anchor_compounds_with_evidence':len({r['Canonical_Molecular_ID'] for r in interactions}),'compounds_including_verified_cointerventions':len({r['Canonical_Molecular_ID'] for r in rel}),'unique_drugs':len(drugs),'interaction_records':len(interactions),'unique_interaction_sources':len({r['source_id'] for r in interactions}),'human_records':sum(r['evidence_type'] in ['Human pharmacokinetic','Controlled clinical','Human clinical'] for r in interactions),'animal_records':sum(r['evidence_type']=='Animal' for r in interactions),'in_vitro_records':sum(r['evidence_type']=='In vitro' for r in interactions),'in_silico_mechanistic_only_records':sum(r['evidence_type'] in ['In silico','Mechanistic'] for r in interactions),'quantitative_PK_PD_records':sum(bool(r['quantitative_result'] or any(r[f] for f in ['AUC_change','Cmax_change','clearance_change','half_life_change'])) for r in interactions),'negative_control_records':sum(r['record_outcome']=='null_finding' for r in interactions),'records_linked_stageA':sum(r['stageA_link_available']=='true' for r in interactions),'OOF_rows':len(oof),'OOF_groups':len(oofgroups),'evidence_distribution':dict(Counter(r['evidence_type'] for r in interactions)),'mechanism_distribution':dict(Counter(c for r in interactions for c in r['mechanism_category'].split(' | ') if c)),'search_hit_truncation_groups':sum(int(r['hit_count'])>25 for r in search)}
(OUT/'stageB_summary.json').write_text(json.dumps(counts,indent=2),encoding='utf-8')
counts.update(dataset_DOIs_audited=len(source_audit),dataset_DOIs_metadata_mismatch=sum(r['status']=='metadata_mismatch_source_verification_required' for r in source_audit),dataset_DOIs_retrieval_unavailable=sum(r['status']=='retrieval_unavailable' for r in source_audit),selected_OOF_rows_master_ineligible=sum(by_record[r['Record_ID']]['Final_Preprocessing_Eligible']!='TRUE' for r in oof),duplicate_standardized_identity_clusters=len(collisions))
counts['quantitative_outcome_records']=counts['quantitative_PK_PD_records']
counts['quantitative_biochemical_assay_records']=sum(bool(r['quantitative_result']) and r['evidence_type']=='In vitro' for r in interactions)
counts['quantitative_PK_PD_records']-=counts['quantitative_biochemical_assay_records']
(OUT/'stageB_summary.json').write_text(json.dumps(counts,indent=2),encoding='utf-8')
print(json.dumps(counts,indent=2))
# Automated QC establishes referential integrity; manual checks are documented separately.
checks={
 'unique_interaction_ids':len({r['interaction_id'] for r in interactions})==len(interactions),
 'complete_compound_universe':set(maps)==set(groups),
 'unique_compound_mapping_ids':len(maps)==len(mapping),
 'unique_drug_ids_and_names':len({r['drug_id'] for r in drugs})==len(drugs)==len(set(drugnames)),
 'mapped_external_identifier_format':all(re.fullmatch(r'\d+',r['PubChem_CID']) and r['InChI'].startswith('InChI=1S/') and re.fullmatch(r'[A-Z]{14}-[A-Z]{10}-[A-Z]',r['InChIKey']) for r in mapping if r['PubChem_CID']),
 'source_DOI_format_where_available':all(re.fullmatch(r'10\.\d{4,9}/\S+',r['doi']) for r in interactions if r['doi']),
 'all_interactions_have_provenance':all(r['source_id'] in source_by_id and r['source_url'] and r['source_title'] and r['source_cache'] for r in interactions),
 'all_interaction_compounds_identity_mapped':all(maps[r['Canonical_Molecular_ID']]['mapping_status'].startswith('verified') for r in rel),
 'source_dates_not_future':all(int(r['year'])<=2026 for r in interactions),
 'all_ids_present':all(r['Canonical_Molecular_ID'] for r in interactions),
 'oof_record_group_and_target_matches':all(by_record[r['Record_ID']]['Canonical_Molecular_ID']==r['Canonical_Molecular_ID'] and abs(float(by_record[r['Record_ID']]['Retention_Final'])-float(r['actual']))<1e-6 for r in oof),
 'unique_selected_oof_records':len({r['Record_ID'] for r in oof})==len(oof),
 'oof_each_group_single_validation_fold':all(len({r['fold'] for r in oof if r['Canonical_Molecular_ID']==g})==1 for g in oofgroups),
 'food_claims_only_studied_preparations':all((not r['food_name'] and r['evidence_level']=='compound') or (r['food_name'] and r['evidence_level'] in ['food_preparation','food_extract']) for r in interactions),
 'preclinical_no_assigned_clinical_significance':all(r['clinical_relevance']=='Clinical relevance not established' for r in interactions if r['evidence_type'] in ['Animal','In vitro']),
 'no_arbitrary_risk_columns':not any('risk_score' in f or 'severity_score' in f for f in fields),
 'all_evidence_records_one_to_one':len(evidence)==len(interactions),
 'unassigned_rows_preserved':len(read(OUT/'stageB_unassigned_observations.csv'))==221,
 'historical_input_hashes_unchanged':all(hashlib.sha256((Path(r['path']) if Path(r['path']).exists() else ROOT/r['bundled_path']).read_bytes()).hexdigest()==r['sha256'] for r in json.loads((ROOT/'audit/input_manifest.json').read_text())),
 'bundled_input_hashes_match':all(hashlib.sha256((ROOT/r['bundled_path']).read_bytes()).hexdigest()==r['sha256'] for r in json.loads((ROOT/'audit/input_manifest.json').read_text()) if 'bundled_path' in r),
}
assert all(checks.values()),checks
(OUT/'stageB_qc_results.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
md('stageB_quality_control.md','# Stage B quality control\n\n'+table(['Automated check','Result'],[(k,'PASS' if v else 'FAIL') for k,v in checks.items()])+f'''\n\nManual evidence review: each of {len(interactions)} records was checked against its cached original-study abstract and, where available/needed, full-text tables. Identity concordance checks compare PubChem structure and names/synonyms, preserve stereochemistry limits, and exclude mixed/ambiguous groups. Quantitative values remain source text with units and source locators; directions without numerical magnitudes leave numerical fields blank. This is one reviewer, not independent dual extraction.

Issues found: 221 rows lack molecular IDs; {counts['uncertain_identity']} groups lack concordant identity; {counts['verified_connectivity']} mapped groups have incomplete structure-form agreement; drug external IDs/classes not resolved; source-abstract label inconsistency in Guo et al.; design/sample statements and clearance wording inconsistency in Rezaee et al.; most search results not exhaustively screened. Food categories absent.

Issues resolved in this release: blank ID rows preserved separately; no uncertain groups assigned; proposed mechanisms marked as proposed; mixed-extract effects not attributed to an isolated ingredient; rat/in-vitro outcomes not promoted to humans; conflicting records retained; no invented risk values; reverse caffeine interactions explicitly labelled. Unsupported numeric values and ambiguous Tmax/half-life labels left blank. Remaining limits are not hidden by automated PASS status.

OOF folds show each group occurs in one validation fold; training-fold membership cannot be independently reconstructed without Stage A runner/train indices. No assertion of a re-run model or clinical validation.
''')
md('stageB_inventory.md',f'''# Input and repository inventory

Inspection completed before interaction searching. Canonical IDs came from the supplied expanded master, not older repository data.

| Material | Role | Verified scope |
| --- | --- | --- |
| Downloads/cookchem_master_expanded_round11.csv | Supplied latest master | 1,350 rows; 198 nonblank molecular groups; 221 unassigned rows; 241 names; 187 food labels |
| Downloads/stageA_oof_predictions.csv | Actual OOF outputs | 5 models x 1,124 records; 197 groups; selected ExtraTrees_reference |
| Downloads/CookRisk_StageA_Benchmark_Report.pdf | Selection and validation context | Retain Extra Trees; aggregate MAE 31.964; RMSE 141.309; R2 0.256 |
| Downloads/literature-review DOCX | Background | Eight cooking/retention/QSAR core papers; not drug evidence |
| data/data_ready/ | Older preprocessing | 901-row master and 560-row molecular ML data; not current Stage A input |
| preprocessing/scripts/ | Historical processing code | Conservative validation and readiness repair |
| molecular_features/scripts/ and outputs/ | Historical identity/descriptor work | PubChem cache and RDKit workflows |
| reports/ | Historical readiness/identity audits | Not modified |
| literature/papers/ | Six historical PDFs | Background only |

Phase 1-3 and full Stage A runner/model artifacts are not present in this checkout. The supplied OOF/report provide linkage; no fitted prediction model is available to deploy. Master-only molecular group MOL-4F1A943C959BC640 (PhIP) has no selected OOF prediction. Exact input paths, hashes and sizes are in audit/input_manifest.json. Actual 97 dataset columns are preserved in the unassigned-observation table; compound identity columns include Canonical_Molecular_ID, Compound_Name, Canonical_Compound_Name, Canonical_SMILES, PubChem_CID and resolved-CID fields. No supplied InChI/InChIKey/CAS columns or Food_Category column were found.
''')
md('stageB_methodology.md',f'''# Stage B methodology

## 1. Objective
Build an initial evidence-mapped Food-Compound-Drug knowledge base. This is an evidence layer, not clinical decision support or a risk score.
## 2. Dataset source
Use the supplied 1,350-row expanded master and original Stage A OOF CSV; SHA-256 hashes lock input provenance. Older checkout outputs are historical context.
## 3. Compound selection
Retain all 198 nonblank Canonical_Molecular_ID groups. Preserve 221 blank-ID observations separately without inventing groups. Molecular groups, names, and distinct standardized CIDs are different counts.
## 4. Identity standardization
Retrieve public PubChem properties and synonyms by existing CIDs. Prefer existing resolved-CID fields over historical CIDs. Require one candidate CID, one concordant structure, and all observed names to match source names/synonyms. RDKit comparison distinguishes exact structure from connectivity-only agreement. No groups are merged. Connectivity-only mappings establish named parent identity but do not verify stereochemical form. Mixed total/individual names and conflicting structures remain uncertain. CAS-like PubChem synonyms require checksum validation; source-reported synonyms are not an independent registry adjudication.
## 5. Literature search strategy
Targeted literature search, 6 October 2026, Europe PMC plus primary-study web discovery and reference follow-up. Each nonblank CookRisk group had a title/abstract query. Cache the first 25 results and hit count; {counts['search_hit_truncation_groups']} queries exceeded that cap. These are searches, not complete systematic-review screening. Selected studies were manually extracted.
## 6. Search concepts
Compound name AND drug interaction, pharmacokinetic, cytochrome, transporter, enzyme inhibition, or drug absorption. Follow-up compound-drug searches covered human PK, AUC/Cmax, clinical outcomes, and cooking/processing. Exact queries, dates and URLs are in outputs/stageB_search_log.csv. Search synonyms and advanced drug-specific concepts remain incomplete for many groups.
## 7. Inclusion criteria
Traceable original study, named CookRisk-compatible compound, therapeutic drug, measured interaction or interaction-relevant null result. Distinguish parent identity from salt/extract/form and retain limitations. Include null controls explicitly, not as proof no interaction exists.
## 8. Exclusion criteria
Uncertain groups, unsupported claims, speculative transfer to food, untraceable quantitative values and unrelated compounds. Selected exclusions include quercetin/total-flavonol group contamination and total-vitamin-C/ascorbic-acid ambiguity. Reviews discover studies but do not replace original evidence.
## 9. Evidence classification
Separate Human pharmacokinetic, Controlled clinical, Animal and In vitro records. Mechanistic interpretation is not an independent clinical study. Model predictions from papers are not observed AUC.
## 10. Interaction extraction
One study/relationship/intervention/context per record. Two human tamoxifen intervention arms remain separate. Human extract and cell nadolol experiments remain separate. Combination preparations have one anchor plus explicit co-intervention links, not inflated duplicated rows for every ingredient. Drug names use local keys; external drug identifiers and classes remain blank unless independently resolved.
## 11. Quantitative data
Preserve units, endpoint identity, confidence intervals, significance, approximate qualifiers and measured-versus-model distinction. Blank means not extracted/reported reliably, not zero. Metabolite ratios and TGI are stored as their own quantitative outcomes, not AUC. affected_entity identifies reverse drug-to-compound interactions.
## 12. Conflict handling
Store separate records and source-supported synthesis in stageB_conflict_synthesis.csv. Distinguish study-context variation from direct same-population replication conflicts.
## 13. Food-compound-drug mapping
Food-compound associations come from master records and retain source Record_IDs. They are not independently verified food composition claims. Main interaction food fields are populated only when a preparation/extract was actually studied. No food-wide interaction is inferred from constituent evidence.
## 14. Cooking relevance
Keep independent processing studies in stageB_processing_evidence.csv. No conversion of supplement doses or assay concentrations into dietary retained exposure.
## 15. Stage A linkage
Join selected-model OOF by Record_ID and Canonical_Molecular_ID; validate actual against Retention_Final. Retain individual outputs and original row pointers. No compound-average retention invented. All benchmark models remain in the original CSV.
## 16. Quality control
Automated key/provenance/join/hash checks plus manual source-context review. No independent second reviewer. Quantitative accuracy requires source inspection, not just schema validation.
## 17. Limitations
Non-exhaustive searches; 25-result cap; mostly abstract extraction; no full Phase 1-3/Stage A runnable model; uncertain/contaminated identities; incomplete stereo, external drug ID/class and CAS adjudication; dataset food-source claims not revalidated; no clinical exposure thresholds. Absence of a retained record is not evidence of absence.
## 18. Future integration
After identity/data provenance repairs, external drug normalization and expanded screening, a fitted model may produce condition-specific retention estimates. A compatible baseline amount x predicted percentage/100 is only a modelling quantity when units, measurement basis and target definition are valid; food amount, bioavailability, active metabolites and clinical applicability require separate evidence. No such exposure/risk values are generated here.
''')
refs=[]
for sid in sorted({r['source_id'] for r in interactions+processing}|{r['candidate_source_id'] for r in excluded}):
    m=metadata(sid); support=[r['interaction_id'] for r in interactions if r['source_id']==sid]+[r['processing_id'] for r in processing if r['source_id']==sid]
    refs.append(f'- **{sid}**: {m["citation"]} DOI: {m["doi"] or "Not available in retrieved metadata"}. [Source]({m["source_url"]}). Supports: {", ".join(support) or "excluded identity-mapping candidate"}. Cache: `{m["source_cache"]}`.')
md('stageB_references.md','# Stage B references\n\n'+'\n\n'.join(refs)+'\n\nIdentity sources: every PubChem CID used is individually cited in stageB_compound_mapping.csv and stageB_identity_audit.csv; properties and full synonym responses are cached. Search source: [Europe PMC API](https://www.ebi.ac.uk/europepmc/webservices/rest/search). Supplied Stage A report and eight-paper DOCX inform context only; their claims are not substituted for interaction evidence.')
md('stageB_reproducibility.md',f'''# Reproducibility

Search/extraction date: 2026-10-06 (Asia/Calcutta). Input absolute paths and SHA-256 hashes: audit/input_manifest.json. Inputs remain in Downloads. Relative output paths are under stageB/outputs and stageB/reports.

Offline rebuild from repository root:
```
.venv/Scripts/python.exe stageB/scripts/build_mapping.py
.venv/Scripts/python.exe stageB/scripts/build_stageB.py
```
RDKit 2026.3.5 is available in the existing repository virtual environment; CSV/JSON are standard-library formats. inspect_inputs.py additionally requires pypdf and python-docx (bundled runtime). build_stageB.py does not need pandas or network. No model is retrained.

Read-only source collection (requires internet) uses collect_sources.py, collect_synonyms.py and collect_selected.py. Cached responses are reused; remove/relocate a cache deliberately to refresh. Original searches retrieve first 25 candidates, not every hit. A fresh online search can change, so exact release reproduction uses saved caches, not new responses. Manual extraction lives in scripts/curated_evidence.py with source/context locators. Rebuild tables after changing curated extraction; automatic QC fails on referential inconsistency.

Input inventory script extracts all PDF text and DOCX paragraphs/tables. No instructions inside background documents were executed. Historical scripts/results and user working changes were left untouched. Local FOOD/DRUG/SB/PROC keys are database keys, not fabricated external identifiers.

Manual decisions: retain uncertain groups without interactions; permit source-name/CID/connectivity parent mapping with explicit stereochemistry limitations; use mixture anchors plus co-intervention relation; retain null controls; leave unverified external drug IDs/classes blank; omit Guo abstract-conflicted Tmax/half-life fields; retain Rezaee reporting discrepancy notes; exclude contaminated quercetin and total-vitamin-C groups; no arbitrary score or dietary-to-clinical conversion. No assumption of absence is made for unretained compounds.

QC: outputs/stageB_qc_results.json and reports/stageB_quality_control.md. Inputs hash-checked; original OOF retained; individual observation pointers exact. {len(interactions)} manually extracted records; source snapshots support audit. This is single-reviewer targeted evidence mapping, not a systematic review, clinical validation, independent double extraction or perfect/exhaustive database.
''')
md('stageB_report.md',f'''# CookRisk Stage B report

## 1. Executive summary
An initial reproducible evidence layer now links the supplied compound universe, food associations, study-level drug evidence and original selected-model OOF predictions. {len(interactions)} evidence records from {counts['unique_interaction_sources']} original studies cover {counts['anchor_compounds_with_evidence']} anchor compounds and {counts['unique_drugs']} drugs. Null findings and preclinical conflicts remain visible. No clinical risk scores or dietary exposure estimates were created.
## 2. Objective
Establish auditable Food-Compound-Drug-Mechanism-Evidence-Source relationships.
## 3. Relationship to Stage A
ExtraTrees_reference is the selected benchmark, as documented by Stage A. All 1,124 OOF records match master Record_ID, molecular group and target. A saved fitted model and Phase 1-3 experiment code are absent in this checkout. No new-condition prediction is claimed.
## 4. CookRisk compound universe
{table(['Measure','Count'], [('Master observations',1350),('Nonblank molecular groups',198),('Rows without molecular ID',221),('Unique compound-name strings',241),('Food-name strings',187),('Food categories','Not supplied'),('Stage A OOF molecular groups',197)])}
The blank-ID bucket is not a 199th molecule. Unassigned rows remain auditable and are not discarded.
## 5. Identity standardization
{table(['Status','Groups'], [('Verified exact structure/name',counts['verified_exact']),('Verified name/CID/connectivity; stereo incomplete',counts['verified_connectivity']),('Uncertain identity',counts['uncertain_identity']),('Distinct standardized source CIDs',counts['distinct_standardized_compounds'])])}
Mapping preserves all 198 original groups. No identity is merged solely by name. Uncertain groups are not assigned drug interactions. Connectivity-only is a qualified parent-identity mapping, not confirmation of chemical form or dietary exposure. Missing external identity fields are blank; inherited historical CIDs retained separately.
## 6. Literature methodology
198 molecular-group searches were retrieved from Europe PMC on 6 October 2026, plus primary-study follow-up. Only the first 25 candidates per query were cached; {counts['search_hit_truncation_groups']} groups exceed the cap. Selected sources manually screened/extracted. Other compounds are searched but not exhaustively screened. This is a targeted search, not a systematic review.
## 7. Interaction evidence
{table(['Anchor compound','Records'], sorted(Counter(r['compound_name'] for r in interactions).items()))}
Combination co-interventions appear in a separate relation table. Evidence coverage including verified co-interventions is {counts['compounds_including_verified_cointerventions']} compound groups. Counts describe records, not independent patients or proven hazards.
## 8. Evidence-type distribution
{table(['Evidence','Records'], counts['evidence_distribution'].items())}
## 9. Mechanisms
{table(['Category','Records (multi-category possible)'], counts['mechanism_distribution'].items())}
Proposed enzyme or transporter explanations are labelled; observed exposure changes alone do not prove the mechanism.
## 10. Quantitative evidence
{counts['quantitative_PK_PD_records']} records contain extracted quantitative PK/PD outcomes; {counts['quantitative_biochemical_assay_records']} additional records contain biochemical assay kinetics, for {counts['quantitative_outcome_records']} quantitative-outcome records total. Dose-only records are not counted. Berberine-cyclosporine AUC +34.5% (Wu et al.); piperine-nevirapine AUCinfinity approximately +170% (Kasibhatta & Naidu); curcumin-plus-piperine tamoxifen AUC -12.8% and endoxifen AUC -12.4% (Hussaarts et al.). These are regimen-specific study results. Endpoint units, CI and significance remain in tables. Source locators are explicit.
## 11. Human versus preclinical
{counts['human_records']} human, {counts['animal_records']} animal, {counts['in_vitro_records']} in-vitro, {counts['in_silico_mechanistic_only_records']} standalone in-silico/mechanistic records. In-silico estimates reported within preclinical sources are not promoted to observed PK. {counts['negative_control_records']} mixture-specific null controls are retained.
## 12. Conflicting evidence
{table(['Relationship','Synthesis'],[(r['conflict_group'],r['synthesis']) for r in conflicts])}
Different species/preparations/regimens limit direct comparisons. Clinical relevance of preclinical bortezomib findings remains unestablished.
## 13. Cooking/processing
Separate evidence describes curcumin/piperine losses in boiled/pressure-cooked spices and green-tea catechin extraction/epimerization during brewing. This does not establish how cooking changes drug-interaction strength. Literature processing values are not Stage A predictions.
## 14. Stage A linkage
{counts['records_linked_stageA']} of {len(interactions)} interaction records link to selected-model groups. Compound linkage preserves observation/food counts; observation linkage preserves food, cooking conditions, baseline concentration and individual OOF values with original row pointers. No invented per-compound retention or retained amount.
## 15. Quality control
All {len(checks)} automated integrity checks passed. Manual context review retained reporting issues rather than hiding them. Historical-input hashes unchanged. Automated checks cannot prove a perfect literature review.
## 16. Limitations
96 uncertain groups; 221 blank-ID observations; 23 qualified connectivity mappings; incomplete external drug identifiers/classes; truncated, non-exhaustively screened searches; abstract-dependent extraction; one reviewer; no source-level revalidation of all modelling food/concentration/DOI claims; no fitted deployment model here; supplement/cell/animal exposures not transferable to cooked-food clinical risk. These limitations restrict conclusions.
## 17. Future integration
Repair identity and source provenance first; extend screening and normalize drug identifiers. Retention predictions can be joined to documented associations only after condition/unit/basis/exposure checks. Do not rank foods/drugs numerically from this database.
## 18. Conclusion
Stage B successfully establishes an initial evidence-based knowledge base with auditable source and Stage A linkage. It is a bounded research evidence release, not an exhaustive or clinically validated interaction system. A missing record means no qualifying evidence was retained under this release's search/identity limits; it does not mean no interaction exists.
''')
source_note=f'''\n\n## Upstream data-source audit (material limitation)
Crossref metadata was retrieved for {len(source_audit)} dataset DOIs: {counts['dataset_DOIs_metadata_mismatch']} have author and/or year metadata discrepancies; {counts['dataset_DOIs_retrieval_unavailable']} could not be retrieved. These are source-verification flags, not automatic proof that every associated measurement is fabricated. Metadata-concordant citations still do not verify measurements.

A confirmed example is DOI 10.1016/j.lwt.2021.111500, assigned to five avocado/Persin cooking rows. The publisher identifies a 2021 Liu et al. fish-oil/gelatin encapsulation paper, rather than the recorded 2022 Molina et al. Persin study. [Publisher source](https://www.sciencedirect.com/science/article/abs/pii/S0023643821006538). This mismatch blocks scientific validation of those food-retention claims. It does not invalidate independently verified Stage B interaction publications.

Additionally, 115 selected OOF records have FALSE in the current master Final_Preprocessing_Eligible flag despite matching molecular IDs and actual target values. The supplied Stage A report describes a frozen 1,124-row experiment, while the current master flags only 1,009 eligible rows. Without the locked Stage A runner/input snapshot, eligibility lineage cannot be reconciled. Original outputs are preserved and no re-training or retrospective repair was attempted.

One standardized-CID cluster (5282102) spans two original groups, Kaempferol-3-Glucoside and Astragalin. Groups remain separate. This is not proof of leakage: their stereochemical representations differ in completeness; cross-fold identity duplication needs a separate Stage A audit.

Therefore food associations and OOF outputs are traceable inherited project data, not newly certified experimental evidence. The knowledge base can support literature evidence lookup; any quantitative retained-dose or clinical extrapolation remains blocked by upstream provenance and form/exposure limits. Detailed flags: stageB_dataset_source_audit.csv, stageB_duplicate_standardized_identities.csv and observation-link metadata fields.
'''
for name in ['stageB_report.md','stageB_quality_control.md','stageB_methodology.md','stageB_reproducibility.md','stageB_inventory.md']:
    p=REPORT/name; p.write_text(p.read_text(encoding='utf-8')+source_note,encoding='utf-8')
md('stageB_dataset_source_audit.md','# Dataset source audit\n\n'+source_note+'\n\nMethod: exact DOI lookup via Crossref. Compare supplied years to publication/issued dates and supplied author strings to retrieved author-family names. Author matches use a conservative ASCII-normalized surname substring; this is a screening heuristic requiring manual review, not source-measurement verification. Preserve each raw response. Source measurements and claimed food-compound relationships are not repaired. DOI retrieval failure is not evidence of a nonexistent DOI. The publisher mismatch above was additionally verified manually.\n')
standardized_log=OUT/'stageB_standardized_search_log.csv'
if standardized_log.exists():
    srows=read(standardized_log); additional=f'\n\nStandardized-name follow-up: {len(srows)} mapped groups additionally queried by verified PubChem title with broader drug/PK/PD/absorption/metabolism/transporter concepts and a 2026-10-06 publication cutoff. Exact queries and retrieval status: stageB_standardized_search_log.csv. Candidate coverage remains limited to 25 and is not exhaustive manual screening.\n'
    for name in ['stageB_methodology.md','stageB_reproducibility.md','stageB_report.md']:
        p=REPORT/name;p.write_text(p.read_text(encoding='utf-8')+additional,encoding='utf-8')
    counts['standardized_name_searches']=len(srows);counts['standardized_search_errors']=sum(r['retrieval_status']=='error' for r in srows)
    (OUT/'stageB_summary.json').write_text(json.dumps(counts,indent=2),encoding='utf-8')
missing={f:sum(not r[f] for r in mapping) for f in ['SMILES','PubChem_CID','InChI','InChIKey','CAS','standardized_compound_name','molecular_formula']}
(OUT/'stageB_identity_missingness.json').write_text(json.dumps(missing,indent=2),encoding='utf-8')
# All delivered CSV columns are documented, including auxiliary relational/audit tables.
defs={
 'Canonical_Molecular_ID':'Unchanged supplied molecular grouping key; blank rows kept separately.',
 'interaction_id':'Local stable evidence-record key, not an external scientific identifier.',
 'compound_id':'CookRisk molecular key, equal to Canonical_Molecular_ID.',
 'food_id':'Local food/preparation dictionary key; does not imply drug interaction.',
 'drug_id':'Local drug dictionary key, not a PubChem/DrugBank ID.',
 'mapping_status':'verified_exact, verified_connectivity, uncertain; exact requires structure and all name aliases concordant.',
 'identity_resolution_scope':'Identity mapping scope; connectivity-only does not establish stereo.',
 'PubChem_CID':'Externally retrieved concordant PubChem candidate; blank when uncertain.',
 'CAS':'Source-reported CAS-like synonyms with valid checksum; multiple entries retained, not independently adjudicated.',
 'SMILES':'Original CookRisk structure string(s), preserved.',
 'standardized_source_SMILES':'PubChem source structure; does not overwrite input stereo.',
 'InChI':'PubChem source InChI for mapped candidate, not independent confirmation of dataset form.',
 'InChIKey':'PubChem source InChIKey for mapped candidate.',
 'evidence_type':'Human pharmacokinetic, Controlled clinical, Animal, In vitro; controlled primary classification.',
 'study_type':'Source study design; reporting ambiguity explicitly noted.',
 'evidence_level':'compound, food_preparation, food_extract; prevents food-level inference.',
 'compound_form':'Actual study ingredient/form or explicit extraction limit.',
 'co_compounds':'Named co-intervention constituents; causal ingredient effects not isolated.',
 'affected_entity':'drug or compound; identifies whose quantitative PK/PD changed.',
 'perpetrator_entity':'drug or compound_or_preparation; direction of effect.',
 'record_outcome':'observed_effect or null_finding; null is regimen-specific.',
 'clinical_relevance':'Evidence-level interpretation; preclinical always Clinical relevance not established.',
 'quantitative_result':'Source-reported endpoint with units/CI/significance; excludes dose-only counts.',
 'AUC_change':'Reported AUC change or control-to-treatment values; endpoint/affected entity specified, never risk.',
 'Cmax_change':'Reported peak-exposure change or values; units preserved.',
 'Tmax_change':'Reported change in time to peak; blank if conflicted/not extracted.',
 'clearance_change':'Reported clearance/CL-F values or change; units preserved.',
 'half_life_change':'Reported half-life values/change; blank if source labels conflict.',
 'dose':'Source ingredient and drug dose, preserving units and regimen.',
 'concentration':'Reported assay/plasma concentration or parameter such as Ki; label preserved.',
 'duration':'Source regimen/observation duration; not invented.',
 'frequency':'Source administration frequency.',
 'mechanism':'Source-reported/proposed explanation; observation does not establish causality.',
 'mechanism_category':'Controlled source-supported category; multiple separated by vertical bar.',
 'interaction_type':'Pharmacokinetic, Pharmacodynamic, or both, based on measured endpoint.',
 'enzyme_or_transporter':'Source named target, including species-specific labels.',
 'pathway':'Specific reported pathway, blank if not reliably extracted.',
 'effect_direction':'Endpoint direction with affected entity; concentration-dependent/null kept explicit.',
 'source_id':'Europe PMC source accession (usually PMID); not a drug identifier.',
 'source_cache':'Relative cache path under stageB supporting extraction.',
 'source_locator':'Abstract, Methods, Results or full-text table used in manual extraction.',
 'source_url':'Verified original-study PubMed/DOI URL; or logged database search URL.',
 'doi':'DOI from retrieved metadata; blank if unavailable.',
 'source_title':'Original source title from retrieved metadata.',
 'authors':'Source author string from metadata, not invented.',
 'journal':'Source journal from metadata.',
 'year':'Publication year from source metadata.',
 'citation':'Metadata-composed citation to source study.',
 'drug_identifier':'External identifier blank unless independently resolved; local key is separate.',
 'drug_class':'External therapeutic class blank when not independently normalized.',
 'processing_relevance':'Availability of independent processing evidence, not an interaction modifier.',
 'processing_effect_description':'Separate processing summary with DOI; no conversion into interaction magnitude.',
 'stageA_link_available':'True if original selected-model OOF contains molecular key.',
 'stageA_prediction_available':'Presence in supplied selected OOF, not availability of deployment inference.',
 'stageA_model':'Selected OOF label ExtraTrees_reference, from report plus file.',
 'OOF_source_row':'One-based original CSV line number including header.',
 'OOF_source_path':'Absolute original Stage A path; immutable source.',
 'OOF_actual_retention_percent':'Original actual column, verified against master Retention_Final.',
 'OOF_predicted_retention_percent':'Original selected-model predicted column; no aggregation or invention.',
 'OOF_fold':'Original validation fold; group integrity checked.',
 'interaction_record_count':'Unique linked records; includes explicit co-interventions without duplicating main rows.',
 'drug_count':'Distinct drug names among linked records.',
 'observation_count':'Master row count for unchanged molecular group.',
 'OOF_observation_count':'Selected-model OOF rows for unchanged group.',
 'food_count':'Distinct nonblank original Food_Name labels in group; categories unavailable.',
 'search_status':'Search performed; not exhaustive screening completion.',
 'interaction_evidence_status':'Retained evidence, uncertain identity, or no evidence retained; never absence proof.',
 'screening_status':'Candidate retrieval or selected-source review; unreviewed candidates remain explicit.',
 'hit_count':'Database hit count at retrieval, not included-study count.',
 'query':'Exact logged database search string.',
 'search_date':'Retrieval date, YYYY-MM-DD using client date.',
 'conflict_group':'Local synthesis key; retains separate study-context records.',
 'role':'anchor_named_identity or co_intervention_not_independently_attributable.',
 'Record_ID':'Unchanged supplied observation key.',
 'Record_IDs':'Vertical-bar-separated source observation keys supporting association.',
 'notes':'Audit interpretation/decision notes; not fabricated source facts.',
 'limitations':'Source/reporting/design/mapping limitations restricting inference.',
 'reason':'Documented exclusion reason.',
}
dictionary=['# Stage B data dictionary','Blank cells mean unavailable, uncertain or not reliably extracted, never zero or evidence of absence. UTF-8 CSV. Lists use ` | `; units remain in text. Food/drug/interaction/processing keys are local database identifiers. Source metadata, manual extraction and model outputs remain separate.']
for p in sorted(OUT.glob('*.csv')):
    columns=next(csv.reader(p.open(encoding='utf-8-sig')))
    dictionary.append('## '+p.name)
    items=[]
    for f in columns:
        desc=defs.get(f)
        if not desc:
            if p.name=='stageB_unassigned_observations.csv': desc='Unmodified original master column; meaning and reported units retained from source dataset. Not revalidated or independently interpreted.'
            else: desc={'CookRisk_compound_name':'All original Compound_Name strings in group.','standardized_compound_name':'PubChem title only for verified mapping.','compound_name':'Named anchor compound or preserved dataset name.','synonyms':'First 20 source-reported PubChem synonyms; complete response cached.','compound_synonyms':'Mapping table source synonyms.','compound_identifier':'Verified source PubChem CID text.','compound_class':'Existing CookRisk class labels, not inferred.','food_sources':'Original/Canonical dataset food labels, not clinical evidence.','food_name':'Original dataset food or actually studied preparation, per scope.','drug_name':'Source therapeutic drug name, acetaminophen/paracetamol normalized as one drug.','molecular_formula':'PubChem formula for mapped candidate.','mapping_source':'PubChem URL or original-dataset/audit reference.','population':'Source study population/model.','species_or_population':'Source study population/model.','effect':'Extracted observed outcome.','effect_description':'Extracted observed outcome.','source_database':'Source MED/AGR/etc. as returned by Europe PMC.','title':'Candidate source title.','cache':'Relative original search-cache path.','processing_id':'Local processing evidence key.','processing_conditions':'Source time/temperature/cooking method.','food_scope':'Dataset label or literature-specific preparation.','source':'Original dataset or literature provenance.','claim_scope':'Dataset association only, no clinical food claim.','supporting_source_ids':'Source accessions supporting local drug usage.','identifier_status':'External ID resolution explicitly incomplete.','candidate_source_id':'Traceable excluded study accession.','candidate_CID':'Unchanged candidate CID examined in identity audit.','PubChem_title':'Title of retrieved candidate record.','structure_comparison':'exact_structure, connectivity_only, mismatch.','all_observed_names_verified':'Whether every observed name matched PubChem aliases.','observed_names':'All dataset name labels subjected to concordance check.','original_PubChem_CIDs':'Preserved original dataset CIDs including conflicts.','candidate_PubChem_CIDs':'Existing resolved CIDs preferred; otherwise original candidates.','search_name':'Dataset name used in original query.','retrieval_status':'Retrieved/error, from actual request.','synthesis':'Context-supported conflict summary.','interaction_ids':'Linked local evidence IDs.'}.get(f,'Original supplied observation/context field; inherited from modelling master, not newly inferred.')
        numeric=f in ['observation_count','food_count','drug_count','interaction_record_count','OOF_observation_count','hit_count','year','OOF_source_row']
        boolean=f in ['stageA_link_available','stageA_prediction_available','all_observed_names_verified']
        required=f in ['Canonical_Molecular_ID','interaction_id','evidence_type','source_id','source_url','mapping_status','drug_id','drug_name'] and p.name!='stageB_unassigned_observations.csv'
        provenance='Source metadata/manual extraction' if f in fields or p.name in ['stageB_literature_evidence.csv','stageB_processing_evidence.csv'] else ('Original modelling/OOF dataset or documented derived counts' if 'stageA' in p.name or 'observations' in p.name else 'Identity source, search log or explicit local relationship/audit')
        items.append([f,desc,'integer' if numeric else ('boolean' if boolean else 'text'),'Nonnegative count/year' if numeric else ('true/false' if boolean else 'Source text or categories defined above'), 'Required' if required else 'Optional',provenance,'Missing stays blank; no clinical score interpretation'])
    dictionary.append(table(['Field','Definition','Type','Expected values','Required','Provenance','Interpretation'],items))
md('stageB_data_dictionary.md','\n\n'.join(dictionary))
# Explicit release-completion crosswalk distinguishes delivered evidence from unresolved scientific coverage.
md('stageB_requirements_checklist.md','''# Stage B delivery crosswalk

| Requested area | Delivered evidence | Scope/remaining limitation |
| --- | --- | --- |
| Inspect inputs/repository | Inventory; input hashes; extracted report/review | Full Phase 1-3/Stage A runnable artifacts absent |
| Complete molecular universe | 198-row mapping; 221 unassigned-row audit | Blank molecular IDs not invented |
| Standardize identities | PubChem properties/synonyms and per-candidate audit | 96 uncertain; 23 connectivity-only; no forced merges |
| Search compounds | 198 original-group + 102 standardized-name searches | 25-hit cap; non-exhaustive manual screening |
| Structured interaction/evidence tables | 33 records; original citation caches/locators | Five anchors; six including verified co-intervention; no comprehensive coverage claim |
| Drug entity dictionary | 18 local drug keys | External identifiers/classes not independently normalized |
| Evidence classification | Human, animal, in-vitro kept separate | No clinical inference from preclinical data |
| Quantitative evidence | Source text, units, endpoints, CI/significance | Missing/ambiguous values left blank; no risk score |
| Conflicting evidence | Four context-sensitive synthesis groups | Different species/regimens are not direct human replications |
| Food-compound-drug levels | Separate food-compound and interaction tables | Food fields only populated for studied preparations/extracts |
| Processing evidence | Three independently sourced processing records | No effect-strength conversion or dietary dose inference |
| Stage A linkage | 198 group rows; 1,124 individual OOF pointers | 115 eligibility flags differ; fitted model absent |
| QC and data dictionary | Automated integrity checks; all CSV columns | One reviewer; metadata checks do not validate measurements |
| References/reproducibility/report | All requested Markdown reports; source snapshots; scripts; immutable inputs | Source data issues prevent full retained-exposure/clinical validation |

The deliverable is a real, reproducible initial evidence database. Exhaustive literature screening, exact form resolution for every group, independent dual review and clinical validation are not completed and are not represented as completed.
''')
# Deterministic output manifest allows manual audit and offline reproducibility.
manifest=[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for folder in [OUT,REPORT] for p in sorted(folder.iterdir()) if p.is_file()]
(ROOT/'audit/output_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
