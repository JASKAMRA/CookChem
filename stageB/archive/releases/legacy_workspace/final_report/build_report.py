"""Create the final report from saved Stage B evidence, without modifying evidence."""
from pathlib import Path
import csv,json,collections,hashlib,re
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[1];OUT=Path(__file__).resolve().parent
def read(p):
 with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def load(p):return json.loads(p.read_text(encoding='utf8'))
E=read(ROOT/'expansion_v2/outputs/stageB_food_drug_interactions_expanded.csv')
INITIAL=read(ROOT/'outputs/stageB_food_drug_interactions.csv')
S=load(ROOT/'expansion_v2/outputs/evidence_summary.json');I=load(ROOT/'outputs/stageB_summary.json')
studies=read(ROOT/'expansion_v2/outputs/study_registry.csv');proc=read(ROOT/'outputs/stageB_processing_evidence.csv')
refs={s['PMID']:f'R{n}' for n,s in enumerate(studies,1)}
def ref(p):return '['+refs[p]+']'
blocks=[]
def h(t,level=1):blocks.append(('heading',t,level))
def p(t):blocks.append(('paragraph',t))
def table(headers,rows,widths=None):blocks.append(('table',headers,rows,widths))
def page():blocks.append(('pagebreak',))

blocks.append(('title','CookRisk Stage B Final Report'))
p('Food Drug Interaction Evidence Layer')
p('Consolidated initial release and expanded release v2')
p('Project context  Predicting Food Drug Interaction Risk Under Different Cooking Methods')
p('Report date  6 October 2026')
h('Executive summary')
p('Stage B has produced an auditable, model-independent literature evidence layer for CookRisk. The final expanded release contains 64 evidence records across nine anchor compounds and 34 named drugs or probe drugs, supported by 45 included primary reports. It adds 31 records to the initial 33-record release while retaining stable evidence identifiers and preserving null findings, combination interventions and context-dependent disagreements.')
table(['Final release measure','Result'],[['Evidence records','64'],['Anchor compounds','9'],['Drugs and probe drugs','34'],['Primary reports grouped by PMID','45'],['Human pharmacokinetic records','49'],['Controlled clinical records','2'],['Animal records','7'],['In vitro records','6'],['Records with quantitative outcomes','42'],['Context dependent conflict pairs','5']],[4.6,1.9])
p('The evidence table supports literature lookup and later exposure integration. It does not supply a clinically validated risk score, a safe dietary dose or a predicted interaction strength for a cooked meal. Major unresolved constraints include inherited food-measurement provenance, uncertain or mixed molecular identities, incomplete stereochemical information and differences between supplement doses and ordinary food exposure.')
p('The original Stage B files remain unchanged. The expanded interaction table is the current evidence output. Earlier Stage A linkage files describe the original release and are not an automatically updated 64-record exposure system. This report consolidates both releases and identifies their different scopes.')
page()
h('Contents')
blocks.append(('toc',))
p('The appendices contain a compact profile of every included evidence record, a complete primary-source bibliography, the field dictionary and a file inventory. The accompanying CSV tables retain the full machine-readable evidence and audit information.')
page()

h('1 Purpose and boundaries of Stage B')
p('CookRisk aims to connect cooking conditions with compound retention and, eventually, documented compound-drug interactions. Stage A benchmarks prediction of retention. Stage B establishes what published experiments report about food-associated compounds and drugs. Stage C is intended to integrate identity, retained amount and exposure. Stage D would evaluate risk using an independently justified framework. The latter two stages were not completed as part of this evidence release.')
p('The intended chain is cooked food, retained compound, estimated exposure, documented interaction evidence and eventual risk assessment. Stage B supplies the documented-evidence part of this chain. The chain remains incomplete until the chemical form, measurement basis, serving size, timing, absorption and clinical applicability are established.')
table(['Layer','Work completed in this task','Interpretation'],[['Stage A context','Reviewed supplied benchmark report and preserved selected-model OOF outputs','No model retraining or new-condition prediction'],['Stage B evidence','Identity inventory, source collection, primary extraction, expansion and QC','Completed bounded evidence release'],['Stage C exposure','Traceability and readiness constraints documented','No retained-dose or exposure estimates generated'],['Stage D risk','Evidence boundaries and limitations documented','No clinical risk score or food ranking generated']],[1.05,2.65,2.8])
p('Stage B is model-independent because published interaction observations do not change when Extra Trees, XGBoost or another retention model is chosen. A later join to predicted retention can change with the model. This separation prevents model performance from being mistaken for confidence in the underlying clinical literature.')

h('2 Inputs and preservation')
p('Four supplied files provided the project context and data. The master CSV defines the molecular and cooking-observation inventory. The OOF CSV supplies saved Stage A predictions. The benchmark PDF describes model selection and validation. The literature-review Word document supplies background; instructions in background documents were not treated as independent authorization for new work.')
table(['Input','Role'],[['cookchem_master_expanded_round11.csv','Master observations, compound groups, food and cooking fields, concentration and provenance metadata'],['stageA_oof_predictions.csv','Saved record-level predictions and actual retention targets for benchmark models'],['CookRisk_StageA_Benchmark_Report.pdf','Stage A validation, results and selected reference-model context'],['CookRisk_BTP_Literature_Review_Assignment_2_FINAL_CORRECTED (1).docx','BTP literature background and project framing']],[2.85,3.65])
p('The input manifest records original paths, byte sizes and SHA-256 hashes. Preserved copies are under stageB/inputs. The initial verification found that the copies match the supplied files and that historical input hashes remained unchanged. No new experiment code, fitted deployment model or locked Stage A training snapshot was supplied in the inspected checkout.')
p('Original Stage B outputs and the first release archive are retained. The expansion resides in stageB/expansion_v2. This report is a consolidation of those saved releases; it does not silently repair their evidence, identity or food-retention inputs.')

