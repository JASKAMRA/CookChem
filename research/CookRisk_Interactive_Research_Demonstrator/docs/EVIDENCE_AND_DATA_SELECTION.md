# Evidence, Dataset Registry, and Data Selection

## Dataset and result roles

These files and result families have different purposes, targets, and provenance. Equal row counts or shared observation IDs do not make them interchangeable.

| Family | Shape / target | Demonstrator role | Identity and principal limit |
| --- | --- | --- | --- |
| Historical Stage A benchmark | 1,124 rows; `Retention_Final` | Saved metrics only | Historical input digest and current referenced digest differ in prior records. Equation, units, and scale are unresolved; source CSV is not loaded. |
| Batch021 ACR | 1,016 × 38; ACR | Saved fixed-audit results and validation metadata | Current file and saved audit input SHA-256: `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`. Not used for live exploration. |
| Reconstruction ACR | 1,016 × 43; ACR | Live record-level exploration in the three approved sections; separate saved model evidence | Owner-approved hash: `f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0`. Approval is limited to this demonstrator use; it does not designate a canonical dataset or establish independent scientific validation. |
| Strict verified subset | 338 rows; saved ACR evaluation record | Saved mean-fold evidence only | Separate subset; no pooled OOF artifact/value was located, so pooled R² is NOT ASSESSABLE. |
| Batch021 post1000 evaluations | Multiple historical model/split outputs | Conflict evidence only | 21 component result rows were compared; three combined aggregate files fail their recorded hashes; 12 rows differ and nine agree numerically. No view is selected. |

No dataset families are combined or ranked together.

## Live Reconstruction registry entry

- **Dataset ID:** `stagea-acr-reconstruction-1016-f939`
- **Path:** `stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv`
- **Approved SHA-256:** `f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0`
- **Shape:** 1,016 rows × 43 columns; `observation_id` has 1,016 unique values.
- **Target:** `target_value_percent`; name `apparent_concentration_ratio_percent`; equation `100 * C_cooked / C_raw`.
- **Permitted live sections:** Evidence Explorer, ACR Distributions, and Cooking & Compound Patterns only.
- **Designation:** owner-approved for demonstrator live exploration only; not canonical and not independently scientifically validated by this approval.

The loader checks the requested dataset ID, recorded approval scope, repository-relative path, SHA-256, row count, ordered schema, unique IDs, and row-level target name/equation/semantics. Missing or changed data, unknown IDs, and invalid target metadata fail closed. There is no fallback to Batch021 or another CSV.

## Batch021 historical reference

- **Dataset ID:** `stagea-batch021-historical-1016-111064`
- **Path:** `stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv`
- **Shape:** 1,016 rows × 38 columns.
- **Target:** ACR, `100 * cooked_concentration / raw_concentration`.
- **Role:** historical dataset metadata and existing saved evaluations only.

The saved fixed-audit summary records the same input SHA-256 as the current Batch021 file. This supports input-byte attribution only; no historical model was freshly rerun. Batch021 remains separate and is not a live-record fallback.

## Model and validation evidence

The application reads the eight read-only deliverables in `reports/final_model_r2_consolidation_2026-11-20/`. The final consolidation is the primary source for displayed model/R² values and statuses. Saved result values are shown as stored; no training, inference, prediction generation, pooled-metric recalculation, or historical artifact repair occurs.

### Historical Stage A — `Retention_Final`

| Model | Pooled OOF R² | Pooled evidence | Mean-fold R² | Mean-fold evidence |
| --- | ---: | --- | ---: | --- |
| Extra Trees | 0.255978 | REPORTED — PROVENANCE INCOMPLETE | 0.380461 | VERIFIED FROM SAVED RECORDS |
| Random Forest | 0.237074 | REPORTED — PROVENANCE INCOMPLETE | 0.341500 | VERIFIED FROM SAVED RECORDS |
| RBF-SVR | 0.254597 | REPORTED — PROVENANCE INCOMPLETE | 0.379352 | VERIFIED FROM SAVED RECORDS |
| XGBoost | 0.275012 | REPORTED — PROVENANCE INCOMPLETE | 0.383296 | VERIFIED FROM SAVED RECORDS |
| Tuned XGBoost initial record | 0.283247 | CONFLICTING SAVED EVIDENCE | 0.400376 | CONFLICTING SAVED EVIDENCE |
| Tuned XGBoost separate replay | 0.275796 | CONFLICTING SAVED EVIDENCE | 0.394287 | CONFLICTING SAVED EVIDENCE |

The four initial untuned mean-fold values match five saved folds each. The replay output report, fold, OOF, and comparison records match its sidecar, but the replay input SHA is absent. Both tuned versions remain visible; neither is selected. The ambiguous QA JSON `R² = 0.380461` matches Extra Trees mean-fold R² and is not a second pooled result. Historical `Retention_Final` equation, units, and scale remain unresolved. Four benchmark configurations are incompletely recorded.

