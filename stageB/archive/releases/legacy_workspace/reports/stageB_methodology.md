# Stage B methodology

## 1. Objective
Build an initial evidence-mapped Food-Compound-Drug knowledge base. This is an evidence layer, not clinical decision support or a risk score.
## 2. Dataset source
Use the supplied 1,350-row expanded master and original Stage A OOF CSV; SHA-256 hashes lock input provenance. Older checkout outputs are historical context.
## 3. Compound selection
Retain all 198 nonblank Canonical_Molecular_ID groups. Preserve 221 blank-ID observations separately without inventing groups. Molecular groups, names, and distinct standardized CIDs are different counts.
## 4. Identity standardization
Retrieve public PubChem properties and synonyms by existing CIDs. Prefer existing resolved-CID fields over historical CIDs. Require one candidate CID, one concordant structure, and all observed names to match source names/synonyms. RDKit comparison distinguishes exact structure from connectivity-only agreement. No groups are merged. Connectivity-only mappings establish named parent identity but do not verify stereochemical form. Mixed total/individual names and conflicting structures remain uncertain. CAS-like PubChem synonyms require checksum validation; source-reported synonyms are not an independent registry adjudication.
## 5. Literature search strategy
Targeted literature search, 6 October 2026, Europe PMC plus primary-study web discovery and reference follow-up. Each nonblank CookRisk group had a title/abstract query. Cache the first 25 results and hit count; 115 queries exceeded that cap. These are searches, not complete systematic-review screening. Selected studies were manually extracted.
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


## Upstream data-source audit (material limitation)
Crossref metadata was retrieved for 208 dataset DOIs: 145 have author and/or year metadata discrepancies; 10 could not be retrieved. These are source-verification flags, not automatic proof that every associated measurement is fabricated. Metadata-concordant citations still do not verify measurements.

A confirmed example is DOI 10.1016/j.lwt.2021.111500, assigned to five avocado/Persin cooking rows. The publisher identifies a 2021 Liu et al. fish-oil/gelatin encapsulation paper, rather than the recorded 2022 Molina et al. Persin study. [Publisher source](https://www.sciencedirect.com/science/article/abs/pii/S0023643821006538). This mismatch blocks scientific validation of those food-retention claims. It does not invalidate independently verified Stage B interaction publications.

Additionally, 115 selected OOF records have FALSE in the current master Final_Preprocessing_Eligible flag despite matching molecular IDs and actual target values. The supplied Stage A report describes a frozen 1,124-row experiment, while the current master flags only 1,009 eligible rows. Without the locked Stage A runner/input snapshot, eligibility lineage cannot be reconciled. Original outputs are preserved and no re-training or retrospective repair was attempted.

One standardized-CID cluster (5282102) spans two original groups, Kaempferol-3-Glucoside and Astragalin. Groups remain separate. This is not proof of leakage: their stereochemical representations differ in completeness; cross-fold identity duplication needs a separate Stage A audit.

Therefore food associations and OOF outputs are traceable inherited project data, not newly certified experimental evidence. The knowledge base can support literature evidence lookup; any quantitative retained-dose or clinical extrapolation remains blocked by upstream provenance and form/exposure limits. Detailed flags: stageB_dataset_source_audit.csv, stageB_duplicate_standardized_identities.csv and observation-link metadata fields.


Standardized-name follow-up: 102 mapped groups additionally queried by verified PubChem title with broader drug/PK/PD/absorption/metabolism/transporter concepts and a 2026-10-06 publication cutoff. Exact queries and retrieval status: stageB_standardized_search_log.csv. Candidate coverage remains limited to 25 and is not exhaustive manual screening.
