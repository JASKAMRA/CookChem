# Reproducibility

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

QC: outputs/stageB_qc_results.json and reports/stageB_quality_control.md. Inputs hash-checked; original OOF retained; individual observation pointers exact. 33 manually extracted records; source snapshots support audit. This is single-reviewer targeted evidence mapping, not a systematic review, clinical validation, independent double extraction or perfect/exhaustive database.


## Upstream data-source audit (material limitation)
Crossref metadata was retrieved for 208 dataset DOIs: 145 have author and/or year metadata discrepancies; 10 could not be retrieved. These are source-verification flags, not automatic proof that every associated measurement is fabricated. Metadata-concordant citations still do not verify measurements.

A confirmed example is DOI 10.1016/j.lwt.2021.111500, assigned to five avocado/Persin cooking rows. The publisher identifies a 2021 Liu et al. fish-oil/gelatin encapsulation paper, rather than the recorded 2022 Molina et al. Persin study. [Publisher source](https://www.sciencedirect.com/science/article/abs/pii/S0023643821006538). This mismatch blocks scientific validation of those food-retention claims. It does not invalidate independently verified Stage B interaction publications.

Additionally, 115 selected OOF records have FALSE in the current master Final_Preprocessing_Eligible flag despite matching molecular IDs and actual target values. The supplied Stage A report describes a frozen 1,124-row experiment, while the current master flags only 1,009 eligible rows. Without the locked Stage A runner/input snapshot, eligibility lineage cannot be reconciled. Original outputs are preserved and no re-training or retrospective repair was attempted.

One standardized-CID cluster (5282102) spans two original groups, Kaempferol-3-Glucoside and Astragalin. Groups remain separate. This is not proof of leakage: their stereochemical representations differ in completeness; cross-fold identity duplication needs a separate Stage A audit.

Therefore food associations and OOF outputs are traceable inherited project data, not newly certified experimental evidence. The knowledge base can support literature evidence lookup; any quantitative retained-dose or clinical extrapolation remains blocked by upstream provenance and form/exposure limits. Detailed flags: stageB_dataset_source_audit.csv, stageB_duplicate_standardized_identities.csv and observation-link metadata fields.


Standardized-name follow-up: 102 mapped groups additionally queried by verified PubChem title with broader drug/PK/PD/absorption/metabolism/transporter concepts and a 2026-10-06 publication cutoff. Exact queries and retrieval status: stageB_standardized_search_log.csv. Candidate coverage remains limited to 25 and is not exhaustive manual screening.
