# COOKRISK APPLICATION DIAGNOSTIC AUDIT

**Audit date:** 2026-11-19  
**Application:** `research/CookRisk_Interactive_Research_Demonstrator/`  
**Scope:** Read-only UI, runtime, source-reference, hash, and scientific-label audit. No application code, dataset, model artifact, requirements file, or historical release was changed. No Git operation was performed. Stage B and restricted Stage C/D source material were not accessed.

## Executive summary

All eight modules loaded, and navigation between them worked. Five modules rendered their available content. Three record-level modules—Evidence Explorer, ACR Analysis, and Cooking & Compound Patterns—correctly failed closed because the selected reconstruction CSV does not match its recorded byte pin. The application remained usable for saved-result review, validation summaries, limitations, and reproducibility tables.

The main confirmed integrity problem is the reconstruction pin mismatch: the demonstrator expects `16dbbd9c38a21675a2644b415289004e5a8eb7091e97a96dae645ed2bf52be99`; the file currently at that exact path hashes to `f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0`. The gate prevented those records from being shown. Separately, Batch021 warnings and documentation say the current file hash is `d866d0…d5d3c1`, but the file currently hashes to `111064…669c8`, which exactly matches the saved validation summary's input hash. Those warnings are stale relative to the inspected files.

No whole-application outage or Python application traceback was observed. No critical severity issue was confirmed. One high-priority issue disables the three core record-level views; a second high-priority issue presents incorrect current Batch021 provenance. Findings and safe remediation order are below.

## Module results

| Module | Initial load | Interactions | Data integrity | Errors | Status |
|---|---|---|---|---|---|
| Research Overview | Passed; formula, target description, and scope notices rendered. | Sidebar navigation tested. | Correctly describes ACR as `100 × cooked/raw`, not total-mass retention. | None observed. | Working |
| Evidence Explorer | Page loaded; dataset-family cards rendered. | Expand/collapse tested. | Record CSV is guarded by the configured SHA-256 and row-count check. | Exact hash error below; record-level exploration unavailable. | Fail-closed / HIGH |
| ACR Analysis | Page loaded; ACR equation rendered. | Sidebar navigation tested; data-dependent controls unavailable behind gate. | Same guarded reconstruction source. | Same exact hash error. | Fail-closed / HIGH |
| Cooking & Compound Patterns | Page loaded. | Sidebar navigation tested; data-dependent selector, support control, and chart unavailable behind gate. | Same guarded reconstruction source. | Same exact hash error. | Fail-closed / HIGH |
| Existing ML Results | Passed; saved-result table rendered. | Result-family, target, and evaluation-design filters changed the table; metric selector changed R² to MAE; chart rendered; table search returned filtered results. | Family and target distinctions were preserved; results are displayed as saved, not recalculated. Catalog files have no expected digest configured. | None observed. | Working with provenance limitation |
| Validation Lab | Passed; split description, pooled values, and fold-wise chart rendered. | Sidebar navigation tested; chart rendered. | Fold-wise and pooled results are presented separately; source-attribution warning uses stale Batch021 hash metadata. | Warning claims current bytes differ and are unavailable; that claim is contradicted by current file and validation-summary hashes. | Renders; stale provenance / HIGH |
| Scientific Limitations | Passed; all eleven expandable disclosures rendered. | Expand/collapse tested across the disclosures. | Scientific cautions around ACR, source independence, missing protocol data, and lack of a validated predictor are appropriately retained. | First disclosure repeats the stale Batch021 hash warning. | Working with stale disclosure |
| Reproducibility & Evidence | Passed; source-family and dataset snapshot tables rendered. | Table search tested; navigation and internal heading links checked. | Referenced local files exist. Static hash/status values include stale Batch021 and reconstruction claims; catalogs are not digest-pinned. | No broken local reference or internal heading link found. | Renders with provenance limitations |

## Findings

