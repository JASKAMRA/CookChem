# CookRisk Stage B Final Report

Food Drug Interaction Evidence Layer

Consolidated initial release and expanded release v2

Project context  Predicting Food Drug Interaction Risk Under Different Cooking Methods

Report date  6 October 2026

## Executive summary

Stage B has produced an auditable, model-independent literature evidence layer for CookRisk. The final expanded release contains 64 evidence records across nine anchor compounds and 34 named drugs or probe drugs, supported by 45 included primary reports. It adds 31 records to the initial 33-record release while retaining stable evidence identifiers and preserving null findings, combination interventions and context-dependent disagreements.

| Final release measure | Result |
| --- | --- |
| Evidence records | 64 |
| Anchor compounds | 9 |
| Drugs and probe drugs | 34 |
| Primary reports grouped by PMID | 45 |
| Human pharmacokinetic records | 49 |
| Controlled clinical records | 2 |
| Animal records | 7 |
| In vitro records | 6 |
| Records with quantitative outcomes | 42 |
| Context dependent conflict pairs | 5 |

The evidence table supports literature lookup and later exposure integration. It does not supply a clinically validated risk score, a safe dietary dose or a predicted interaction strength for a cooked meal. Major unresolved constraints include inherited food-measurement provenance, uncertain or mixed molecular identities, incomplete stereochemical information and differences between supplement doses and ordinary food exposure.

The original Stage B files remain unchanged. The expanded interaction table is the current evidence output. Earlier Stage A linkage files describe the original release and are not an automatically updated 64-record exposure system. This report consolidates both releases and identifies their different scopes.

## Contents

The appendices contain a compact profile of every included evidence record, a complete primary-source bibliography, the field dictionary and a file inventory. The accompanying CSV tables retain the full machine-readable evidence and audit information.

## 1 Purpose and boundaries of Stage B

CookRisk aims to connect cooking conditions with compound retention and, eventually, documented compound-drug interactions. Stage A benchmarks prediction of retention. Stage B establishes what published experiments report about food-associated compounds and drugs. Stage C is intended to integrate identity, retained amount and exposure. Stage D would evaluate risk using an independently justified framework. The latter two stages were not completed as part of this evidence release.

The intended chain is cooked food, retained compound, estimated exposure, documented interaction evidence and eventual risk assessment. Stage B supplies the documented-evidence part of this chain. The chain remains incomplete until the chemical form, measurement basis, serving size, timing, absorption and clinical applicability are established.

| Layer | Work completed in this task | Interpretation |
| --- | --- | --- |
| Stage A context | Reviewed supplied benchmark report and preserved selected-model OOF outputs | No model retraining or new-condition prediction |
| Stage B evidence | Identity inventory, source collection, primary extraction, expansion and QC | Completed bounded evidence release |
| Stage C exposure | Traceability and readiness constraints documented | No retained-dose or exposure estimates generated |
| Stage D risk | Evidence boundaries and limitations documented | No clinical risk score or food ranking generated |

Stage B is model-independent because published interaction observations do not change when Extra Trees, XGBoost or another retention model is chosen. A later join to predicted retention can change with the model. This separation prevents model performance from being mistaken for confidence in the underlying clinical literature.

## 2 Inputs and preservation

Four supplied files provided the project context and data. The master CSV defines the molecular and cooking-observation inventory. The OOF CSV supplies saved Stage A predictions. The benchmark PDF describes model selection and validation. The literature-review Word document supplies background; instructions in background documents were not treated as independent authorization for new work.

| Input | Role |
| --- | --- |
| cookchem_master_expanded_round11.csv | Master observations, compound groups, food and cooking fields, concentration and provenance metadata |
| stageA_oof_predictions.csv | Saved record-level predictions and actual retention targets for benchmark models |
| CookRisk_StageA_Benchmark_Report.pdf | Stage A validation, results and selected reference-model context |
| CookRisk_BTP_Literature_Review_Assignment_2_FINAL_CORRECTED (1).docx | BTP literature background and project framing |

The input manifest records original paths, byte sizes and SHA-256 hashes. Preserved copies are under stageB/inputs. The initial verification found that the copies match the supplied files and that historical input hashes remained unchanged. No new experiment code, fitted deployment model or locked Stage A training snapshot was supplied in the inspected checkout.

Original Stage B outputs and the first release archive are retained. The expansion resides in stageB/expansion_v2. This report is a consolidation of those saved releases; it does not silently repair their evidence, identity or food-retention inputs.

## 3 Master dataset inventory

| Inventory measure | Count or status |
| --- | --- |
| Master observations | 1,350 |
| Columns in master CSV | 97 |
| Nonblank molecular groups | 198 |
| Observations without molecular group ID | 221 |
| Unique compound name strings | 241 |
| Food name strings | 187 |
| Food categories | Not supplied |
| Selected Stage A OOF observations | 1,124 |
| Selected Stage A OOF molecular groups | 197 |

The 221 observations with blank molecular identifiers are retained in a separate table. They are not treated as a 199th molecule and are not assigned interaction evidence. Name strings, molecular groups and standardized source identities are different counting units; they must not be substituted for each other.

The original compound and food relations preserve the supplied molecular group and Record_ID pointers. Food labels and concentration fields are inherited project observations, not newly certified food-composition facts. A food-compound association alone does not establish that a serving produces the exposure used in a drug-interaction experiment.

## 4 Molecular identity verification

Identity verification compared original names and structures with PubChem identifiers, source structures and synonyms. RDKit structure comparison distinguished exact agreement from parent-connectivity agreement with incomplete stereochemical representation. Groups were not merged solely because names appeared similar, and historical identifiers were retained separately from resolved source identifiers.

| Initial identity status | Groups | Meaning |
| --- | --- | --- |
| Verified exact structure and name | 79 | Exact mapping within the stated source representation |
| Verified parent connectivity | 23 | Parent identity supported; stereochemistry incomplete |
| Uncertain identity | 96 | No interaction assigned |
| Mapped groups in initial release | 102 | 79 exact plus 23 connectivity |
| Distinct standardized source CIDs | 101 | One CID spans two original groups |

A later QC overlay excludes the ascorbic-acid group because it mixes single L-ascorbic acid with total L-AA plus DHAA measurements. Consequently the expansion priority table has 97 excluded or uncertain groups: the 96 unresolved groups plus this mixed-analyte group. The initial 79/23/96 mapping counts remain historical counts and were not rewritten.

The quercetin group combines quercetin and total-flavonol labels and remains ineligible for compound-specific interaction assignment. Other unresolved identity groups remain visible in the QC table rather than disappearing from the inventory. An interaction published for a reliable chemical does not automatically belong to an unreliable CookRisk measurement group.

Resveratrol and naringin were admitted only at the verified-parent scope. Their input stereochemistry does not establish an isomer-specific cooking exposure. Existing EGCG and piperine mappings carry related restrictions. Genistein and capsaicin have exact structure mappings. A parent-scope link supports retrieval of relevant literature but not automatic transfer of a stereospecific experimental effect into the retention model.

One standardized CID, 5282102, spans the original Kaempferol-3-Glucoside and Astragalin groups. Those groups remain separate. This finding merits a separate identity and Stage A fold audit; it does not by itself establish leakage.

## 5 Work sequence and release history

| Work package | Completed action |
| --- | --- |
| Inventory and input preservation | Read supplied tables and reports; recorded hashes and source pointers |
| Identity standardization | Built a 198-group mapping and retained uncertain groups without interactions |
| Initial source collection | Cached molecular-group queries, source identifiers and standardized-name follow-up |
| Initial evidence release | Extracted 33 records from 26 primary reports across five anchors and 18 drugs |
| Processing and Stage A context | Separated three processing records and preserved original OOF linkage |
| Inherited source audit | Checked 208 dataset DOIs and recorded provenance discrepancies |
| Controlled expansion | Searched nine selected compounds using 45 logged queries; added 31 evidence records |
| Final validation and packaging | Built final tables, source registry, priority and QC outputs; verified keys and caches |

The expansion began with the existing berberine, caffeine, curcumin, EGCG and piperine anchors. Resveratrol, genistein, naringin and capsaicin were then added because their reliable exact or parent identities and primary evidence provided meaningful CookRisk bridges. No new verified berberine row was added in this batch; the existing five berberine records remain. This is an evidence-driven result rather than a quota for each compound.

The initial release searched the full molecular inventory. The later expansion did not repeat generic searches for all 198 groups; it focused on nine selected compounds. The two phases therefore have different query counts, retrieval caps and coverage claims.

## 6 Compound prioritization

| Expansion priority | Groups | Decision basis |
| --- | --- | --- |
| High priority | 9 | Existing anchors or selected compounds with primary human interaction evidence |
| Medium priority | 18 | Verified identity and useful retention coverage; no interaction assigned without extraction |
| Low priority | 74 | Verified identity with limited input coverage; deferred in the bounded expansion |
| Excluded or uncertain identity | 97 | Unresolved structure/name agreement or mixed analyte measurement |

The prioritization CSV covers every one of the 198 inventory groups. Inventory consideration does not mean literature screening was completed for every group. Low-frequency genistein and naringin were deliberately selected because available human probe or transporter evidence was useful despite only one master observation each. A high priority label is a research-selection label, not a high clinical-risk label.

| Anchor | Initial records | Final records | Master observations | Identity scope |
| --- | --- | --- | --- | --- |
| Berberine | 5 | 5 | 1 | Exact structure |
| Piperine | 10 | 13 | 3 | Parent connectivity |
| Curcumin | 6 | 9 | 19 | Exact structure |
| EGCG | 6 | 7 | 4 | Parent connectivity |
| Caffeine | 6 | 14 | 1 | Exact structure |
| Resveratrol | 0 | 10 | 8 | Parent connectivity |
| Genistein | 0 | 3 | 1 | Exact structure |
| Capsaicin | 0 | 1 | 10 | Exact structure |
| Naringin | 0 | 2 | 1 | Parent connectivity |

## 7 Literature search protocol

The initial phase used Europe PMC and primary-source follow-up, PubChem identity data and Crossref provenance checks. It retrieved the first 25 candidates per molecular-group query, with 115 groups exceeding that cap. The original search log also preserves the blank-ID bucket retrieval, which is not an additional molecular group. A further 102 standardized-name queries used mapped PubChem titles and a 6 October 2026 publication cutoff. These are candidate searches, not exhaustive review of all results.

The expansion used Europe PMC core metadata and abstracts with primary PubMed MED identifiers. Primary PubMed and PMC pages supported targeted discovery and checking. Forty-five exact queries are saved: 16 broad searches, nine title-based searches, nine historical title-based searches through 2020, nine exact or specific-source searches and two probe-study searches. Each retrieved at most 100 results. Query caps and ordering limit recall.

| Illustrative actual expansion query | Purpose |
| --- | --- |
| (piperine) AND (pharmacokinetics OR interaction) AND (human OR volunteers OR clinical) | Compound-level discovery |
| TITLE:resveratrol AND (TITLE:pharmacokinetic OR TITLE:interaction OR TITLE:volunteers OR TITLE:bioavailability OR TITLE:metabolism) AND FIRST_PDATE:[1900-01-01 TO 2026-10-06] | Title-focused discovery |
| TITLE:caffeine AND (TITLE:volunteers OR TITLE:human OR TITLE:interaction OR TITLE:drug) AND FIRST_PDATE:[1900-01-01 TO 2020-12-31] | Earlier literature retrieval |
| EXT_ID:20716633 AND SRC:MED | Exact primary study verification |

The search date is 6 October 2026. Exact query text, hit count, number retrieved, database, date and cache path are in the saved search logs. Broad-query preprints, secondary sources and records outside the eligible date are not promoted to included evidence. MED candidates have screening states; non-MED results remain available in raw response caches.

A review could identify a primary reference but was not counted as a primary clinical experiment. This release does not claim a Google Scholar systematic search, an exhaustive systematic Crossref search or PRISMA compliance. Saved response snapshots make the release reproducible even when future rankings and metadata change.

### 7 1 Inclusion and exclusion criteria

Inclusion required a traceable primary report, an identified drug or probe relationship, a reliable CookRisk-compatible exact or parent compound identity, and an actually measured effect or tested null. Human, animal and cell contexts had to be distinguishable. Extracts, salts and mixtures were described as studied rather than assumed to be isolated compounds.

Exclusions included unresolved CookRisk identity, unsupported effect direction, abstract-free outcomes without verified primary text, review-only assertions, modeling predictions misrepresented as measured PK, and whole-food or juice effects attributed to an untested constituent. Potential overlapping reports were deferred where independent experiments could not be established.

### 7 2 Screening and independence

The source screening log distinguishes included sources, specifically excluded or deferred sources, and candidates not fully screened. The last category is not falsely described as a complete exclusion decision. Primary reports share a PMID-based Study_ID. Rows from one report can describe distinct drugs or human, animal and cell experiments, but they are not counted as separate reports.

