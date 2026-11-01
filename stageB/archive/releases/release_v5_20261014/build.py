"""Offline Stage B v5 append-only builder using saved primary snapshots."""
from pathlib import Path
import sys,csv,json,hashlib,re,html,xml.etree.ElementTree as ET,collections,difflib
sys.dont_write_bytecode=True
from curation import ROWS
O=Path(__file__).resolve().parent;R=O.parents[1];B=R/'stageB';V4=B/'release_v4_20261014'
DATE='2026-10-14'
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rows,fields=None):
    with (O/'outputs'/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
def load(p):return json.loads(p.read_text(encoding='utf8'))
def norm(t):return re.sub('[^a-z0-9]','',html.unescape(re.sub(r'</?[A-Za-z][^>]*>','',t)).lower())
def paper(pmid):return next(m for m in load(O/'sources'/f'pmid_{pmid}.json')['resultList']['result'] if str(m['id'])==pmid and m['source']=='MED')
def key(name):return name.lower().replace(' ','_')
baseline=read(V4/'outputs/stageB_food_drug_interactions_v4.csv');reg=read(V4/'outputs/compound_registry.csv');mapping=read(B/'outputs/stageB_compound_mapping.csv');fields=list(baseline[0])
assert len(baseline)==73 and len(reg)==14
freeze={};inventory=[]
for folder in ['stageB','data','docs','literature','reports','molecular_features','preprocessing']:
    for p in sorted((R/folder).rglob('*')):
        if not p.is_file() or O in p.parents or '__pycache__' in p.parts:continue
        rel=p.relative_to(R).as_posix();freeze[rel]=hashlib.sha256(p.read_bytes()).hexdigest();rows='';cols=[]
        if p.suffix=='.csv':
            rr=read(p);rows=len(rr);cols=list(rr[0]) if rr else []
        inventory.append(dict(File=rel,Purpose='Saved primary/source cache' if '/sources/' in rel else 'Registry, evidence, input, script, audit or documentation',Rows=rows,Source_Fields=' | '.join(c for c in cols if any(v in c.lower() for v in ['doi','pmid','source','reference'])),Inspection='Headers and row count' if p.suffix=='.csv' else 'Metadata and hash only; review level separately recorded',SHA256=freeze[rel]))
mp=O/'audit/preservation_manifest.json'
if not mp.exists():mp.write_text(json.dumps(freeze,indent=2),encoding='utf8')
write('file_inventory.csv',inventory)
short=[x for x in inventory if x['File'].startswith('stageB/release_v4_20261014/') and '/sources/' not in x['File'] and '/qa/' not in x['File']]
write('baseline_key_file_inventory.csv',short)
v4actual=dict(compounds=len(reg),records=len(baseline),drugs=len({x['Drug'] for x in baseline}),primary_reports=len({x['PMID'] for x in baseline}),types=dict(collections.Counter(x['Evidence_Type'] for x in baseline)),numerical=sum(bool(x['Quantitative_Outcome']) for x in baseline),technical_validation=load(V4/'audit/validation_report.json'),mutation_tests=load(V4/'audit/mutation_tests.json'),original_v2_preserved=baseline[:64]==read(B/'expansion_v2/outputs/stageB_food_drug_interactions_expanded.csv'))
(O/'audit/verified_v4_baseline.json').write_text(json.dumps(v4actual,indent=2),encoding='utf8')
specs={
'Myricetin':('21442417','Berries; primary food-composition PMID 10794622; aglycone/glycoside measurement scope must be distinguished','Human hepatic assay and animal PK give complementary positive and null evidence','Standalone parent; ambiguous supplied myricetin group not remapped'),
'Luteolin':('18446505','Celery in supplied inventory; food measurements not newly certified','GHB transport inhibition and animal clearance changes add a renal reabsorption mechanism','Reuse exact verified structure; experimental IV doses not dietary exposure'),
'Ellagic acid':('30678660','Walnut in supplied exact group; distinct from total ellagic-acid label','Verified isolated-constituent warfarin arm separates extract and compound effects','Exact parent group retained; total analyte group excluded'),
'Gallic acid':('34144662','Button mushroom in supplied inventory; primary paper also describes fruit-associated polyphenol','Named renal probe-substrate assays and paclitaxel null evidence','Only isolated gallic-acid assays included; human RLQ PK is not human drug-interaction evidence'),
'Ferulic acid':('21704146','Barley and wheat bran in supplied inventory','Reverse clopidogrel interaction adds affected-entity directionality','Exact mapping retained; no compound-to-drug exposure reversal'),
'Caffeic acid':('21697612','Coffee, fruits and vegetables in primary study; coffee inventory','Named OAT1/OAT3 substrates give measured transport interaction endpoints','Parent-connectivity only; stereochemical transfer prohibited'),
'Chlorogenic acid':('27396204','Coffee and vegetables in supplied inventory; primary processing PMID 15309458','Platinum-drug cell experiments include potentiation, antagonism and null contexts','Exact source representation reused; other chlorogenic isomers remain separate'),
'Rosmarinic acid':('33435470','Rosemary in supplied inventory','Transport-mediated furosemide effect, valsartan null and reverse probenecid interaction','Parent-connectivity only; IV experiments do not establish oral meal effects'),
'Naringenin':('23883365','Grapefruit-related aglycone; dietary context in primary simvastatin comparison; processing PMID 15309458','Drug PK and microsomal null findings distinct from glycoside naringin','Stereochemically unspecified parent CID 932; no link to uncertain original group'),
'Bergamottin':('15592332','Grapefruit juice; verified in primary human felodipine study','Human isolated-compound capsules separate effects from whole juice','External parent identity; not merged with dihydroxybergamottin'),
'Chrysin':('16003560','Honey, propolis and herbs as stated in primary PMID 27098862','Human pilot and rat caffeine null test different contexts','External parent; clinical pilot uncontrolled, not clinical proof of safety'),
'Fisetin':('26884726','Fruits and vegetables as stated in primary PMID 26692948','Named chemotherapy combinations include synergy and nonsynergistic findings','External parent identity; in-vitro findings not human clinical effects'),
}
decisions=[];selection=read(V4/'outputs/selection_sources.csv');newreg=[]
for n,(name,(pmid,food,reason,limit)) in enumerate(specs.items(),1):
    identityname='naringenin_parent' if name=='Naringenin' else key(name)
    prop=load(O/'sources'/f'identity_{identityname}.json')['PropertyTable']['Properties'];assert len(prop)==1
    pr=prop[0];cid=str(pr['CID']);syn=load(O/'sources'/f'synonyms_{identityname}.json')['InformationList']['Information'][0]['Synonym']
    if name=='Naringenin':assert cid=='932' and any('naringenin' in s.casefold() for s in syn) and '/t' not in pr['InChI']
    else:assert name.casefold() in [s.casefold() for s in syn]
    matches=[m for m in mapping if m['PubChem_CID']==cid and m['mapping_status'] in ['verified_exact','verified_connectivity']]
    old=matches[0] if len(matches)==1 else None
    compid=old['Canonical_Molecular_ID'] if old else 'CHEM-PUBCHEM-'+cid
    status=old['mapping_status'] if old else 'verified_external_parent_no_automatic_master_link'
    source=paper(pmid);r={k:'' for k in reg[0]}
    r.update(Compound_ID=compid,Canonical_Name=name,Aliases=' | '.join(syn[:25]),PubChem_CID=cid,SMILES=old['SMILES'] if old else pr.get('ConnectivitySMILES',''),InChI=pr['InChI'],InChIKey=pr['InChIKey'],Identity_Status=status,Identity_Source=f'https://pubchem.ncbi.nlm.nih.gov/compound/{cid}',Origin='added_v5',Selection_Rationale=reason,Selection_Source=f'SEL-V5-{n:02d}; dated current decision in candidate_selection.csv',Selection_DOI=source.get('doi',''),Selection_PMID=pmid,Selection_URL=f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/',Date_Added=DATE,First_Documented_Release_Date=DATE,Date_Status='Current v5 decision; not inferred historical selection',Coverage_Status='Primary evidence manually extracted in bounded expansion',Provenance_Status='current_decision_documented_primary_support_verified',Original_Molecular_Group=old['Canonical_Molecular_ID'] if old else '',Retention_Status=(old['observation_count']+' inherited observations; identity and food measurement provenance not automatically certified') if old else 'No validated master retention link',Food_Context=food,Evidence_Records=sum(x['compound']==name for x in ROWS),Link_Restriction=limit,Release_Reviewed='v5_20261014',Selection_Verification='Dated v5 decision with primary citation and separately stated food source',Earliest_Verified_Selection_Date=DATE,Selection_Temporality='contemporaneous v5 decision',Remaining_Provenance_Gap='Retention and clinical exposure remain outside the selection decision; see restrictions')
    newreg.append(r);selection.append({**{k:'' for k in selection[0]},'Selection_Record_ID':f'SEL-V5-{n:02d}','Compound_ID':compid,'Decision_Date':DATE,'Source_Role':'primary_interaction_support_for_current_v5_decision','Source_Locator':f'sources/pmid_{pmid}.json abstract; candidate_selection.csv rationale','DOI':source.get('doi',''),'PMID':pmid,'URL':r['Selection_URL'],'Supports':reason,'Does_Not_Establish':'Historical selection, native cooked-food retained dose, or clinical risk','Provenance_Status':'current_decision_documented'})
    decisions.append(dict(Candidate_ID=f'CAND-V5-{n:02d}',Canonical_Name=name,Compound_ID=compid,Aliases=r['Aliases'],Identity_Source=r['Identity_Source'],Identity_Confidence=status,Food_Source=food,Selection_Rationale=reason,Primary_Eligibility_PMID=pmid,DOI=source.get('doi',''),URL=r['Selection_URL'],Processing_Status=r['Retention_Status'],Evidence_Types=' | '.join(sorted({x['type'] for x in ROWS if x['compound']==name})),Decision='selected',Reason=reason,Date=DATE,Limitation=limit))
deferred={'Hesperetin':('26530401','Primary abstract combines hesperetin/naringenin wording; isolated preparation attribution not established in this pass'),'Baicalein':('19827298','Medicinal-food boundary and primary preparation review deferred; no record admitted from general pharmacology'),'Theobromine':('5132558','Old interaction citation without verified modern experimental details; no new evidence extracted'),'Lycopene':('','Cooking and bioavailability literature is not by itself a drug-interaction endpoint')}
for n,(name,(pmid,reason)) in enumerate(deferred.items(),13):
    prop=load(O/'sources'/f'identity_{key(name)}.json').get('PropertyTable',{}).get('Properties',[{}])[0]
    decisions.append(dict(Candidate_ID=f'CAND-V5-{n:02d}',Canonical_Name=name,Compound_ID='',Aliases='',Identity_Source=f"https://pubchem.ncbi.nlm.nih.gov/compound/{prop.get('CID','')}",Identity_Confidence='Candidate identity snapshot only; no registry assignment',Food_Source='Food-associated candidate; exact preparation not newly certified',Selection_Rationale='Considered for incremental primary interaction coverage',Primary_Eligibility_PMID=pmid,DOI='',URL=f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/' if pmid else '',Processing_Status='Not evaluated for retention integration',Evidence_Types='not admitted',Decision='deferred',Reason=reason,Date=DATE,Limitation='Deferred does not mean no interaction exists'))
reg+=newreg;byname={r['Canonical_Name']:r for r in reg};new=[];claims=[]
for n,r in enumerate(ROWS,74):
    m=paper(r['pmid']);cr=byname[r['compound']];row={k:'' for k in fields};eid=f'SB-{n:04d}';locator='Abstract: methods and results; no full-text re-extraction claimed';review='primary_abstract_manual_extraction';claimsource=f'sources/pmid_{r["pmid"]}.json'
    if r['full']:locator=r['full'];review='selected_full_text_methods_or_outcome_review';claimsource='sources/'+r['full'].split(':')[0]
    direction=('reverse compound disposition effect' if r['affected']=='compound' else ('null or nonsynergistic at tested conditions' if r['outcome'] in ['null finding','no synergy detected','nonsignificant mean changes'] else 'source-specific effect; see endpoint'))
    row.update(Evidence_ID=eid,Compound=r['compound'],Compound_ID=cr['Compound_ID'],Drug=r['drug'],Interaction_Effect=r['effect'],Mechanism=r['mechanism'],Evidence_Type=r['type'],Evidence_Level='compound' if not 'formulation' in r['preparation'].lower() else 'formulation',Direction=direction,Quantitative_Outcome=r['quantity'],Dose=r['dose'],Population=r['pop'],Study_Design=('Controlled laboratory experiment' if r['type'] in ['Animal','In vitro'] else 'Human PK study; design and comparator in population/limitations'),Source_Title=m['title'],Authors=m.get('authorString',''),Year=m.get('pubYear',''),DOI=m.get('doi',''),PMID=r['pmid'],Source_Type='Primary research',Limitations=('Preclinical evidence; no human clinical effect established. ' if r['type'] in ['Animal','In vitro'] else 'Small primary human study; no meal exposure equivalence. ')+r['extra'],Confidence='Source-supported extraction; descriptive confidence only; applicability limited by study context',Notes='v5 manual primary review; no modeled effects or clinical risk score. Verification level: '+review,Study_ID='PMID:'+r['pmid'],Source_URL=f'https://pubmed.ncbi.nlm.nih.gov/{r["pmid"]}/',Source_Cache=f'release_v5_20261014/sources/pmid_{r["pmid"]}.json',Source_Locator=locator,Preparation=r['preparation'],Affected_Entity=r['affected'],Perpetrator='drug' if r['affected']=='compound' else 'compound_or_preparation',Outcome=r['outcome'],Identity_Status=cr['Identity_Status'],Release_Origin='v5_20261014',Clinical_Extrapolation='No automatic clinical classification; model/species/dose specific',CookRisk_Exposure_Link=cr['Link_Restriction'])
    if r['compound']=='Quercetin' and r['drug']=='Talinolol':row['Conflict_Group']='Quercetin-Talinolol_context'
    if r['compound']=='Myricetin' and r['drug']=='Paclitaxel':row['Conflict_Group']='Myricetin-Paclitaxel_vs_other_drugs'
    new.append(row);claims.append(dict(Evidence_ID=eid,PMID=r['pmid'],Claim_Field='Quantitative_Outcome',Claim=r['quantity'],Qualitative_Claim=r['effect'],Source=claimsource,Locator=locator,Verification_Level=review,Review_Status='Manual endpoint, context and direction comparison; numeric checks are diagnostics only',Outcome=r['outcome']))
e=baseline+new
for r in reg:r['Evidence_Records']=sum(x['Compound_ID']==r['Compound_ID'] for x in e)
write('compound_registry.csv',reg);write('candidate_selection.csv',decisions);write('selection_sources.csv',selection);write('stageB_food_drug_interactions_v5.csv',e,fields);write('new_evidence_records.csv',new,fields);write('claim_support_and_outcome_audit.csv',claims)
write('compound_selection_provenance_audit.csv',[{k:r[k] for k in ['Compound_ID','Canonical_Name','Origin','Selection_Rationale','Selection_Source','Selection_PMID','Selection_DOI','Date_Added','Provenance_Status','Retention_Status','Link_Restriction']} for r in reg])
write('identity_structure_audit.csv',[{k:r[k] for k in ['Compound_ID','Canonical_Name','PubChem_CID','InChIKey','Identity_Status','Identity_Source','Original_Molecular_Group','Link_Restriction']} for r in reg])
write('evidence_change_log.csv',[dict(Evidence_ID=r['Evidence_ID'],Action='added',Before='',After='new primary evidence record',Reason='Primary study and named drug endpoint verified',Source=r['Source_URL']) for r in new])
oldstudies={r['PMID']:r for r in read(V4/'outputs/study_registry.csv')};study=[];audit=[]
for pmid in sorted({r['PMID'] for r in e}):
    rr=[r for r in e if r['PMID']==pmid];r=rr[0];fresh=pmid not in oldstudies;status='inherited v4 bibliographic verification, not newly re-extracted'
    if fresh:
        cp=O/'sources'/f'crossref_{pmid}.json';d=load(cp).get('message',{}) if cp.exists() else {};sim=difflib.SequenceMatcher(None,norm(' '.join(d.get('title',[]))),norm(r['Source_Title'])).ratio() if isinstance(d,dict) else 0
        status='fresh Crossref title concordant' if sim>=.90 else ('DOI not supplied; MED verified' if not r['DOI'] else ('Crossref unavailable; MED verified' if not d else 'Crossref title requires review'))
    study.append(dict(Study_ID='PMID:'+pmid,PMID=pmid,DOI=r['DOI'],Title=r['Source_Title'],Authors=r['Authors'],Year=r['Year'],Evidence_Records=len(rr),Source_Cache=r['Source_Cache'],Source_URL=r['Source_URL'],Origin='new_v5_primary' if fresh else 'inherited_v4_primary',Verification=status,Independence='Unique PMID; not proof of separate participants or trial independence'))
    audit.append(dict(PMID=pmid,DOI=r['DOI'],Title=r['Source_Title'],Metadata_Status=status,Extraction_Scope='New abstract or selected full-text scope in claim ledger' if fresh else 'Inherited review levels retained in v4 audit',Evidence_IDs=' | '.join(x['Evidence_ID'] for x in rr),Source_Cache=r['Source_Cache']))
write('study_registry.csv',study);write('interaction_evidence_source_audit.csv',audit)
screens={};retrieved=0
for p in sorted((O/'sources').glob('*.json')):
    if not p.name.startswith(('search_','historical_')):continue
    for m in load(p).get('resultList',{}).get('result',[]):
        retrieved+=1;sid=(m.get('source',''),str(m.get('id','')))
        if sid not in screens:screens[sid]=dict(Source=sid[0],Source_ID=sid[1],Title=m.get('title',''),DOI=m.get('doi',''),Status='candidate_not_fully_screened',Reason='Capped retrieval is not a completed exclusion decision',Cache=p.relative_to(O).as_posix())
raw_unique_retrieved=len(screens)
selected={r['pmid'] for r in ROWS}
for pmid in sorted(selected):
    m=paper(pmid);screens[('MED',pmid)]=dict(Source='MED',Source_ID=pmid,Title=m['title'],DOI=m.get('doi',''),Status='included_primary',Reason='Manual primary interaction extraction',Cache=f'sources/pmid_{pmid}.json')
for pmid,why in [('27875319','Abstract does not unambiguously separate gallic and ellagic preparation groups; deferred'),('28766866','Separate-compound attribution not verified from accessible abstract; deferred'),('26530401','Hesperetin/naringenin grouping unresolved from abstract; deferred'),('12587952','Comparative model-method paper; not added as a duplicate simvastatin outcome'),('10794622','Food composition only; not interaction'),('11032486','Processing context only; not interaction'),('15309458','Processing/bioavailability context only; not interaction')]:
    m=paper(pmid);screens[('MED',pmid)]=dict(Source='MED',Source_ID=pmid,Title=m['title'],DOI=m.get('doi',''),Status='deferred_or_context_only',Reason=why,Cache=f'sources/pmid_{pmid}.json')
write('screening_log.csv',list(screens.values()))
processing=read(V4/'outputs/processing_provenance_audit.csv')
for pmid,comp,finding in [('10794622','Myricetin','Edible berry flavonol composition; analyte preparation must be distinguished from native free aglycone'),('11032486','Myricetin and Quercetin','Domestic berry processing affects flavonol recovery; no values imported into retention model'),('15309458','Naringenin and Chlorogenic acid','Cooked tomato bioavailability experiment; not a compound-drug interaction or a master-row validation')]:
    m=paper(pmid);processing.append(dict(Compound=comp,Source_Title=m['title'],DOI=m.get('doi',''),URL=f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/',Cache=f'sources/pmid_{pmid}.json',Review_Level='Primary abstract selected food/processing context',Finding=finding,Master_Link='not established; no automatic merge',Counted_As_Interaction_Report=False))
write('processing_provenance_audit.csv',processing)
warnings=read(V4/'outputs/warning_resolution_ledger.csv')
for r in warnings:r['Action']='Carried into v5; prior source review retained. '+r['Action'];r['After']='resolved in v4; retained audit history' if r['After'].startswith('resolved') else r['After']
for code,affected,detail in [('parent_identity_scope','Myricetin; Naringenin; Chrysin; Fisetin; Bergamottin','Standalone external identity is not a repaired master measurement link; study stereochemistry may be unspecified'),('new_abstract_detail_gaps','New abstract-level records','Missing sample sizes/doses remain explicit; no independent second reviewer'),('source_reporting_units','Naringenin-Felodipine; Ferulic acid-Clopidogrel; Quercetin-Pravastatin','Ambiguous AUC units, concentration units or human percentage/CI wording withheld'),('target_not_fully_reached','Evidence-record target','Only supported curated primary outcomes added; capped discovery not comprehensive'),('possible_participant_overlap','Quercetin genotype studies','Shared 165-person genotype pool mentioned; unique PMIDs are not independent-trial counts')]:
    warnings.append(dict(Warning_ID='V5-'+code,Code=code,Description=detail,Affected=affected,Classification='research or provenance limitation',Before='new scope in v5',Action='Documented; no imputation or retrospective repair',After='unresolved or accepted with stated scope',Remaining_Limitations=detail))
write('warning_resolution_ledger.csv',warnings)
summary=dict(version='v5',date=DATE,baseline=dict(compounds=14,records=73,drugs=v4actual['drugs'],primary_reports=v4actual['primary_reports']),compounds=len(reg),records=len(e),drugs=len({r['Drug'] for r in e}),primary_reports=len(study),new_compounds=len(newreg),new_records=len(new),new_primary_reports=sum(r['Origin']=='new_v5_primary' for r in study),corrected_records=0,removed_records=0,types=dict(collections.Counter(r['Evidence_Type'] for r in e)),new_types=dict(collections.Counter(r['Evidence_Type'] for r in new)),numerical_records=sum(bool(r['Quantitative_Outcome']) for r in e),new_numerical_records=sum(bool(r['Quantitative_Outcome']) for r in new),candidate_decisions=dict(collections.Counter(r['Decision'] for r in decisions)),new_verification_levels=dict(collections.Counter(r['Verification_Level'] for r in claims)),retrieved_candidate_occurrences=retrieved,unique_retrieved_candidates=len(screens),new_null_records=sum(r['Outcome']=='null finding' for r in new),new_nonsynergistic_records=sum(r['Outcome']=='no synergy detected' for r in new),inheritance_unchanged=e[:73]==baseline,planning_compound_range_met=25<=len(reg)<=30,planning_record_range_met=150<=len(e)<=200,planning_primary_range_met=80<=len(study)<=120)
(O/'outputs/release_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8');print(json.dumps(summary,indent=2))
summary.update(raw_unique_retrieved_candidates=raw_unique_retrieved,duplicate_retrieval_occurrences=retrieved-raw_unique_retrieved,adjudicated_primary_or_context_sources=sum(x['Status']!='candidate_not_fully_screened' for x in screens.values()),candidate_rejected=0)
(O/'outputs/release_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
gaps=[r['PMID']+': '+r['Verification'] for r in study if r['Origin']=='new_v5_primary' and r['Verification']!='fresh Crossref title concordant']
warnings.append(dict(Warning_ID='V5-bibliographic-gaps',Code='new_bibliographic_gaps',Description=' | '.join(gaps),Affected='New primary reports with unavailable DOI lookup or DOI not supplied',Classification='bibliographic limitation',Before='new primary sources',Action='Verified primary MED metadata; did not invent missing DOI',After='unresolved',Remaining_Limitations='Independent DOI verification incomplete for these reports'))
write('warning_resolution_ledger.csv',warnings)
oldreg={r['Compound_ID']:r for r in read(V4/'outputs/compound_registry.csv')};registrychanges=[]
for r in reg:
    old=oldreg.get(r['Compound_ID'],{})
    for k,value in r.items():
        if old.get(k,'')!=str(value):registrychanges.append(dict(Compound_ID=r['Compound_ID'],Field=k,Before=old.get(k,''),After=value,Action='new compound field' if not old else 'evidence coverage count updated'))
write('registry_change_log.csv',registrychanges)
write('inherited_v4_claim_support.csv',read(V4/'outputs/claim_support_and_outcome_audit.csv'))
write('original_nine_interaction_reference_map.csv',read(V4/'outputs/original_nine_interaction_reference_map.csv'))
priorreviews={r['Evidence_ID']:r for r in read(V4/'outputs/record_source_review_audit.csv')};newclaims={r['Evidence_ID']:r for r in claims}
write('all_record_review_audit.csv',[dict(Evidence_ID=r['Evidence_ID'],PMID=r['PMID'],Origin='new_v5' if r['Evidence_ID'] in newclaims else 'inherited_v4_unchanged',Verification_Level=newclaims[r['Evidence_ID']]['Verification_Level'] if r['Evidence_ID'] in newclaims else priorreviews[r['Evidence_ID']]['Verification_Level'],Source_Locator=r['Source_Locator'],Scope='New source-specific manual review' if r['Evidence_ID'] in newclaims else 'V4 review scope retained; not newly re-extracted in v5') for r in e])
newconflicts=[]
for pair in sorted({r['Compound']+'-'+r['Drug'] for r in e}):
    rr=[r for r in e if r['Compound']+'-'+r['Drug']==pair]
    if len(rr)>1 and any(r['Release_Origin']=='v5_20261014' for r in rr):newconflicts.append(dict(Pair=pair,Evidence_IDs=' | '.join(r['Evidence_ID'] for r in rr),Evidence_Types=' | '.join(sorted({r['Evidence_Type'] for r in rr})),Outcomes=' | '.join(r['Outcome'] for r in rr),Interpretation='Different preparations, species, routes, assays or regimens; not automatically direct contradictions; no pooling'))
write('context_comparison_audit.csv',newconflicts)