Severity definitions: **CRITICAL** blocks the application broadly; **HIGH** breaks an important feature or materially misstates provenance; **MEDIUM** creates a meaningful but bounded integrity, labeling, or reproducibility gap; **LOW** is cosmetic or future compatibility; **EXPECTED RESTRICTION** is intentional fail-closed/scientific behavior.

### F-01 — Reconstruction pin mismatch disables three record-level modules

- **Severity:** HIGH. The fail-closed response itself is an **EXPECTED RESTRICTION** and behaved correctly.
- **Modules/components:** Evidence Explorer, ACR Analysis, Cooking & Compound Patterns; shared loader in `research/CookRisk_Interactive_Research_Demonstrator/research_data.py` (`load_reconstruction`, configured digest and row-count check); corresponding page renderers in `app.py`.
- **Exact UI message:** `Record-level ACR exploration is unavailable: The selected ACR file does not match this demonstrator's recorded byte snapshot. Expected 16dbbd9c38a21675a2644b415289004e5a8eb7091e97a96dae645ed2bf52be99; found f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0. Record-level exploration is disabled until the snapshot is reviewed.` The same source mismatch blocks the ACR summaries and cooking-pattern analysis.
- **Reproduction:** Open each of the three modules at `http://127.0.0.1:8501/`. The source-integrity error appears instead of record-derived controls/results.
- **Verified cause:** The configured relative path exists, but the actual file digest differs from `RECONSTRUCTION_SHA256`. The file is 1,016 rows, and the loader checks both the digest and expected row count before returning records. The loader does not substitute another dataset.
- **Recommended correction:** First establish which exact source snapshot is intended and review its provenance/content. If the inspected file is the authorized snapshot, update its documented pin only after owner review and revalidate schema, target, and source lineage. If it is not, restore the intended bytes only from a trusted, identified source. Do not bypass the check or silently repoint the app.
- **Owner authorization:** Yes, for selecting/approving the intended scientific snapshot or changing its pin.

### F-02 — Batch021 current-hash warning is stale

- **Severity:** HIGH for incorrect provenance status across Validation Lab and Scientific Limitations; MEDIUM in the static reproducibility descriptions.
- **Components:** `app.py` Batch021 alert and limitation expander; `research_data.py` constants; demonstrator README, evidence-selection document, and completion report.
- **Exact displayed claim:** `Historical audit input SHA-256: 111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8` and `Current Batch021 CSV SHA-256: d866d0ffab8c335e0469f2815c3cdf518b3d019be1bdf2e37ba2ced2e7d5d3c1`, followed by `Exact historical bytes have not been recovered; current-snapshot attribution is BLOCKED/UNVERIFIED.`
- **Reproduction:** Open Validation Lab or expand “Batch021 audit input hash mismatch” in Scientific Limitations; compare the displayed hashes to the file and `stageA/molecular_vs_source_validation_audit/validation_summary.json`.
- **Verified cause:** The current `stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv` hashes to `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`. That equals the stored validation summary `input_sha256`. The app's displayed “current” constant (`d866d0…`) is stale. This establishes matching bytes for the inspected input path; it does not itself certify every downstream result or justify recalculating metrics.
- **Recommended correction:** Reconcile the validation summary, fold table, Batch021 file, and run/provenance notes as one versioned audit package; then correct the current hash/status wording while retaining historical traceability. Keep metrics explicitly reported unless their reproduction status is separately evidenced.
- **Owner authorization:** App/data owner should approve status changes that alter the scientific interpretation. Correcting the factual current digest after independent recheck is technically straightforward.

### F-03 — Reconstruction target field label differs from registry label