h('3 Master dataset inventory')
table(['Inventory measure','Count or status'],[['Master observations','1,350'],['Columns in master CSV','97'],['Nonblank molecular groups','198'],['Observations without molecular group ID','221'],['Unique compound name strings','241'],['Food name strings','187'],['Food categories','Not supplied'],['Selected Stage A OOF observations','1,124'],['Selected Stage A OOF molecular groups','197']],[4.6,1.9])
p('The 221 observations with blank molecular identifiers are retained in a separate table. They are not treated as a 199th molecule and are not assigned interaction evidence. Name strings, molecular groups and standardized source identities are different counting units; they must not be substituted for each other.')
p('The original compound and food relations preserve the supplied molecular group and Record_ID pointers. Food labels and concentration fields are inherited project observations, not newly certified food-composition facts. A food-compound association alone does not establish that a serving produces the exposure used in a drug-interaction experiment.')

h('4 Molecular identity verification')
p('Identity verification compared original names and structures with PubChem identifiers, source structures and synonyms. RDKit structure comparison distinguished exact agreement from parent-connectivity agreement with incomplete stereochemical representation. Groups were not merged solely because names appeared similar, and historical identifiers were retained separately from resolved source identifiers.')
table(['Initial identity status','Groups','Meaning'],[['Verified exact structure and name','79','Exact mapping within the stated source representation'],['Verified parent connectivity','23','Parent identity supported; stereochemistry incomplete'],['Uncertain identity','96','No interaction assigned'],['Mapped groups in initial release','102','79 exact plus 23 connectivity'],['Distinct standardized source CIDs','101','One CID spans two original groups']],[2.4,.65,3.45])
p('A later QC overlay excludes the ascorbic-acid group because it mixes single L-ascorbic acid with total L-AA plus DHAA measurements. Consequently the expansion priority table has 97 excluded or uncertain groups: the 96 unresolved groups plus this mixed-analyte group. The initial 79/23/96 mapping counts remain historical counts and were not rewritten.')
p('The quercetin group combines quercetin and total-flavonol labels and remains ineligible for compound-specific interaction assignment. Other unresolved identity groups remain visible in the QC table rather than disappearing from the inventory. An interaction published for a reliable chemical does not automatically belong to an unreliable CookRisk measurement group.')
p('Resveratrol and naringin were admitted only at the verified-parent scope. Their input stereochemistry does not establish an isomer-specific cooking exposure. Existing EGCG and piperine mappings carry related restrictions. Genistein and capsaicin have exact structure mappings. A parent-scope link supports retrieval of relevant literature but not automatic transfer of a stereospecific experimental effect into the retention model.')
p('One standardized CID, 5282102, spans the original Kaempferol-3-Glucoside and Astragalin groups. Those groups remain separate. This finding merits a separate identity and Stage A fold audit; it does not by itself establish leakage.')

h('5 Work sequence and release history')
table(['Work package','Completed action'],[['Inventory and input preservation','Read supplied tables and reports; recorded hashes and source pointers'],['Identity standardization','Built a 198-group mapping and retained uncertain groups without interactions'],['Initial source collection','Cached molecular-group queries, source identifiers and standardized-name follow-up'],['Initial evidence release','Extracted 33 records from 26 primary reports across five anchors and 18 drugs'],['Processing and Stage A context','Separated three processing records and preserved original OOF linkage'],['Inherited source audit','Checked 208 dataset DOIs and recorded provenance discrepancies'],['Controlled expansion','Searched nine selected compounds using 45 logged queries; added 31 evidence records'],['Final validation and packaging','Built final tables, source registry, priority and QC outputs; verified keys and caches']],[1.65,4.85])
p('The expansion began with the existing berberine, caffeine, curcumin, EGCG and piperine anchors. Resveratrol, genistein, naringin and capsaicin were then added because their reliable exact or parent identities and primary evidence provided meaningful CookRisk bridges. No new verified berberine row was added in this batch; the existing five berberine records remain. This is an evidence-driven result rather than a quota for each compound.')
p('The initial release searched the full molecular inventory. The later expansion did not repeat generic searches for all 198 groups; it focused on nine selected compounds. The two phases therefore have different query counts, retrieval caps and coverage claims.')

h('6 Compound prioritization')
table(['Expansion priority','Groups','Decision basis'],[['High priority','9','Existing anchors or selected compounds with primary human interaction evidence'],['Medium priority','18','Verified identity and useful retention coverage; no interaction assigned without extraction'],['Low priority','74','Verified identity with limited input coverage; deferred in the bounded expansion'],['Excluded or uncertain identity','97','Unresolved structure/name agreement or mixed analyte measurement']],[1.8,.6,4.1])
p('The prioritization CSV covers every one of the 198 inventory groups. Inventory consideration does not mean literature screening was completed for every group. Low-frequency genistein and naringin were deliberately selected because available human probe or transporter evidence was useful despite only one master observation each. A high priority label is a research-selection label, not a high clinical-risk label.')
links={x['Canonical_Molecular_ID']:x for x in read(ROOT/'outputs/stageB_stageA_linkage.csv')}
table(['Anchor','Initial records','Final records','Master observations','Identity scope'],[[c,str(sum(e['compound_name']==c for e in INITIAL)),str(n),links[next(e['Compound_ID'] for e in E if e['Compound']==c)]['observation_count'],'Parent connectivity' if next(e['Identity_Status'] for e in E if e['Compound']==c)=='verified_connectivity' else 'Exact structure'] for c,n in S['compound_counts'].items()],[1.5,.8,.8,.85,2.55])

