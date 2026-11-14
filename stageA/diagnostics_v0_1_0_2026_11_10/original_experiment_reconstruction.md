# Original experiment reconstruction

## Verdict: NOT REPRODUCIBLE AND SCIENTIFICALLY NOT COMPARABLE

Repository searches found no serialized Stage A model, fold assignments, run manifest, preprocessing state, or output carrying the claimed `R²≈0.4861`, `RMSE≈41.37`, and `MAE≈20.77` combination. The current tracked Stage A benchmark uses `log1p(Retention_Final)`, grouped folds by `Canonical_Molecular_ID`, and reports different pooled OOF results. The Stage B manifest describes a separate artifact with a Yeo–Johnson target transform and fold-mean R² 0.390691. These cannot establish the claimed 0.4861 run.

The historical 1,124-row target is `Retention_Final`; it is not scientifically interchangeable with the source-verified apparent-ratio target used by v0.2/v0.3.