The original report used the expression original studies. In the consolidated release the more precise count is 45 primary reports grouped by unique PMID. Complete trial-registry confirmation of cross-paper independence was not performed. In particular PMID 2853056 was withheld because overlap with the 1987 quinolone experiment PMID 3480885 could not be ruled out.

## 8 Evidence representation and extraction

The evidence unit is a study, compound, drug and experimental context, with preparation and co-intervention distinctions retained. Most dose arms and endpoints are summarized within one row. The inherited curcumin-alone and curcumin-plus-piperine tamoxifen rows remain separate because their co-interventions differ. Human extract nadolol evidence and transporter-cell evidence remain separate contexts.

The expanded table has 36 columns. These include source identifiers and locators, direction and affected entity, preparation and co-compounds, dose and population, quality limitations and exposure-link scope. Appendix C defines every column. Evidence_Level describes preparation specificity, such as compound, extract or food preparation; it is not a quality grade.

Quantitative extraction preserves endpoint identity, units, reported confidence intervals, approximate qualifiers and direction. Metabolic parent/metabolite ratios are not labeled AUC changes. Assay Ki values are not clinical thresholds. Tumor-growth inhibition is not a drug concentration. Missing or disputed values remain blank or explicitly not extracted rather than becoming zero.

Reverse interactions are retained. For example ciprofloxacin and fluvoxamine can alter caffeine disposition. In those rows the measured effect belongs to the food compound, not necessarily to the prescription drug. Affected_Entity and Perpetrator prevent this directional distinction from being lost in later analysis.

Confidence labels are descriptive extraction-level judgments. Primary human observations generally receive moderate support with population and dose limitations. Preclinical evidence has limited applicability to human inference. Reporting inconsistencies can reduce confidence. This is not formal GRADE assessment, a validated clinical score or independent two-reviewer adjudication.

## 9 Final evidence results

| Measure | Initial release | Expanded release | Change |
| --- | --- | --- | --- |
| Records | 33 | 64 | 31 added |
| Anchor compounds | 5 | 9 | 4 added |
| Drugs and probes | 18 | 34 | 16 added |
| Primary reports | 26 | 45 | 19 added |
| Human PK records | 24 | 49 | 25 added |
| Controlled clinical records | 1 | 2 | 1 added |
| Animal records | 5 | 7 | 2 added |
| In vitro records | 3 | 6 | 3 added |
| Quantitative outcome records | 20 | 42 | 22 added |
| Context dependent conflict pairs | 4 | 5 | 1 added |

The final table contains 51 human records when human PK and controlled clinical evidence are combined. Forty-two records have extracted numerical outcomes; this includes metabolic indices and biochemical assay kinetics as well as PK or PD measurements. Dose-only records do not qualify as quantitative-outcome records. The remaining 22 records are qualitative, null without an extracted effect size, or have disputed/unavailable numerical outcomes.

The 64 rows are not 64 independent trials, 64 established hazards or 64 validated compound-food-drug risks. Several rows come from a single primary report, some involve probe drugs, and preclinical findings retain their evidence-type limits. Nine anchors describe the main row compounds; additional co-ingredients in mixture experiments are not counted as independent anchors.

### 9 1 Representative initial findings

Berberine with cyclosporine increased exposure in a small renal-transplant PK substudy, including a reported AUC increase of 34.5%. The clinical and PK sample sizes differ and remain visible. Berberine with midazolam increased exposure in a human probe study, while dextromethorphan and losartan findings used metabolic ratios. [R6] [R19]

Piperine with fexofenadine increased AUC from 3403.7 to 5724.7 ng.h/mL in a 12-person sequential study. Human curcumin with or without piperine reduced tamoxifen exposure; combination treatment also reduced endoxifen exposure. These observations describe the studied supplement regimens, not standard pepper or turmeric servings. [R35] [R40]

### 9 2 Representative additions

Piperine pretreatment increased carbamazepine AUC by 47.9% and Cmax by 68.7% in healthy volunteers. Separate piperine studies reported greater chlorzoxazone and diclofenac exposure. Small sequential designs and high supplement exposure restrict clinical extrapolation. [R34] [R33] [R30]

A single EGCG co-dose reduced rosuvastatin AUC_last with a geometric mean ratio of 0.81 and 90% CI 0.67-0.97. After ten-day pretreatment no significant AUC or Cmax difference was detected. The single-dose Cmax CI crossed 1; its reduction is not treated as a statistically established effect. [R36]

Resveratrol was supported by human studies with diclofenac, carbamazepine, chlorzoxazone and celecoxib, and a four-probe enzyme study. In the latter, buspirone AUC increased while dextromethorphan and losartan metabolic ratios changed; the caffeine/paraxanthine ratio suggested greater CYP1A2 activity. These endpoints are not interchangeable. [R28] [R27] [R29] [R44] [R16]

Genistein changed caffeine-based enzyme indices and modestly reduced midazolam and talinolol exposure in separate human studies. Aqueous naringin reduced fexofenadine AUC to 75% of the water-control result; the larger grapefruit-juice effect was not attributed to naringin alone. Oral capsaicin did not detectably modify aspirin platelet inhibition at the tested doses, preserving an outcome-specific null. [R17] [R20] [R9] [R26]

### 9 3 Mechanistic coverage

The database covers proposed or experimentally supported enzyme inhibition and induction, transporter uptake and efflux effects, altered absorption or elimination, pharmacodynamic augmentation and antagonism. A measured exposure change may support a mechanism hypothesis without proving it. Human PK, cell transport, microsomal kinetics and animal tissue findings remain separate evidence contexts.

Evidence for CYP3A4, CYP2C9, CYP2D6, CYP1A2 and CYP2E1 probe effects is represented alongside OATP, BCRP, P-glycoprotein, MRP2 and OAT findings. These are source-specific mechanisms. The final release does not turn them into a generic list of every substrate that might be affected.

## 10 Null findings and conflicting evidence

Null findings are retained only where an experiment tested a relationship and failed to detect the specified effect. Absence of a database row means no qualifying evidence was retained under this bounded search and identity policy. It does not mean that no interaction exists.

| Pair | Context that explains differing findings |
| --- | --- |
| Piperine and carbamazepine | Human studies increased exposure; repeated rat treatment decreased systemic and brain exposure. Microsomal inhibition is a separate mechanistic observation. |
| Piperine and midazolam | Isolated piperine affected sedation/clearance; a short curcuminoid-piperine mixture study found no meaningful parent-drug PK change. |
| Curcumin and tamoxifen | Rat oral exposure increased; human exposure decreased under different supplement regimens. |
| EGCG and bortezomib | Cell antagonism and concentration-dependent xenograft findings; no human interaction established. |
| EGCG and rosuvastatin | Single co-dose AUC reduction contrasted with a repeated-pretreatment null in the same report. |

These five groups are context-dependent divergences, not five directly replicated contradictions in the same population and regimen. Species, dose, preparation, duration, endpoint and metabolite differences are preserved. The database does not select a majority direction or combine incompatible effect coefficients.

## 11 Cooking and processing evidence

Three processing records from two primary publications remain in a separate table. They help connect cooking questions to compound availability, but they are not included in the 64 interaction-record count or the 45 interaction-report count.

| Compound and process | Reported processing observation | Boundary |
| --- | --- | --- |
| Piperine in heated black pepper | 16-34% loss under tested boiling or pressure-cooking conditions | No universal pepper retention coefficient |
| Curcumin in heated turmeric | 27-53% loss; 12-30% with tamarind under tested conditions | Matrix-specific processing observation |
| Green tea brewing and catechins | Extraction and epimerization depend on conditions; total catechins peaked at 95 C for 10 min | Total-catechin optimum is not isolated EGCG retention |

The spice study tested boiling for 10 or 20 minutes and pressure cooking for 10 minutes. The tea study examined infusions at 60 C or 95 C across 5-300 minutes. These observations do not establish how much any cooking method changes a drug-interaction effect. A cooking loss, a supplement PK effect and a clinically meaningful outcome require separate links. [R46] [R47]

## 12 Stage A traceability and model separation

The supplied benchmark report retained Extra Trees as the selected reference among evaluated configurations. It used 1,124 observations from 197 molecular groups, five-fold molecular GroupKFold and the locked retention target. Stage B verified that every selected OOF record matched the master Record_ID, molecular group and actual retention target.

The original compound-linkage table preserves group and food counts, model identity and whether an OOF observation is available. The observation-linkage table preserves original row pointers, food and cooking conditions, baseline concentration, actual and predicted retention, fold and provenance flags. It does not invent a compound-average retention or retained amount.

| Linkage fact | Verified scope |
| --- | --- |
| Original evidence linked to selected-model groups | 33 of 33 initial evidence records |
| Saved OOF observations | 1,124 selected-model records |
| OOF molecular groups | 197 |
| Master-only molecular group | PhIP group with five rows; no selected OOF |
| Expanded evidence link status | Nine anchors retain CookRisk molecular IDs; original linkage files are not regenerated as 64-record evidence-exposure joins |

The current master marks only 1,009 rows eligible, while 115 selected OOF rows have FALSE in its current Final_Preprocessing_Eligible flag. Molecular IDs and target values still match. Without the frozen Stage A input and runner, eligibility lineage cannot be reconciled. No retrospective retraining or repair was performed.

OOF predictions are validation outputs for existing observations, not deployable predictions for a new cooking condition. No fitted deployment model was saved in the inspected materials. A later retention-model change can alter the linkage or exposure estimate while leaving the Stage B literature evidence unchanged.

## 13 Source provenance and quality control

### 13 1 Inherited retention data provenance

| Inherited dataset DOI audit | Result |
| --- | --- |
| Distinct DOIs audited | 208 |
| Author or year metadata discrepancies | 145 |
| Lookup unavailable | 10 |
| Metadata concordant by subtraction | 53 |
| Confirmed example | Five Persin and avocado rows cite an unrelated DOI |

DOI 10.1016/j.lwt.2021.111500 belongs to a 2021 Liu et al. fish-oil/gelatin encapsulation publication, while five supplied Persin/avocado cooking observations attribute it to a 2022 Molina et al. study. This is a confirmed source mismatch and blocks validation of those retention claims. The publisher source is https://www.sciencedirect.com/science/article/abs/pii/S0023643821006538.

Metadata disagreement is a source-verification flag, not automatic proof that every associated measurement is fabricated. Conversely, matching title metadata does not validate a compound concentration, cooking condition or retention value. Independently checked Stage B interaction reports are a separate provenance layer and are not invalidated merely because an inherited food citation is wrong.

### 13 2 Primary interaction source verification

| Final primary report DOI audit | Reports |
| --- | --- |
| Crossref title concordant | 33 |
| Manual concordance with omitted subtitle | 1 |
| Crossref lookup unavailable but MED PMID verified | 9 |
| No DOI supplied but primary PMID verified | 2 |
| Unreviewed accepted title mismatches | 0 |

For PMID 17963429, Crossref omits the design subtitle but the principal title, authors Kasibhatta and Naidu, and year 2007 agree. Eleven primary reports therefore lack complete independent DOI confirmation: nine unavailable lookups and two without supplied DOIs. Their primary PubMed identifiers remain available. This limitation is disclosed rather than converted into an all-DOIs-verified claim.

### 13 3 Reporting inconsistencies and withheld claims

| Primary report | QC decision |
| --- | --- |
| PMID 28533679 | Cmax CI includes 1; retain AUC finding and regimen contrast without claiming significant Cmax reduction |
| PMID 22300367 | Abstract and results prose disagree on dose-specific human AUC folds; disputed magnitudes withheld |
| PMID 26633237 | Malformed absolute AUC unit; dimensionless reported ratios retained |
| PMID 21943317 | Suspicious clearance units; those clearance values omitted |
| PMID 25624269 | Reversed metabolite-formation wording; measured ratios and parent PK retained |
| PMID 21870106 | Abstract Tmax/half-life labels conflict with table; disputed fields not silently corrected |
| PMID 24398010 | Design, sample-size and clearance wording inconsistencies remain explicit |

Claims that small supplement PK studies demonstrate therapeutic benefit, reduced adverse events or safe dose reduction were not promoted to verified clinical conclusions. Animal and cell observations were not labeled human clinical risk. Modeled AUC increases in a microsomal source were not recorded as observed human PK.

### 13 4 Duplicate handling and exclusions

No duplicate key was found for study, compound, drug, evidence context, preparation and co-intervention. Initial evidence identifiers SB-0001 through SB-0033 remain stable; additions are SB-0034 through SB-0064. Same-report contexts share Study_ID. Exact checks prevent row duplication but do not alone establish independent trial populations.