h('7 Literature search protocol')
p('The initial phase used Europe PMC and primary-source follow-up, PubChem identity data and Crossref provenance checks. It retrieved the first 25 candidates per molecular-group query, with 115 groups exceeding that cap. The original search log also preserves the blank-ID bucket retrieval, which is not an additional molecular group. A further 102 standardized-name queries used mapped PubChem titles and a 6 October 2026 publication cutoff. These are candidate searches, not exhaustive review of all results.')
p('The expansion used Europe PMC core metadata and abstracts with primary PubMed MED identifiers. Primary PubMed and PMC pages supported targeted discovery and checking. Forty-five exact queries are saved: 16 broad searches, nine title-based searches, nine historical title-based searches through 2020, nine exact or specific-source searches and two probe-study searches. Each retrieved at most 100 results. Query caps and ordering limit recall.')
table(['Illustrative actual expansion query','Purpose'],[['(piperine) AND (pharmacokinetics OR interaction) AND (human OR volunteers OR clinical)','Compound-level discovery'],['TITLE:resveratrol AND (TITLE:pharmacokinetic OR TITLE:interaction OR TITLE:volunteers OR TITLE:bioavailability OR TITLE:metabolism) AND FIRST_PDATE:[1900-01-01 TO 2026-10-06]','Title-focused discovery'],['TITLE:caffeine AND (TITLE:volunteers OR TITLE:human OR TITLE:interaction OR TITLE:drug) AND FIRST_PDATE:[1900-01-01 TO 2020-12-31]','Earlier literature retrieval'],['EXT_ID:20716633 AND SRC:MED','Exact primary study verification']],[4.5,2.0])
p('The search date is 6 October 2026. Exact query text, hit count, number retrieved, database, date and cache path are in the saved search logs. Broad-query preprints, secondary sources and records outside the eligible date are not promoted to included evidence. MED candidates have screening states; non-MED results remain available in raw response caches.')
p('A review could identify a primary reference but was not counted as a primary clinical experiment. This release does not claim a Google Scholar systematic search, an exhaustive systematic Crossref search or PRISMA compliance. Saved response snapshots make the release reproducible even when future rankings and metadata change.')
h('7 1 Inclusion and exclusion criteria',2)
p('Inclusion required a traceable primary report, an identified drug or probe relationship, a reliable CookRisk-compatible exact or parent compound identity, and an actually measured effect or tested null. Human, animal and cell contexts had to be distinguishable. Extracts, salts and mixtures were described as studied rather than assumed to be isolated compounds.')
p('Exclusions included unresolved CookRisk identity, unsupported effect direction, abstract-free outcomes without verified primary text, review-only assertions, modeling predictions misrepresented as measured PK, and whole-food or juice effects attributed to an untested constituent. Potential overlapping reports were deferred where independent experiments could not be established.')
h('7 2 Screening and independence',2)
p('The source screening log distinguishes included sources, specifically excluded or deferred sources, and candidates not fully screened. The last category is not falsely described as a complete exclusion decision. Primary reports share a PMID-based Study_ID. Rows from one report can describe distinct drugs or human, animal and cell experiments, but they are not counted as separate reports.')
p('The original report used the expression original studies. In the consolidated release the more precise count is 45 primary reports grouped by unique PMID. Complete trial-registry confirmation of cross-paper independence was not performed. In particular PMID 2853056 was withheld because overlap with the 1987 quinolone experiment PMID 3480885 could not be ruled out.')

h('8 Evidence representation and extraction')
p('The evidence unit is a study, compound, drug and experimental context, with preparation and co-intervention distinctions retained. Most dose arms and endpoints are summarized within one row. The inherited curcumin-alone and curcumin-plus-piperine tamoxifen rows remain separate because their co-interventions differ. Human extract nadolol evidence and transporter-cell evidence remain separate contexts.')
p('The expanded table has 36 columns. These include source identifiers and locators, direction and affected entity, preparation and co-compounds, dose and population, quality limitations and exposure-link scope. Appendix C defines every column. Evidence_Level describes preparation specificity, such as compound, extract or food preparation; it is not a quality grade.')
p('Quantitative extraction preserves endpoint identity, units, reported confidence intervals, approximate qualifiers and direction. Metabolic parent/metabolite ratios are not labeled AUC changes. Assay Ki values are not clinical thresholds. Tumor-growth inhibition is not a drug concentration. Missing or disputed values remain blank or explicitly not extracted rather than becoming zero.')
p('Reverse interactions are retained. For example ciprofloxacin and fluvoxamine can alter caffeine disposition. In those rows the measured effect belongs to the food compound, not necessarily to the prescription drug. Affected_Entity and Perpetrator prevent this directional distinction from being lost in later analysis.')
p('Confidence labels are descriptive extraction-level judgments. Primary human observations generally receive moderate support with population and dose limitations. Preclinical evidence has limited applicability to human inference. Reporting inconsistencies can reduce confidence. This is not formal GRADE assessment, a validated clinical score or independent two-reviewer adjudication.')

