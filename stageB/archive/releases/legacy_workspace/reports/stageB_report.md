# CookRisk Stage B report

## 1. Executive summary
An initial reproducible evidence layer now links the supplied compound universe, food associations, study-level drug evidence and original selected-model OOF predictions. 33 evidence records from 26 original studies cover 5 anchor compounds and 18 drugs. Null findings and preclinical conflicts remain visible. No clinical risk scores or dietary exposure estimates were created.
## 2. Objective
Establish auditable Food-Compound-Drug-Mechanism-Evidence-Source relationships.
## 3. Relationship to Stage A
ExtraTrees_reference is the selected benchmark, as documented by Stage A. All 1,124 OOF records match master Record_ID, molecular group and target. A saved fitted model and Phase 1-3 experiment code are absent in this checkout. No new-condition prediction is claimed.
## 4. CookRisk compound universe
| Measure | Count |
| --- | --- |
| Master observations | 1350 |
| Nonblank molecular groups | 198 |
| Rows without molecular ID | 221 |
| Unique compound-name strings | 241 |
| Food-name strings | 187 |
| Food categories | Not supplied |
| Stage A OOF molecular groups | 197 |
The blank-ID bucket is not a 199th molecule. Unassigned rows remain auditable and are not discarded.
## 5. Identity standardization
| Status | Groups |
| --- | --- |
| Verified exact structure/name | 79 |
| Verified name/CID/connectivity; stereo incomplete | 23 |
| Uncertain identity | 96 |
| Distinct standardized source CIDs | 101 |
Mapping preserves all 198 original groups. No identity is merged solely by name. Uncertain groups are not assigned drug interactions. Connectivity-only is a qualified parent-identity mapping, not confirmation of chemical form or dietary exposure. Missing external identity fields are blank; inherited historical CIDs retained separately.
## 6. Literature methodology
198 molecular-group searches were retrieved from Europe PMC on 6 October 2026, plus primary-study follow-up. Only the first 25 candidates per query were cached; 115 groups exceed the cap. Selected sources manually screened/extracted. Other compounds are searched but not exhaustively screened. This is a targeted search, not a systematic review.
## 7. Interaction evidence
| Anchor compound | Records |
| --- | --- |
| Berberine | 5 |
| Caffeine | 6 |
| Curcumin | 6 |
| EGCG | 6 |
| Piperine | 10 |
Combination co-interventions appear in a separate relation table. Evidence coverage including verified co-interventions is 6 compound groups. Counts describe records, not independent patients or proven hazards.
## 8. Evidence-type distribution
| Evidence | Records |
| --- | --- |
| Human pharmacokinetic | 24 |
| In vitro | 3 |
| Animal | 5 |
| Controlled clinical | 1 |
## 9. Mechanisms
| Category | Records (multi-category possible) |
| --- | --- |
| Enzyme inhibition | 11 |
| Absorption | 7 |
| Metabolism | 4 |
| Transporter inhibition | 3 |
| Transporter regulation | 1 |
| Antagonistic effect | 2 |
| Additive effect | 1 |
Proposed enzyme or transporter explanations are labelled; observed exposure changes alone do not prove the mechanism.
## 10. Quantitative evidence
18 records contain extracted quantitative PK/PD outcomes; 2 additional records contain biochemical assay kinetics, for 20 quantitative-outcome records total. Dose-only records are not counted. Berberine-cyclosporine AUC +34.5% (Wu et al.); piperine-nevirapine AUCinfinity approximately +170% (Kasibhatta & Naidu); curcumin-plus-piperine tamoxifen AUC -12.8% and endoxifen AUC -12.4% (Hussaarts et al.). These are regimen-specific study results. Endpoint units, CI and significance remain in tables. Source locators are explicit.
## 11. Human versus preclinical
25 human, 5 animal, 3 in-vitro, 0 standalone in-silico/mechanistic records. In-silico estimates reported within preclinical sources are not promoted to observed PK. 3 mixture-specific null controls are retained.
## 12. Conflicting evidence
| Relationship | Synthesis |
| --- | --- |
| Piperine-Carbamazepine | Human single-dose piperine increased exposure; repeated rat co-treatment decreased exposure despite metabolic inhibition. Species/regimen/context differ. Microsomal inhibition is a separate assay result; no common effect coefficient. |
| Piperine-Midazolam | Isolated piperine study reported longer sedation/lower clearance; short-term curcuminoid/piperine mixture showed no meaningful parent-midazolam PK change. Different preparation/regimen; not a pure same-intervention replication. |
| Curcumin-Tamoxifen | Rat oral exposure increased; human tamoxifen exposure decreased with curcumin with/without piperine. Different species and metabolites; curcumin-only human endoxifen contrast p=0.07. |
| EGCG-Bortezomib | Cell assays showed antagonism; xenografts showed concentration dependence and no antagonism at 11-16 uM, but antagonism above 200 uM. No human clinical interaction established. |
Different species/preparations/regimens limit direct comparisons. Clinical relevance of preclinical bortezomib findings remains unestablished.
## 13. Cooking/processing
Separate evidence describes curcumin/piperine losses in boiled/pressure-cooked spices and green-tea catechin extraction/epimerization during brewing. This does not establish how cooking changes drug-interaction strength. Literature processing values are not Stage A predictions.
## 14. Stage A linkage
33 of 33 interaction records link to selected-model groups. Compound linkage preserves observation/food counts; observation linkage preserves food, cooking conditions, baseline concentration and individual OOF values with original row pointers. No invented per-compound retention or retained amount.
## 15. Quality control
All 20 automated integrity checks passed. Manual context review retained reporting issues rather than hiding them. Historical-input hashes unchanged. Automated checks cannot prove a perfect literature review.
## 16. Limitations
96 uncertain groups; 221 blank-ID observations; 23 qualified connectivity mappings; incomplete external drug identifiers/classes; truncated, non-exhaustively screened searches; abstract-dependent extraction; one reviewer; no source-level revalidation of all modelling food/concentration/DOI claims; no fitted deployment model here; supplement/cell/animal exposures not transferable to cooked-food clinical risk. These limitations restrict conclusions.
## 17. Future integration
Repair identity and source provenance first; extend screening and normalize drug identifiers. Retention predictions can be joined to documented associations only after condition/unit/basis/exposure checks. Do not rank foods/drugs numerically from this database.
## 18. Conclusion
Stage B successfully establishes an initial evidence-based knowledge base with auditable source and Stage A linkage. It is a bounded research evidence release, not an exhaustive or clinically validated interaction system. A missing record means no qualifying evidence was retained under this release's search/identity limits; it does not mean no interaction exists.