| Source or issue | Reason excluded or deferred |
| --- | --- |
| PMIDs 19221726 and 21680781 | Quercetin primary evidence cannot be assigned to the contaminated CookRisk group |
| PMID 3444866 | No abstract; effect not verified from accessible primary text |
| PMID 2853056 | Potential overlap with an earlier quinolone experiment |
| PMID 23765408 | Tacrolimus letter metadata found; outcome not verified |
| PMID 40524804 | Abstract did not resolve drug-specific direction |
| PMID 40761345 | Animal source deferred in human-first batch |
| Other retrieved candidates | Not fully screened; no unsupported interaction assigned |

### 13 5 Automated validation

All 20 initial integrity checks passed. The separate initial release verification reported disk-table integrity, source matching, original counts, food-claim separation, unique contexts, immutable input copies and byte-identical offline rebuild as PASS. All 13 expanded-release checks passed. They assess structure and traceability, not exhaustive literature coverage or clinical validity.

| Expansion validation check | Saved result |
| --- | --- |
| 64-row count matches summary | PASS |
| Evidence IDs are unique | PASS |
| Initial identifiers and relationships retained | PASS |
| No excluded identity receives evidence | PASS |
| All 198 groups prioritized | PASS |
| Evidence types sum to 64 | PASS |
| 45 distinct primary PMIDs | PASS |
| Required descriptive fields present | PASS |
| Cached PMID title and DOI match each row | PASS |
| Included publication years not later than 2026 | PASS |
| Conflict references resolve | PASS |
| Logged expansion query caches present | PASS |
| No unresolved accepted Crossref title mismatch | PASS |

The source-date check validates included publication years; it is not a complete day-level publication-date audit. Cache matching confirms bibliographic association, not every extracted numerical interpretation. The manual review complements these checks, but it was conducted by one reviewer and does not establish error-free or exhaustive evidence.

## 14 Output catalogue and how to use it

Use the expanded evidence CSV for current interaction lookup and the report for interpretation. The initial tables remain useful for inventory, food associations, processing evidence and preserved Stage A context. They must not be treated as if every old count or join were updated by the expansion.

| Current expanded output | Purpose |
| --- | --- |
| stageB_food_drug_interactions_expanded.csv | 64-row current evidence table with 36 fields |
| compound_prioritization.csv | 198-group research priority and eligibility inventory |
| qc_identity.csv | Original identity, standardized identity, verification status and problem overlay |
| evidence_summary.json | Final machine-readable counts |
| study_registry.csv | 45 primary reports and per-report record counts |
| drug_identity_registry.csv | 34 drug names with supporting primary identifiers |
| source_screening_log.csv | Included sources and explicit deferred screening states |
| literature_search_log.csv | 45 exact expansion queries with dates and cache locations |
| primary_source_DOI_audit.csv | Independent bibliographic confirmation and unresolved lookups |
| conflict_synthesis.csv | Five context-dependent divergence groups |
| validation_results.json | 13 saved expansion checks |
| inherited audit tables | Copies of upstream DOI audit, blank-ID observations and duplicate-CID cluster |

These files are under stageB/expansion_v2/outputs. The matching reports folder contains evidence_summary.md, qc_report.md, literature_search_methodology.md and data_dictionary.md. The expansion scripts preserve search collection, manual extraction, table building and validation. Source caches and manifest_sha256.json support traceability.

| Initial output family | Retained purpose |
| --- | --- |
| Compound mapping and identity audit | 198-group structures, identifiers, synonym checks and missingness |
| Foods and food compound relations | Inherited food labels and Record_ID associations |
| Initial interaction and literature tables | Historical 33-record evidence release |
| Interaction compound relation | Mixture anchor and verified co-intervention relations |
| Processing evidence | Three separate processing records from two sources |
| Stage A compound and observation links | Preserved selected-model OOF lineage |
| Search and source audit logs | Initial query snapshots and dataset DOI flags |
| Reports and manifests | Methodology, references, reproducibility and hash verification |

The original archive is CookRisk_StageB_Evidence_Release.zip. The current expanded archive is CookRisk_StageB_Expanded_v2.zip. They are separate release packages. The final report is supplied as an editable Word document and a PDF, with a readable source copy and report-specific output audit. Full file paths are documented in Appendix D.

### 14 1 Suggested lookup workflow

Start with a CookRisk molecular group and its identity status. If identity is uncertain or mixed, stop compound-specific assignment. For an eligible group, filter the expanded evidence table by Compound_ID and drug, then read Evidence_Type, Preparation, Co_Compounds, Dose, Population and Direction together. Check Source_Locator, limitations and any conflict group before considering exposure integration. A high-priority label or a populated evidence row is not a clinical recommendation.

## 15 Reproducibility and audit trail

The initial release can be rebuilt offline from cached identity and publication data using its saved mapping and build scripts. The existing repository environment supplies RDKit 2026.3.5 for molecular comparison. The expansion build uses saved JSON responses, the original mapping table, original interaction table and explicit manual extraction in expansion_v2/scripts/curation.py. No retention model is trained during either evidence-table build.

The authoritative record of online searches is the logged query text and cached response, not the current live ranking. Source collection scripts were adapted during retrieval; the complete historical query set is retained in CSV and JSON logs. Re-running a live search can produce different results. Exact release reproduction should use preserved snapshots and hashes.

| Audit artefact | What it establishes |
| --- | --- |
| audit/input_manifest.json | Original inputs and preserved-copy SHA-256 hashes |
| audit/output_manifest.json | Initial release output hashes |
| audit/release_verification.json | Initial disk and rebuild checks |
| expansion_v2/manifest_sha256.json | Expansion file hashes |
| Evidence Source_Cache and Source_Locator | Publication snapshot and extraction location |
| Study_ID and PMID | Primary report grouping |
| Release_Origin | Initial or added evidence provenance |

Reproducibility establishes that the recorded process recreates the saved release. It does not establish that inherited source measurements are accurate, that all relevant studies were found or that a clinical inference is justified. Scientific correction should be a new documented version rather than an unrecorded change to the original inputs.

## 16 Limitations and readiness for later stages

The completed evidence database has a deliberately bounded scope. Searches were capped and many candidates remain unscreened. Extraction often relies on abstracts. Full study protocols and numerical tables were not verified for every included report. Drug external identifiers and salt/form normalization remain incomplete. Descriptive confidence is not a formal risk-of-bias framework, and no independent second reviewer performed adjudication.

The retention data also contain 96 uncertain molecular groups, an additional mixed-analyte exclusion, 221 unassigned observations, parent-connectivity mappings and unresolved provenance problems. The 115 eligibility-flag discrepancies require the original frozen Stage A lineage. These issues limit exposure interpretation even when the interaction paper itself is correctly identified.

Supplement doses, aqueous isolated-compound solutions, concentrated extracts, cell concentrations and animal mg/kg regimens cannot be equated to a cooked serving. Active metabolites, timing, repeated dosing, absorption, physiological state and prescribed drug regimen can change the relationship. None of those missing links is filled with an arbitrary multiplier or numerical hazard score.

| Stage C requirement | Current state and next action |
| --- | --- |
| Verified measurement source | Inherited DOI issues remain; validate food compound and processing values in primary sources |
| Exact analyte and form | Resolve mixed groups and stereochemistry; retain salts and mixtures as studied |
| Compatible retention output | Recover locked model lineage and fitted model if new predictions are needed |
| Amount and basis | Validate units, wet/dry basis, concentration definition and serving size |
| Exposure context | Establish timing, dosing frequency, bioavailability and active metabolites |
| Clinical applicability | Match drug regimen and population; do not transfer animal/cell effects automatically |

Stage D requires a separately justified risk framework and validation. It would need effect-size relevance, exposure plausibility, uncertainty, clinical endpoints and appropriate expert assessment. Stage B supplies traceable evidence inputs; it does not make dietary restriction, drug-dose adjustment or safety decisions.

## 17 Final project status

Stage B is complete as a bounded, auditable evidence release. The work established the molecular inventory, identity qualification, primary-source extraction, human versus preclinical separation, quantitative and null outcome handling, conflict synthesis, processing context, inherited-data audits and reproducible outputs. The controlled expansion nearly doubled the record count, from 33 to 64, while adding four anchors and retaining source-specific limitations.

The defensible conclusion is that CookRisk now has a structured evidence layer ready for literature retrieval and carefully controlled subsequent integration. It is not yet an exhaustive literature database or a clinically validated cooked-food interaction predictor. The remaining constraints are part of the scientific result and are explicitly preserved for further work.

## Appendix A Complete evidence profiles

All 64 included evidence records are listed below. These profiles summarize the saved final table. Preparation, evidence type and endpoint must be read together. A blank quantitative outcome is described as not extracted; it is not converted to zero. Full dose, population, confidence, notes, identity scope and source-cache fields remain in the CSV.

### SB-0001 Berberine and Cyclosporine

Human pharmacokinetic | PMID:16133554 [R6] | increased drug exposure.

Cyclosporine exposure increased. Mechanism: CYP3A4 inhibition proposed by authors.

Dose and preparation: Berberine 0.2 g; cyclosporine 3 mg/kg in PK substudy; Berberine three times daily; cyclosporine twice daily; 12 days PK; 3 months clinical trial. Berberine as named by study; precise preparation not extracted. Population: Renal-transplant recipients; 104 clinical; 6 PK.

Quantitative outcome: PK: AUC +34.5%; CL/F -40.4%; trial final trough concentration 29.3% higher than comparator. Limitations: Small PK substudy; no cooked-food exposure equivalence; mechanism proposed.

### SB-0002 Berberine and Cyclosporine

Human pharmacokinetic | PMID:18928093 [R13] | increased drug concentration.

Steady-state C0 and C2 increased with berberine hydrochloride. Mechanism: Mechanism not established in abstract.

Dose and preparation: Dose not extracted. Berberine hydrochloride; parent moiety link only. Population: Heart-transplant recipients; 22.

Quantitative outcome: No reliable numerical effect extracted Limitations: Salt intervention; counterion not represented by CookRisk parent ID. No quantitative magnitude or dosing extracted.

### SB-0003 Berberine and Midazolam

Human pharmacokinetic | PMID:21870106 [R19] | increased drug exposure.

Midazolam exposure increased. Mechanism: CYP3A activity decreased.

Dose and preparation: Berberine 300 mg; Three times daily; 2 weeks. Berberine as named by study; precise preparation not extracted. Population: Healthy male volunteers.

Quantitative outcome: AUC0-infinity +40%; Cmax +38%; oral clearance -27%. Limitations: Probe-drug effect, not a clinical outcome. Abstract appears to reverse Tmax and half-life labels; these fields left blank.

### SB-0004 Berberine and Dextromethorphan

Human pharmacokinetic | PMID:21870106 [R19] | reduced drug metabolism.

Urinary parent/metabolite ratio increased, indicating lower CYP2D6 activity. Mechanism: CYP2D6 inhibition.

Dose and preparation: Berberine 300 mg; Three times daily; 2 weeks. Berberine as named by study; precise preparation not extracted. Population: Healthy male volunteers.

Quantitative outcome: 0-8 h urinary dextromethorphan/dextrorphan ratio increased ninefold. Limitations: Metabolic ratio is not a drug AUC increase or a clinical outcome.

### SB-0005 Berberine and Losartan

Human pharmacokinetic | PMID:21870106 [R19] | reduced metabolite formation.

Parent/active-metabolite ratio increased, indicating lower CYP2C9 activity. Mechanism: CYP2C9 inhibition.

Dose and preparation: Berberine 300 mg; Three times daily; 2 weeks. Berberine as named by study; precise preparation not extracted. Population: Healthy male volunteers.

Quantitative outcome: Losartan/E-3174 ratio doubled. Limitations: Metabolic ratio alone does not establish therapeutic failure.

### SB-0006 Piperine and Propranolol

Human pharmacokinetic | PMID:1815977 [R12] | increased drug exposure.

Higher AUC and Cmax; earlier Tmax. Mechanism: Bioavailability enhancement; precise mechanism not established.

Dose and preparation: Piperine 20 mg; propranolol 40 mg; Piperine daily; 7 days. Piperine as named by study; precise preparation not extracted. Population: Healthy volunteers; 6 in propranolol group.

Quantitative outcome: No reliable numerical effect extracted Limitations: Abstract supplies direction without numerical PK magnitudes. CookRisk name/CID/connectivity match; input SMILES stereochemistry incomplete. Link is to named parent identity, not a verified stereochemical exposure.

### SB-0007 Piperine and Theophylline

Human pharmacokinetic | PMID:1815977 [R12] | increased drug exposure.

Higher AUC and Cmax; longer elimination half-life. Mechanism: Bioavailability enhancement; precise mechanism not established.

Dose and preparation: Piperine 20 mg; theophylline 150 mg; Piperine daily; 7 days. Piperine as named by study; precise preparation not extracted. Population: Healthy volunteers; 6 in theophylline group.