h('9 Final evidence results')
table(['Measure','Initial release','Expanded release','Change'],[['Records','33','64','31 added'],['Anchor compounds','5','9','4 added'],['Drugs and probes','18','34','16 added'],['Primary reports','26','45','19 added'],['Human PK records','24','49','25 added'],['Controlled clinical records','1','2','1 added'],['Animal records','5','7','2 added'],['In vitro records','3','6','3 added'],['Quantitative outcome records','20','42','22 added'],['Context dependent conflict pairs','4','5','1 added']],[2.7,1.1,1.2,1.5])
p('The final table contains 51 human records when human PK and controlled clinical evidence are combined. Forty-two records have extracted numerical outcomes; this includes metabolic indices and biochemical assay kinetics as well as PK or PD measurements. Dose-only records do not qualify as quantitative-outcome records. The remaining 22 records are qualitative, null without an extracted effect size, or have disputed/unavailable numerical outcomes.')
p('The 64 rows are not 64 independent trials, 64 established hazards or 64 validated compound-food-drug risks. Several rows come from a single primary report, some involve probe drugs, and preclinical findings retain their evidence-type limits. Nine anchors describe the main row compounds; additional co-ingredients in mixture experiments are not counted as independent anchors.')
h('9 1 Representative initial findings',2)
p('Berberine with cyclosporine increased exposure in a small renal-transplant PK substudy, including a reported AUC increase of 34.5%. The clinical and PK sample sizes differ and remain visible. Berberine with midazolam increased exposure in a human probe study, while dextromethorphan and losartan findings used metabolic ratios. '+ref('16133554')+' '+ref('21870106'))
p('Piperine with fexofenadine increased AUC from 3403.7 to 5724.7 ng.h/mL in a 12-person sequential study. Human curcumin with or without piperine reduced tamoxifen exposure; combination treatment also reduced endoxifen exposure. These observations describe the studied supplement regimens, not standard pepper or turmeric servings. '+ref('27981349')+' '+ref('30909366'))
h('9 2 Representative additions',2)
p('Piperine pretreatment increased carbamazepine AUC by 47.9% and Cmax by 68.7% in healthy volunteers. Separate piperine studies reported greater chlorzoxazone and diclofenac exposure. Small sequential designs and high supplement exposure restrict clinical extrapolation. '+ref('27776366')+' '+ref('27670974')+' '+ref('27052193'))
p('A single EGCG co-dose reduced rosuvastatin AUC_last with a geometric mean ratio of 0.81 and 90% CI 0.67-0.97. After ten-day pretreatment no significant AUC or Cmax difference was detected. The single-dose Cmax CI crossed 1; its reduction is not treated as a statistically established effect. '+ref('28533679'))
p('Resveratrol was supported by human studies with diclofenac, carbamazepine, chlorzoxazone and celecoxib, and a four-probe enzyme study. In the latter, buspirone AUC increased while dextromethorphan and losartan metabolic ratios changed; the caffeine/paraxanthine ratio suggested greater CYP1A2 activity. These endpoints are not interchangeable. '+ref('26633237')+' '+ref('25624269')+' '+ref('26680654')+' '+ref('37935204')+' '+ref('20716633'))
p('Genistein changed caffeine-based enzyme indices and modestly reduced midazolam and talinolol exposure in separate human studies. Aqueous naringin reduced fexofenadine AUC to 75% of the water-control result; the larger grapefruit-juice effect was not attributed to naringin alone. Oral capsaicin did not detectably modify aspirin platelet inhibition at the tested doses, preserving an outcome-specific null. '+ref('21222115')+' '+ref('21943317')+' '+ref('17301733')+' '+ref('25532954'))
h('9 3 Mechanistic coverage',2)
p('The database covers proposed or experimentally supported enzyme inhibition and induction, transporter uptake and efflux effects, altered absorption or elimination, pharmacodynamic augmentation and antagonism. A measured exposure change may support a mechanism hypothesis without proving it. Human PK, cell transport, microsomal kinetics and animal tissue findings remain separate evidence contexts.')
p('Evidence for CYP3A4, CYP2C9, CYP2D6, CYP1A2 and CYP2E1 probe effects is represented alongside OATP, BCRP, P-glycoprotein, MRP2 and OAT findings. These are source-specific mechanisms. The final release does not turn them into a generic list of every substrate that might be affected.')

h('10 Null findings and conflicting evidence')
p('Null findings are retained only where an experiment tested a relationship and failed to detect the specified effect. Absence of a database row means no qualifying evidence was retained under this bounded search and identity policy. It does not mean that no interaction exists.')
table(['Pair','Context that explains differing findings'],[['Piperine and carbamazepine','Human studies increased exposure; repeated rat treatment decreased systemic and brain exposure. Microsomal inhibition is a separate mechanistic observation.'],['Piperine and midazolam','Isolated piperine affected sedation/clearance; a short curcuminoid-piperine mixture study found no meaningful parent-drug PK change.'],['Curcumin and tamoxifen','Rat oral exposure increased; human exposure decreased under different supplement regimens.'],['EGCG and bortezomib','Cell antagonism and concentration-dependent xenograft findings; no human interaction established.'],['EGCG and rosuvastatin','Single co-dose AUC reduction contrasted with a repeated-pretreatment null in the same report.']],[2.05,4.45])
p('These five groups are context-dependent divergences, not five directly replicated contradictions in the same population and regimen. Species, dose, preparation, duration, endpoint and metabolite differences are preserved. The database does not select a majority direction or combine incompatible effect coefficients.')

h('11 Cooking and processing evidence')
p('Three processing records from two primary publications remain in a separate table. They help connect cooking questions to compound availability, but they are not included in the 64 interaction-record count or the 45 interaction-report count.')
table(['Compound and process','Reported processing observation','Boundary'],[['Piperine in heated black pepper','16-34% loss under tested boiling or pressure-cooking conditions','No universal pepper retention coefficient'],['Curcumin in heated turmeric','27-53% loss; 12-30% with tamarind under tested conditions','Matrix-specific processing observation'],['Green tea brewing and catechins','Extraction and epimerization depend on conditions; total catechins peaked at 95 C for 10 min','Total-catechin optimum is not isolated EGCG retention']],[1.9,2.8,1.8])
p('The spice study tested boiling for 10 or 20 minutes and pressure cooking for 10 minutes. The tea study examined infusions at 60 C or 95 C across 5-300 minutes. These observations do not establish how much any cooking method changes a drug-interaction effect. A cooking loss, a supplement PK effect and a clinically meaningful outcome require separate links. [R46] [R47]')

h('12 Stage A traceability and model separation')
p('The supplied benchmark report retained Extra Trees as the selected reference among evaluated configurations. It used 1,124 observations from 197 molecular groups, five-fold molecular GroupKFold and the locked retention target. Stage B verified that every selected OOF record matched the master Record_ID, molecular group and actual retention target.')
p('The original compound-linkage table preserves group and food counts, model identity and whether an OOF observation is available. The observation-linkage table preserves original row pointers, food and cooking conditions, baseline concentration, actual and predicted retention, fold and provenance flags. It does not invent a compound-average retention or retained amount.')
table(['Linkage fact','Verified scope'],[['Original evidence linked to selected-model groups','33 of 33 initial evidence records'],['Saved OOF observations','1,124 selected-model records'],['OOF molecular groups','197'],['Master-only molecular group','PhIP group with five rows; no selected OOF'],['Expanded evidence link status','Nine anchors retain CookRisk molecular IDs; original linkage files are not regenerated as 64-record evidence-exposure joins']],[2.6,3.9])
p('The current master marks only 1,009 rows eligible, while 115 selected OOF rows have FALSE in its current Final_Preprocessing_Eligible flag. Molecular IDs and target values still match. Without the frozen Stage A input and runner, eligibility lineage cannot be reconciled. No retrospective retraining or repair was performed.')
p('OOF predictions are validation outputs for existing observations, not deployable predictions for a new cooking condition. No fitted deployment model was saved in the inspected materials. A later retention-model change can alter the linkage or exposure estimate while leaving the Stage B literature evidence unchanged.')

