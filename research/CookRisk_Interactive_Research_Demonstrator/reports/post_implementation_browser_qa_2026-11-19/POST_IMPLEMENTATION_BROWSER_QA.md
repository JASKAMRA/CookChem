# CookRisk Post-Implementation Browser QA

**Date:** 2026-11-19  
**Result:** BLOCKED — the demonstrator was not running, and the instructions prohibit starting it for this QA.

## Availability check

- Checked local listening ports **8501** (the documented Streamlit port) and **8502** (the temporary verification port used in the prior implementation turn). Neither had a listening process.
- The available browser inventory had no CookRisk local-app tab. Chrome had two ChatGPT tabs; the in-app browser had no tabs.
- No application URL was loaded or requested. The Streamlit server was not started, stopped, reconfigured, or otherwise changed during this QA.

## Module results

| Module | Status | Result |
| --- | --- | --- |
| Research Overview | BLOCKED | Could not open without a running app. |
| Evidence Explorer | BLOCKED | Reconstruction identity, table, and filters not browser-tested. |
| ACR Distributions | BLOCKED | Charts, summaries, stored-target behavior, and filters not browser-tested. |
| Cooking & Compound Patterns | BLOCKED | Group selector, minimum-support control, empty-result case, summaries, and noncausal labels not browser-tested. |
| Existing ML Results | BLOCKED | Batch021 result rendering, default selection, provenance labels, and family/target/design controls not browser-tested. |
| Validation & Generalization | BLOCKED | Saved summary, fold chart, dataset/target/split labels, and pooled-versus-mean-fold distinction not browser-tested. |
| Scientific Limitations | BLOCKED | Limitation expanders and historical `Retention_Final` wording not browser-tested. |
| Reproducibility & Evidence | BLOCKED | Registry, snapshot table, target scope, and provenance display not browser-tested. |

## Interaction and rendering checks

No module navigation or page interactions were possible. In particular, the following remain untested:

- Reconstruction dataset ID, full hash, row count, and limited approval status in each live section.
- Food matrix, compound, cooking method, and DOI/source filters, including blank values and zero-result combinations.
- ACR distributions and evidence tables, including whether all source observations remain represented.
- Cooking group selector and minimum-observation slider, including groups below threshold and empty results.
- Batch021 historical metrics and validation evidence remaining separate from live Reconstruction exploration.
- Target labels, historical `Retention_Final` separation, pooled out-of-fold R² versus mean-fold R², and source-generalization caveats.
- Navigation recovery, page-level exceptions, Streamlit tracebacks, browser console errors, and failed network requests.

**Errors, screenshots, and logs:** none captured. No application page was available to produce them. This does not establish that the modules are error-free.

## Usability and preservation

- Whether the app remains usable after navigating between modules: **NOT VERIFIED**.
- All eight modules: **BLOCKED**, not passed or failed.
- No application, registry, dataset, prediction, model artifact, dependency, lock file, or existing report was modified. No Git operation was performed.
- No Stage B or restricted Stage C/D material was accessed. `research/EXISTING_RESULTS_METRICS_CATALOG.csv` was not inspected or hashed.

## Next step

Repeat this read-only QA when the demonstrator is already running at its local URL. This task intentionally left the server stopped rather than changing the environment.