Quantitative outcome: No reliable numerical effect extracted Limitations: Abstract supplies direction without numerical PK magnitudes. CookRisk name/CID/connectivity match; input SMILES stereochemistry incomplete. Link is to named parent identity, not a verified stereochemical exposure.

### SB-0008 Piperine and Phenytoin

Human pharmacokinetic | PMID:16767797 [R8] | increased drug exposure.

AUC and Cmax increased; Tmax and elimination-rate changes were not significant. Mechanism: Increased absorption proposed.

Dose and preparation: Piperine 20 mg once; phenytoin 150 or 200 mg twice daily. Piperine as named by study; precise preparation not extracted. Population: Patients with uncontrolled epilepsy; 20; 10 per phenytoin dose group.

Quantitative outcome: No reliable numerical effect extracted Limitations: Single piperine dose; numerical magnitude not available in abstract. CookRisk name/CID/connectivity match; input SMILES stereochemistry incomplete. Link is to named parent identity, not a verified stereochemical exposure.

### SB-0009 Piperine and Phenytoin

Human pharmacokinetic | PMID:11808866 [R4] | increased drug exposure.

Black-pepper-containing soup increased phenytoin AUC and delayed elimination. Mechanism: Absorption and elimination effects suggested.

Dose and preparation: Phenytoin 300 mg; black-pepper dose not extracted; Soup ingested 30 min before phenytoin. Piperine-containing black pepper in soup; not isolated piperine. Population: Healthy volunteers; 6.

Quantitative outcome: No reliable numerical effect extracted Limitations: Preparation-specific finding; cannot generalize to all pepper foods or exact piperine exposure. CookRisk name/CID/connectivity match; input SMILES stereochemistry incomplete. Link is to named parent identity, not a verified stereochemical exposure.

### SB-0010 Piperine and Carbamazepine

Human pharmacokinetic | PMID:19283724 [R15] | increased drug exposure.

AUC increased in both dose groups; Cmax and Tmax increased significantly only in 500 mg group. Mechanism: Reduced elimination and/or increased absorption proposed.

Dose and preparation: Piperine 20 mg once; carbamazepine 300 or 500 mg twice daily. Piperine as named by study; precise preparation not extracted. Population: Patients with poorly controlled epilepsy; 20; 10 per carbamazepine dose group.

Quantitative outcome: No reliable numerical effect extracted Limitations: Single dose and dose-dependent endpoints; exact PK magnitudes absent from abstract. CookRisk name/CID/connectivity match; input SMILES stereochemistry incomplete. Link is to named parent identity, not a verified stereochemical exposure.

### SB-0011 Piperine and Nevirapine

Human pharmacokinetic | PMID:17963429 [R11] | increased drug exposure.

Nevirapine exposure increased. Mechanism: Enhanced bioavailability; causal enzyme mechanism not established.

Dose and preparation: Piperine 20 mg; nevirapine 200 mg on day 7; Piperine each morning; 7 days. Piperine as named by study; precise preparation not extracted. Population: Healthy adult males; 8.

Quantitative outcome: AUCt +167%, AUCinfinity +170%, Cmax +120%, Clast +146% (all approximate). Limitations: Small healthy-volunteer pilot; not HIV treatment outcomes. CookRisk name/CID/connectivity match; input SMILES stereochemistry incomplete. Link is to named parent identity, not a verified stereochemical exposure.

### SB-0012 Piperine and Midazolam

Human pharmacokinetic | PMID:24398010 [R25] | increased sedative duration.

Longer sedation and half-life; reduced clearance. Mechanism: CYP3A4 inhibition proposed.

Dose and preparation: Piperine 15 mg; midazolam 10 mg; Piperine daily; 3 days pretreatment. Piperine as named by study; precise preparation not extracted. Population: Healthy volunteers; 20 per abstract; methods/group descriptions inconsistent.

Quantitative outcome: Sedation 102 +/- 43 to 188 +/- 59 min; half-life and clearance as in Table 2. Limitations: Sparse PK sampling; internally inconsistent sample-size/design statements and abstract says clearance higher despite lower numerical value. CookRisk name/CID/connectivity match; input SMILES stereochemistry incomplete. Link is to named parent identity, not a verified stereochemical exposure.

### SB-0013 Piperine and Fexofenadine

Human pharmacokinetic | PMID:27981349 [R35] | increased drug exposure.

Fexofenadine exposure increased and oral clearance decreased. Mechanism: P-gp efflux inhibition proposed.

Dose and preparation: Piperine 20 mg; fexofenadine 120 mg; Piperine daily; 10 days. Piperine as named by study; precise preparation not extracted. Population: Healthy volunteers; 12.

Quantitative outcome: AUC 3403.7 to 5724.7 ng.h/mL; Cmax 406.9 to 767 ng/mL; CL/F 35.4 to 20.7 L/h. Limitations: Small sequential study; mechanism attributed, not directly demonstrated in humans. CookRisk name/CID/connectivity match; input SMILES stereochemistry incomplete. Link is to named parent identity, not a verified stereochemical exposure.

### SB-0014 Piperine and Carbamazepine

In vitro | PMID:30611786 [R39] | reduced drug metabolism.

Time-dependent inhibition of carbamazepine metabolism. Mechanism: Metabolic enzyme inhibition.

Dose and preparation: Human KI 9.45 uM; rat KI 18.34 uM. Piperine as named by study; precise preparation not extracted. Population: Human and rat liver microsomes.

Quantitative outcome: Human kinact 0.0093 min^-1; rat kinact 0.0153 min^-1; KI values are assay parameters. Limitations: Static-model AUC predictions (7% rat, 11% human) are not observed PK; omitted from AUC_change. CookRisk name/CID/connectivity match; input SMILES stereochemistry incomplete. Link is to named parent identity, not a verified stereochemical exposure.

### SB-0015 Piperine and Carbamazepine

Animal | PMID:31321577 [R41] | decreased drug exposure.

Repeated combination decreased systemic and brain exposure; single-dose combination did not change PK significantly. Mechanism: Multiple disposition processes; inhibited rat Cyp3a2 alongside lower exposure.

Dose and preparation: Piperine 3.5 or 35 mg/kg once daily; carbamazepine 40 mg/kg three times daily; Single dose and 2 weeks. Piperine as named by study; precise preparation not extracted. Population: Rats; separate seizure models in zebrafish and mice.

Quantitative outcome: No reliable numerical effect extracted Limitations: Species and regimen differ from human study. Model-derived percentage process changes not presented as observed AUC. CookRisk name/CID/connectivity match; input SMILES stereochemistry incomplete. Link is to named parent identity, not a verified stereochemical exposure.

### SB-0016 Curcumin and Tamoxifen

Human pharmacokinetic | PMID:30909366 [R40] | decreased drug exposure.

Tamoxifen AUC decreased; endoxifen reduction did not meet statistical significance in curcumin-only comparison. Mechanism: Mechanism unresolved; CYP and transporter pathways discussed.

Dose and preparation: Curcumin 1200 mg three times daily; tamoxifen 20-30 mg/day; 28 days per treatment period. Curcumin as named by study; precise preparation not extracted. Population: Breast-cancer patients; 16.

Quantitative outcome: Endoxifen AUC0-24h -7.7% (95% CI -15.4 to +0.7; p=0.07). Limitations: PK outcomes, not cancer recurrence; endoxifen-only contrast nonsignificant.

### SB-0017 Curcumin and Tamoxifen

Human pharmacokinetic | PMID:30909366 [R40] | decreased drug exposure.

Curcumin plus piperine reduced tamoxifen and endoxifen exposure. Mechanism: Mechanism unresolved; ingredients not independently attributable.

Dose and preparation: Curcumin 1200 mg plus piperine 10 mg, each three times daily; tamoxifen 20-30 mg/day; 28 days per treatment period. Curcumin as named by study; precise preparation not extracted. Co-intervention: Piperine. Population: Breast-cancer patients; 16.

Quantitative outcome: Endoxifen AUC0-24h -12.4% (95% CI -21.9 to -1.9; p=0.02). Limitations: Combination effect; not piperine alone. PK change does not establish a measured cancer outcome.

### SB-0018 Curcumin and Midazolam

Human pharmacokinetic | PMID:22725836 [R23] | no meaningful PK change observed.

No meaningful change in parent-drug PK under the tested preparation and regimen. Mechanism: No in-vivo inhibition demonstrated under tested conditions.

Dose and preparation: 4 g curcuminoids plus 24 mg piperine per administration; Four administrations over 2 days; 2 days. Standardized curcuminoid/piperine mixture. Co-intervention: Piperine | Demethoxycurcumin | Bisdemethoxycurcumin. Population: Healthy volunteers; 8.

Quantitative outcome: No reliable numerical effect extracted Limitations: Mixture-specific negative result; not isolated curcumin or isolated piperine and not proof of absence at other regimens.

### SB-0019 Curcumin and Flurbiprofen

Human pharmacokinetic | PMID:22725836 [R23] | no meaningful PK change observed.

No meaningful change in parent-drug PK under the tested preparation and regimen. Mechanism: No in-vivo inhibition demonstrated under tested conditions.

Dose and preparation: 4 g curcuminoids plus 24 mg piperine per administration; Four administrations over 2 days; 2 days. Standardized curcuminoid/piperine mixture. Co-intervention: Piperine | Demethoxycurcumin | Bisdemethoxycurcumin. Population: Healthy volunteers; 8.

Quantitative outcome: No reliable numerical effect extracted Limitations: Mixture-specific negative result; not isolated curcumin or isolated piperine and not proof of absence at other regimens.

### SB-0020 Curcumin and Acetaminophen

Human pharmacokinetic | PMID:22725836 [R23] | no meaningful PK change observed.

No meaningful change in parent-drug PK under the tested preparation and regimen. Mechanism: No in-vivo inhibition demonstrated under tested conditions.

Dose and preparation: 4 g curcuminoids plus 24 mg piperine per administration; Four administrations over 2 days; 2 days. Standardized curcuminoid/piperine mixture. Co-intervention: Piperine | Demethoxycurcumin | Bisdemethoxycurcumin. Population: Healthy volunteers; 8.

Quantitative outcome: No reliable numerical effect extracted Limitations: Mixture-specific negative result; not isolated curcumin or isolated piperine and not proof of absence at other regimens.

### SB-0021 Curcumin and Tamoxifen

Animal | PMID:22512082 [R22] | increased drug exposure.

Oral tamoxifen exposure increased. Mechanism: CYP3A4 and P-gp inhibition proposed.

Dose and preparation: Curcumin 0.5, 2.5, 10 mg/kg; oral tamoxifen 9 mg/kg; IV tamoxifen 2 mg/kg. Curcumin as named by study; precise preparation not extracted. Population: Rats.

Quantitative outcome: Absolute bioavailability 27.2-33.5% versus 20.4% oral control. Limitations: Rat findings cannot override human results; metabolite studied is 4-hydroxytamoxifen, not endoxifen.

### SB-0022 EGCG and Nadolol

Human pharmacokinetic | PMID:29480324 [R38] | decreased drug exposure.

EGCG-concentrated green tea extract reduced nadolol exposure; blood pressure/pulse changes not significant. Mechanism: Uptake inhibition supported by separate cell experiment.

Dose and preparation: Nadolol 30 mg; low/high GTE doses not quantified in abstract. EGCG-concentrated extract; not pure EGCG human intervention. Population: Healthy volunteers; 13.

Quantitative outcome: AUC_change: AUC0-infinity GMR 0.72 (90% CI 0.56-0.87) low; 0.60 (0.51-0.69) high Limitations: Mixed extract in humans; transporter mechanism independently tested in vitro. No demonstrated human PD change. CookRisk name/CID/connectivity match; input SMILES stereochemistry incomplete. Link is to named parent identity, not a verified stereochemical exposure.

### SB-0023 EGCG and Nadolol

In vitro | PMID:29480324 [R38] | reduced transporter uptake.

EGCG inhibited OATP1A2-mediated nadolol uptake. Mechanism: Competitive uptake-transporter inhibition.

Dose and preparation: Ki 19.4 uM for nadolol transport. EGCG as named by study; precise preparation not extracted. Population: OATP1A2-expressing HEK293 cells.

Quantitative outcome: Ki 19.4 uM (nadolol); 21.6 uM (sulphobromophthalein probe). Limitations: Ki is not a human exposure threshold; human extract result stored separately. CookRisk name/CID/connectivity match; input SMILES stereochemistry incomplete. Link is to named parent identity, not a verified stereochemical exposure.

### SB-0024 EGCG and Nadolol

Animal | PMID:23920278 [R24] | decreased drug exposure.

Isolated EGCG reduced nadolol Cmax and AUC. Mechanism: Intestinal uptake inhibition proposed.