h('13 Source provenance and quality control')
h('13 1 Inherited retention data provenance',2)
table(['Inherited dataset DOI audit','Result'],[['Distinct DOIs audited','208'],['Author or year metadata discrepancies','145'],['Lookup unavailable','10'],['Metadata concordant by subtraction','53'],['Confirmed example','Five Persin and avocado rows cite an unrelated DOI']],[3.7,2.8])
p('DOI 10.1016/j.lwt.2021.111500 belongs to a 2021 Liu et al. fish-oil/gelatin encapsulation publication, while five supplied Persin/avocado cooking observations attribute it to a 2022 Molina et al. study. This is a confirmed source mismatch and blocks validation of those retention claims. The publisher source is https://www.sciencedirect.com/science/article/abs/pii/S0023643821006538.')
p('Metadata disagreement is a source-verification flag, not automatic proof that every associated measurement is fabricated. Conversely, matching title metadata does not validate a compound concentration, cooking condition or retention value. Independently checked Stage B interaction reports are a separate provenance layer and are not invalidated merely because an inherited food citation is wrong.')
h('13 2 Primary interaction source verification',2)
table(['Final primary report DOI audit','Reports'],[['Crossref title concordant','33'],['Manual concordance with omitted subtitle','1'],['Crossref lookup unavailable but MED PMID verified','9'],['No DOI supplied but primary PMID verified','2'],['Unreviewed accepted title mismatches','0']],[5.2,1.3])
p('For PMID 17963429, Crossref omits the design subtitle but the principal title, authors Kasibhatta and Naidu, and year 2007 agree. Eleven primary reports therefore lack complete independent DOI confirmation: nine unavailable lookups and two without supplied DOIs. Their primary PubMed identifiers remain available. This limitation is disclosed rather than converted into an all-DOIs-verified claim.')
h('13 3 Reporting inconsistencies and withheld claims',2)
table(['Primary report','QC decision'],[['PMID 28533679','Cmax CI includes 1; retain AUC finding and regimen contrast without claiming significant Cmax reduction'],['PMID 22300367','Abstract and results prose disagree on dose-specific human AUC folds; disputed magnitudes withheld'],['PMID 26633237','Malformed absolute AUC unit; dimensionless reported ratios retained'],['PMID 21943317','Suspicious clearance units; those clearance values omitted'],['PMID 25624269','Reversed metabolite-formation wording; measured ratios and parent PK retained'],['PMID 21870106','Abstract Tmax/half-life labels conflict with table; disputed fields not silently corrected'],['PMID 24398010','Design, sample-size and clearance wording inconsistencies remain explicit']],[1.6,4.9])
p('Claims that small supplement PK studies demonstrate therapeutic benefit, reduced adverse events or safe dose reduction were not promoted to verified clinical conclusions. Animal and cell observations were not labeled human clinical risk. Modeled AUC increases in a microsomal source were not recorded as observed human PK.')
h('13 4 Duplicate handling and exclusions',2)
p('No duplicate key was found for study, compound, drug, evidence context, preparation and co-intervention. Initial evidence identifiers SB-0001 through SB-0033 remain stable; additions are SB-0034 through SB-0064. Same-report contexts share Study_ID. Exact checks prevent row duplication but do not alone establish independent trial populations.')
table(['Source or issue','Reason excluded or deferred'],[['PMIDs 19221726 and 21680781','Quercetin primary evidence cannot be assigned to the contaminated CookRisk group'],['PMID 3444866','No abstract; effect not verified from accessible primary text'],['PMID 2853056','Potential overlap with an earlier quinolone experiment'],['PMID 23765408','Tacrolimus letter metadata found; outcome not verified'],['PMID 40524804','Abstract did not resolve drug-specific direction'],['PMID 40761345','Animal source deferred in human-first batch'],['Other retrieved candidates','Not fully screened; no unsupported interaction assigned']],[2.2,4.3])
h('13 5 Automated validation',2)
p('All 20 initial integrity checks passed. The separate initial release verification reported disk-table integrity, source matching, original counts, food-claim separation, unique contexts, immutable input copies and byte-identical offline rebuild as PASS. All 13 expanded-release checks passed. They assess structure and traceability, not exhaustive literature coverage or clinical validity.')
checks=load(ROOT/'expansion_v2/outputs/validation_results.json')
labels={'record_count_matches_summary':'64-row count matches summary','unique_evidence_ids':'Evidence IDs are unique','initial_identifiers_preserved':'Initial identifiers and relationships retained','no_excluded_identity_assigned':'No excluded identity receives evidence','complete_priorities':'All 198 groups prioritized','evidence_categories_sum':'Evidence types sum to 64','primary_report_count':'45 distinct primary PMIDs','required_fields_present':'Required descriptive fields present','source_cache_PMID_title_DOI_concordance':'Cached PMID title and DOI match each row','no_source_after_search_date':'Included publication years not later than 2026','conflict_records_refer_to_existing_ids':'Conflict references resolve','all_search_caches_present':'Logged expansion query caches present','no_unreviewed_Crossref_title_mismatches':'No unresolved accepted Crossref title mismatch'}
table(['Expansion validation check','Saved result'],[[labels[k],'PASS' if v else 'FAIL'] for k,v in checks.items()],[5.5,1.0])
p('The source-date check validates included publication years; it is not a complete day-level publication-date audit. Cache matching confirms bibliographic association, not every extracted numerical interpretation. The manual review complements these checks, but it was conducted by one reviewer and does not establish error-free or exhaustive evidence.')

