# Existing Results — Gaps, Limitations, and Unresolved Work

**Status:** extraction of existing documented evidence only; no experiment was rerun.

## Scientific endpoint and comparability

- `Retention_Final` (historical 1,124-row task) has unresolved original equation semantics. Do not call its metric ACR or total-mass retention.
- ACR is the explicitly defined concentration quotient `100 × C_cooked / C_raw`; it is not analyte mass retained. ACR above 100% is present in the source-reported distribution and is not intrinsically invalid.
- Cooked concentration prediction is a separate endpoint and the controlled package notes heterogeneous units/bases. Its metrics cannot be used as ACR performance.
- Versioned ACR datasets are not interchangeable. 338/374/379/439/948/989/1,016 row figures describe different evidence filters or snapshots. Two 1,016-row files differ in canonical identity counts (51 labels/48 IDs vs 48 identities in reconstruction) and have distinct paths/hashes; equal row and DOI counts do not establish same observations.
- The final prototype's current source bytes were reported to differ from its manifest parent hash. Do not attribute its stored model/ablation results to the current bytes until the provenance mismatch is reconciled.
- Batch021 manifest does not provide a dataset SHA; the verified reconstruction manifest also lacks a hash matching its current data artifact per existing inventory. Hash-linked releases are a reproducibility gap.

## Validation and model limitations

- DOI is used as a source-family proxy; it does not guarantee independent laboratories or protocols.
- Compound-grouped CV can retain DOI overlap; source-held-out CV can retain compounds across sources. The saved overlap audits document this rather than assuming one split solves all leakage.
- Source-held-out R² is negative in the 439-row prototype and every model in the Batch021 package. The controlled ExtraTrees audit reports both molecular-grouped and source-heldout pooled R² < 0. This supports “no demonstrated generalization under these evaluations,” not “no chemical signal exists.”
- Strict qualified 338-row subset reports mean molecular fold R² −2.462845. The small set and changed inclusion/provenance make comparison with older broad results invalid.
- Extreme target values materially influence RMSE/R²; the sensitivity analysis removes highest 1% only as a diagnostic, not a reason to exclude those values from the primary result.
- Results are mostly existing reported outputs. Only the Stage A historical benchmark rerun/repeatability is identified as prior reproduction in the closure record. This task did not independently recalculate or rerun any result.
- No reported source-held-out result currently supports deployment. Four serialized experimental models are marked non-deployable; final prototype saved_model=false. OOF values are validation predictions, not inference for new cases.

## Evidence acquisition and target harmonization gaps

- v0.5 report: a phenolic dataset was excluded because fresh/dry basis was not specified; another candidate remained pending because primary table/method access was not obtained. Search-snippet values were explicitly not used.
- v0.7 report distinguishes an article's separately reported true-retention statistic from concentration-pair ACR and says no FW-to-DW conversion was applied.
- Total-mass retention still needs compatible raw/cooked food mass or yield, moisture/basis reconciliation, and handling of cooking liquid/edible portion. No such conversion should be inferred from concentration ratio alone.
- v1.0 reports zero strict protocol matches and no new observations; source/matrix overlap remains the central experimental evidence gap.
- The 989 arithmetic audit preserves 651 records with missing metadata/ambiguity/source conflict, plus 81 discrepant and 54 non-comparable records; arithmetic agreement alone is not accepted as provenance verification.

## Reproducibility and governance gaps

- Historical benchmark dependency lock/provenance was not recorded for the original run. The current lock supports a fresh reproducible run, but the stored-vs-regenerated prediction difference remains unresolved.
- Main Stage A prior reproduction passed two clean runs with byte-identical generated outputs; that fact is inherited from its dated audit, not rerun today. Linux/Windows execution and some inference readiness remain unverified in those reports.
- RF-01–RF-15 are recorded as pending human decisions in the Stage A closure record. Engineering results do not imply scientific-owner approval.
- Several package reports contain scripts/locks; current environment compatibility and package completeness vary. This extraction did not install dependencies or test the scripts.
- Stage B was not accessed. Stage C/D sources remain restricted in this extraction; any assertions in the earlier research evidence map about them are secondary and not freshly validated. Do not treat this report as a full-stage C/D audit.

## Negative, failed, inconclusive, or blocked results preserved

1. Tuned XGBoost does not improve MAE with its RMSE/R² gain vs the independent ExtraTrees OOF benchmark; project retains ExtraTrees.
2. Source-held-out ACR scores are negative or near zero in multiple packages; no demonstrated generalization.
3. Source-verified 338 subset scores poorly under molecular folds; not directly comparable to historical benchmark.
4. Final-prototype parent hash mismatch blocks association of results to current bytes.
5. Historical predictions differ despite matching folds; missing historical environment prevents causal diagnosis.
6. v1.0 candidate acquisition found no strict protocol matches and trained no model.
7. Independent cross-source replication cells are reported as zero in Batch021.
8. Four experimental joblib artifacts remain non-deployable; no verified inference package.

## Work labelled PROPOSED (not results)

- Obtain independent studies that replicate compound–food-matrix–method cells across DOI/lab families.
- Predefine source-heldout or external confirmatory protocol and analysis plan before seeing outcomes.
- Resolve target/basis/yield compatibility for any true mass-retention endpoint.
- Reconcile mismatched/omitted dataset hashes and tie output bundles to immutable exact-byte snapshots.
- Resolve historical pipeline provenance if original environment/artifacts can be recovered.
- Request and complete RF-01–RF-15 decisions with named authority and evidence.
- Evaluate future feature-ablation/uncertainty and subgroup analyses without interpreting feature importance causally.

All proposed items above are recommendations recorded as future work, not completed results.
