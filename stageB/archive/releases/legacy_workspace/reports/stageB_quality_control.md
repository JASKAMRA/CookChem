# Stage B quality control

| Automated check | Result |
| --- | --- |
| unique_interaction_ids | PASS |
| complete_compound_universe | PASS |
| unique_compound_mapping_ids | PASS |
| unique_drug_ids_and_names | PASS |
| mapped_external_identifier_format | PASS |
| source_DOI_format_where_available | PASS |
| all_interactions_have_provenance | PASS |
| all_interaction_compounds_identity_mapped | PASS |
| source_dates_not_future | PASS |
| all_ids_present | PASS |
| oof_record_group_and_target_matches | PASS |
| unique_selected_oof_records | PASS |
| oof_each_group_single_validation_fold | PASS |
| food_claims_only_studied_preparations | PASS |
| preclinical_no_assigned_clinical_significance | PASS |
| no_arbitrary_risk_columns | PASS |
| all_evidence_records_one_to_one | PASS |
| unassigned_rows_preserved | PASS |
| historical_input_hashes_unchanged | PASS |
| bundled_input_hashes_match | PASS |

Manual evidence review: each of 33 records was checked against its cached original-study abstract and, where available/needed, full-text tables. Identity concordance checks compare PubChem structure and names/synonyms, preserve stereochemistry limits, and exclude mixed/ambiguous groups. Quantitative values remain source text with units and source locators; directions without numerical magnitudes leave numerical fields blank. This is one reviewer, not independent dual extraction.

Issues found: 221 rows lack molecular IDs; 96 groups lack concordant identity; 23 mapped groups have incomplete structure-form agreement; drug external IDs/classes not resolved; source-abstract label inconsistency in Guo et al.; design/sample statements and clearance wording inconsistency in Rezaee et al.; most search results not exhaustively screened. Food categories absent.

Issues resolved in this release: blank ID rows preserved separately; no uncertain groups assigned; proposed mechanisms marked as proposed; mixed-extract effects not attributed to an isolated ingredient; rat/in-vitro outcomes not promoted to humans; conflicting records retained; no invented risk values; reverse caffeine interactions explicitly labelled. Unsupported numeric values and ambiguous Tmax/half-life labels left blank. Remaining limits are not hidden by automated PASS status.

OOF folds show each group occurs in one validation fold; training-fold membership cannot be independently reconstructed without Stage A runner/train indices. No assertion of a re-run model or clinical validation.


## Upstream data-source audit (material limitation)
Crossref metadata was retrieved for 208 dataset DOIs: 145 have author and/or year metadata discrepancies; 10 could not be retrieved. These are source-verification flags, not automatic proof that every associated measurement is fabricated. Metadata-concordant citations still do not verify measurements.

A confirmed example is DOI 10.1016/j.lwt.2021.111500, assigned to five avocado/Persin cooking rows. The publisher identifies a 2021 Liu et al. fish-oil/gelatin encapsulation paper, rather than the recorded 2022 Molina et al. Persin study. [Publisher source](https://www.sciencedirect.com/science/article/abs/pii/S0023643821006538). This mismatch blocks scientific validation of those food-retention claims. It does not invalidate independently verified Stage B interaction publications.

Additionally, 115 selected OOF records have FALSE in the current master Final_Preprocessing_Eligible flag despite matching molecular IDs and actual target values. The supplied Stage A report describes a frozen 1,124-row experiment, while the current master flags only 1,009 eligible rows. Without the locked Stage A runner/input snapshot, eligibility lineage cannot be reconciled. Original outputs are preserved and no re-training or retrospective repair was attempted.

One standardized-CID cluster (5282102) spans two original groups, Kaempferol-3-Glucoside and Astragalin. Groups remain separate. This is not proof of leakage: their stereochemical representations differ in completeness; cross-fold identity duplication needs a separate Stage A audit.

Therefore food associations and OOF outputs are traceable inherited project data, not newly certified experimental evidence. The knowledge base can support literature evidence lookup; any quantitative retained-dose or clinical extrapolation remains blocked by upstream provenance and form/exposure limits. Detailed flags: stageB_dataset_source_audit.csv, stageB_duplicate_standardized_identities.csv and observation-link metadata fields.