h('14 Output catalogue and how to use it')
p('Use the expanded evidence CSV for current interaction lookup and the report for interpretation. The initial tables remain useful for inventory, food associations, processing evidence and preserved Stage A context. They must not be treated as if every old count or join were updated by the expansion.')
table(['Current expanded output','Purpose'],[['stageB_food_drug_interactions_expanded.csv','64-row current evidence table with 36 fields'],['compound_prioritization.csv','198-group research priority and eligibility inventory'],['qc_identity.csv','Original identity, standardized identity, verification status and problem overlay'],['evidence_summary.json','Final machine-readable counts'],['study_registry.csv','45 primary reports and per-report record counts'],['drug_identity_registry.csv','34 drug names with supporting primary identifiers'],['source_screening_log.csv','Included sources and explicit deferred screening states'],['literature_search_log.csv','45 exact expansion queries with dates and cache locations'],['primary_source_DOI_audit.csv','Independent bibliographic confirmation and unresolved lookups'],['conflict_synthesis.csv','Five context-dependent divergence groups'],['validation_results.json','13 saved expansion checks'],['inherited audit tables','Copies of upstream DOI audit, blank-ID observations and duplicate-CID cluster']],[2.7,3.8])
p('These files are under stageB/expansion_v2/outputs. The matching reports folder contains evidence_summary.md, qc_report.md, literature_search_methodology.md and data_dictionary.md. The expansion scripts preserve search collection, manual extraction, table building and validation. Source caches and manifest_sha256.json support traceability.')
table(['Initial output family','Retained purpose'],[['Compound mapping and identity audit','198-group structures, identifiers, synonym checks and missingness'],['Foods and food compound relations','Inherited food labels and Record_ID associations'],['Initial interaction and literature tables','Historical 33-record evidence release'],['Interaction compound relation','Mixture anchor and verified co-intervention relations'],['Processing evidence','Three separate processing records from two sources'],['Stage A compound and observation links','Preserved selected-model OOF lineage'],['Search and source audit logs','Initial query snapshots and dataset DOI flags'],['Reports and manifests','Methodology, references, reproducibility and hash verification']],[2.7,3.8])
p('The original archive is CookRisk_StageB_Evidence_Release.zip. The current expanded archive is CookRisk_StageB_Expanded_v2.zip. They are separate release packages. The final report is supplied as an editable Word document and a PDF, with a readable source copy and report-specific output audit. Full file paths are documented in Appendix D.')
h('14 1 Suggested lookup workflow',2)
p('Start with a CookRisk molecular group and its identity status. If identity is uncertain or mixed, stop compound-specific assignment. For an eligible group, filter the expanded evidence table by Compound_ID and drug, then read Evidence_Type, Preparation, Co_Compounds, Dose, Population and Direction together. Check Source_Locator, limitations and any conflict group before considering exposure integration. A high-priority label or a populated evidence row is not a clinical recommendation.')

h('15 Reproducibility and audit trail')
p('The initial release can be rebuilt offline from cached identity and publication data using its saved mapping and build scripts. The existing repository environment supplies RDKit 2026.3.5 for molecular comparison. The expansion build uses saved JSON responses, the original mapping table, original interaction table and explicit manual extraction in expansion_v2/scripts/curation.py. No retention model is trained during either evidence-table build.')
p('The authoritative record of online searches is the logged query text and cached response, not the current live ranking. Source collection scripts were adapted during retrieval; the complete historical query set is retained in CSV and JSON logs. Re-running a live search can produce different results. Exact release reproduction should use preserved snapshots and hashes.')
table(['Audit artefact','What it establishes'],[['audit/input_manifest.json','Original inputs and preserved-copy SHA-256 hashes'],['audit/output_manifest.json','Initial release output hashes'],['audit/release_verification.json','Initial disk and rebuild checks'],['expansion_v2/manifest_sha256.json','Expansion file hashes'],['Evidence Source_Cache and Source_Locator','Publication snapshot and extraction location'],['Study_ID and PMID','Primary report grouping'],['Release_Origin','Initial or added evidence provenance']],[2.8,3.7])
p('Reproducibility establishes that the recorded process recreates the saved release. It does not establish that inherited source measurements are accurate, that all relevant studies were found or that a clinical inference is justified. Scientific correction should be a new documented version rather than an unrecorded change to the original inputs.')

h('16 Limitations and readiness for later stages')
p('The completed evidence database has a deliberately bounded scope. Searches were capped and many candidates remain unscreened. Extraction often relies on abstracts. Full study protocols and numerical tables were not verified for every included report. Drug external identifiers and salt/form normalization remain incomplete. Descriptive confidence is not a formal risk-of-bias framework, and no independent second reviewer performed adjudication.')
p('The retention data also contain 96 uncertain molecular groups, an additional mixed-analyte exclusion, 221 unassigned observations, parent-connectivity mappings and unresolved provenance problems. The 115 eligibility-flag discrepancies require the original frozen Stage A lineage. These issues limit exposure interpretation even when the interaction paper itself is correctly identified.')
p('Supplement doses, aqueous isolated-compound solutions, concentrated extracts, cell concentrations and animal mg/kg regimens cannot be equated to a cooked serving. Active metabolites, timing, repeated dosing, absorption, physiological state and prescribed drug regimen can change the relationship. None of those missing links is filled with an arbitrary multiplier or numerical hazard score.')
table(['Stage C requirement','Current state and next action'],[['Verified measurement source','Inherited DOI issues remain; validate food compound and processing values in primary sources'],['Exact analyte and form','Resolve mixed groups and stereochemistry; retain salts and mixtures as studied'],['Compatible retention output','Recover locked model lineage and fitted model if new predictions are needed'],['Amount and basis','Validate units, wet/dry basis, concentration definition and serving size'],['Exposure context','Establish timing, dosing frequency, bioavailability and active metabolites'],['Clinical applicability','Match drug regimen and population; do not transfer animal/cell effects automatically']],[2.0,4.5])
p('Stage D requires a separately justified risk framework and validation. It would need effect-size relevance, exposure plausibility, uncertainty, clinical endpoints and appropriate expert assessment. Stage B supplies traceable evidence inputs; it does not make dietary restriction, drug-dose adjustment or safety decisions.')

h('17 Final project status')
p('Stage B is complete as a bounded, auditable evidence release. The work established the molecular inventory, identity qualification, primary-source extraction, human versus preclinical separation, quantitative and null outcome handling, conflict synthesis, processing context, inherited-data audits and reproducible outputs. The controlled expansion nearly doubled the record count, from 33 to 64, while adding four anchors and retaining source-specific limitations.')
p('The defensible conclusion is that CookRisk now has a structured evidence layer ready for literature retrieval and carefully controlled subsequent integration. It is not yet an exhaustive literature database or a clinically validated cooked-food interaction predictor. The remaining constraints are part of the scientific result and are explicitly preserved for further work.')

