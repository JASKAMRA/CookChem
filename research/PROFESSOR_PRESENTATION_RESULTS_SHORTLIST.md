# Professor Presentation — Existing Results Shortlist

**Purpose:** a concise set of existing findings that is strongest, honest, and scientifically meaningful for an academic discussion. These are reported repository results, not fresh experiments. Show each result with its dataset and endpoint printed on the same slide.

## 1. The endpoint distinction is a core methodological result

**Finding:** the historical 1,124-row Stage A benchmark uses `Retention_Final`, whose original equation remains unresolved. Later source-verified datasets use ACR `100 × C_cooked / C_raw`; ACR is concentration change, not total-mass retention.  
**Evidence:** `stageA/stageA_reproducibility.md`; `stageA/recovery_v0_2_0_2026_11_10/target_definition_contract.md`; `stageA/verified_concentration_ratio_reconstruction/final_dataset_eda_report.md`.  
**Why include it:** prevents a misleading “retention” interpretation and demonstrates target discipline.  
**Slide label:** “Two endpoints, two datasets — do not compare their scores as one leaderboard.”

## 2. Source-held-out performance does not support generalization

**Finding:** on a fixed 1,016-row ACR master, the saved ExtraTrees audit reports molecular-grouped pooled R² −0.0678 and DOI-heldout pooled R² −0.0656; DOI holdout has zero source overlap by design. Both are negative.  
**Evidence:** `stageA/molecular_vs_source_validation_audit/validation_comparison_report.md`, `validation_summary.json`, `validation_summary_rows.csv`; figure `stageA/molecular_vs_source_validation_audit/molecular_vs_source_r2.png`.  
**Why include it:** the same fixed pipeline contrasts group definitions and reveals that neither split shows acceptable predictive transfer.  
**Caveat:** molecular and DOI folds are not identical test sets; DOI is only a proxy for independent source family; negative R² is not negative “accuracy.”

## 3. ACR values above 100% are common in the source-backed dataset

**Finding:** verified reconstruction reports 346/1,016 ACR observations above 100%; mean 156.661%, median 88.377%, maximum 6,536.364%.  
**Evidence:** `stageA/verified_concentration_ratio_reconstruction/final_dataset_eda_report.md`; plots `stageA/verified_concentration_ratio_reconstruction/eda_plots/target_distribution.png` and `stageA/final_dataset_historical_model_and_eda_audit/eda_plots/target_histogram.png`.  
**Why include it:** makes the endpoint and extreme tail visible, motivating robust error analysis and care around denominator/basis/matrix changes.  
**Caveat:** values are retained for source review; do not call them mass-retention percentages or “improvements.”

## 4. Existing model comparisons do not yield a deployment model

**Finding:** Batch021 reports 7 model families under compound-grouped, food-matrix-grouped, and source-LOSO designs. Source-LOSO R² is negative for all models; controlled ExtraTrees audit reports source R² −0.0656. Strict protocol-identical source replication cells are reported as 0.  
**Evidence:** `stageA/dataset_expansion_1000/batch_021/post1000_model_comparison.csv`; `post1000_validation_summary.json`; `molecular_vs_source_validation_audit/validation_comparison_report.md`; `batch_021/dataset_expansion_report.md`.  
**Why include it:** honest negative evidence is more valuable than highlighting random split performance.  
**Caveat:** batch package and verified reconstruction are not assumed byte-identical; state the dataset used on the slide.

## 5. Source/protocol proxy warning from ablation and importance

**Finding:** in v0.6, full ACR model source-LOSO R² is −0.0416; removing microwave medium drops it to −0.6461, and full-fit one-hot `cooking_medium_Microwave` importance is 0.6984. Molecular-descriptor-only source R² is −0.4171.  
**Evidence:** `stageA/recovery_v0_6_0_2026_11_10/feature_ablation_comparison.csv`, `full_fit_feature_importance.csv`, `source_confounding_report.md`.  
**Why include it:** demonstrates that a prominent feature can be a source/protocol proxy; it motivates independent matched experiments.  
**Caveat:** feature importance and ablation are model-specific, associational and not causal.

## 6. Stage A historical model reproduction is repeatable but not historically reconciled

**Finding:** prior audit records two clean Python 3.12.14 runs with byte-identical generated folds/OOF outputs, while regenerated predictions differ from stored historical values; historical package-level provenance is missing.  
**Evidence:** `stageA/STAGE_A_REPRODUCTION_AUDIT_2026-11-04.md`; `stageA/STAGE_A_CLOSURE_AND_TRANSITION_2026-11-04.md`.  
**Why include it:** showcases reproducibility practice and transparent handling of a discrepancy.  
**Caveat:** it is a prior reproduction documented in reports, not rerun for this inventory, and the discrepancy remains unresolved.

## 7. Evidence qualification materially changes what can be claimed

**Finding:** of 989 arithmetic-matching candidates, 338 are reported source-and-arithmetic verified; 651 were not retained due to metadata gaps/ambiguity/conflict. The strict 338 subset's fixed historical-XGBoost molecular-CV mean fold R² is −2.4628 (SD 6.7756).  
**Evidence:** `stageA/989_observation_recovery_audit/989_recovery_audit_report.md`; `recovery_and_exclusion_summary.csv`; `source_overlap_audit.csv`.  
**Why include it:** shows why exact numerical agreement is not enough without source identity and evidence.  
**Caveat:** this restricted subset is not directly comparable with the broad historical score.

## Recommended slide order

1. Research question and endpoint definitions.
2. Dataset lineage / evidence tiers (117 → 338 → 374 → 379 → 439 and separate 1,016-row families; do not imply all are one monotonically verified dataset unless individual lineage is shown).
3. ACR distribution and coverage.
4. Same-snapshot molecular versus DOI-heldout comparison.
5. Ablation/source-proxy finding.
6. Negative conclusion, limitations, and next independent evidence needed.
7. Reproducibility discrepancy and governance status as a short transparency slide or appendix.

## Claims to avoid

- “Model predicts retention accurately” without naming target/snapshot/split.
- “R² 0.4 on unseen sources” — the historical ~0.4 is mean molecular-fold R², not a source-heldout score.
- “346 compounds increased during cooking” — 346 is observation count >100% ACR, not compound count.
- “Microwave causes retention” from feature importance.
- “The 1,016-row datasets are identical.”
- “True retention”, bioavailability, exposure, or clinical risk from ACR.
- “Independently validated/deployable.”
