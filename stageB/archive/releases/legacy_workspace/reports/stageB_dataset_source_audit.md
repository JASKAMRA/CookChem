# Dataset source audit



## Upstream data-source audit (material limitation)
Crossref metadata was retrieved for 208 dataset DOIs: 145 have author and/or year metadata discrepancies; 10 could not be retrieved. These are source-verification flags, not automatic proof that every associated measurement is fabricated. Metadata-concordant citations still do not verify measurements.

A confirmed example is DOI 10.1016/j.lwt.2021.111500, assigned to five avocado/Persin cooking rows. The publisher identifies a 2021 Liu et al. fish-oil/gelatin encapsulation paper, rather than the recorded 2022 Molina et al. Persin study. [Publisher source](https://www.sciencedirect.com/science/article/abs/pii/S0023643821006538). This mismatch blocks scientific validation of those food-retention claims. It does not invalidate independently verified Stage B interaction publications.

Additionally, 115 selected OOF records have FALSE in the current master Final_Preprocessing_Eligible flag despite matching molecular IDs and actual target values. The supplied Stage A report describes a frozen 1,124-row experiment, while the current master flags only 1,009 eligible rows. Without the locked Stage A runner/input snapshot, eligibility lineage cannot be reconciled. Original outputs are preserved and no re-training or retrospective repair was attempted.

One standardized-CID cluster (5282102) spans two original groups, Kaempferol-3-Glucoside and Astragalin. Groups remain separate. This is not proof of leakage: their stereochemical representations differ in completeness; cross-fold identity duplication needs a separate Stage A audit.

Therefore food associations and OOF outputs are traceable inherited project data, not newly certified experimental evidence. The knowledge base can support literature evidence lookup; any quantitative retained-dose or clinical extrapolation remains blocked by upstream provenance and form/exposure limits. Detailed flags: stageB_dataset_source_audit.csv, stageB_duplicate_standardized_identities.csv and observation-link metadata fields.


Method: exact DOI lookup via Crossref. Compare supplied years to publication/issued dates and supplied author strings to retrieved author-family names. Author matches use a conservative ASCII-normalized surname substring; this is a screening heuristic requiring manual review, not source-measurement verification. Preserve each raw response. Source measurements and claimed food-compound relationships are not repaired. DOI retrieval failure is not evidence of a nonexistent DOI. The publisher mismatch above was additionally verified manually.
