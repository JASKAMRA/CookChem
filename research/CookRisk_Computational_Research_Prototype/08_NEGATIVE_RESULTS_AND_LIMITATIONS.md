# Negative Results, Limitations, and Unresolved Questions

## Negative and inconclusive results to retain

1. **REPORTED:** Stage A tuned XGBoost improved aggregate OOF RMSE/R² relative to the independent ExtraTrees reference but worsened MAE; the report retained ExtraTrees rather than claiming an overall winner.
2. **REPORTED:** the saved Batch021 post-1000 source-LOSO table has negative source-heldout R² across listed models; its current input snapshot is not hash-pinned.
3. **REPORTED; current-snapshot attribution BLOCKED/UNVERIFIED:** the fixed ExtraTrees audit reports negative pooled R² under molecular grouping and DOI holdout for historical input SHA-256 `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`. Current Batch021 bytes hash to `d866d0ffab8c335e0469f2815c3cdf518b3d019be1bdf2e37ba2ced2e7d5d3c1`; the historical input bytes were not found.
4. The strict 338-row source-verified subset produced mean fold molecular R² −2.462845 (SD 6.775628), and its report warns it is not comparable to the historical broad benchmark.
5. The 439-row final-prototype source metrics are negative, but saved outputs are not verified against current input bytes because of parent-hash mismatch.
6. Historical predictions differ from regenerated predictions even though fold membership matches; missing historical runtime provenance prevents resolution.
7. v0.9 and v1.0 report zero strict fully documented protocol-identical cross-source replications; v1.0 acquired no new observations and trained no model.
8. No verified inference package or accepted deployable model is established. Existing `.joblib` models are marked experimental/non-deployable.

## Scientific limitations

- Source, compound, food, preparation, analytical method, basis, and study are clustered rather than crossed in a balanced design.
- DOI is only a proxy for research source; it does not ensure independent laboratories or identical protocols.
- Missing temperature/time and method-detail fields reduce transferability; e.g., final ACR EDA reports temperature absent in 578/1,016 and duration absent in 206/1,016.
- Some measurement bases and matrices vary. No silent conversion should be made.
- ACR can exceed 100%; it cannot establish total-mass retention without yield/mass and compatible basis.
- Observational stratifications cannot isolate causal effects of cooking methods or molecular structures.
- Feature importance is not mechanism evidence or causality.
- No clinical, nutritional, bioavailability, human exposure, health risk, or consumer-cooking inference is supported.

## Reproducibility and snapshot limitations

- The 1,124-row benchmark’s fresh-run reproducibility is documented, but its stored historical run differs in prediction values; original transitive dependencies/configuration are incomplete.
- The 439-row final-prototype manifest/current-file hash mismatch blocks exact association of stored model results with current bytes.
- Batch021 and verified reconstruction both have 1,016 rows but different identity counts, target/recovery representations, and artifact hashes. They must remain distinct.
- Some version manifests do not pin the dataset file hash. Presence of scripts, model outputs, or OOF files does not prove that the current data file matches the original run.

## Current claim boundary

**Supported:** “The project has assembled multiple source-linked ACR research datasets and performed exploratory/grouped ML comparisons. Existing DOI-heldout results do not show robust cross-source predictive transfer.”

**Not supported:** “The model predicts cooking retention accurately,” “the model generalizes to new labs,” “a feature causes concentration change,” “ACR is total retention,” or any clinical/nutritional utility claim.

## Blocked versus proposed

- **BLOCKED/UNVERIFIED:** owner designation of a canonical ACR dataset; historical prediction discrepancy; final prototype hash linkage; independent protocol-identical evidence; model deployment/inference package; external scientific approval.
- **PROPOSED:** secure independent matched studies, pre-register a source-heldout confirmatory test, reconcile snapshot manifests, and develop a measured mass-retention endpoint only if compatible yield/mass data are acquired.
