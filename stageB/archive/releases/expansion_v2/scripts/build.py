import csv,json,sys,re,hashlib,collections,html,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1]; B=R.parent;O=R/'outputs';P=R/'reports'
sys.path.insert(0,str(R/'scripts'));from curation import N
def read(p):
 with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rows,fields=None):
 with open(O/name,'w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
metadata={};caches={};candidates={}
for root in [B/'sources',R/'sources']:
 for p in sorted(root.glob('*.json')):
  d=json.loads(p.read_text(encoding='utf8'))
  for s in d.get('resultList',{}).get('result',[]):
   if s.get('source')!='MED':continue
   sid=s['id'];metadata[sid]=s;caches[sid]=str(p.relative_to(B));
   if root==R/'sources':candidates[sid]=s
mapping=read(B/'outputs/stageB_compound_mapping.csv')
names={'Berberine':'MOL-E8216E9AF4FCDA58','Caffeine':'MOL-693364CB16A9EA2D','Curcumin':'MOL-16B10569D6F0625E','EGCG':'MOL-6B599D234F2062A2','Piperine':'MOL-A888520F9EA99648','Resveratrol':'MOL-25433E39C2198405','Genistein':'MOL-68234627A0347BFF','Naringin':'MOL-B87D9FA9FAF4DDCD','Capsaicin':'MOL-1F36FE6AE1F46586'}
byid={r['Canonical_Molecular_ID']:r for r in mapping};rows=[]
for old in read(B/'outputs/stageB_food_drug_interactions.csv'):
 rows.append(dict(Evidence_ID=old['interaction_id'],Compound=old['compound_name'],Compound_ID=old['compound_id'],Drug=old['drug_name'],Interaction_Effect=old['effect_description'],Mechanism=old['mechanism'],Evidence_Type=old['evidence_type'],Evidence_Level=old['evidence_level'],Direction=old['effect_direction'],Quantitative_Outcome=old['quantitative_result'] or '; '.join(x+': '+old[x] for x in ['AUC_change','Cmax_change','clearance_change','half_life_change'] if old[x]),Dose='; '.join(filter(None,[old['dose'],old['concentration'],old['frequency'],old['duration']])),Population='; '.join(filter(None,[old['species_or_population'],old['sample_size']])),Study_Design=old['study_type'],Source_Title=old['source_title'],Authors=old['authors'],Year=old['year'],DOI=old['doi'],PMID=old['source_id'],Source_Type='Primary research',Limitations=old['limitations'],Confidence='',Notes=old['notes'],Study_ID='PMID:'+old['source_id'],Source_URL=old['source_url'],Source_Cache=old['source_cache'],Source_Locator=old['source_locator'],Preparation=old['compound_form'],Co_Compounds=old['co_compounds'],Affected_Entity=old['affected_entity'],Perpetrator=old['perpetrator_entity'],Outcome=old['record_outcome'],Conflict_Group=old['conflict_group'],Identity_Status=old['identity_resolution_scope'],Release_Origin='initial_33'))
for n,new in enumerate(N,34):
 s=metadata[new['PMID']];r={k:'' for k in rows[0]};r.update(new)
 r.update(Evidence_ID=f'SB-{n:04}',Compound_ID=names[new['Compound']],Evidence_Level='compound',Source_Title=html.unescape(s['title']),Authors=s.get('authorString',''),Year=s['pubYear'],DOI=s.get('doi',''),Source_Type='Primary research',Study_ID='PMID:'+new['PMID'],Source_URL='https://pubmed.ncbi.nlm.nih.gov/'+new['PMID']+'/',Source_Cache=caches[new['PMID']],Identity_Status=byid[names[new['Compound']]]['mapping_status'],Release_Origin='expansion_v2')
 r['Preparation']=r['Preparation'] or new['Compound']+' as named in primary source; salt/form not fully extracted'
 r['Affected_Entity']=r['Affected_Entity'] or 'drug/probe';r['Perpetrator']=r['Perpetrator'] or 'compound';r['Outcome']=r['Outcome'] or 'observed effect';rows.append(r)
for r in rows:
 assert r['PMID'] in metadata,r['PMID']
 assert r['Compound_ID'] in byid
 assert byid[r['Compound_ID']]['mapping_status'].startswith('verified')
 assert 'review' not in [x.lower() for x in metadata[r['PMID']].get('pubTypeList',{}).get('pubType',[])]
 r['Confidence']='Moderate: primary human evidence; limited dose/population generalizability' if r['Evidence_Type'] in ['Human pharmacokinetic','Controlled clinical'] else 'Limited for human inference: primary '+r['Evidence_Type'].lower()+' evidence'
 if 'inconsistent' in r['Limitations'].lower() or 'disagree' in r['Limitations'].lower():r['Confidence']='Limited: primary evidence with reporting inconsistency'
 r['Clinical_Extrapolation']='No automatic clinical risk classification'
 r['CookRisk_Exposure_Link']='Parent connectivity only; stereochemistry unresolved in retention input' if r['Identity_Status']=='verified_connectivity' else 'Exact structure mapping; food measurement provenance still requires validation'
 r['Notes']=('; '.join(filter(None,[r['Notes'],'Inherited retention dataset DOI/provenance audit unresolved; Stage B source independently verified.'])))
keys=[(r['Study_ID'],r['Compound'],r['Drug'],r['Evidence_Type'],r['Preparation'],r['Co_Compounds']) for r in rows];assert len(keys)==len(set(keys))
write('stageB_food_drug_interactions_expanded.csv',rows)
priority=[];identity=[]
for m in mapping:
 mid=m['Canonical_Molecular_ID']; name=m['CookRisk_compound_name'];status=m['mapping_status'];mixed='Vitamin C (total' in name
 if not status.startswith('verified') or mixed:pr='Excluded / uncertain identity';reason='Unresolved structure/name agreement' if not mixed else 'Single group mixes ascorbic acid with total L-AA+DHAA measurement; not a single analyte'
 elif mid in names.values():pr='High priority';reason='Existing anchor or verified-parent compound with primary human interaction evidence'
 elif int(m['observation_count'])>=10:pr='Medium priority';reason='Useful retention coverage and verified identity; no interaction evidence assigned without primary extraction'
 else:pr='Low priority';reason='Verified identity but limited CookRisk coverage; deferred in bounded expansion'
 priority.append(dict(Compound_ID=mid,Original_Identity=name,Standardized_Identity=m['standardized_compound_name'],Observation_Count=m['observation_count'],Priority=pr,Reason=reason,Search_Status='Targeted search performed' if mid in names.values() else 'Inventory considered; not searched in expansion',Evidence_Records=sum(r['Compound_ID']==mid for r in rows)))
 identity.append(dict(Compound_ID=mid,Original_Identity=name,Standardized_Identity=m['standardized_compound_name'],Identifier_Used='PubChem CID:'+m['PubChem_CID'] if m['PubChem_CID'] else '',Status='excluded_mixed_analyte' if mixed else status,Problem_Found=reason if pr.startswith('Excluded') else ('Input stereochemistry incomplete; parent connectivity established' if status=='verified_connectivity' else 'Inherited food-source DOI audit unresolved'),Resolution='No identity silently changed; exclude mixed/uncertain groups; retain parent scope where stated',Verification_Source=m['mapping_source']))
write('compound_prioritization.csv',priority);write('qc_identity.csv',identity)
selected={r['PMID'] for r in rows};screen=[]
exclusions={'19221726':'Quercetin CookRisk group has mixed/unresolved analyte identity','21680781':'Quercetin CookRisk group has mixed/unresolved analyte identity','3444866':'No abstract and full-text effect not verified','2853056':'Potential overlapping 1987 quinolone experiment; independence unresolved; do not count twice','23765408':'Tacrolimus letter: metadata found; outcome not verified from accessible primary text','40524804':'Abstract does not resolve drug-specific direction; defer full-text extraction','40761345':'Animal evidence available; defer to human-first batch; not evidence of no interaction'}
for sid,s in sorted(candidates.items()):
 state='Included' if sid in selected else ('Excluded/deferred with specific reason' if sid in exclusions else 'Not fully screened / deferred')
 screen.append(dict(PMID=sid,DOI=s.get('doi',''),Title=html.unescape(s.get('title','')),Status=state,Reason='Primary findings extracted; relationship/context deduplicated' if sid in selected else exclusions.get(sid,'Bounded human-first expansion; no evidence claim assigned'),Cache=caches[sid]))
for sid,reason in exclusions.items():
 if sid not in candidates:screen.append(dict(PMID=sid,DOI='',Title='',Status='Excluded/deferred with specific reason',Reason=reason,Cache='Discovery in primary PubMed page; outcome not retained'))
write('source_screening_log.csv',screen)
studies=[]
for sid in sorted(selected):
 s=metadata[sid];studies.append(dict(Study_ID='PMID:'+sid,PMID=sid,DOI=s.get('doi',''),Title=html.unescape(s['title']),Authors=s.get('authorString',''),Year=s['pubYear'],Evidence_Records=sum(r['PMID']==sid for r in rows),Cache=caches[sid],Independence_Assessment='Same PMID grouped as one primary report; cross-paper overlap manually screened; no registry-level exhaustive independence verification'))
write('study_registry.csv',studies)
drugs=[]
for d in sorted({r['Drug'] for r in rows}):drugs.append(dict(Drug=d,Verification='Named administered drug/probe in included primary source',Supporting_PMIDs=' | '.join(sorted({r['PMID'] for r in rows if r['Drug']==d})),Scope='Parent drug name; dose/salt/form retained per evidence record; no guessed external ID'))
write('drug_identity_registry.csv',drugs)
conflicts=[]
for group in sorted({r['Conflict_Group'] for r in rows if r['Conflict_Group']}):
 rr=[r for r in rows if r['Conflict_Group']==group];conflicts.append(dict(Pair=group,Evidence_IDs=' | '.join(r['Evidence_ID'] for r in rr),Context=' | '.join(sorted({r['Evidence_Type'] for r in rr})),Interpretation='Context/regimen-dependent divergence; not necessarily directly contradictory replicated experiments',Resolution='Retain findings separately; no pooled risk or direction'))
write('conflict_synthesis.csv',conflicts)
types=collections.Counter(r['Evidence_Type'] for r in rows)
summary=dict(evidence_records=len(rows),new_records=len(N),unique_anchor_compounds=len({r['Compound'] for r in rows}),unique_drugs=len(drugs),primary_reports=len(studies),original_studies_operational_definition='Unique included primary PMIDs, same-report contexts collapsed; registry-level independence not established for every paper',human_PK_records=types['Human pharmacokinetic'],clinical_records=types['Controlled clinical'],animal_records=types['Animal'],in_vitro_records=types['In vitro'],quantitative_outcome_records=sum(bool(r['Quantitative_Outcome']) for r in rows),conflict_context_pairs=len(conflicts),compound_counts=dict(collections.Counter(r['Compound'] for r in rows)),priority_counts=dict(collections.Counter(r['Priority'] for r in priority)),model_independent=True)
(O/'evidence_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
for filename in ['stageB_dataset_source_audit.csv','stageB_unassigned_observations.csv','stageB_duplicate_standardized_identities.csv']:
 shutil.copyfile(B/'outputs'/filename,O/('inherited_'+filename))
searchlog=[]
for p in sorted(O.glob('*search_log.json')):searchlog.extend(json.loads(p.read_text(encoding='utf8')))
write('literature_search_log.csv',sorted(searchlog,key=lambda x:x['query_id']))
report=f'''# CookRisk Stage B expanded evidence release v2

Search and extraction date: 2026-10-06. This bounded expansion retains the initial 33 records and adds {len(N)} primary-source records. Stage B remains independent of the retention model.

| Measure | Count |
|---|---:|
| Evidence records | {len(rows)} |
| Anchor compounds | {summary['unique_anchor_compounds']} |
| Drugs/probe drugs | {len(drugs)} |
| Primary reports / operational study count | {len(studies)} |
| Human PK | {types['Human pharmacokinetic']} |
| Controlled clinical | {types['Controlled clinical']} |
| Animal | {types['Animal']} |
| In vitro | {types['In vitro']} |
| Records with numerical outcomes | {summary['quantitative_outcome_records']} |
| Context-dependent conflict pairs | {len(conflicts)} |

Numerical outcomes include metabolic indices and assay constants, not only AUC or clinical effects. Compound count refers to anchors; ingredients of mixtures are not counted as independent evidence. Same study/drug/context dose arms and endpoints are combined. One PMID can contribute several genuine drug relationships or human/animal/in-vitro contexts. The study count is a primary-report count: complete trial-registry verification of cross-paper independence was not feasible. The possible overlapping 1988 quinolone report was excluded from this count.

## Practical interpretation

Human supplementation studies usually involve much greater exposures than a cooked serving. Animal and cell results retain their own classifications. No numerical interaction-risk score, clinical risk category, or exposure threshold has been invented. A missing search result means no evidence retained, not proof of no interaction. Null and regimen-dependent findings remain in the database.

Resveratrol, genistein, naringin and capsaicin join the original five anchors. Exact structures are established for genistein and capsaicin. Resveratrol and naringin have verified parent connectivity but unresolved stereochemical detail in the input; automated isomer-specific retention/exposure linkage is not authorized by these mappings. Existing EGCG and piperine mappings carry the same parent-scope restriction. Dose/preparation and inherited food-measurement provenance must be verified before Stage C.

See `compound_prioritization.csv` for every one of the 198 inventory groups considered. Inventory consideration is not a literature search: this expansion searches nine selected anchor compounds, not all groups. See `source_screening_log.csv` for inclusion, specific exclusions and honestly marked deferred candidates.
'''
(P/'evidence_summary.md').write_text(report,encoding='utf8')
qc='''# QC report

No exact duplicate study/compound/drug/evidence-context/preparation/co-intervention rows were found. Original SB-0001–SB-0033 identifiers remain; additions begin at SB-0034. Same-report experiments share a PMID-based Study_ID. Different dose arms are summarized, not padded into separate records; the inherited curcumin alone versus curcumin+piperine tamoxifen arms remain distinct co-interventions. The 1988 quinolone study PMID 2853056 was deferred because overlap with PMID 3480885 could not be ruled out. Related publications and correction notices are not counted as independent evidence.

Independent Crossref audit: 33 primary titles concordant, one manually verified omitted subtitle (PMID 17963429; authors Kasibhatta/Naidu and year 2007 concordant), nine Crossref lookups unavailable, and two primary records without a supplied DOI. These eleven cases remain verifiable by primary PMID, but independent DOI confirmation is incomplete. No unresolved title mismatch was accepted. See primary_source_DOI_audit.csv.

## Identities and inherited provenance

The initial audit's 96 uncertain groups remain excluded from evidence assignment. In addition, the ascorbic-acid group mixes single L-ascorbic acid and total L-AA+DHAA measurements; it is explicitly excluded in this release's identity/priority tables. This is a QC overlay, not a silent rewrite of the initial release. Parent connectivity is distinguished from complete stereochemical verification. No uncertain group receives an interaction record. Drug names are checked against primary administered probes; external identifiers are not guessed.

The inherited retention dataset audit found 145 author/year metadata discrepancies among 208 DOI lookups and ten unavailable lookups. Those are provenance flags, not proof that every concentration is wrong. DOI 10.1016/j.lwt.2021.111500 is a confirmed source mismatch for the five Persin/avocado records: its publication concerns fish-oil/gelatin nanofibrous membranes. These issues remain unresolved and are copied into the inherited source-audit table; no original identity, DOI or measurement has been silently changed. The 221 observations without molecular IDs remain unassigned and are not linked to interaction evidence.

## Unsupported or disputed claims withheld

- PMID 28533679: Cmax ratio 0.85 has 90% CI 0.70–1.04. Do not call this a statistically established Cmax reduction. AUC reduction and repeated-regimen null are separately described within one record.
- PMID 22300367: conflicting abstract/results prose on human dose-specific AUC fold changes; those magnitudes are withheld. Mouse AUC and vesicle Ki belong only to their separate experimental contexts.
- PMID 26633237: malformed absolute AUC unit in abstract; reported dimensionless ratios retained.
- PMID 21943317: suspicious clearance units; those values omitted.
- PMID 25624269: reversed metabolite-formation wording; measured epoxide/parent ratio and parent PK retained.
- Proposed therapeutic benefits in small piperine/resveratrol PK studies are not verified clinical outcomes and were not promoted to clinical risk or benefit claims.
- Reviews, modeling-only predictions, extract effects attributed to an untested constituent, and uncertain compound identities are not included as primary clinical interaction evidence.

Every specific excluded/deferred source is listed in `source_screening_log.csv`. Other retrieved candidates are marked not fully screened, not falsely called excluded after full review. Confidence is an extraction-level descriptive assessment, not GRADE, a validated risk score, or independent second-reviewer adjudication.

## Conflicting evidence

`conflict_synthesis.csv` retains four inherited context groups and the added EGCG–rosuvastatin regimen contrast. They differ in species, dose, formulation or endpoints; the count does not imply five directly replicated contradictions. No majority-vote direction is assigned.
'''
(P/'qc_report.md').write_text(qc,encoding='utf8')
method='''# Literature search and extraction methodology

Search date: 2026-10-06. Main database: Europe PMC REST core metadata/abstracts (PubMed MED primary identifiers). Primary PubMed and PMC pages used for targeted discovery and source checking. Reviews may identify primary references but are not counted as primary experiments. Crossref/PubChem verification from the initial release remains cached; new primary titles/authors/DOIs/PMIDs are checked in MED metadata. No Google Scholar or new systematic Crossref search is claimed.

The exact 45 queries, retrieved counts, database, date and source-cache paths are in `literature_search_log.csv`. Initial broad compound/interaction/human queries retrieved at most 100 hits each. More selective title-based queries were then used, followed by historical queries through 2020 to reduce recent-hit truncation and exact identifier queries. Broad-query records beyond the stated date, preprints and secondary sources are not eligible for evidence. This is a reproducible bounded expansion, not an exhaustive systematic review or PRISMA claim. Result order/capping can omit relevant studies; MED candidates are retained with a transparent screening state, while other database sources remain in the raw query caches.

Priority 1: the existing five anchors. Priority 2: reliable-parent CookRisk compounds with plausible primary evidence and useful retention links. Nine compounds were searched: berberine, caffeine, curcumin, EGCG, piperine, resveratrol, genistein, naringin and capsaicin. All 198 inventory groups receive an explicit priority status; unresolved or mixed measurements are excluded. Genistein and naringin have low input frequencies but were selected because human primary evidence provides meaningful mechanistic bridges. Frequency alone is not an evidence criterion.

Inclusion requires an identifiable primary report, a named drug/probe relationship, reliable exact/parent identity with scope stated, an actually measured interaction or tested null, and a source-supported result. Drug and preparation identity, species, experimental context and affected entity must be distinguished. Exclude unsupported direction, review-only assertion, unverified abstract-free outcomes, uncertain mixed identity, generalized juice-to-constituent inference and unresolved same-experiment duplication. Modeling predictions are not measured AUC.

Extraction unit: study/compound/drug/experimental evidence context. Collapse dose arms/endpoints; split actual human, animal and cell contexts. PMID-based Study_ID links rows from one source. Check titles, authors, year, DOI and available methods/context for related reports; defer uncertain overlap instead of increasing the study count. Full-text values are used only with a table/section locator; otherwise abstract-only scope is explicit. Missing dose/magnitude is left blank or marked not extracted.

Quality: moderate for source-supported primary human observations with design/population/dose limitations; limited for human inference from animal/cell work; limited for unresolved reporting inconsistencies. This descriptive scheme is not a validated evidence grade. It evaluates support for the extracted observation and transportability separately from evidence type. No second independent reviewer or comprehensive formal risk-of-bias scoring was performed. Preserve null findings and context-dependent divergences in linked synthesis rows.

Stage B contains no model predictions. Later exposure linkage must verify food preparation, retained compound identity/isomer, concentration and serving size, timing and repeated dosing. A change of retention model changes that separate linkage, not the primary interaction findings.

Offline reproduction: run `scripts/build.py` using saved JSON caches and the unchanged initial release. `scripts/curation.py` is the explicit extraction record. Internet query provenance is in the CSV log; queries can be rerun against the API using the recorded strings. Saved caches, file hashes and input hashes enable auditing even if live search ranking changes.
'''
(P/'literature_search_methodology.md').write_text(method,encoding='utf8')
dictionary=['# Evidence schema','', 'One row is a distinct study/compound/drug/evidence context. Blank means not extracted or not available, never zero or no interaction.','']
for k in rows[0]:dictionary.append('- **'+k+'**: '+({'Evidence_ID':'Stable evidence-record key.','Compound_ID':'Original CookRisk molecular group key; no groups merged.','Evidence_Level':'Preparation specificity (compound, extract, food preparation), not quality rank.','Confidence':'Descriptive support/generalizability assessment, not a risk score.','Study_ID':'Primary PMID grouping key.','Quantitative_Outcome':'Reported units, ratios, assay constants or statistical intervals; affected entity must be read.','Source_Cache':'Cache path relative to stageB root.','Conflict_Group':'Context/regimen divergence synthesis key; blank does not prove consistency.','CookRisk_Exposure_Link':'Identity scope and remaining source constraints for later linkage.','Release_Origin':'Initial evidence versus new expansion.','Clinical_Extrapolation':'Guard against automatic clinical inference.'}.get(k,'Source-extracted '+k.replace('_',' ').lower()+'; use alongside preparation, evidence type and limitations.')))
(P/'data_dictionary.md').write_text('\n'.join(dictionary),encoding='utf8')
(R/'README.md').write_text('''# CookRisk Stage B expansion v2

Open reports/evidence_summary.md first. The main table is outputs/stageB_food_drug_interactions_expanded.csv. Other required deliverables are compound_prioritization.csv, qc_identity.csv, reports/qc_report.md and reports/literature_search_methodology.md. The original stageB/outputs release remains unchanged. Sources and extraction scripts are included for audit. This evidence layer is model-independent. Read limitations before Stage C exposure integration.
''',encoding='utf8')
manifest={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for sub in ['outputs','reports','scripts','sources'] for p in sorted((R/sub).glob('*')) if p.is_file()}
(R/'manifest_sha256.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps(summary,indent=2))
