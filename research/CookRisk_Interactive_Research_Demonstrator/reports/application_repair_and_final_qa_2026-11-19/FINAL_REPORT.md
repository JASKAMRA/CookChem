# CookRisk — End-to-End Application Repair and Final QA

**Overall result: PASS**  
Verification completed: 2026-11-20

## Launch and server status

- Existing environment: `research/CookRisk_Interactive_Research_Demonstrator/.audit-venv-20261119`.
- Python 3.14.7, Streamlit 1.67.0, Plotly 7.1.0, NumPy 2.5.5, pandas 3.1.1.
- Startup command used for the final live server:

  ```powershell
  cd C:\Users\dakshant\Desktop\CookChem\research\CookRisk_Interactive_Research_Demonstrator
  .\.audit-venv-20261119\Scripts\python.exe -u -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false
  ```

- The initial 8501 listener belonged to CookRisk. Its old process showed a stale `ImportError: cannot import name 'LIVE_EXPLORATION_DATASET_ID' from 'research_data'`; the on-disk module contained the symbol, and restarting the identified CookRisk process resolved that stale-process error. The final 8501 app returns HTTP 200 at `/_stcore/health` and remains available at [http://127.0.0.1:8501/](http://127.0.0.1:8501/).
- A clean regression server was started on 8503 after confirming it was free. It returned HTTP 200, completed the browser regression, and shut down with Ctrl+C; the 8503 listener is gone. A prior QA server on 8502 was also verified as CookRisk-owned and stopped. Final listener check found only the intended 8501 server; the temporary Chrome DevTools port is closed.

## Defects found and repairs

1. **ACR first-render failure — fixed.** A clean server reproduced a Plotly histogram exception on the first ACR visit: `AttributeError: partially initialized module 'numpy' ... has no attribute 'ndarray'`. After a NumPy-only preload, the next clean run exposed the same partial-initialization failure for pandas (`... has no attribute 'Series'`). The traceback originated in Plotly's array validator, which inspects both modules. `app.py` now imports NumPy and pandas before Plotly. The fresh-server first ACR visit then rendered all three charts; no traceback recurred, and the final 8501 instance also rendered the charts after reloading the fix. No values, targets, or scientific calculations changed.
2. **Stale 8501 process — resolved by restart.** The earlier import error came from the old app process; restarting the verified CookRisk process loaded the current code. No unrelated process was stopped.
3. **Deprecated Streamlit sizing argument — corrected in the demonstrator.** Dataframes and charts use the supported `width="stretch"` argument in place of `use_container_width`.
4. **Historical result-family scope — corrected in the demonstrator.** Existing ML Results filters saved results to the `Batch021 fixed audit` family and displays its dataset and evaluation provenance. It does not offer live Reconstruction results in that section.

## Module-by-module browser results

All eight modules were opened in Chrome 157 through the local DevTools Protocol on the final clean server. Each rendered its expected content without a Streamlit traceback. The ACR chart and scientific-expander checks were repeated after the first-load defect was fixed.

| Module | Rendering and content | Controls/interactions exercised | Errors / final result |
|---|---|---|---|
| Research Overview | Research question, target equation, and research-boundary statements rendered. | Sidebar navigation and return navigation. | No error; **PASS**. |
| Evidence Explorer | Reconstruction ID, full hash, 1,016 × 43 dimensions, limited approval, and noncanonical status rendered. | Four filters (food, compound, cooking method, DOI/source); browser selected food matrix `Potato` and showed **88 of 1,016** records. AppTest also exercised blank/missing and zero-result filter states. | No error; **PASS**. |
| ACR Distributions | Stored target used; all 1,016 rows had numeric target values in the unfiltered view; three charts rendered on the first page visit after the fix. Missing/nonnumeric rows are counted explicitly and are not removed from the evidence table. | Shared four live filters; blank and empty numeric-result cases exercised in AppTest. | Pre-fix first render failed as described above; post-fix first render and regression passed; **PASS**. |
| Cooking & Compound Patterns | Descriptive chart and noncausal interpretation rendered. | Grouped by cooking method; minimum support set to 2 and 30; selector and both settings completed without exceptions. | No error; **PASS**. |
| Existing ML Results | Batch021 ID, full hash, 1,016 × 38 dimensions, and historical-evidence notice rendered. Reconstruction ID was absent from this page. | Result-family, target, evaluation-design, and saved metric selectors exercised in AppTest; only Batch021 is available as a family. | Saved metrics remain historical; no retraining or recalculation; **PASS**. |
| Validation & Generalization | Saved summary and fold chart rendered with dataset/target/split provenance. | Checked accessible table headers `pooled_oof_r2` and `mean_fold_r2` separately. | No error; saved result explicitly not freshly reproduced; **PASS**. |
| Scientific Limitations | Opened all **11/11** expanders; unresolved `Retention_Final` semantics/units, source independence limits, and ACR-versus-total-mass distinction were visible. | Each expander opened and content checked. | No error; **PASS**. |
| Reproducibility & Evidence | Dataset registry and snapshot tables rendered; both dataset IDs were present in the accessible grid; limited approval and noncanonical status were visible. | Navigated to the module and inspected registry table cells and disclosures. | No error; **PASS**. |

The live ACR label remains `100 × C_cooked / C_raw`, an apparent concentration ratio, not total-mass retention. Group summaries are explicitly descriptive and noncausal. Historical `Retention_Final` remains separate, with its equation and units unresolved. Pooled out-of-fold R² and mean-fold R² remain separate saved summaries.

## Verification results

- `python -m py_compile app.py research_data.py`: **passed**.
- `python -m unittest discover -s tests -v`: **14 passed, 0 failed**.
- Streamlit AppTest after the final import fix: **8/8 modules** navigated with 0 exceptions and 0 `st.error` elements; cooking support values 2 and 30 passed; only the Batch021 result family was available.
- Focused AppTest interaction checks from the final selector/filter regression: **11/11 assertions passed**, including blank/missing and empty-result handling, result-family/target/design/metric selection, and navigation. An earlier 13/13 focused navigation/filter sequence also passed.
- Final Chrome browser regression: **8/8 modules** verified across the main pass and the waited-for expander follow-up; ACR first render showed 3 charts; all 11 limitation expanders opened; return navigation to Research Overview passed.
- Browser food-matrix interaction: selecting `Potato` displayed `Showing 88 of 1,016 source records`.
- Final browser diagnostics: **0 JavaScript/console errors and 0 failed network requests**. Browser testing used installed Chrome 157 headless through CDP; Playwright was unavailable and was not installed. The Windows browser-control bridge was not used.
- Final HTTP health: 8501 **200 `ok`**; temporary 8503 **200 `ok`** before its clean shutdown.

## Dataset and preservation checks

| Dataset | Final SHA-256 | Dimensions | Result |
|---|---|---:|---|
| Reconstruction (`stagea-acr-reconstruction-1016-f939`) | `f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0` | 1,016 × 43 | Matches the approved live-exploration registry pin. Approval is limited to demonstrator exploration; it is not canonical designation or independent scientific validation. |
| Batch021 (`stagea-batch021-historical-1016-111064`) | `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8` | 1,016 × 38 | Matches the preserved historical reference and saved evaluation input identity. Historical metrics were not reproduced or changed. |

No dataset, prediction, model artifact, saved metric, validation output, dependency file, or lockfile was modified. No Git write operation was performed. Stage B, restricted Stage C/D content, and `research/EXISTING_RESULTS_METRICS_CATALOG.csv` were not accessed. Hashes were recalculated only for the two approved datasets named above.

## Files changed and evidence

- `research/CookRisk_Interactive_Research_Demonstrator/app.py` — demonstrator-only rendering/provenance and Batch021 separation changes described above, plus the final eager NumPy/pandas initialization fix. No data or scientific logic changed.
- This report and supporting QA screenshots/JSON/logs are in this new isolated directory. Final screenshots include `browser_fixed_acr_distributions.png`, `browser_fixed_evidence_explorer.png`, `browser_fixed_potato_filter.png`, `browser_fixed_limitations_expanded.png`, `browser_fixed_validation.png`, and `browser_fixed_reproducibility.png`. `browser_fixed_final_results.json` records the final eight-module result; pre-fix server logs preserve the reproduced errors.

`research_data.py`, tests, datasets, results, requirements, and lockfiles were not modified. The 8501 application is left running for use; the temporary 8503 regression server and QA browser have been closed.

## Remaining blockers

None identified for local demonstrator use. The scientific/provenance limitations documented in the application remain unchanged and are not resolved by this UI repair.
