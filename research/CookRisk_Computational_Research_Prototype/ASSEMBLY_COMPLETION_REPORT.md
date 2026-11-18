# Assembly Completion Report — CookRisk Computational Research Prototype

**Status:** assembled from existing evidence; not a new experiment or software product.  
**Date:** 18 November 2026.

## Deliverables created

Created the requested 11-chapter academic research narrative plus three appendices, two curated data tables, and a curated six-figure package. All files are additive under `research/CookRisk_Computational_Research_Prototype/`. Existing source reports, datasets, metrics, figures, and model artifacts were preserved.

## Existing results used

- 1,124-row historical Stage A `Retention_Final` benchmark and its saved model comparison, fold/OOF outputs, reproduction audit, and historical discrepancy report.
- Versioned ACR recovery and source-admission results, including v0.2–v1.0 reports and the 1,016-row Batch021 and verified reconstruction packages.
- Saved EDA, grouped/source-heldout validation, model comparison, ablation, importance, error/OOF, and integrity artifacts.
- Existing project research plan, overall evidence map, results inventory, metric catalog, figure catalog, gap report, and professor shortlist.

Result status is labeled in the curated narrative tables and figure catalog, using REPORTED, REPRODUCED only where a prior dated report supports it, PROPOSED, or BLOCKED/UNVERIFIED. This is not a claim that every underlying result in the repository has been re-audited. The narrative distinguishes ACR, total-mass retention, cooked concentration, and `Retention_Final`.

## Figures selected

Six existing Stage A figures were copied byte-for-byte into `figures/` for convenient professor review: ACR target distribution, source coverage, molecular-vs-DOI validation, source overlap in molecular folds, foldwise RMSE, and experimental-field missingness. Figure 2 shows the top 15 of 32 DOI families. Figure 3 is fold-wise R² and includes one positive molecular-grouped fold; separately reported pooled R² values are negative for both designs. The audit behind Figures 3–5 records input SHA-256 `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`, which differs from current Batch021 bytes `d866d0ffab8c335e0469f2815c3cdf518b3d019be1bdf2e37ba2ced2e7d5d3c1`; current-snapshot attribution is BLOCKED/UNVERIFIED. `figures/FIGURE_SELECTION.csv` records exact original paths, dataset/target context, interpretation/limitation, source report, and copy SHA-256. Original figures were not modified; no plot was regenerated.

## Main evidence-based conclusion

Existing source-linked ACR datasets and computational comparisons support a research prototype and a methodological finding: reported compound-grouped results do not establish generalization to unseen research sources. The saved Batch021 ExtraTrees audit reports molecular-grouped and DOI-heldout pooled R² of −0.0678 and −0.0656, respectively, for the historical input recorded as SHA-256 `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`. The exact input bytes were not found; current Batch021 bytes hash to `d866d0ffab8c335e0469f2815c3cdf518b3d019be1bdf2e37ba2ced2e7d5d3c1`, so attribution to the current file is BLOCKED/UNVERIFIED. Other source-heldout ACR evaluations are also negative or weak. These findings do not prove absence of chemical signal and do not support a deployable cooking predictor.

## Claims remaining unverified or blocked

- No canonical ACR snapshot is owner-designated. The 439-row package has a recorded manifest/current-data hash mismatch.
- Batch021 and verified reconstruction are separate 1,016-row datasets; equal row counts do not make them identical.
- Historical benchmark fresh-run repeatability is documented, but its regenerated predictions differ from saved historical predictions; the historical full environment/provenance is missing.
- Strict protocol-identical cross-source replication is reported as zero.
- Existing experimental `.joblib` models are not verified deployable artifacts; no accepted general model or new-record inference claim is made.
- Total-mass retention, bioavailability, exposure, clinical risk, and cooking advice are not established.
- Stage B was not accessed; restricted Stage C/D sources were not reopened, and no fresh claims about those stages are made.

## Work required before new experiments

1. Owner/scientific lead designates and hash-locks one ACR snapshot and approves its target/inclusion contract.
2. Resolve or explicitly bound the 439-row hash mismatch and any missing dataset hashes.
3. Ensure the approved compatible environment/lock for the selected research package is available.
4. Acquire independent primary-source observations that replicate compound–matrix–method–basis cells across sources.
5. Pre-specify the source-heldout case set, features, primary metrics, and analysis before confirmatory evaluation.
6. Keep mass-retention questions blocked until compatible food mass/yield, basis/moisture, and liquid/portion data are measured.

No experiments or tests were run during assembly, in accordance with the task. No scientific data or historical outputs were modified.
