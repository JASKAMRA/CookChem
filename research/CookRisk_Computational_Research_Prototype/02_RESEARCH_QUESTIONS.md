# Research Questions and Existing Answers

## Central question

Can computational analysis and machine learning characterize cooking-associated changes in bioactive compound concentrations, and do the observed patterns generalize across unseen compounds and research sources?

## Questions and evidence status

| Research question | Existing evidence and result | Status | What remains unknown |
|---|---|---|---|
| RQ1. What concentration changes are reported for compatible raw/cooked analyte pairs? | Multiple ACR packages preserve source-linked raw/cooked values and calculate `100 × cooked/raw`; the 1,016-row reconstruction reports complete raw/cooked concentration fields. | REPORTED | A single owner-designated ACR snapshot is not established. Primary source values have not been independently re-extracted for this assembly. |
| RQ2. How do ACR observations vary across compounds, food matrices, methods, and sources? | Existing EDA and coverage tables/plots describe target distribution and source/compound/matrix/method composition. | REPORTED | Unbalanced, clustered observational data prevent causal method or compound-effect claims; subgroup support varies. |
| RQ3. Do molecular descriptors improve predictive performance? | Existing feature-set ablations exist, especially for the 379-row v0.6 ACR diagnostic and 439-row final prototype. Descriptor-only DOI-held-out performance is poor/negative in reported analyses. | REPORTED | Ablation is package- and snapshot-specific; no single confirmatory, owner-approved snapshot/split is selected. |
| RQ4. Does compound-grouped validation indicate generalization to unseen sources? | No. Compound folds can contain DOI overlap; source-held-out metrics are separately reported and often negative. | REPORTED | More source families with protocol-matched replication are needed to distinguish transfer from extrapolation. |
| RQ5. Is performance robust to source holdout? | The saved Batch021-labelled fixed ExtraTrees audit reports pooled R² −0.0678 molecular grouped and −0.0656 DOI-heldout; both are negative. Its historical input hash differs from the current Batch021 CSV, so current-snapshot attribution is BLOCKED/UNVERIFIED. The separate Batch021 seven-model source-LOSO table reports negative R² for each listed model. | REPORTED | DOI is a source-family proxy, not guaranteed lab independence; held-out sets differ between split strategies. |
| RQ6. Does ACR measure total compound mass retained after cooking? | No. ACR uses concentrations only. Existing packages explicitly state yield/mass/moisture/liquid information is insufficient for total-mass retention. | REPORTED | A mass-retention endpoint needs compatible raw/cooked food mass, yield, basis/moisture reconciliation, and liquid/edible-portion disposition. |
| RQ7. Are historical model results reproducible? | Prior Stage A audit records two clean Python 3.12.14 runs of the specific 1,124-row `Retention_Final` benchmark with byte-identical generated OOF/fold outputs; this is not evidence of ACR-package reproducibility. Historical outputs differ in predictions/metrics. | REPRODUCED for fresh-run repeatability; BLOCKED/UNVERIFIED for historical equivalence | Historical transitive dependency and run provenance were not retained; the separate Batch021 validation input is also unavailable at its recorded hash. |

## Hypothesis status

The existing evidence is exploratory and does not support a confirmatory hypothesis test. A future confirmatory hypothesis could ask whether a pre-specified feature block improves error on a pre-registered, independent source-held-out set. That experiment is **PROPOSED**, and requires an owner-designated dataset, locked source groups, independent compatible observations, and an analysis plan fixed before evaluation.

## Interpretation rules

1. Keep R², MAE, RMSE, sample count, group count, target, snapshot, and split together.
2. Negative R² means worse than a constant-mean predictor on the held-out observations; it does not mean “negative accuracy.”
3. Molecular grouping blocks same canonical identities across folds, but may leave source families overlapping. DOI holdout blocks DOI overlap but does not guarantee independent laboratories.
4. Feature importance is model attribution, not causation.
