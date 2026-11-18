# Updated Research Readiness Assessment

## Verdict: Requires substantial revision

The package is clearer and more academically cautious after the documentation corrections, but a central validation result still cannot be tied to the currently available Batch021 CSV. This prevents an unqualified presentation of that comparison as verified on the named current dataset. The saved result may be shown only as a reported historical audit with the limitation stated beside it.

## What is now presented more accurately

- The Batch021 audit's historical input hash and the current CSV hash are both explicit. Their mismatch and the unavailable historical bytes are labeled **BLOCKED/UNVERIFIED**; saved metrics were not recalculated or replaced.
- Figure 2 is described as the top 15 of 32 DOI families.
- Figure 3 is described as fold-wise R², including one positive molecular-grouped fold. Its pooled molecular and DOI-held-out R² values are separately shown as negative historical results.
- Curated numerical tables distinguish `REPORTED` from `REPRODUCED` and mark current-snapshot attribution blocked where appropriate.
- ACR MAE/RMSE are identified as ACR percentage points. Historical `Retention_Final` remains a separate target with unresolved original units.
- “Five model evaluations” is used instead of wording that implies five fitted models were saved.
- Reproducibility is limited to the prior documented two-run check of the specific 1,124-row `Retention_Final` benchmark; it is not generalized to ACR packages or the whole project.

## Remaining readiness gaps

1. Recover the exact historical Batch021 audit input matching SHA-256 `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`, and establish its authoritative provenance. If unavailable, retain the audit as a historical result with unresolved current-dataset attribution.
2. Keep the 439-row prototype metrics separate and blocked from current-byte attribution until its parent-hash discrepancy is resolved.
3. Obtain an owner-designated canonical ACR snapshot and target/inclusion contract before describing one package as the definitive research dataset.
4. Preserve the unresolved historical `Retention_Final` target-unit semantics and historical prediction mismatch; do not imply exact historical equivalence.
5. Treat all ACR model outputs as saved reported results unless an existing prior reproduction record explicitly covers that exact package. No experimental validation occurred in this correction cycle.

## Suitable use now

This corrected package can be used for a cautious internal discussion of the project, its evidence architecture, exploratory analyses, and known limitations. For an initial professor review, present the Batch021 comparison only as **reported historical evidence, current-snapshot attribution blocked**, and lead with the limitations rather than treating it as a verified result on the current file. The package is not ready to support a confirmatory conclusion, external-validation claim, deployable predictor, or broad reproducibility claim.

## Review scope and preservation

This was a documentation and provenance correction, not experimental validation. No model training, experiment rerun, scientific validation test, dependency installation, dataset recalculation, or plot generation was performed. Stage B and restricted Stage C/D sources were not accessed. Scientific datasets, model artifacts, stored metric values, historical outputs, and figure image bytes were preserved.