- **Severity:** MEDIUM (metadata inconsistency; no numeric discrepancy was observed).
- **Components:** `app.py` ACR/cooking summaries read `target_value_percent`; `research_data.py` `DATASET_FAMILIES` describes the selected target as `verified_concentration_ratio_percent`; `docs/EVIDENCE_AND_DATA_SELECTION.md` calls the target `target_value_percent`.
- **Reproduction:** Compare the family-register row/target description with the field used by the page components and the CSV header.
- **Verified cause/effect:** The 1,016-row file contains both columns; they are exactly equal across all rows. The stored target is labeled `apparent_concentration_ratio_percent` with equation `100 * C_cooked / C_raw`. Formula deviations were at most 0.0048224485 percentage points, with none above 0.01 pp. The mismatch is a field-name/registry inconsistency, not a currently observed numerical error.
- **Recommended correction:** After the source snapshot is approved, select one canonical display-field label and make the registry, page captions, and documentation agree; preserve the underlying field and meaning.
- **Owner authorization:** App owner approval recommended; scientific owner approval if the target definition or designation changes.

### F-04 — Historical `Retention_Final` documented digest differs from the present file

- **Severity:** MEDIUM; currently bounded because this file is not loaded into the demonstrator's record-level explorer and the UI labels its metrics as historical/reported.
- **Component:** Static benchmark provenance represented in `EXISTING_METRICS_SELECTED.csv`, `DATASET_SNAPSHOT_CATALOG.csv`, and the demonstrator evidence documentation.
- **Observed hashes:** Documented historical input SHA-256 `750124efc8b89dff1f67764064b1049b5db51fb1b2f222d4f91cd94c56945f89`; present `stageA/input/cookchem_molecular_retention_preprocessed.csv` SHA-256 `cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27`.
- **Reproduction:** Compare the documented benchmark input digest with the current referenced path. The app displays saved metrics only and does not load this dataset for record-level analysis.
- **Verified cause:** Current bytes do not match the documented historical digest. The app correctly avoids claiming that current records reproduce the saved metrics; historical target semantics/equivalence remain unresolved.
- **Recommended correction:** Keep the benchmark metrics isolated and reported. Identify the exact historical input artifact or update the catalog to state that the documented digest is historical and current bytes differ. Do not recalculate or equate `Retention_Final` with ACR.
- **Owner authorization:** Yes, before changing target interpretation, snapshot identity, or metric attribution.

### F-05 — 439-row parent-hash warning is stale; model-output linkage is still incomplete

- **Severity:** MEDIUM.
- **Component:** The 439-row family status in `research_data.py`/dataset catalog and result-source metadata.
- **Reproduction:** Compare the parent hash recorded in `stageA/final_prototype_2026_11_10/manifest.json` with the current `stageA/recovery_v1_0_0_2026_11_10/expanded_clean_stageA_dataset.csv` digest.
- **Verified cause:** The parent file's current SHA-256 is `d3960dc6ec808ca1783cbb2c57d35fb4676da04feeff675280c1f07eb072005a`, matching the manifest parent digest. Thus the wording that the parent currently mismatches is stale. The prototype's final modelling dataset and model-comparison output do not have a corresponding pinned output digest in the app, so the full output-to-metric linkage remains unverified.
- **Recommended correction:** Correct the parent-status statement after confirming manifest version and retain a separate explicit limitation for missing output-artifact digest/provenance. Do not label the prototype results freshly reproduced.
- **Owner authorization:** App/data owner approval for changing displayed provenance status.

### F-06 — Runtime catalogs and fold table lack configured expected digests

- **Severity:** MEDIUM (reproducibility/integrity control gap).
- **Components:** `research_data.py` catalog readers and sources: `EXISTING_METRICS_SELECTED.csv`, `DATASET_SNAPSHOT_CATALOG.csv`, and `stageA/molecular_vs_source_validation_audit/fold_metrics.csv`.
- **Observed current digests:** Metrics catalog `8f01d2692b7f8479a8762aeaa2f0b40102e704e3c722ab7a6706ff9fb578d71b` (8 rows); snapshot catalog `32de281aad0f1f549d7583d069f57e2a19eb8284880934b86c3461f6e781ccfc` (10 rows); fold table `21d8925e0349b994ea5b58c6875a952c00ee5e99db04e0663ffb7e400acfac65` (10 rows). No expected digest is configured for these loaded sources.
- **Reproduction:** Inspect the three loader paths and catalog metadata; compute current digests. Table/search rendering works, but runtime code does not verify a saved digest before display.
- **Verified cause:** These files are read directly without an expected-hash assertion. Their current hashes are recorded here for audit; they are not claims of an approved snapshot.
- **Recommended correction:** Introduce an owner-reviewed manifest or expected digests in a future authorized change, with clear version and lifecycle policy. Do not make an ad hoc pin from this audit report alone.
- **Owner authorization:** Yes, for defining approved artifact versions and pins.

