# Phase 5 — Research Prototype Completion Report

Date: 2026-11-20  
Project: CookRisk Interactive Research Demonstrator  
Phase exit decision: **READY FOR UI POLISH WITH DOCUMENTED LIMITATIONS**

## Outcome

The existing research prototype now presents the consolidated Phase 4 model-evidence registers in separate, provenance-labelled families; makes pooled OOF R² and arithmetic mean-fold R² visibly distinct; exposes the historical conflicts and scientific limitations; and gives the three approved live exploration sections a verified, fail-closed Reconstruction data path. The Research Overview, Evidence Explorer, ACR Distributions, Cooking & Compound Patterns, Existing ML Results, Validation & Generalization, Scientific Limitations, and Reproducibility & Evidence sections were visited in the running app. All rendered without a Python exception or blank page. Tested live filters and group controls yielded expected results and explicit empty states.

No model was trained, no prediction or benchmark regenerated, no scientific value recalculated, and no dataset, saved prediction, historical model artifact, schema, registry pin, requirement, or lockfile changed. The historical `Retention_Final` source CSV was not opened. No Git write operation was performed.

## Data integrity checked for the two approved ACR snapshots

| Dataset role | File | Rows × columns | Fresh SHA-256 | Registered value | Result |
|---|---|---:|---|---|---|
| Live exploration only | `stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv` | 1,016 × 43 | `f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0` | Same | MATCH |
| Separate historical reference | `stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv` | 1,016 × 38 | `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8` | Same | MATCH |

Reconstruction remains owner-approved for demonstrator live exploration only. It is not designated canonical and this approval is not independent scientific validation. Batch021 remains a separate source for its saved historical results and metadata. There is no live-data fallback to Batch021.

## Scientific and provenance boundaries

- ACR is the stored apparent concentration ratio `100 × C_cooked / C_raw`, not total-mass retention. Total-mass retention is not inferred without compatible paired food masses or validated yield.
- Historical `Retention_Final` remains a separate target with unresolved equation, scale, and units. The app does not load its source CSV.
- Saved metrics are displayed, not recalculated. Stage A, Batch021, Reconstruction, and strict-subset families are not merged into a common leaderboard.
- The initial and replay tuned-XGBoost records remain conflicting; no preferred version or cause is claimed. Post1000 aggregate checksum and component/combined-row conflicts remain visible without ranking or repair.
- Friend-reported pooled 0.3301 and mean-fold 0.2990 remain UNVERIFIED.
- DOI/source-held-out is a source-family proxy, not independent laboratory, prospective, or external validation.

## Implementation files

- `app.py` — adds separate result-family evidence cards, visible status labels, saved conflict and provenance sections, complete limitations disclosures, and a clear zero-record state.
- `research_data.py` — fail-closed readers for consolidated evidence registers, finite numeric handling, and the 17-entry scientific limitation register.
- `tests/test_research_evidence.py` — regression checks for evidence-register loading, statuses, conflicts, absent pooled evidence, and limitations coverage.
- `README.md` and `docs/EVIDENCE_AND_DATA_SELECTION.md` — document module scope, data roles, evidence values and status meanings, scientific boundaries, and local run/test instructions.
- Seven reports and supporting Streamlit logs are in this directory.

`DEMONSTRATOR_COMPLETION_REPORT.md`, approved dataset registry entries, source CSVs, requirements, lockfiles, predictions, and historical artifacts remain unchanged.

## Verification

- Python compilation: PASS (`app.py`, `research_data.py`, `tests/test_dataset_registry.py`, `tests/test_research_evidence.py`).
- Focused and existing unit suite: PASS, 22 tests.
- Registry/evidence loaders: PASS; expected saved registers loaded (33 model rows, 349 fold rows, 17 conflict entries, 11 provenance-gap entries).
- Reconstruction/Batch021 fresh full SHA-256 and shape checks: PASS; both match their registered pins.
- Streamlit process: PASS on `http://127.0.0.1:8501/` using the existing `.audit-venv-20261119` environment. The prior process had stale imported code and showed `ImportError: cannot import name 'SCIENTIFIC_LIMITATIONS' from research_data`; only the verified CookRisk process on port 8501 was refreshed. The current app returned HTTP health 200 and loaded all eight modules.
- Browser page checks: PASS; all eight modules nonblank, no page traceback, no browser console errors returned. Filter/group and no-result interactions are detailed in `RESEARCH_FEATURE_ACCEPTANCE_MATRIX.csv`.
- Headless Streamlit `AppTest.from_file` attempt: did not complete within the environment and was stopped; manual functional checks used the actual browser instead.
- Server log: current port-8501 startup line only; no Python traceback. The browser automation surface did not provide a usable request-level failed-network ledger; that check is recorded as an environment/tooling limitation, not a clean independent network audit.
- Environment check limitation: the existing virtual environment imports Streamlit, pandas, NumPy, and Plotly and has Streamlit 1.67.0, but has no `pip` module; therefore `pip check` could not run. No package was installed or changed.
- Verification was local to this computer; a second physical laptop was not tested.

