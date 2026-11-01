# Input and repository inventory

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


## Upstream data-source audit (material limitation)
Crossref metadata was retrieved for 208 dataset DOIs: 145 have author and/or year metadata discrepancies; 10 could not be retrieved. These are source-verification flags, not automatic proof that every associated measurement is fabricated. Metadata-concordant citations still do not verify measurements.

A confirmed example is DOI 10.1016/j.lwt.2021.111500, assigned to five avocado/Persin cooking rows. The publisher identifies a 2021 Liu et al. fish-oil/gelatin encapsulation paper, rather than the recorded 2022 Molina et al. Persin study. [Publisher source](https://www.sciencedirect.com/science/article/abs/pii/S0023643821006538). This mismatch blocks scientific validation of those food-retention claims. It does not invalidate independently verified Stage B interaction publications.

Additionally, 115 selected OOF records have FALSE in the current master Final_Preprocessing_Eligible flag despite matching molecular IDs and actual target values. The supplied Stage A report describes a frozen 1,124-row experiment, while the current master flags only 1,009 eligible rows. Without the locked Stage A runner/input snapshot, eligibility lineage cannot be reconciled. Original outputs are preserved and no re-training or retrospective repair was attempted.

One standardized-CID cluster (5282102) spans two original groups, Kaempferol-3-Glucoside and Astragalin. Groups remain separate. This is not proof of leakage: their stereochemical representations differ in completeness; cross-fold identity duplication needs a separate Stage A audit.

Therefore food associations and OOF outputs are traceable inherited project data, not newly certified experimental evidence. The knowledge base can support literature evidence lookup; any quantitative retained-dose or clinical extrapolation remains blocked by upstream provenance and form/exposure limits. Detailed flags: stageB_dataset_source_audit.csv, stageB_duplicate_standardized_identities.csv and observation-link metadata fields.