Dose and preparation: EGCG 150 mg/kg; nadolol 10 mg/kg; Pretreatment 30 min before nadolol. EGCG as named by study; precise preparation not extracted. Population: Male Sprague-Dawley rats.

Quantitative outcome: No reliable numerical effect extracted Limitations: 85% Cmax and 74% AUC reductions reported for GTE arm, not isolated EGCG; deliberately not assigned to this record. CookRisk name/CID/connectivity match; input SMILES stereochemistry incomplete. Link is to named parent identity, not a verified stereochemical exposure.

### SB-0025 EGCG and Nadolol

Animal | PMID:34303263 [R42] | decreased drug exposure.

Nadolol exposure and blood-pressure lowering decreased. Mechanism: Intestinal transporter transcription changes.

Dose and preparation: EGCG 10 mg/kg; nadolol 10 mg/kg on day 14; EGCG daily; 14 days. EGCG as named by study; precise preparation not extracted. Population: Male spontaneously hypertensive rats.

Quantitative outcome: Nadolol AUC -51%; Cmax -53%; SBP higher than nadolol-only controls. Limitations: Hypertensive rat model; not human dosing or clinical significance. CookRisk name/CID/connectivity match; input SMILES stereochemistry incomplete. Link is to named parent identity, not a verified stereochemical exposure.

### SB-0026 EGCG and Bortezomib

In vitro | PMID:19190249 [R14] | decreased drug effect.

EGCG antagonized bortezomib-induced tumor-cell death. Mechanism: Direct chemical reaction with boronic acid group.

Dose and preparation: Dose not extracted. EGCG as named by study; precise preparation not extracted. Population: Multiple-myeloma and glioblastoma cell lines.

Quantitative outcome: No reliable numerical effect extracted Limitations: In-vitro result; animal work also reported in source. No clinical interaction demonstrated. CookRisk name/CID/connectivity match; input SMILES stereochemistry incomplete. Link is to named parent identity, not a verified stereochemical exposure.

### SB-0027 EGCG and Bortezomib

Animal | PMID:21400028 [R18] | concentration-dependent.

Antagonism at >200 uM EGCG; no antagonism at 11-16 uM. Mechanism: Concentration-dependent antagonism.

Dose and preparation: EGCG >200 uM versus 11-16 uM. EGCG as named by study; precise preparation not extracted. Population: Immunocompromised mice; human prostate tumor xenografts.

Quantitative outcome: TGI -17.7% at >200 uM; TGI 63.5% at 11-16 uM; bortezomib-alone TGI 53.9-58.9%. Limitations: Preclinical TGI, not human efficacy; human EGCG supplement concentration 0.6-3 uM cited by source. CookRisk name/CID/connectivity match; input SMILES stereochemistry incomplete. Link is to named parent identity, not a verified stereochemical exposure.

### SB-0028 Caffeine and Clozapine

Human pharmacokinetic | PMID:10606838 [R3] | increased drug exposure.

Clozapine AUC increased and oral clearance decreased. Mechanism: Metabolism inhibition suggested.

Dose and preparation: Caffeine mean 550 mg/day (400-1000); clozapine 12.5 mg once. Caffeine as named by study; precise preparation not extracted. Population: Nonsmoking healthy male volunteers; 12.

Quantitative outcome: Clozapine AUC +19%; clearance -14%. Limitations: Healthy volunteers and low single clozapine dose; does not establish uniform patient effects.

### SB-0029 Caffeine and Clozapine

Human pharmacokinetic | PMID:14725610 [R5] | increased drug concentration.

Coffee-associated trough concentration increase depended on compliance analysis. Mechanism: CYP1A2 inhibition proposed.

Dose and preparation: 7 days per coffee phase after 1-week run-in. Caffeine as named by study; precise preparation not extracted. Population: Hospitalized clozapine-treated patients; 12 enrolled; 6 fully compliant; combined analysis includes 4 partially compliant.

Quantitative outcome: Fully compliant: clozapine trough +26% (95% CI -3 to +54; p=0.07); combined data +20% (3 to 37; p=0.03). Limitations: Ad-libitum coffee and compliance-sensitive result; fully compliant contrast nonsignificant.

### SB-0030 Caffeine and Acetaminophen

Controlled clinical | PMID:17442681 [R10] | increased analgesic effect.

Caffeine accelerated absorption and enhanced/prolonged acetaminophen analgesia. Mechanism: Absorption acceleration and analgesic augmentation.

Dose and preparation: Caffeine 130 mg; acetaminophen 1000 mg; Pain effects assessed up to 3 h. Caffeine as named by study; precise preparation not extracted. Population: Healthy experimental-pain subjects; 24.

Quantitative outcome: No reliable numerical effect extracted Limitations: Experimental pain model; exact PK magnitude not extracted.

### SB-0031 Caffeine and Fluvoxamine

Human pharmacokinetic | PMID:8807660 [R45] | increased compound exposure.

Fluvoxamine reduced caffeine clearance and prolonged caffeine half-life. Mechanism: CYP1A2 inhibition by drug.

Dose and preparation: Caffeine 200 mg; fluvoxamine 50 mg/day for 4 days then 100 mg/day for 8 days. Caffeine as named by study; precise preparation not extracted. Population: Healthy volunteers; 8.

Quantitative outcome: Caffeine clearance 107 to 21 mL/min; half-life 5 to 31 h. Limitations: Reverse direction: drug alters food compound. Not an increase in fluvoxamine exposure.

### SB-0032 Caffeine and Fluvoxamine

Human pharmacokinetic | PMID:16236038 [R7] | increased compound exposure.

Fluvoxamine impaired caffeine clearance without detected single-dose PD changes. Mechanism: CYP1A2 inhibition by drug.

Dose and preparation: Caffeine 250 mg; fluvoxamine four 100 mg doses over 2 days. Caffeine as named by study; precise preparation not extracted. Population: Healthy subjects; 7.

Quantitative outcome: Caffeine clearance 105 to 9.1 mL/min; half-life 4.9 to 56 h; measured PD unchanged. Limitations: Single caffeine dose; repeated dietary caffeine accumulation not tested.

### SB-0033 Caffeine and Ciprofloxacin

Human pharmacokinetic | PMID:2729942 [R31] | increased compound exposure.

Ciprofloxacin increased caffeine exposure and delayed caffeine conversion to paraxanthine. Mechanism: Reduced compound clearance; delayed demethylation.

Dose and preparation: Caffeine 100 mg; ciprofloxacin 750 mg every 12 h. Caffeine as named by study; precise preparation not extracted. Population: Healthy fasting males; 10.

Quantitative outcome: Caffeine AUC and clearance as specified; a small ciprofloxacin AUC increase also reported without magnitude. Limitations: Main quantitative values apply to caffeine, not ciprofloxacin; clinical significance not established.

### SB-0034 Piperine and Carbamazepine

Human pharmacokinetic | PMID:27776366 [R34] | increased drug exposure.

Drug exposure rose; epoxide/parent ratios fell. Mechanism: CYP3A4 inhibition proposed.

Dose and preparation: Piperine 20 mg daily 10 days; carbamazepine 200 mg once. Piperine as named in primary source; salt/form not fully extracted. Population: 12 healthy volunteers.

Quantitative outcome: Cmax +68.7%; AUC +47.9%; half-life +43.2%; CL/F -38.9%. Limitations: Small sequential volunteer study; no clinical efficacy or adverse-event benefit established; supplement doses cannot be equated to cooked food.

### SB-0035 Piperine and Chlorzoxazone

Human pharmacokinetic | PMID:27670974 [R33] | increased drug exposure.

Parent exposure rose while hydroxy-metabolite exposure fell. Mechanism: CYP2E1 inhibition proposed.

Dose and preparation: Piperine 20 mg daily 10 days; chlorzoxazone 250 mg once. Piperine as named in primary source; salt/form not fully extracted. Population: 12 healthy volunteers.

Quantitative outcome: AUC 10.46 to 17.78 microgram.h/mL; Cmax 3.14 to 4.96 microgram/mL; half-life 1.26 to 1.82 h. Limitations: Small sequential volunteer study; no clinical efficacy or adverse-event benefit established; supplement doses cannot be equated to cooked food.

### SB-0036 Piperine and Diclofenac

Human pharmacokinetic | PMID:27052193 [R30] | increased drug exposure.

Diclofenac exposure rose and clearance fell. Mechanism: CYP2C9 inhibition proposed.

Dose and preparation: Piperine 20 mg daily 10 days; diclofenac sodium 100 mg once. Piperine as named in primary source; salt/form not fully extracted. Population: 12 healthy volunteers.

Quantitative outcome: AUC 7.09 to 11.81 microgram.h/mL; Cmax 2.24 to 3.68 microgram/mL; CL/F 7.57 to 4.52 L/h (p<0.05). Limitations: Small sequential volunteer study; no clinical efficacy or adverse-event benefit established; supplement doses cannot be equated to cooked food. Authors suggest benefit; benefit was not tested.

### SB-0037 EGCG and Rosuvastatin

Human pharmacokinetic | PMID:28533679 [R36] | regimen-dependent.

Single co-dose lowered AUC; after ten-day pretreatment no significant AUC/Cmax difference was detected. Mechanism: Transporter involvement proposed; not causally resolved.

Dose and preparation: EGCG 300 mg; rosuvastatin 20 mg; single and ten-day EGCG pretreatment. EGCG as named by study. Population: 13 healthy volunteers.

Quantitative outcome: Single co-dose AUC_last GMR 0.81 (90% CI 0.67-0.97); Cmax GMR 0.85 (0.70-1.04). Limitations: Eight-hour sampling; Cmax CI includes 1 despite abstract significance wording; repeated-regimen null retained in same row.

### SB-0038 Resveratrol and Diclofenac

Human pharmacokinetic | PMID:26633237 [R28] | increased drug exposure.

Exposure increased; clearance decreased. Mechanism: CYP2C9 inhibition proposed.

Dose and preparation: Resveratrol 500 mg daily 10 days; Diclofenac 100 mg once. Resveratrol as named in primary source; salt/form not fully extracted. Population: 12 healthy volunteers.

Quantitative outcome: Cmax GMR 1.75; AUC GMR 2.12; half-life GMR 1.65; CL/F GMR 0.47. Limitations: Small sequential volunteer study; no clinical efficacy or adverse-event benefit established; supplement doses cannot be equated to cooked food. Abstract AUC absolute unit appears erroneous (g.h/mL); use dimensionless reported ratios.

### SB-0039 Resveratrol and Carbamazepine

Human pharmacokinetic | PMID:25624269 [R27] | increased drug exposure.

Exposure and half-life increased; epoxide/parent ratio decreased. Mechanism: CYP3A4 inhibition proposed.

Dose and preparation: Resveratrol 500 mg daily 10 days; Carbamazepine 200 mg once. Resveratrol as named in primary source; salt/form not fully extracted. Population: 12 healthy volunteers.

Quantitative outcome: No reliable numerical effect extracted Limitations: Small sequential volunteer study; no clinical efficacy or adverse-event benefit established; supplement doses cannot be equated to cooked food. Abstract reverses formation wording CBZE to CBZ; interpret measured ratios only.

### SB-0040 Resveratrol and Chlorzoxazone

Human pharmacokinetic | PMID:26680654 [R29] | increased drug exposure.

Exposure increased; metabolite/parent ratios decreased. Mechanism: CYP2E1 inhibition proposed.

Dose and preparation: Resveratrol 500 mg daily 10 days; Chlorzoxazone 250 mg once. Resveratrol as named in primary source; salt/form not fully extracted. Population: 12 healthy volunteers.

Quantitative outcome: No reliable numerical effect extracted Limitations: Small sequential volunteer study; no clinical efficacy or adverse-event benefit established; supplement doses cannot be equated to cooked food. No numerical magnitude extracted.

### SB-0041 Resveratrol and Celecoxib

Human pharmacokinetic | PMID:37935204 [R44] | increased drug exposure.

Exposure and half-life increased; apparent clearance decreased. Mechanism: Metabolic inhibition interpretation; not directly established.

Dose and preparation: Resveratrol 500 mg daily 10 days; Celecoxib 200 mg once. Resveratrol as named in primary source; salt/form not fully extracted. Population: 12 healthy volunteers.

Quantitative outcome: No reliable numerical effect extracted Limitations: Small sequential volunteer study; no clinical efficacy or adverse-event benefit established; supplement doses cannot be equated to cooked food. Authors suggest therapeutic benefit; inflammation outcomes not tested.

### SB-0042 Genistein and Caffeine

Human pharmacokinetic | PMID:21222115 [R17] | altered probe metabolism.

Caffeine metabolic indices changed; NAT2 index did not change significantly. Mechanism: CYP1A2/XO inhibition and CYP2A6 induction suggested by probe ratios.

