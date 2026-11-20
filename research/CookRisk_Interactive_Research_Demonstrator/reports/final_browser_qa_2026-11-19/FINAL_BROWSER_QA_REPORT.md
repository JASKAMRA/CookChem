# CookRisk Final Browser QA Report

**Date:** 2026-11-19  
**Overall result:** **BLOCKED — partial browser smoke check completed; full module QA could not proceed.**

## Summary

The existing demonstrator environment was available (`.audit-venv-20261119`, Python 3.14.7, Streamlit 1.67.0, Plotly 7.1.0). Starting on the documented port 8501 failed with Streamlit's exact message `Port 8501 is not available`. A listener/process check found no TCP listener or owning process on 8501, so the conflict source could not be identified. Port 8502 was checked as free, used for this QA, and the app started there.

The Research Overview rendered in the in-app browser and showed its heading, navigation, research description, ACR equation, and scientific boundary text. No other module was opened or tested. When I attempted to proceed with Windows browser control, the computer-use bridge stopped the session with: `Computer Use has been stopped for this turn because it could not determine the current browser URL on Windows with enough confidence to enforce policy. Stop your work and send a final message noting why Computer Use ended.` I stopped further browser interactions as directed.

## Startup and shutdown

- **Initial documented command:** `python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false`
- **8501 result:** startup failed with `Port 8501 is not available`; no listener/owning process was visible in the subsequent port check. The underlying reason is **unverified**.
- **Safe alternate port:** 8502 was verified free before launch.
- **Started command:** `.audit-venv-20261119/Scripts/python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502 --server.headless true --browser.gatherUsageStats false`
- **Startup result:** Streamlit reported `Uvicorn server started on 127.0.0.1:8502` and printed `http://127.0.0.1:8502`; the browser rendered the Research Overview.
- **Shutdown:** sent Ctrl+C to the session started for QA. It exited. A final check found no listener on 8501 or 8502.
- **Direct HTTP status:** no separate health/root HTTP status was recorded in this QA. Browser rendering is the observed page-load evidence.

## Module results

| Module | Rendering result | Controls/interactions tested | Errors observed | Fixes | Regression result |
| --- | --- | --- | --- | --- | --- |
| Research Overview | **PARTIAL** — initial page rendered with content and navigation visible | No navigation control activated | No page exception observed in the rendered accessibility content; console not checked | None | Only the initial render was observed; this is not a module PASS |
| Evidence Explorer | **BLOCKED** — not opened | None | Not observable | None | Not run |
| ACR Distributions | **BLOCKED** — not opened | None | Not observable | None | Not run |
| Cooking & Compound Patterns | **BLOCKED** — not opened | None | Not observable | None | Not run |
| Existing ML Results | **BLOCKED** — not opened | None | Not observable | None | Not run |
| Validation & Generalization | **BLOCKED** — not opened | None | Not observable | None | Not run |
| Scientific Limitations | **BLOCKED** — not opened | None | Not observable | None | Not run |
| Reproducibility & Evidence | **BLOCKED** — not opened | None | Not observable | None | Not run |

## Required controls and scientific checks

The following checks were **not performed**, because the browser automation safeguard stopped interaction after the initial page render:

- Evidence Explorer's Reconstruction ID, full hash, row/column count, limited approval text, table consistency, and filters for food matrix, compound, cooking method, DOI/source, blanks, and zero-result combinations.
- ACR chart/summary behavior, stored-target consistency, filter combinations, missing observations, and confirmation that source records remain represented.
- Cooking group selection and support threshold at low/high settings, empty results, filter consistency, and noncausal summary labels.
- Batch021 result family/default, full dataset identity, family/target/design selectors, historical provenance and saved metric display.
- Validation summary, fold chart, target and split labels, pooled out-of-fold versus mean-fold R² distinction, and source-generalization limitations.
- Scientific Limitations expanders and Reproducibility & Evidence registry/snapshot display.
- Navigation across all eight modules, return navigation, page recovery, and continued usability after navigation.
- Browser console errors and failed requests. The browser tool did not expose a console capture in the performed check; no claim of console verification is made.

The owner-approved Reconstruction and Batch021 hashes were not recomputed during this partial browser QA. The preceding implementation verification recorded Reconstruction `f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0` and Batch021 `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`, but this report does not treat those prior checks as browser confirmation.

## Defects and fixes

- **Port 8501 startup failure:** Streamlit reported the port unavailable while the listener check showed no owner. Cause remains unverified. I used port 8502 only after confirming it was free; I did not terminate any unrelated process or change app configuration.
- **Browser interaction blocker:** the computer-use bridge declined further interaction because it could not verify the current Windows browser URL confidently. This prevented further QA; it did not establish an application defect.
- **Code fixes:** none. No UI/runtime defect could be reproduced and diagnosed without further interaction.

## Artifacts, logs, and preservation

- No screenshots or server log files were saved. The startup output and initial browser accessibility view were observed during the session; the report records the key evidence.
- No application, registry, dataset, prediction, model artifact, validation output, dependency, lock file, or existing report was modified.
- No models were trained and no historical metrics were recalculated.
- No Git operation was performed.
- No Stage B or restricted Stage C/D source/data was accessed. `research/EXISTING_RESULTS_METRICS_CATALOG.csv` was not accessed.
- The only file created for this task is this report.

## Remaining blocker and next step

Seven modules remain untested, and Research Overview has only an initial-render check. The browser-control safeguard prevented the required interactive pass. Repeat this QA when the available browser-control surface can safely bind to the local app URL; start on a confirmed available local port, then test each listed control and verify all eight modules before assigning PASS. No owner decision is needed for the remaining work.