## Remaining limitations and Phase 5 exit

All known remaining issues are non-blocking for the stated read-only research prototype: scientific uncertainty remains accurately displayed; `pip check` and the request-level browser network ledger were unavailable in this environment; and a second physical laptop was not tested. No unresolved blocking functional defect was observed in the authorized app scope.

**Phase 5 exit: READY FOR UI POLISH WITH DOCUMENTED LIMITATIONS.** Phase 6 may now cover only visual polish, responsive presentation, visual consistency, smoke checks, and release readiness; it is not needed to finish an outstanding Phase 5 functional or scientific task.

## Saved model metric register represented in the app

| Family / model | Target | Evaluation / grouping | Pooled OOF R² | Pooled status | Mean-fold R² | Mean-fold status |
|---|---|---|---:|---|---:|---|
| Historical Stage A benchmark — ExtraTrees_reference | Retention_Final; equation and units unresolved | GroupKFold(5); Canonical_Molecular_ID; zero intersections per QA / Canonical_Molecular_ID | 0.2559778949866835 | REPORTED â€” PROVENANCE INCOMPLETE | 0.380460979215581 | VERIFIED FROM SAVED RECORDS |
| Historical Stage A benchmark — RandomForest | Retention_Final; equation and units unresolved | GroupKFold(5); Canonical_Molecular_ID; zero intersections per QA / Canonical_Molecular_ID | 0.2370738737499425 | REPORTED â€” PROVENANCE INCOMPLETE | 0.341500180786333 | VERIFIED FROM SAVED RECORDS |
| Historical Stage A benchmark — RBF_SVR | Retention_Final; equation and units unresolved | GroupKFold(5); Canonical_Molecular_ID; zero intersections per QA / Canonical_Molecular_ID | 0.2545971240074941 | REPORTED â€” PROVENANCE INCOMPLETE | 0.379351673737018 | VERIFIED FROM SAVED RECORDS |
| Historical Stage A benchmark — XGBoost | Retention_Final; equation and units unresolved | GroupKFold(5); Canonical_Molecular_ID; zero intersections per QA / Canonical_Molecular_ID | 0.2750117549141373 | REPORTED â€” PROVENANCE INCOMPLETE | 0.383296203894281 | VERIFIED FROM SAVED RECORDS |
| Historical Stage A benchmark — XGBoost_tuned | Retention_Final; equation and units unresolved | GroupKFold(5); Canonical_Molecular_ID; zero intersections per QA / Canonical_Molecular_ID | 0.2832468313018399 | CONFLICTING SAVED EVIDENCE | 0.40037582421724 | CONFLICTING SAVED EVIDENCE |
| Historical Stage A separate replay — XGBoost_tuned replay | Retention_Final; equation and units unresolved | GroupKFold(5); Canonical_Molecular_ID / Canonical_Molecular_ID | 0.27579634550899224 | CONFLICTING SAVED EVIDENCE | 0.394286907871563 | CONFLICTING SAVED EVIDENCE |
| Batch021 ACR fixed audit — ExtraTreesRegressor 25 trees | target_value_percent=100*C_cooked/C_raw (ACR) | GroupKFold(5) / canonical_molecular_id | -0.0678329296938553 | VERIFIED FROM SAVED RECORDS | -0.256216157206555 | VERIFIED FROM SAVED RECORDS |
| Batch021 ACR fixed audit — ExtraTreesRegressor 25 trees | target_value_percent=100*C_cooked/C_raw (ACR) | GroupKFold(5) / doi | -0.0656453820532739 | VERIFIED FROM SAVED RECORDS | -0.206526781706722 | VERIFIED FROM SAVED RECORDS |
| Verified Reconstruction ACR — Historical XGBoost; reduced features | verified_concentration_ratio_percent=100*C_cooked/C_raw (ACR) | molecular_grouped / canonical_molecular_id | 0.059830782905310076 | REPORTED â€” PROVENANCE INCOMPLETE | 0.0835036726049201 | VERIFIED FROM SAVED RECORDS |
| Verified Reconstruction ACR — Historical XGBoost; reduced features | verified_concentration_ratio_percent=100*C_cooked/C_raw (ACR) | source_held_out / doi | -0.07370962306226225 | REPORTED â€” PROVENANCE INCOMPLETE | -0.253519411629122 | VERIFIED FROM SAVED RECORDS |
| 338-row strict verified subset — Fixed historical XGBoost | ACR recovery subset | Five-fold molecular grouped / Molecular identity | — | NOT ASSESSABLE | -2.46284508675258 | VERIFIED FROM SAVED RECORDS |
| UNSPECIFIED — UNSPECIFIED | UNSPECIFIED | UNSPECIFIED / UNSPECIFIED | 0.3301 | REPORTED â€” SUPPORTING RECORDS NOT FOUND | 0.2990 | REPORTED â€” SUPPORTING RECORDS NOT FOUND |

These are the existing saved values and their recorded statuses; displaying them does not recompute them.