Dose and preparation: Genistein 1 g daily 14 days; caffeine 100 mg once before and after. Genistein as named in primary source; salt/form not fully extracted. Population: 18 healthy Chinese female volunteers.

Quantitative outcome: CYP1A2 urinary index -41% (90% CI 28-51%); XO -29%; CYP2A6 +47%. Limitations: Metabolic ratios are not caffeine AUC; high supplement dose; no clinical outcome.

### SB-0043 Genistein and Midazolam

Human pharmacokinetic | PMID:21943317 [R20] | decreased drug exposure.

Probe drug exposure decreased. Mechanism: CYP3A induction suggested.

Dose and preparation: Genistein for 14 days; numerical doses not stated in extracted abstract. Genistein as named in primary source; salt/form not fully extracted. Population: 18 healthy adult men.

Quantitative outcome: AUC_infinity 209.18 to 180.59 ng.h/mL; Cmax 48.86 to 36.25 ng/mL (p<0.05). Limitations: Abstract clearance units h^-1 appear inconsistent; clearance omitted. Probe-dose findings do not establish therapeutic failure.

### SB-0044 Genistein and Talinolol

Human pharmacokinetic | PMID:21943317 [R20] | decreased drug exposure.

Probe drug exposure decreased. Mechanism: P-gp induction proposed.

Dose and preparation: Genistein for 14 days; numerical doses not stated in extracted abstract. Genistein as named in primary source; salt/form not fully extracted. Population: 18 healthy adult men.

Quantitative outcome: AUC_infinity 2980.45 to 2626.92 ng.h/mL; Cmax 326.58 to 293.42 ng/mL (p<0.05). Limitations: Abstract clearance units h^-1 appear inconsistent; clearance omitted. Probe-dose findings do not establish therapeutic failure.

### SB-0045 Capsaicin and Aspirin

Controlled clinical | PMID:25532954 [R26] | no detected effect.

Co-administration did not detectably alter aspirin platelet inhibition. Mechanism: No modification of aspirin antiplatelet effect detected.

Dose and preparation: Capsaicin 400 or 800 micrograms orally; aspirin 500 mg. Capsaicin as named in primary source; salt/form not fully extracted. Population: 15 healthy men.

Quantitative outcome: No reliable numerical effect extracted Limitations: Outcome-specific null; does not rule out gastric or other interactions. No effect-size/CI extracted.

### SB-0046 Curcumin and Sulfasalazine

Human pharmacokinetic | PMID:22300367 [R21] | increased drug exposure.

Oral sulfasalazine exposure increased at microdose and therapeutic dose. Mechanism: Intestinal BCRP inhibition supported by parallel experiments.

Dose and preparation: Curcumin 2 g 30 min before sulfasalazine 100 micrograms or 2 g. Curcumin as named in primary source; salt/form not fully extracted. Population: 8 healthy Japanese subjects.

Quantitative outcome: No reliable numerical effect extracted Limitations: Source abstract and full-text prose disagree on dose-specific fold changes; magnitudes withheld pending reconciliation. No cooked-food dose equivalence.

### SB-0047 Curcumin and Sulfasalazine

Animal | PMID:22300367 [R21] | increased drug exposure.

Exposure rose in wild-type mice; not in Bcrp knockout mice. Mechanism: Bcrp-dependent limitation of oral absorption.

Dose and preparation: Curcumin 300 or 400 mg/kg. Curcumin as named in primary source; salt/form not fully extracted. Population: Wild-type and Bcrp knockout mice.

Quantitative outcome: Wild-type AUC0-8 approximately eightfold higher. Limitations: High-dose mouse experiment; human mechanism supported indirectly, not human effect size.

### SB-0048 Curcumin and Sulfasalazine

In vitro | PMID:22300367 [R21] | reduced transporter efflux.

Inhibited hBCRP-mediated sulfasalazine transport. Mechanism: BCRP inhibition.

Dose and preparation: Dose not extracted. Curcumin as named in primary source; salt/form not fully extracted. Population: hBCRP-expressing membrane vesicles.

Quantitative outcome: Ki 0.70 +/- 0.41 micromolar. Limitations: Assay inhibition constant does not establish human exposure threshold.

### SB-0049 Naringin and Fexofenadine

Human pharmacokinetic | PMID:17301733 [R9] | decreased drug exposure.

Aqueous isolated naringin reduced fexofenadine exposure; whole juice had a larger effect. Mechanism: Enteric uptake inhibition proposed.

Dose and preparation: Naringin 1200 micromolar in 300 mL aqueous solution; fexofenadine 120 mg. Aqueous naringin; juice comparator. Population: 12 healthy subjects in naringin trial.

Quantitative outcome: Naringin-arm AUC 75% of water control (p<0.05); grapefruit arm 55% (p<0.001). Limitations: Do not assign whole-juice effect to isolated naringin; overlap of nine participants across two source experiments disclosed.

### SB-0050 Naringin and Fexofenadine

In vitro | PMID:17301733 [R9] | reduced uptake.

Naringin inhibited OATP1A2 transport. Mechanism: OATP1A2 inhibition.

Dose and preparation: Dose not extracted. Naringin as named in primary source; salt/form not fully extracted. Population: Human OATP1A2 in-vitro transport system.

Quantitative outcome: Half-maximal inhibition 3.6 micromolar. Limitations: Different evidence context from human experiment; not a clinical concentration threshold.

### SB-0051 Resveratrol and Buspirone

Human pharmacokinetic | PMID:20716633 [R16] | increased drug exposure.

Probe disposition or metabolic index changed. Mechanism: Phenotypic enzyme modulation; inhibition of CYP3A4/2D6/2C9, induction of CYP1A2 as applicable.

Dose and preparation: Resveratrol 1 g daily four weeks; Buspirone 10 mg. Resveratrol as named in primary source; salt/form not fully extracted. Population: 42 enrolled; 40 completed enzyme assessment; 39 evaluable.

Quantitative outcome: AUC GMR 1.33 (90% CI 1.11-1.59). Limitations: Pharmacological supplementation; metabolic ratios are not AUC; no clinical efficacy/toxicity endpoint.

### SB-0052 Resveratrol and Dextromethorphan

Human pharmacokinetic | PMID:20716633 [R16] | reduced probe metabolism.

Probe disposition or metabolic index changed. Mechanism: Phenotypic enzyme modulation; inhibition of CYP3A4/2D6/2C9, induction of CYP1A2 as applicable.

Dose and preparation: Resveratrol 1 g daily four weeks; Dextromethorphan 30 mg. Resveratrol as named in primary source; salt/form not fully extracted. Population: 42 enrolled; 40 completed enzyme assessment; 38 baseline/35 post.

Quantitative outcome: Urinary parent/metabolite ratio GMR 1.70 (90% CI 1.23-2.19). Limitations: Pharmacological supplementation; metabolic ratios are not AUC; no clinical efficacy/toxicity endpoint.

### SB-0053 Resveratrol and Losartan

Human pharmacokinetic | PMID:20716633 [R16] | reduced metabolite formation.

Probe disposition or metabolic index changed. Mechanism: Phenotypic enzyme modulation; inhibition of CYP3A4/2D6/2C9, induction of CYP1A2 as applicable.

Dose and preparation: Resveratrol 1 g daily four weeks; Losartan 25 mg. Resveratrol as named in primary source; salt/form not fully extracted. Population: 42 enrolled; 40 completed enzyme assessment; 39 evaluable.

Quantitative outcome: Urinary parent/E3174 ratio GMR 2.71 (90% CI 2.22-3.31). Limitations: Pharmacological supplementation; metabolic ratios are not AUC; no clinical efficacy/toxicity endpoint.

### SB-0054 Resveratrol and Caffeine

Human pharmacokinetic | PMID:20716633 [R16] | increased probe metabolism.

Probe disposition or metabolic index changed. Mechanism: Phenotypic enzyme modulation; inhibition of CYP3A4/2D6/2C9, induction of CYP1A2 as applicable.

Dose and preparation: Resveratrol 1 g daily four weeks; Caffeine 100 mg. Resveratrol as named in primary source; salt/form not fully extracted. Population: 42 enrolled; 40 completed enzyme assessment; 36 evaluable.

Quantitative outcome: Four-hour caffeine/paraxanthine ratio GMR 0.84 (90% CI 0.78-0.91). Limitations: Pharmacological supplementation; metabolic ratios are not AUC; no clinical efficacy/toxicity endpoint.

### SB-0055 Caffeine and Ofloxacin

Human pharmacokinetic | PMID:3480885 [R43] | no detected effect.

Drug effect on caffeine elimination assessed. Mechanism: Drug inhibits caffeine elimination where an effect occurred.

Dose and preparation: Caffeine 220-230 mg once; Ofloxacin 200 mg twice daily. Caffeine as named in primary source; salt/form not fully extracted. Population: 12 healthy men.

Quantitative outcome: No reliable numerical effect extracted Limitations: Reverse direction: values belong to caffeine. Possible overlap with 1988 follow-up withheld as separate study.

### SB-0056 Caffeine and Ciprofloxacin

Human pharmacokinetic | PMID:3480885 [R43] | increased compound exposure.

Drug effect on caffeine elimination assessed. Mechanism: Drug inhibits caffeine elimination where an effect occurred.

Dose and preparation: Caffeine 220-230 mg once; Ciprofloxacin 250 mg twice daily. Caffeine as named in primary source; salt/form not fully extracted. Population: 12 healthy men.

Quantitative outcome: Caffeine clearance -33%; half-life +15%. Limitations: Reverse direction: values belong to caffeine. Possible overlap with 1988 follow-up withheld as separate study.

### SB-0057 Caffeine and Enoxacin

Human pharmacokinetic | PMID:3480885 [R43] | increased compound exposure.

Drug effect on caffeine elimination assessed. Mechanism: Drug inhibits caffeine elimination where an effect occurred.

Dose and preparation: Caffeine 220-230 mg once; Enoxacin 400 mg twice daily. Caffeine as named in primary source; salt/form not fully extracted. Population: 12 healthy men.

Quantitative outcome: Caffeine clearance -78%; half-life +260%; Cmax +41%. Limitations: Reverse direction: values belong to caffeine. Possible overlap with 1988 follow-up withheld as separate study.

### SB-0058 Caffeine and Mexiletine

Human pharmacokinetic | PMID:10217339 [R2] | endpoint-dependent.

Total mexiletine clearance was unchanged; one metabolic pathway decreased. Mechanism: CYP1A2 contribution to N-hydroxylation suggested.

Dose and preparation: Caffeine 100 mg four times daily; racemic mexiletine hydrochloride 200 mg once. Caffeine as named in primary source; salt/form not fully extracted. Population: 14 healthy subjects: ten extensive/four poor CYP2D6 metabolizers.

Quantitative outcome: R-enantiomer metabolite urinary recovery -16% extensive/-14% poor metabolizers. Limitations: No significant total-clearance change; metabolic finding is not uniform exposure increase.

### SB-0059 Caffeine and Pefloxacin

Human pharmacokinetic | PMID:10096258 [R1] | increased compound exposure.

Antibiotic reduced steady-state caffeine clearance. Mechanism: CYP1A2 inhibition by drug.

Dose and preparation: Caffeine 183 mg daily; antibiotic 400 mg twice daily. Caffeine as named in primary source; salt/form not fully extracted. Population: 12 healthy young volunteers.

Quantitative outcome: Caffeine clearance ratio 0.53 (90% CI 0.49-0.58); Cmax ratio 1.11 (0.99-1.26). Limitations: Reverse direction; pefloxacin Cmax CI includes 1.

### SB-0060 Caffeine and Enoxacin

Human pharmacokinetic | PMID:10096258 [R1] | increased compound exposure.

Antibiotic reduced steady-state caffeine clearance. Mechanism: CYP1A2 inhibition by drug.

Dose and preparation: Caffeine 183 mg daily; antibiotic 400 mg twice daily. Caffeine as named in primary source; salt/form not fully extracted. Population: 12 healthy young volunteers.

Quantitative outcome: Caffeine clearance ratio 0.17 (90% CI 0.16-0.19); Cmax ratio 1.99 (1.77-2.23). Limitations: Reverse direction; pefloxacin Cmax CI includes 1.

### SB-0061 Caffeine and Norfloxacin

Human pharmacokinetic | PMID:2920498 [R37] | increased compound exposure.

Caffeine AUC increased and clearance decreased. Mechanism: Drug inhibition of caffeine N-demethylation.

Dose and preparation: Numerical dose not extracted. Caffeine as named in primary source; salt/form not fully extracted. Population: Six healthy volunteers; two additional subjects in repeated-caffeine experiment.

Quantitative outcome: No reliable numerical effect extracted Limitations: Main trial small; numerical AUC magnitude unavailable; additional experiment is not another independent study.

