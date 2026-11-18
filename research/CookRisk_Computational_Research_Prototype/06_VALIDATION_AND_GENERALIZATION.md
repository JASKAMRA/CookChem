# Validation and Generalization

## Validation designs that already exist

- **Random record split:** present as a diagnostic in the 439-row prototype and controlled comparisons. It allows correlated rows from a source on both sides and is not a source-generalization estimate.
- **Compound-grouped:** GroupKFold by canonical molecular identity. This tests held-out molecular identities, but DOI families may overlap.
- **Food-matrix-grouped:** evaluates held-out food groups where implemented; food/method/source support can be sparse.
- **Cooking-method grouped/LOSO:** present in selected recovery reports; normalized labels can be semantically heterogeneous and singleton folds make R² undefined.
- **DOI/source-held-out or LOSO:** tests held-out DOI family. DOI is a proxy for source family, not guaranteed lab independence; held-out groups may be out-of-domain relative to training.
- **Connected cross-source matched cells:** v0.9/v1.0 report six categorical cross-source overlaps but zero strict fully reported protocol-identical replications.

## Same recipe, altered grouping: saved ExtraTrees audit labelled Batch021

**Evidence status: REPORTED. Current-snapshot attribution: BLOCKED/UNVERIFIED.** The saved `validation_summary.json` records input SHA-256 `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`. The audit script identifies its input path as `stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv`, but the currently available file at that path hashes to `d866d0ffab8c335e0469f2815c3cdf518b3d019be1bdf2e37ba2ced2e7d5d3c1`. A scan of 779 Stage A working-tree files found no file with the recorded historical hash, and no local zip/tar archive was found. Stage A checksum/state documentation records the historical hash, but documentation is not the missing data bytes. Therefore the following are preserved reported results for the hash-identified historical input, not verified results on current Batch021 bytes.

The saved audit describes n=1,016; 48 canonical molecular identities; 32 DOI families; target `target_value_percent = 100 × cooked/raw`; ExtraTrees with 25 trees, `min_samples_leaf=2`, `max_features=0.8`, random state 42, one core; five GroupKFold folds and fold-local preprocessing. The saved design changes the grouping column. For ACR, MAE and RMSE below are **ACR percentage points**; R² is dimensionless.

| Design | Pooled OOF R² | MAE (ACR percentage points) | RMSE (ACR percentage points) | Mean fold R² ± SD | Group integrity | Evidence status |
|---|---:|---:|---:|---:|---|---|
| Molecular-grouped | −0.067833 | 102.391241 | 432.812778 | −0.256216 ± 0.305977 | 0 molecular overlap; 17–20 DOI overlaps | REPORTED; current-snapshot attribution BLOCKED/UNVERIFIED |
| DOI-held-out | −0.065645 | 114.218984 | 432.369224 | −0.206527 ± 0.193669 | 0 DOI overlap; 6–18 molecular overlaps | REPORTED; current-snapshot attribution BLOCKED/UNVERIFIED |

**Interpretation:** both saved pooled results are negative. The pooled R² difference is small (+0.0022 for source holdout), but the fold comparison is mixed (source better on two fold-number comparisons, molecular on three). This does not show a meaningful transfer advantage or prove that no chemical relationship exists. The plotted fold-wise values are not all negative: the molecular-grouped plot shows a positive fold. These historical results should not be presented as validated against the current Batch021 file.

## Other source-heldout results

- **REPORTED:** the Batch021 seven-model table reports negative source-LOSO R² for every listed model. Its manifest does not pin the dataset file hash; treat this as a saved result, not a reproduced or current-byte-verified analysis. See `stageA/dataset_expansion_1000/batch_021/post1000_model_comparison.csv`.
- **REPORTED; current-data attribution BLOCKED/UNVERIFIED:** all five saved 439-row prototype source results are negative (e.g. RF R² −.047508; XGB −.110401), but the manifest/current parent hash mismatch blocks verification against current data bytes. See `stageA/final_prototype_2026_11_10/model_comparison.csv` and `manifest.json`.
- **REPORTED:** verified 1,016-row reconstruction with fixed historical XGB has source pooled R² −.073710, mean fold R² −.253519. Reduced semantic feature set means this is not an exact historical-feature replay.
- **REPORTED:** strict 338 source-verified subset has extremely low molecular-fold mean R²; DOI overlap is present in every molecular fold.

## Reproducibility status

**REPRODUCED (prior documented run, not this assembly):** the Stage A reproduction audit reports the 1,124-row runner executed in two isolated Python 3.12.14 environments with byte-identical OOF predictions and fold assignments. Dataset hash, fold/group checks and metric recalculation were recorded.

**BLOCKED/UNVERIFIED:** stored historical predictions are not identical to current regenerated predictions although fold assignments match. The report notes 1,063/1,124 ExtraTrees predictions differ, and historical complete transitive dependencies/run provenance are unavailable. Do not assert exact historical reproducibility or choose the score that looks better.

## Conclusion

The existing evaluations justify a cautious statement: predictive patterns have been explored, but the saved source-heldout results do not demonstrate robust transfer to unseen DOI families. Independent, protocol-comparable experimental replication and a pre-specified validation set are required before stronger claims.
