# Molecular-grouped versus source-held-out validation audit

## Recovered historical implementation
- `batch_021/run_one_post1000_model.py` uses `GroupKFold(n_splits=5)` for `compound_grouped_5fold`, grouping with `canonical_molecular_id`; molecular groups cannot overlap within a fold. It uses `LeaveOneGroupOut` grouped by `doi` for its previous source test. That resource-bounded runner uses 10-tree Extra Trees and omits raw concentration and measurement basis.
- `final_prototype/run_final_prototype.py` also uses canonical molecular IDs for compound grouping; source holdout there is DOI-based. Its full feature recipe includes raw concentration and measurement basis, with 25-tree Extra Trees. This new audit adopts that full, fixed recipe for both strategies.
- Neither historical implementation uses a source ID as a predictive feature. Molecular grouping does not, however, guarantee that DOI families are separated.

## New controlled design
- Dataset: Batch-021 master, 1,016 rows; 48 canonical molecular groups; 32 DOI groups. Target is the stored `target_value_percent`, verified against its documented equation within the historical 0.01 percentage-point rounding tolerance.
- Identical pipeline in both strategies: raw concentration, temperature, time, eight RDKit descriptors; cooking method, medium, measurement basis, compound class and food matrix; fold-local median imputation + scaling for numeric fields and most-frequent imputation + one-hot encoding for categoricals.
- Fixed model: Extra Trees, 25 trees, `min_samples_leaf=2`, `max_features=0.8`, seed 42, one core. No tuning was performed.
- Both strategies use five-fold `GroupKFold`; only the grouping column changes: canonical molecular ID versus DOI.

## Summary

| strategy | n | molecular groups | source groups | pooled OOF R² | pooled MAE | pooled RMSE | mean fold R² ± SD |
|---|---:|---:|---:|---:|---:|---:|---:|
| molecular_grouped | 1016 | 48 | 32 | -0.0678 | 102.3912 | 432.8128 | -0.2562 ± 0.3060 |
| source_held_out | 1016 | 48 | 32 | -0.0656 | 114.2190 | 432.3692 | -0.2065 ± 0.1937 |

## Split audit
- Molecular-grouped folds have zero molecular-ID overlap by assertion and 17–20 overlapping DOI groups. DOI overlap is therefore substantial, not an assumption.
- Source-held-out folds have zero DOI overlap by assertion. Molecular overlap is measured and ranges from 6 to 18 groups because the same compounds appear in multiple DOI families.
- Preprocessing is constructed and fit separately inside every fold training partition.

## Scientific interpretation
- Molecular-grouped CV estimates transfer to a held-out molecular identity while retaining familiar study/source conditions through other compounds from the same DOI.
- In this fixed audit, pooled source-held-out R² is -0.0656 versus -0.0678 molecular-grouped (difference +0.0022). Source-held-out is better in 2 fold-number comparisons and molecular-grouped is better in 3. Thus the performance difference is small and not consistent across these non-identical grouped partitions.
- Both estimates are negative and neither demonstrates transferable predictive performance. This does not prove experimental heterogeneity is the cause, or that no chemical relationship exists; it establishes that this fixed model does not show robust generalisation under either held-out construction.
- R² is a goodness-of-fit metric, not accuracy. Negative R² means performance worse than a constant-mean baseline on that held-out set; it does not mean negative accuracy.
- No deployment or Stage C integration is warranted from these results.

## Limitations and recommendation
- DOI is used as the available source-family identifier; it is not a guarantee that all related studies are independent. Results should be read as DOI-held-out, not a broader causal claim about laboratory independence.
- The data retain heterogeneous measurement bases as an explicit feature, without conversion. Future evidence should prioritize pre-specified, cross-source replicated protocol cells before considering source-general prediction.