### SB-0062 Caffeine and Pipemidic acid

Human pharmacokinetic | PMID:2920498 [R37] | increased compound exposure.

Caffeine AUC increased and clearance decreased. Mechanism: Drug inhibition of caffeine N-demethylation.

Dose and preparation: Numerical dose not extracted. Caffeine as named in primary source; salt/form not fully extracted. Population: Six healthy volunteers; two additional subjects in repeated-caffeine experiment.

Quantitative outcome: Two additional multiple-dose subjects had approximately fourfold caffeine concentration increase. Limitations: Main trial small; numerical AUC magnitude unavailable; additional experiment is not another independent study.

### SB-0063 Resveratrol and Methotrexate

Animal | PMID:27377006 [R32] | altered drug disposition.

Intestinal absorption increased; renal clearance decreased; renal injury improved. Mechanism: Transporter-mediated absorption/elimination changes.

Dose and preparation: Dose not extracted. Resveratrol as named in primary source; salt/form not fully extracted. Population: Rats.

Quantitative outcome: No reliable numerical effect extracted Limitations: No dose or numerical magnitude extracted; preclinical protective outcome does not establish human safety.

### SB-0064 Resveratrol and Methotrexate

In vitro | PMID:27377006 [R32] | reduced transport.

Efflux and renal uptake inhibited; transporter-cell cytotoxicity decreased. Mechanism: P-gp/MRP2 and OAT1/OAT3 inhibition.

Dose and preparation: Dose not extracted. Resveratrol as named in primary source; salt/form not fully extracted. Population: MDR1/MRP2 MDCK monolayers; hOAT1/3 HEK293 cells; rat kidney slices.

Quantitative outcome: No reliable numerical effect extracted Limitations: Transporter-dependent findings; not human PK; assay doses not extracted.

## Appendix B Primary source bibliography

R1 through R45 identify the included interaction reports. R46 and R47 identify separate processing publications. The interaction study count therefore remains 45. Each evidence profile links to its primary-report entry rather than treating a review as an experiment.

[R1] Kinzig-Schippers M, Fuhr U, Zaigler M, Dammeyer J, Rüsing G, Labedzki A, Bulitta J, Sörgel F. (1999). Interaction of pefloxacin and enoxacin with the human cytochrome P450 enzyme CYP1A2. PMID 10096258. DOI 10.1016/s0009-9236(99)70105-0. https://pubmed.ncbi.nlm.nih.gov/10096258/

[R2] Labbé L, Abolfathi Z, Robitaille NM, St-Maurice F, Gilbert M, Turgeon J. (1999). Stereoselective disposition of the antiarrhythmic agent mexiletine during the concomitant administration of caffeine. PMID 10217339. DOI 10.1097/00007691-199904000-00009. https://pubmed.ncbi.nlm.nih.gov/10217339/

[R3] Hägg S, Spigset O, Mjörndal T, Dahlqvist R. (2000). Effect of caffeine on clozapine pharmacokinetics in healthy volunteers. PMID 10606838. DOI 10.1046/j.1365-2125.2000.00111.x. https://pubmed.ncbi.nlm.nih.gov/10606838/

[R4] Velpandian T, Jasuja R, Bhardwaj RK, Jaiswal J, Gupta SK. (2001). Piperine in food: interference in the pharmacokinetics of phenytoin. PMID 11808866. DOI 10.1007/bf03226378. https://pubmed.ncbi.nlm.nih.gov/11808866/

[R5] Raaska K, Raitasuo V, Laitila J, Neuvonen PJ. (2004). Effect of caffeine-containing versus decaffeinated coffee on serum clozapine concentrations in hospitalised patients. PMID 14725610. DOI 10.1111/j.1742-7843.2004.pto_940104.x. https://pubmed.ncbi.nlm.nih.gov/14725610/

[R6] Wu X, Li Q, Xin H, Yu A, Zhong M. (2005). Effects of berberine on the blood concentration of cyclosporin A in renal transplanted recipients: clinical and pharmacokinetic study. PMID 16133554. DOI 10.1007/s00228-005-0952-3. https://pubmed.ncbi.nlm.nih.gov/16133554/

[R7] Culm-Merdek KE, von Moltke LL, Harmatz JS, Greenblatt DJ. (2005). Fluvoxamine impairs single-dose caffeine clearance without altering caffeine pharmacodynamics. PMID 16236038. DOI 10.1111/j.1365-2125.2005.02467.x. https://pubmed.ncbi.nlm.nih.gov/16236038/

[R8] Pattanaik S, Hota D, Prabhakar S, Kharbanda P, Pandhi P. (2006). Effect of piperine on the steady-state pharmacokinetics of phenytoin in patients with epilepsy. PMID 16767797. DOI 10.1002/ptr.1937. https://pubmed.ncbi.nlm.nih.gov/16767797/

[R9] Bailey DG, Dresser GK, Leake BF, Kim RB. (2007). Naringin is a major and selective clinical inhibitor of organic anion-transporting polypeptide 1A2 (OATP1A2) in grapefruit juice. PMID 17301733. DOI 10.1038/sj.clpt.6100104. https://pubmed.ncbi.nlm.nih.gov/17301733/

[R10] Renner B, Clarke G, Grattan T, Beisel A, Mueller C, Werner U, Kobal G, Brune K. (2007). Caffeine accelerates absorption and enhances the analgesic effect of acetaminophen. PMID 17442681. DOI 10.1177/0091270007299762. https://pubmed.ncbi.nlm.nih.gov/17442681/

[R11] Kasibhatta R, Naidu MU. (2007). Influence of piperine on the pharmacokinetics of nevirapine under fasting conditions: a randomised, crossover, placebo-controlled study. PMID 17963429. DOI 10.2165/00126839-200708060-00006. https://pubmed.ncbi.nlm.nih.gov/17963429/

[R12] Bano G, Raina RK, Zutshi U, Bedi KL, Johri RK, Sharma SC. (1991). Effect of piperine on bioavailability and pharmacokinetics of propranolol and theophylline in healthy volunteers. PMID 1815977. DOI 10.1007/bf00314996. https://pubmed.ncbi.nlm.nih.gov/1815977/

[R13] Huang XS, Yang GF, Pan YC. (2008). [Effect of berberin hydrochloride on blood concentration of cyclosporine A in cardiac transplanted recipients]. PMID 18928093. DOI not supplied in extracted metadata. https://pubmed.ncbi.nlm.nih.gov/18928093/

[R14] Golden EB, Lam PY, Kardosh A, Gaffney KJ, Cadenas E, Louie SG, Petasis NA, Chen TC, Schönthal AH. (2009). Green tea polyphenols block the anticancer effects of bortezomib and other boronic acid-based proteasome inhibitors. PMID 19190249. DOI 10.1182/blood-2008-07-171389. https://pubmed.ncbi.nlm.nih.gov/19190249/

[R15] Pattanaik S, Hota D, Prabhakar S, Kharbanda P, Pandhi P. (2009). Pharmacokinetic interaction of single dose of piperine with steady-state carbamazepine in epilepsy patients. PMID 19283724. DOI 10.1002/ptr.2676. https://pubmed.ncbi.nlm.nih.gov/19283724/

[R16] Chow HH, Garland LL, Hsu CH, Vining DR, Chew WM, Miller JA, Perloff M, Crowell JA, Alberts DS. (2010). Resveratrol modulates drug- and carcinogen-metabolizing enzymes in a healthy volunteer study. PMID 20716633. DOI 10.1158/1940-6207.capr-09-0155. https://pubmed.ncbi.nlm.nih.gov/20716633/

[R17] Chen Y, Xiao CQ, He YJ, Chen BL, Wang G, Zhou G, Zhang W, Tan ZR, Cao S, Wang LP, Zhou HH. (2011). Genistein alters caffeine exposure in healthy female volunteers. PMID 21222115. DOI 10.1007/s00228-010-0964-5. https://pubmed.ncbi.nlm.nih.gov/21222115/

[R18] Bannerman B, Xu L, Jones M, Tsu C, Yu J, Hales P, Monbaliu J, Fleming P, Dick L, Manfredi M, Claiborne C, Bolen J, Kupperman E, Berger A. (2011). Preclinical evaluation of the antitumor activity of bortezomib in combination with vitamin C or with epigallocatechin gallate, a component of green tea. PMID 21400028. DOI 10.1007/s00280-011-1591-2. https://pubmed.ncbi.nlm.nih.gov/21400028/

[R19] Guo Y, Chen Y, Tan ZR, Klaassen CD, Zhou HH. (2012). Repeated administration of berberine inhibits cytochromes P450 in humans. PMID 21870106. DOI 10.1007/s00228-011-1108-2. https://pubmed.ncbi.nlm.nih.gov/21870106/

[R20] Xiao CQ, Chen R, Lin J, Wang G, Chen Y, Tan ZR, Zhou HH. (2012). Effect of genistein on the activities of cytochrome P450 3A and P-glycoprotein in Chinese healthy participants. PMID 21943317. DOI 10.3109/00498254.2011.615954. https://pubmed.ncbi.nlm.nih.gov/21943317/

[R21] Kusuhara H, Furuie H, Inano A, Sunagawa A, Yamada S, Wu C, Fukizawa S, Morimoto N, Ieiri I, Morishita M, Sumita K, Mayahara H, Fujita T, Maeda K, Sugiyama Y. (2012). Pharmacokinetic interaction study of sulphasalazine in healthy subjects and the impact of curcumin as an in vivo inhibitor of BCRP. PMID 22300367. DOI 10.1111/j.1476-5381.2012.01887.x. https://pubmed.ncbi.nlm.nih.gov/22300367/

[R22] Cho YA, Lee W, Choi JS. (2012). Effects of curcumin on the pharmacokinetics of tamoxifen and its active metabolite, 4-hydroxytamoxifen, in rats: possible role of CYP3A4 and P-glycoprotein inhibition by curcumin. PMID 22512082. DOI not supplied in extracted metadata. https://pubmed.ncbi.nlm.nih.gov/22512082/

[R23] Volak LP, Hanley MJ, Masse G, Hazarika S, Harmatz JS, Badmaev V, Majeed M, Greenblatt DJ, Court MH. (2013). Effect of a herbal extract containing curcumin and piperine on midazolam, flurbiprofen and paracetamol (acetaminophen) pharmacokinetics in healthy volunteers. PMID 22725836. DOI 10.1111/j.1365-2125.2012.04364.x. https://pubmed.ncbi.nlm.nih.gov/22725836/

[R24] Misaka S, Miyazaki N, Fukushima T, Yamada S, Kimura J. (2013). Effects of green tea extract and (-)-epigallocatechin-3-gallate on pharmacokinetics of nadolol in rats. PMID 23920278. DOI 10.1016/j.phymed.2013.07.003. https://pubmed.ncbi.nlm.nih.gov/23920278/

[R25] Rezaee MM, Kazemi S, Kazemi MT, Gharooee S, Yazdani E, Gharooee H, Shiran MR, Moghadamnia AA. (2014). The effect of piperine on midazolam plasma concentration in healthy volunteers, a research on the CYP3A-involving metabolism. PMID 24398010. DOI 10.1186/2008-2231-22-8. https://pubmed.ncbi.nlm.nih.gov/24398010/

[R26] Sandor B, Papp J, Mozsik G, Szolcsanyi J, Keszthelyi Z, Juricskay I, Toth K, Habon T. (2014). Orally given gastroprotective capsaicin does not modify aspirin-induced platelet aggregation in healthy male volunteers (human phase I examination). PMID 25532954. DOI 10.1556/aphysiol.101.2014.4.4. https://pubmed.ncbi.nlm.nih.gov/25532954/

[R27] Bedada SK, Nearati P. (2015). Effect of resveratrol on the pharmacokinetics of carbamazepine in healthy human volunteers. PMID 25624269. DOI 10.1002/ptr.5302. https://pubmed.ncbi.nlm.nih.gov/25624269/

[R28] Bedada SK, Yellu NR, Neerati P. (2016). Effect of Resveratrol Treatment on the Pharmacokinetics of Diclofenac in Healthy Human Volunteers. PMID 26633237. DOI 10.1002/ptr.5539. https://pubmed.ncbi.nlm.nih.gov/26633237/

[R29] Bedada SK, Neerati P. (2016). Resveratrol Pretreatment Affects CYP2E1 Activity of Chlorzoxazone in Healthy Human Volunteers. PMID 26680654. DOI 10.1002/ptr.5549. https://pubmed.ncbi.nlm.nih.gov/26680654/

[R30] Bedada SK, Boga PK, Kotakonda HK. (2017). Study on influence of piperine treatment on the pharmacokinetics of diclofenac in healthy volunteers. PMID 27052193. DOI 10.3109/00498254.2016.1163752. https://pubmed.ncbi.nlm.nih.gov/27052193/