page();h('Appendix A Complete evidence profiles')
p('All 64 included evidence records are listed below. These profiles summarize the saved final table. Preparation, evidence type and endpoint must be read together. A blank quantitative outcome is described as not extracted; it is not converted to zero. Full dose, population, confidence, notes, identity scope and source-cache fields remain in the CSV.')
for e in E:
 h(e['Evidence_ID']+' '+e['Compound']+' and '+e['Drug'],2)
 p(e['Evidence_Type']+' | '+e['Study_ID']+' '+ref(e['PMID'])+' | '+e['Direction']+'.')
 p(e['Interaction_Effect']+' Mechanism: '+(e['Mechanism'] or 'Not established in extraction')+'.')
 p('Dose and preparation: '+(e['Dose'] or 'Dose not extracted')+'. '+e['Preparation']+('. Co-intervention: '+e['Co_Compounds'] if e['Co_Compounds'] else '')+'. Population: '+e['Population']+'.')
 p('Quantitative outcome: '+(e['Quantitative_Outcome'] or 'No reliable numerical effect extracted')+' Limitations: '+e['Limitations'])

page();h('Appendix B Primary source bibliography')
p('R1 through R45 identify the included interaction reports. R46 and R47 identify separate processing publications. The interaction study count therefore remains 45. Each evidence profile links to its primary-report entry rather than treating a review as an experiment.')
for s in studies:
 p('['+refs[s['PMID']]+'] '+s['Authors']+' ('+s['Year']+'). '+s['Title']+' PMID '+s['PMID']+'.'+(' DOI '+s['DOI']+'.' if s['DOI'] else ' DOI not supplied in extracted metadata.')+' https://pubmed.ncbi.nlm.nih.gov/'+s['PMID']+'/')
seen=set();n=46
for x in proc:
 if x['doi'] in seen:continue
 seen.add(x['doi']);p(f'[R{n}] '+x['authors']+' ('+x['year']+'). '+x['source_title']+'. '+x['journal']+'. DOI '+x['doi']+'. '+x['source_url']);n+=1

page();h('Appendix C Evidence field dictionary')
definitions={
'Evidence_ID':'Stable row identifier SB-0001 to SB-0064.', 'Compound':'Anchor chemical named in the primary relationship.', 'Compound_ID':'Original CookRisk molecular group; groups are not merged.', 'Drug':'Named administered drug or metabolic probe.', 'Interaction_Effect':'Measured effect or tested null summarized in words.', 'Mechanism':'Source-supported or explicitly proposed mechanism.', 'Evidence_Type':'Human pharmacokinetic, Controlled clinical, Animal or In vitro.', 'Evidence_Level':'Preparation specificity; not evidence strength.', 'Direction':'Direction of the reported endpoint; can be regimen or endpoint dependent.', 'Quantitative_Outcome':'Extracted effect size, ratio, interval or assay result; not dose alone.', 'Dose':'Compound/drug dose, concentration, frequency or duration when extracted.', 'Population':'Human sample or animal/cell experimental system.', 'Study_Design':'Design of the source experiment.', 'Source_Title':'Primary publication title.', 'Authors':'Primary publication author metadata.', 'Year':'Source publication year; online and print dates can differ.', 'DOI':'Digital object identifier where supplied.', 'PMID':'Primary PubMed identifier.', 'Source_Type':'Primary research for included evidence.', 'Limitations':'Source, extraction and applicability constraints.', 'Confidence':'Descriptive support; not GRADE or a clinical risk score.', 'Notes':'Additional interpretation and provenance cautions.', 'Study_ID':'PMID-based grouping for records from one primary report.', 'Source_URL':'Primary source link.', 'Source_Cache':'Saved source response path relative to stageB.', 'Source_Locator':'Abstract, section or table used for extraction.', 'Preparation':'Actual isolated compound, salt, extract or food preparation scope.', 'Co_Compounds':'Named co-interventions; avoids duplicate ingredient attribution.', 'Affected_Entity':'Whether the measured change concerns drug, compound or probe.', 'Perpetrator':'Compound/preparation or drug producing the disposition change.', 'Outcome':'Observed effect, null or mixed endpoint status.', 'Conflict_Group':'Context-dependent synthesis key where assigned.', 'Identity_Status':'Exact structure or parent-connectivity scope.', 'Release_Origin':'Initial 33 records or expansion additions.', 'Clinical_Extrapolation':'Explicit guard against automatic clinical-risk classification.', 'CookRisk_Exposure_Link':'Identity/provenance constraints before exposure transfer.'}
table(['Field','Meaning'],[[k,definitions[k]] for k in E[0]],[1.9,4.6])
p('Blank means unavailable, not extracted or not reliably resolved. It never means zero, normal, safe or no interaction. Source_Cache paths are relative to stageB; expansion caches include the expansion_v2 prefix.')

page();h('Appendix D File inventory')
p('Workspace root: C:/Users/dakshant/Documents/CookChem. Paths below are relative to this root. CSV row counts exclude the header. This inventory is derived directly from the saved files, rather than copied from an earlier narrative count.')
for sub,label in [('outputs','Initial Stage B tables'),('expansion_v2/outputs','Expanded release tables')]:
 h(label,2)
 files=[]
 for f in sorted((ROOT/sub).glob('*.csv')):files.append([str(f.relative_to(ROOT.parent)).replace('\\','/'),str(len(read(f)))])
 table(['File','Rows'],files,[5.75,.75])
h('Reports and audit material',2)
for t in ['stageB/reports contains the original inventory, methodology, QC, data dictionary, references, requirements checklist, reproducibility report and dataset-source audit.', 'stageB/expansion_v2/reports contains the expansion evidence summary, QC report, search methodology and data dictionary.', 'stageB/audit contains original input and output manifests, extracted background documents and initial release verification.', 'stageB/sources and stageB/expansion_v2/sources preserve query responses, source metadata, identity data and available full text.', 'stageB/scripts and stageB/expansion_v2/scripts preserve collection, extraction, build and validation logic.', 'stageB/final_report contains this consolidated Word and PDF report, readable source, builder and report-specific audit.'] :p(t)
h('Preserved input hashes',2)
for x in load(ROOT/'audit/input_manifest.json'):p(Path(x['bundled_path']).name+' SHA-256 '+x['sha256'])