### F-07 — Streamlit width parameter is deprecated

- **Severity:** LOW.
- **Component:** `app.py` calls to `st.dataframe` and `st.plotly_chart` using `use_container_width=True` (lines 117, 122, 237, 251, 311, 314).
- **Observed message:** Streamlit reports that `use_container_width` is deprecated and will be removed after 2025-12-31.
- **Reproduction:** Start the app with the existing installed Streamlit environment and inspect server output while navigating through table/chart pages.
- **Verified cause:** Deprecated API parameter remains in the app. It currently renders successfully in Streamlit 1.67.0.
- **Recommended correction:** In a separately authorized maintenance change, replace with the supported width argument and verify layouts across the affected pages.
- **Owner authorization:** App owner approval; no scientific approval needed.

### F-08 — Nonfatal client-connection reset appeared in server output

- **Severity:** LOW / unconfirmed transient event.
- **Component:** Streamlit/Uvicorn connection handling; not traced to an application component.
- **Observed error:** One `ConnectionResetError [WinError 10054]` from the Windows asyncio Proactor transport while a client connection closed.
- **Reproduction:** Not consistently reproduced. The server remained running and the browser continued to load pages.
- **Root cause:** Unverified; evidence is consistent with a transient client disconnect, but that attribution is not confirmed.
- **Recommended correction:** None based on this isolated observation. Revisit only if repeatable failed requests or a correlated traceback appears.
- **Owner authorization:** No change recommended.

## Data-source integrity ledger

“Expected digest” below means the digest documented or configured by the inspected app/catalog; `none` means no expected digest was recorded in the runtime app. Resolved paths are repository-relative and existed during this audit.