[R31] Healy DP, Polk RE, Kanawati L, Rock DT, Mooney ML. (1989). Interaction between oral ciprofloxacin and caffeine in normal volunteers. PMID 2729942. DOI 10.1128/aac.33.4.474. https://pubmed.ncbi.nlm.nih.gov/2729942/

[R32] Jia Y, Liu Z, Wang C, Meng Q, Huo X, Liu Q, Sun H, Sun P, Yang X, Ma X, Liu K. (2016). P-gp, MRP2 and OAT1/OAT3 mediate the drug-drug interaction between resveratrol and methotrexate. PMID 27377006. DOI 10.1016/j.taap.2016.06.030. https://pubmed.ncbi.nlm.nih.gov/27377006/

[R33] Bedada SK, Boga PK. (2017). Effect of piperine on CYP2E1 enzyme activity of chlorzoxazone in healthy volunteers. PMID 27670974. DOI 10.1080/00498254.2016.1241450. https://pubmed.ncbi.nlm.nih.gov/27670974/

[R34] Bedada SK, Appani R, Boga PK. (2017). Effect of Piperine on the Metabolism and Pharmacokinetics of Carbamazepine in Healthy Volunteers. PMID 27776366. DOI 10.1055/s-0042-118173. https://pubmed.ncbi.nlm.nih.gov/27776366/

[R35] Bedada SK, Boga PK. (2017). The influence of piperine on the pharmacokinetics of fexofenadine, a P-glycoprotein substrate, in healthy volunteers. PMID 27981349. DOI 10.1007/s00228-016-2173-3. https://pubmed.ncbi.nlm.nih.gov/27981349/

[R36] Kim TE, Ha N, Kim Y, Kim H, Lee JW, Jeon JY, Kim MG. (2017). Effect of epigallocatechin-3-gallate, major ingredient of green tea, on the pharmacokinetics of rosuvastatin in healthy volunteers. PMID 28533679. DOI 10.2147/dddt.s130050. https://pubmed.ncbi.nlm.nih.gov/28533679/

[R37] Carbó M, Segura J, De la Torre R, Badenas JM, Camí J. (1989). Effect of quinolones on caffeine disposition. PMID 2920498. DOI 10.1038/clpt.1989.23. https://pubmed.ncbi.nlm.nih.gov/2920498/

[R38] Abe O, Ono T, Sato H, Müller F, Ogata H, Miura I, Shikama Y, Yabe H, Onoue S, Fromm MF, Kimura J, Misaka S. (2018). Role of (-)-epigallocatechin gallate in the pharmacokinetic interaction between nadolol and green tea in healthy volunteers. PMID 29480324. DOI 10.1007/s00228-018-2436-2. https://pubmed.ncbi.nlm.nih.gov/29480324/

[R39] Ren T, Yang M, Xiao M, Zhu J, Xie W, Zuo Z. (2019). Time-dependent inhibition of carbamazepine metabolism by piperine in anti-epileptic treatment. PMID 30611786. DOI 10.1016/j.lfs.2018.12.060. https://pubmed.ncbi.nlm.nih.gov/30611786/

[R40] Hussaarts KGAM, Hurkmans DP, Oomen-de Hoop E, van Harten LJ, Berghuis S, van Alphen RJ, Spierings LEA, van Rossum-Schornagel QC, Vastbinder MB, van Schaik RHN, van Gelder T, Jager A, van Leeuwen RWF, Mathijssen RHJ. (2019). Impact of Curcumin (with or without Piperine) on the Pharmacokinetics of Tamoxifen. PMID 30909366. DOI 10.3390/cancers11030403. https://pubmed.ncbi.nlm.nih.gov/30909366/

[R41] Ren T, Xiao M, Yang M, Zhao J, Zhang Y, Hu M, Cheng Y, Xu H, Zhang C, Yan X, Zuo Z. (2019). Reduced Systemic and Brain Exposure with Inhibited Liver Metabolism of Carbamazepine After Its Long-Term Combination Treatment with Piperine for Epilepsy Control in Rats. PMID 31321577. DOI 10.1208/s12248-019-0357-3. https://pubmed.ncbi.nlm.nih.gov/31321577/

[R42] Tan HJ, Ling WC, Chua AL, Lee SK. (2021). Oral epigallocatechin gallate reduces intestinal nadolol absorption via modulation of Oatp1a5 and Oct1 transcriptional levels in spontaneously hypertensive rats. PMID 34303263. DOI 10.1016/j.phymed.2021.153623. https://pubmed.ncbi.nlm.nih.gov/34303263/

[R43] Stille W, Harder S, Mieke S, Beer C, Shah PM, Frech K, Staib AH. (1987). Decrease of caffeine elimination in man during co-administration of 4-quinolones. PMID 3480885. DOI 10.1093/jac/20.5.729. https://pubmed.ncbi.nlm.nih.gov/3480885/

[R44] Helal NI, El-Khodary NM, Omran GA, El-Masry SM. (2023). Effects of Resveratrol Co-Administration on Celecoxib Disposition and Pharmacokinetics in Healthy Volunteers. PMID 37935204. DOI 10.1055/a-2160-2186. https://pubmed.ncbi.nlm.nih.gov/37935204/

[R45] Jeppesen U, Loft S, Poulsen HE, Brśen K. (1996). A fluvoxamine-caffeine interaction study. PMID 8807660. DOI 10.1097/00008571-199606000-00003. https://pubmed.ncbi.nlm.nih.gov/8807660/

[R46] Suresh D, Manjunatha H, Srinivasan K. (2007). Effect of heat processing of spices on the concentrations of their bioactive principles: Turmeric (Curcuma longa), red pepper (Capsicum annuum) and black pepper (Piper nigrum). Journal of food composition and analysis : an official publication of the United Nations University, International Network of Food Data Systems. DOI 10.1016/j.jfca.2006.10.002. https://doi.org/10.1016/j.jfca.2006.10.002

[R47] Jin Y, Zhao J, Kim EM, Kim KH, Kang S, Lee H, Lee J. (2019). Comprehensive Investigation of the Effects of Brewing Conditions in Sample Preparation of Green Tea Infusions.. Molecules (Basel, Switzerland). DOI 10.3390/molecules24091735. https://pubmed.ncbi.nlm.nih.gov/31060206/

## Appendix C Evidence field dictionary

| Field | Meaning |
| --- | --- |
| Evidence_ID | Stable row identifier SB-0001 to SB-0064. |
| Compound | Anchor chemical named in the primary relationship. |
| Compound_ID | Original CookRisk molecular group; groups are not merged. |
| Drug | Named administered drug or metabolic probe. |
| Interaction_Effect | Measured effect or tested null summarized in words. |
| Mechanism | Source-supported or explicitly proposed mechanism. |
| Evidence_Type | Human pharmacokinetic, Controlled clinical, Animal or In vitro. |
| Evidence_Level | Preparation specificity; not evidence strength. |
| Direction | Direction of the reported endpoint; can be regimen or endpoint dependent. |
| Quantitative_Outcome | Extracted effect size, ratio, interval or assay result; not dose alone. |
| Dose | Compound/drug dose, concentration, frequency or duration when extracted. |
| Population | Human sample or animal/cell experimental system. |
| Study_Design | Design of the source experiment. |
| Source_Title | Primary publication title. |
| Authors | Primary publication author metadata. |
| Year | Source publication year; online and print dates can differ. |
| DOI | Digital object identifier where supplied. |
| PMID | Primary PubMed identifier. |
| Source_Type | Primary research for included evidence. |
| Limitations | Source, extraction and applicability constraints. |
| Confidence | Descriptive support; not GRADE or a clinical risk score. |
| Notes | Additional interpretation and provenance cautions. |
| Study_ID | PMID-based grouping for records from one primary report. |
| Source_URL | Primary source link. |
| Source_Cache | Saved source response path relative to stageB. |
| Source_Locator | Abstract, section or table used for extraction. |
| Preparation | Actual isolated compound, salt, extract or food preparation scope. |
| Co_Compounds | Named co-interventions; avoids duplicate ingredient attribution. |
| Affected_Entity | Whether the measured change concerns drug, compound or probe. |
| Perpetrator | Compound/preparation or drug producing the disposition change. |
| Outcome | Observed effect, null or mixed endpoint status. |
| Conflict_Group | Context-dependent synthesis key where assigned. |
| Identity_Status | Exact structure or parent-connectivity scope. |
| Release_Origin | Initial 33 records or expansion additions. |
| Clinical_Extrapolation | Explicit guard against automatic clinical-risk classification. |
| CookRisk_Exposure_Link | Identity/provenance constraints before exposure transfer. |

Blank means unavailable, not extracted or not reliably resolved. It never means zero, normal, safe or no interaction. Source_Cache paths are relative to stageB; expansion caches include the expansion_v2 prefix.

## Appendix D File inventory

Workspace root: C:/Users/dakshant/Documents/CookChem. Paths below are relative to this root. CSV row counts exclude the header. This inventory is derived directly from the saved files, rather than copied from an earlier narrative count.

### Initial Stage B tables

| File | Rows |
| --- | --- |
| stageB/outputs/stageB_compound_mapping.csv | 198 |
| stageB/outputs/stageB_conflict_synthesis.csv | 4 |
| stageB/outputs/stageB_dataset_source_audit.csv | 208 |
| stageB/outputs/stageB_drugs.csv | 18 |
| stageB/outputs/stageB_duplicate_standardized_identities.csv | 1 |
| stageB/outputs/stageB_exclusions.csv | 4 |
| stageB/outputs/stageB_food_compounds.csv | 333 |
| stageB/outputs/stageB_food_drug_interactions.csv | 33 |
| stageB/outputs/stageB_foods.csv | 190 |
| stageB/outputs/stageB_identity_audit.csv | 203 |
| stageB/outputs/stageB_interaction_compounds.csv | 40 |
| stageB/outputs/stageB_literature_evidence.csv | 33 |
| stageB/outputs/stageB_processing_evidence.csv | 3 |
| stageB/outputs/stageB_search_candidates.csv | 3379 |
| stageB/outputs/stageB_search_log.csv | 198 |
| stageB/outputs/stageB_stageA_linkage.csv | 198 |
| stageB/outputs/stageB_stageA_observation_links.csv | 1124 |
| stageB/outputs/stageB_standardized_search_log.csv | 102 |
| stageB/outputs/stageB_unassigned_observations.csv | 221 |

### Expanded release tables

| File | Rows |
| --- | --- |
| stageB/expansion_v2/outputs/compound_prioritization.csv | 198 |
| stageB/expansion_v2/outputs/conflict_synthesis.csv | 5 |
| stageB/expansion_v2/outputs/drug_identity_registry.csv | 34 |
| stageB/expansion_v2/outputs/inherited_stageB_dataset_source_audit.csv | 208 |
| stageB/expansion_v2/outputs/inherited_stageB_duplicate_standardized_identities.csv | 1 |
| stageB/expansion_v2/outputs/inherited_stageB_unassigned_observations.csv | 221 |
| stageB/expansion_v2/outputs/literature_search_log.csv | 45 |
| stageB/expansion_v2/outputs/primary_source_DOI_audit.csv | 45 |
| stageB/expansion_v2/outputs/qc_identity.csv | 198 |
| stageB/expansion_v2/outputs/source_screening_log.csv | 2608 |
| stageB/expansion_v2/outputs/stageB_food_drug_interactions_expanded.csv | 64 |
| stageB/expansion_v2/outputs/study_registry.csv | 45 |

### Reports and audit material

stageB/reports contains the original inventory, methodology, QC, data dictionary, references, requirements checklist, reproducibility report and dataset-source audit.

stageB/expansion_v2/reports contains the expansion evidence summary, QC report, search methodology and data dictionary.

stageB/audit contains original input and output manifests, extracted background documents and initial release verification.

stageB/sources and stageB/expansion_v2/sources preserve query responses, source metadata, identity data and available full text.

stageB/scripts and stageB/expansion_v2/scripts preserve collection, extraction, build and validation logic.

stageB/final_report contains this consolidated Word and PDF report, readable source, builder and report-specific audit.

### Preserved input hashes

cookchem_master_expanded_round11.csv SHA-256 06f576355f2b3e7d7ee1569fa91930ea36f2f360b1971d4be19bc0bfac3469f5

stageA_oof_predictions.csv SHA-256 6425f4dbcf53a1a982ce14f93a61723e433afb6f1c6adb40178abf6cfdcb9141

CookRisk_StageA_Benchmark_Report.pdf SHA-256 9cadae03121ce00b7935fd6829924eb7ca0c888ec988829f2a25ac44152e67fc

CookRisk_BTP_Literature_Review_Assignment_2_FINAL_CORRECTED (1).docx SHA-256 94926387baa7ada3290124b0614597814dd7eeccda40eeae428ff419610ae334