### Batch021 fixed ACR audit

| Evaluation | Pooled OOF R² | Mean-fold R² | Evidence |
| --- | ---: | ---: | --- |
| Molecular grouped | −0.067833 | −0.256216 | VERIFIED FROM SAVED RECORDS |
| DOI/source-held-out | −0.065645 | −0.206527 | VERIFIED FROM SAVED RECORDS |

The result records identify ExtraTreesRegressor (25 trees), GroupKFold(5), and their exact grouping. Six targeted artifacts match sidecars and the summary input SHA matches Batch021. These remain historical metrics, not fresh reproduction. DOI/source-held-out is a source-family proxy, not independent-laboratory validation.

### Reconstruction ACR saved evaluation

| Evaluation | Pooled OOF R² | Pooled evidence | Mean-fold R² | Mean-fold evidence |
| --- | ---: | --- | ---: | --- |
| Molecular grouped | 0.059831 | REPORTED — PROVENANCE INCOMPLETE | 0.083504 | VERIFIED FROM SAVED RECORDS |
| Source held-out | −0.073710 | REPORTED — PROVENANCE INCOMPLETE | −0.253519 | VERIFIED FROM SAVED RECORDS |

The saved configuration is historical XGBoost with reduced features. Mean-fold values are supported by saved folds; an output sidecar/build-time digest is absent. The record is not the Batch021 experiment and is not independent validation.

### Strict subset and unresolved claim

- **Strict verified subset:** XGBoost mean-fold R² −2.462845, VERIFIED FROM SAVED RECORDS; mean-fold standard deviation 6.775628 is documented in the consolidation. Pooled R² is NOT ASSESSABLE because no pooled OOF artifact/value was located.
- **Friend-reported claim:** pooled 0.3301 and mean-fold 0.2990 remain UNVERIFIED; supporting dataset, target, model, split, and records were not found. These values are not model achievements.

### Post1000 conflict handling

Twenty-one per-model comparison/fold/OOF component files and JSON/Markdown summaries match their sidecars. Three combined comparison/fold/OOF files fail their recorded hashes. Twelve of 21 model/protocol comparison rows differ in R², MAE, and RMSE; nine rows agree numerically, while the aggregate remains checksum-invalid. The JSON lacks a run-specific input SHA. An alternate static runner is only a possible explanation. Both versions remain in the conflict register; no leaderboard, preferred view, overwrite claim, or repaired artifact is created.

## Evidence labels

- **VERIFIED FROM SAVED RECORDS:** the displayed value is traceable to cited saved evidence; no fresh model run is implied.
- **REPORTED — PROVENANCE INCOMPLETE:** a saved metric exists, but run/input identity or other provenance is incomplete.
- **CONFLICTING SAVED EVIDENCE:** preserved records disagree; no version is selected.
- **UNVERIFIED:** supporting records or essential identity details were not found.
- **NOT ASSESSABLE:** available saved evidence cannot establish the requested value.

Pooled OOF R² is computed from concatenated out-of-fold predictions; mean-fold R² is the arithmetic mean of fold R² values. They are not interchangeable. A negative R² means performance below the evaluated data's mean-prediction baseline; it does not by itself show that a historical result was overwritten.

## Scientific limits shown in the app

- ACR is `100 × C_cooked / C_raw`, an apparent concentration ratio, not total-mass retention. Compatible paired masses or validated yield plus compatible measurements would be required for total-mass retention.
- Reconstruction has 20 unit labels and 15 measurement-basis labels; bases/units remain heterogeneous and unharmonized. Paired raw/cooked source-level assay, basis, and unit compatibility is not confirmed for every source.
- Analytical definitions and replicate design are missing for some records. Repeated contexts are not established independent replicates.
- The Phase 3 report records 118 strict numeric target differences that match at displayed precision; underlying source precision remains unverified. Stored values are preserved.
- Two cooked-concentration values are zero; true zero versus detection-limit/reporting meaning is unknown.
- Outlier flags are review indicators, not error thresholds or deletion rules. Sparse groups and repeated DOI/source families limit interpretation.
- No external/prospective/independent-laboratory validation or deployment readiness is established. No clinical, patient-specific, causal, exposure, or consumer-ready claim is made.

## Local start and verification

From the repository root in Windows PowerShell:

```powershell
Set-Location .\research\CookRisk_Interactive_Research_Demonstrator
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Open `http://127.0.0.1:8501/`. For syntax and focused tests, run `python -m py_compile app.py research_data.py tests\test_dataset_registry.py tests\test_research_evidence.py` and `python -m unittest discover -s tests -v` from this folder. Do not change a registry hash to work around a failed integrity check.