| Dataset/source identity and use | Expected SHA-256 | Actual SHA-256 | Resolved path | Target/approval and audit result |
|---|---|---|---|---|
| Selected verified concentration-ratio reconstruction; sole record-level source for Evidence Explorer, ACR Analysis, Cooking & Compound Patterns | `16dbbd9c38a21675a2644b415289004e5a8eb7091e97a96dae645ed2bf52be99` | `f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0` | `stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv` | 1,016 rows; `apparent_concentration_ratio_percent = 100 * C_cooked / C_raw`; separate reported evidence family, not owner-designated canonical. Fail-closed. All total-mass-retention statuses are `NOT_ESTABLISHED`; no replacement selected. |
| Batch021 master; status/provenance reference, not record-level loaded by app | `d866d0ffab8c335e0469f2815c3cdf518b3d019be1bdf2e37ba2ced2e7d5d3c1` (app's stale “current” value); historical audit digest `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8` | `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8` | `stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv` | 1,016 ACR records. Actual equals validation summary `input_sha256`; current BLOCKED/UNVERIFIED warning is stale relative to this path. Kept separate from reconstruction and historical benchmark. |
| Molecular/source validation summary and saved fold metrics | No expected digest in runtime app | JSON `0d7563a63f6bca310ab5d16d4b15e07ba4cc78388a4dc7443c4e9ba8851cc662`; CSV `21d8925e0349b994ea5b58c6875a952c00ee5e99db04e0663ffb7e400acfac65` | `stageA/molecular_vs_source_validation_audit/validation_summary.json`; `stageA/molecular_vs_source_validation_audit/fold_metrics.csv` | Saved validation evidence. Summary input hash matches Batch021 current bytes. Pooled R² is displayed separately from fold-wise R²; no metrics were recalculated. |
| Historical benchmark input; metric context only | `750124efc8b89dff1f67764064b1049b5db51fb1b2f222d4f91cd94c56945f89` (documented historical digest) | `cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27` | `stageA/input/cookchem_molecular_retention_preprocessed.csv` | 1,124 rows, `Retention_Final`; current file differs from documented historical digest. Kept distinct from ACR; app does not load it for record-level analysis. |
| 439-row prototype parent dataset | Manifest parent digest `d3960dc6ec808ca1783cbb2c57d35fb4676da04feeff675280c1f07eb072005a` | `d3960dc6ec808ca1783cbb2c57d35fb4676da04feeff675280c1f07eb072005a` | `stageA/recovery_v1_0_0_2026_11_10/expanded_clean_stageA_dataset.csv` | 439-row ACR parent; current parent matches manifest. Prototype modelling output digest is not pinned, so downstream linkage is incomplete. |
| 439-row prototype final modelling output and saved comparison table | No expected digest in app | Dataset `1fea513ac44777411357df6ac7d084eecd97cd08f956d3ac23e38695552554d1`; comparison `b42e462801d1b9ad576433d8c74e7092d9502356e6044b9ac3e670da1ac937f7` | `stageA/final_prototype_2026_11_10/final_modelling_dataset.csv`; `stageA/final_prototype_2026_11_10/model_comparison.csv` | 439-row prototype family and 20-row comparison output. Not selected as record-level source; absent app output pins limit artifact-to-metric verification. |
| Existing ML Results metric catalog | None | `8f01d2692b7f8479a8762aeaa2f0b40102e704e3c722ab7a6706ff9fb578d71b` | `research/CookRisk_Computational_Research_Prototype/tables/EXISTING_METRICS_SELECTED.csv` | 8 curated saved metric rows; all catalog `source_file` paths exist. Displayed only, not recalculated. |
| Reproducibility dataset snapshot catalog | None | `32de281aad0f1f549d7583d069f57e2a19eb8284880934b86c3461f6e781ccfc` | `research/CookRisk_Computational_Research_Prototype/tables/DATASET_SNAPSHOT_CATALOG.csv` | 10 rows; static family status includes stale Batch021 and reconstruction descriptions. |
| 338-row strict subset reference | No runtime pin | `6d8637bf00ec700ede9b03275e9faf5ab55cb93cf7d2dea07defff3274e32ec8` | `stageA/final_prototype_2026_11_10/reports/strict_subset_338_recovery_report.md` | Referenced as a report, not loaded as record-level evidence; file exists. |

All inspected metric-catalog `source_file` paths and dataset-catalog `primary_reference` paths existed. The page did not silently combine Batch021, the 1,124-row benchmark, the 439-row prototype, and the reconstruction.

### Snapshot-catalog row coverage

The 10-row runtime `DATASET_SNAPSHOT_CATALOG.csv` has no expected-hash column. The following are its complete row-level primary references. For file references, “actual” is the SHA-256 computed during this audit; for folder references, no folder digest is defined or recorded. The catalog's statuses are reported metadata, not independent owner approval.

| Catalog family | Target and intended app role | Primary reference path(s) and actual identity | Catalog status / audit result |
|---|---|---|---|
| Historical Stage A benchmark | `Retention_Final`; reported metrics only | `stageA/input/cookchem_molecular_retention_preprocessed.csv` — `cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27`; `stageA/stageA_reproducibility.md` — `c4de39a60dccd90251fe27d9fcc466b42e5494dbbf107003034d93385b17a8c2` | REPORTED; prior reproduction documented. Current CSV differs from historical input digest; not ACR. |
| Recovery v0.2.0 | ACR; initial narrow verified set | `stageA/recovery_v0_2_0_2026_11_10/` — existing directory, no directory digest in catalog | REPORTED; reference is folder-level, exact file snapshot not pinned by catalog. |
| Recovery v0.3.0 | ACR; recovery evidence report | `stageA/recovery_v0_3_0_2026_11_10/dataset_expansion_report.md` — `15fecff2e25716696d39741677807688e19cb8745b9c37e097433f7d81504eb4` | REPORTED; report reference exists. |
| Recovery v0.4.0 | ACR; recovery evidence report | `stageA/recovery_v0_4_0_2026_11_10/dataset_expansion_report.md` — `cce1ceee2e7da817e8db070b2aa2abccd4203758f8b5c8c10aee78fab63d89e1` | REPORTED; report reference exists. |
| Recovery v0.5.0 / v0.6 diagnostic | ACR; two recovery folders | `stageA/recovery_v0_5_0_2026_11_10/` and `stageA/recovery_v0_6_0_2026_11_10/` — both existing directories, no directory digests in catalog | REPORTED; v0.6 adds no observations; folder-level identity is not byte-pinned. |
| Recovery v0.7 | ACR; matched-evidence report | `stageA/recovery_v0_7_0_2026_11_10/matched_evidence_report.md` — `ea544f952db011feecdfbf04a305562eaee7e974a405e5fbdb6f4ba0ddf3689a` | REPORTED; report reference exists. |
| 439-row prototype family | ACR; manifest reference and saved results | `stageA/final_prototype_2026_11_10/manifest.json` — `2f2d36baf0540b43c6050f755d090f10437cd52eb73d5968e57d20fbccd6c3c4` | Catalog says parent linkage BLOCKED; the recorded parent digest matches current parent bytes, but output linkage remains unpinned. |
| Batch021 ACR master | `target_value_percent = 100*cooked/raw`; metadata/status only | `stageA/dataset_expansion_1000/batch_021/` — existing directory, no directory digest in catalog; the explicitly referenced master CSV is separately hashed in the main ledger | REPORTED; catalog says manifest lacks dataset hash. Current master matches the validation summary input SHA. |
| Verified ACR reconstruction | `verified_concentration_ratio_percent = 100*cooked/raw`; selected record-level source | `stageA/verified_concentration_ratio_reconstruction/` — existing directory, no directory digest in catalog; the explicitly loaded CSV is separately hashed in the main ledger | REPORTED / snapshot linkage unverified; selected CSV fails its configured byte pin, so all record-level views remain gated. |
| Evidence tiers | ACR; summary metrics reference | `stageA/dual_dataset_sensitivity_analysis/summary_metrics.csv` — `85217e0e64aba2aabf4c0f993918538a30baa4ff0d8bb7a5ee20e0967f573720` | REPORTED; tiers are not interchangeable. Reference exists; no expected digest is recorded. |

No missing catalog reference was found. File references above are the exact files cited by the catalog; directory references are not treated as a digest-verified dataset snapshot.

## Scientific correctness and behavior

- **ACR versus total-mass retention:** The overview's equation and limitation are correct. ACR is a concentration ratio; it cannot establish total analyte-mass retention without compatible cooked yield/mass and basis information. The reconstruction records mark total-mass retention as `NOT_ESTABLISHED`; no mass-retention calculation was asserted.
- **Target naming:** The observed target is apparent concentration ratio (`100 × cooked concentration / raw concentration`). The registry field-name mismatch is metadata-only for this file because the two numeric fields match exactly, but it should be made consistent before restoring record views.
- **Pooled versus fold-wise R²:** Validation Lab labels and separates pooled results from fold-wise values. They must not be treated as interchangeable. The saved pooled values observed were −0.067833 and −0.065645; fold values were rendered individually, with one molecular-grouped fold positive. This is not evidence of robust source generalization.
- **Validation designs:** Existing ML Results distinguishes molecular-grouped and DOI/source-held-out designs. DOI is a source-family proxy, not proof of independence across lab, protocol, or investigators.
- **Reported versus reproduced:** The UI states that saved metrics are displayed, not recalculated. No fresh training or metric reproduction was performed in this diagnostic. Historical benchmark results remain separate from ACR results.
- **Scientific limitations:** The warnings about source transfer, missing cooking/assay metadata, extreme values, no validated predictor, and absence of clinical/cooking guidance are visible and scientifically appropriate. The first Batch021 limitation is the exception: its current-hash wording is outdated.
- **References/layout:** No broken local source references or internal heading links were found. Search/filter controls and charts that were available worked. Wide tables rely on the normal horizontal table scroll; no blocking rendering or layout defect was observed.

## Runtime and interaction checks

- Browser opened `http://127.0.0.1:8501/`; all module navigation and final return to Research Overview succeeded.
- Browser console errors: none observed.
- Streamlit server remained running; no application exception/traceback observed during the reviewed navigation.
- Nonfatal Streamlit deprecation warnings for `use_container_width` appeared. One isolated Windows client-connection reset occurred without a page failure; its cause is unverified.
- Existing dedicated environment used for the running app: Python 3.14.7 and Streamlit 1.67.0. No packages were installed during this audit.
- Hash gates were not bypassed; source files were read-only throughout.

## Recommended correction order

1. **Resolve reconstruction identity with the data owner.** Review the intended snapshot's provenance and content at the existing path. Keep the three pages blocked until an authorized decision identifies the exact valid bytes. Do not change the expected digest merely to make the pages load.
2. **Reconcile the Batch021 audit package.** Confirm the saved summary's input path/version and fold/pooled metric provenance against the current `111064…669c8` file. Then correct the stale `d866d0…` current-hash/status text while retaining the historical hash and audit trace.
3. **Correct 439-row linkage wording.** The manifest's parent hash matches current parent bytes; fix the stale mismatch statement only after confirming the manifest version, and retain the unresolved prototype-output-to-metric linkage.
4. **Align reconstruction target labels.** Make the target name and field used by the app/registry/docs consistent after step 1; preserve the ACR equation and explicit non-equivalence to total-mass retention.
5. **Add reviewed artifact integrity metadata.** Decide and document expected digests/version policy for metric, snapshot, and fold catalogs before changing runtime checks.
6. **Update static evidence documentation.** Reconcile README, evidence-selection, completion, and runtime catalog statements to verified source status; keep historical and current snapshots clearly separated.
7. **Address the low-priority Streamlit deprecation.** Update the width parameter only in a separate authorized code change and verify all affected table/chart layouts.

## Files inspected

Application and demonstrator documentation:

- `research/CookRisk_Interactive_Research_Demonstrator/app.py`
- `research/CookRisk_Interactive_Research_Demonstrator/research_data.py`
- `research/CookRisk_Interactive_Research_Demonstrator/README.md`
- `research/CookRisk_Interactive_Research_Demonstrator/DEMONSTRATOR_COMPLETION_REPORT.md`
- `research/CookRisk_Interactive_Research_Demonstrator/docs/EVIDENCE_AND_DATA_SELECTION.md`
- `research/CookRisk_Interactive_Research_Demonstrator/requirements.txt` (read only)
- `research/CookRisk_Computational_Research_Prototype/tables/EXISTING_METRICS_SELECTED.csv`
- `research/CookRisk_Computational_Research_Prototype/tables/DATASET_SNAPSHOT_CATALOG.csv`

Stage A references read only for path/hash/target checks:

- `stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv`
- `stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv`
- `stageA/molecular_vs_source_validation_audit/validation_summary.json`
- `stageA/molecular_vs_source_validation_audit/fold_metrics.csv`
- `stageA/input/cookchem_molecular_retention_preprocessed.csv`
- `stageA/final_prototype_2026_11_10/manifest.json`
- `stageA/final_prototype_2026_11_10/final_modelling_dataset.csv`
- `stageA/final_prototype_2026_11_10/model_comparison.csv`
- `stageA/recovery_v1_0_0_2026_11_10/expanded_clean_stageA_dataset.csv`
- `stageA/final_prototype_2026_11_10/reports/strict_subset_338_recovery_report.md`

**Files changed:** This new report only. Application code, datasets, model artifacts, pins, dependency files, and historical releases were not modified.