# Write reusable text source and machine-readable report plan.
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'report_content.json').write_text(json.dumps(blocks,ensure_ascii=False,indent=2),encoding='utf8')
md=[]
for b in blocks:
 if b[0]=='title':md.extend(['# '+b[1],''])
 elif b[0]=='heading':md.extend(['#'*(b[2]+1)+' '+b[1],''])
 elif b[0]=='paragraph':md.extend([b[1],''])
 elif b[0]=='table':
  md.append('| '+' | '.join(b[1])+' |');md.append('| '+' | '.join('---' for _ in b[1])+' |')
  md.extend('| '+' | '.join(str(c).replace('|',' / ') for c in row)+' |' for row in b[2]);md.append('')
(OUT/'CookRisk_StageB_Final_Report.md').write_text('\n'.join(md),encoding='utf8')

doc=Document();sec=doc.sections[0];sec.page_height=Inches(11.7);sec.page_width=Inches(8.3)
sec.top_margin=Inches(.72);sec.bottom_margin=Inches(.7);sec.left_margin=Inches(.85);sec.right_margin=Inches(.85)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','TOC 1','TOC 2']:
 if name not in doc.styles:continue
 st=doc.styles[name];st.font.name='Calibri';st.font.color.rgb=RGBColor(0,0,0)
st=doc.styles['Normal'];st.font.size=Pt(10.5);st.paragraph_format.line_spacing=1.1;st.paragraph_format.space_after=Pt(6)
for name,size in [('Title',25),('Heading 1',16),('Heading 2',12)]:
 st=doc.styles[name];st.font.size=Pt(size);st.paragraph_format.space_before=Pt(13);st.paragraph_format.space_after=Pt(7);st.paragraph_format.keep_with_next=True
doc.styles['Title'].paragraph_format.space_before=Pt(0)
for border in list(doc.styles.element.iter(qn('w:pBdr'))):border.getparent().remove(border)
toc_title=doc.styles.add_style('ContentsTitle',1);toc_title.base_style=doc.styles['Normal'];toc_title.font.size=Pt(16);toc_title.font.bold=True;toc_title.font.color.rgb=RGBColor(0,0,0);toc_title.paragraph_format.space_after=Pt(10)
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
footer.add_run('CookRisk Stage B  |  Page ').font.size=Pt(8)
for field in ['PAGE','NUMPAGES']:
 if field=='NUMPAGES':footer.add_run(' of ')
 run=footer.add_run();el=OxmlElement('w:fldSimple');el.set(qn('w:instr'),field);run._r.addnext(el)
def cell_fill(cell,color):
 pr=cell._tc.get_or_add_tcPr();sh=OxmlElement('w:shd');sh.set(qn('w:fill'),color);pr.append(sh)
def cell_border(cell):
 pr=cell._tc.get_or_add_tcPr();bd=OxmlElement('w:tcBorders')
 for side in ['top','left','bottom','right']:
  el=OxmlElement('w:'+side);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');bd.append(el)
 pr.append(bd);m=OxmlElement('w:tcMar')
 for side,v in [('top',85),('bottom',85),('left',100),('right',100)]:
  el=OxmlElement('w:'+side);el.set(qn('w:w'),str(v));el.set(qn('w:type'),'dxa');m.append(el)
 pr.append(m)
for b in blocks:
 kind=b[0]
 if kind=='title':
  para=doc.add_paragraph(b[1],'Title');bd=OxmlElement('w:pBdr');bottom=OxmlElement('w:bottom');bottom.set(qn('w:val'),'nil');bd.append(bottom);para._p.get_or_add_pPr().append(bd)
 elif kind=='heading':
  if b[1]=='Contents':doc.add_paragraph(b[1],'ContentsTitle')
  else:doc.add_heading(b[1],b[2])
 elif kind=='paragraph':doc.add_paragraph(b[1])
 elif kind=='pagebreak':doc.add_page_break()
 elif kind=='toc':
  para=doc.add_paragraph();fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'TOC \\o "1-1" \\h \\z \\u');para._p.append(fld)
 elif kind=='table':
  headers,rs,widths=b[1:];t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
  for i,w in enumerate(widths or [6.5/len(headers)]*len(headers)):t.columns[i].width=Inches(w)
  for i,c in enumerate(headers):t.rows[0].cells[i].text=c
  rep=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(rep)
  for row in rs:
   cells=t.add_row().cells
   for i,c in enumerate(row):cells[i].text=str(c).replace('_','_\u200b') if 'File' in headers or 'Field' in headers else str(c)
  for ri,row in enumerate(t.rows):
   # Keep each table row intact; allow long tables to flow with repeated headings.
   cant=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(cant)
   for ci,cell in enumerate(row.cells):
    cell.width=Inches((widths or [6.5/len(headers)]*len(headers))[ci]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER;cell_border(cell)
    if ri==0:cell_fill(cell,'333333')
    elif ri%2==0:cell_fill(cell,'F3F4F5')
    for para in cell.paragraphs:
     para.paragraph_format.space_after=Pt(0);para.paragraph_format.line_spacing=1.04
     if ci>0 and all(len(str(x[ci]))<14 for x in rs):para.alignment=WD_ALIGN_PARAGRAPH.CENTER
     for run in para.runs:run.font.size=Pt(9);run.font.bold=ri==0;run.font.color.rgb=RGBColor(255,255,255) if ri==0 else RGBColor(0,0,0)
  doc.add_paragraph().paragraph_format.space_after=Pt(2)
doc.core_properties.title='CookRisk Stage B Final Report';doc.core_properties.subject='Consolidated food drug interaction evidence release';doc.core_properties.author='CookRisk Project';doc.core_properties.keywords='CookRisk; Stage B; literature evidence; pharmacokinetics; quality control'
doc.save(OUT/'CookRisk_StageB_Final_Report.docx')
assert len(E)==64 and len(studies)==45 and sum(S[k] for k in ['human_PK_records','clinical_records','animal_records','in_vitro_records'])==64
print('Report authored with',len(blocks),'content blocks and',len(E),'evidence profiles')