## Upstream data-source audit (material limitation)
Crossref metadata was retrieved for 208 dataset DOIs: 145 have author and/or year metadata discrepancies; 10 could not be retrieved. These are source-verification flags, not automatic proof that every associated measurement is fabricated. Metadata-concordant citations still do not verify measurements.

A confirmed example is DOI 10.1016/j.lwt.2021.111500, assigned to five avocado/Persin cooking rows. The publisher identifies a 2021 Liu et al. fish-oil/gelatin encapsulation paper, rather than the recorded 2022 Molina et al. Persin study. [Publisher source](https://www.sciencedirect.com/science/article/abs/pii/S0023643821006538). This mismatch blocks scientific validation of those food-retention claims. It does not invalidate independently verified Stage B interaction publications.

Additionally, 115 selected OOF records have FALSE in the current master Final_Preprocessing_Eligible flag despite matching molecular IDs and actual target values. The supplied Stage A report describes a frozen 1,124-row experiment, while the current master flags only 1,009 eligible rows. Without the locked Stage A runner/input snapshot, eligibility lineage cannot be reconciled. Original outputs are preserved and no re-training or retrospective repair was attempted.

One standardized-CID cluster (5282102) spans two original groups, Kaempferol-3-Glucoside and Astragalin. Groups remain separate. This is not proof of leakage: their stereochemical representations differ in completeness; cross-fold identity duplication needs a separate Stage A audit.

Therefore food associations and OOF outputs are traceable inherited project data, not newly certified experimental evidence. The knowledge base can support literature evidence lookup; any quantitative retained-dose or clinical extrapolation remains blocked by upstream provenance and form/exposure limits. Detailed flags: stageB_dataset_source_audit.csv, stageB_duplicate_standardized_identities.csv and observation-link metadata fields.


Standardized-name follow-up: 102 mapped groups additionally queried by verified PubChem title with broader drug/PK/PD/absorption/metabolism/transporter concepts and a 2026-10-06 publication cutoff. Exact queries and retrieval status: stageB_standardized_search_log.csv. Candidate coverage remains limited to 25 and is not exhaustive manual screening.
