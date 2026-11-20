# Generalization and Reproducibility Summary

## Generalization evidence is protocol-specific

The app labels each saved metric with its dataset family, target, model/configuration, split protocol, grouping unit, and evidence status. Molecular grouping and DOI/source-held-out results are not interchangeable. DOI grouping is a source-family proxy and does not demonstrate independent laboratories, external validity, prospective performance, or future generalization. Negative R² indicates performance below the evaluated observations' mean-prediction baseline; it is not evidence of overwrite by itself.

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

## Reproducibility status

- **Batch021 fixed audit:** the saved summary input hash matches the current Batch021 SHA-256. This supports attribution to the saved input bytes; it is not a fresh reproduction. The recorded model is ExtraTreesRegressor with 25 trees, `min_samples_leaf=2`, `max_features=0.8`, `random_state=42`, and GroupKFold(5).
- **Historical Stage A benchmark:** prior records document different historical/current `Retention_Final` input digests; the original source CSV was not opened in this task. Pooled values are reported with incomplete provenance. Fold-derived means for the untuned baseline match saved fold records.
- **Stage A tuned XGBoost:** the initial and replay result pairs conflict; no preferred version is established. Replay output sidecars match, but replay input identity is incomplete.
- **Reconstruction XGBoost:** saved fold records support the mean-fold values; output sidecar/build-time digest is absent, so pooled values retain incomplete provenance.
- **Strict verified subset:** five saved folds support its mean-fold result; pooled OOF evidence was not located and remains NOT ASSESSABLE.
- **Post1000:** three combined aggregate hashes conflict with recorded pins; 12 of 21 comparisons differ and nine agree. No aggregate winner is selected.

## Data identity and role

The live Reconstruction snapshot is 1,016 × 43, SHA-256 `f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0`. It is owner-approved for live demonstrator exploration only, not canonical designation or independent scientific validation. Batch021 is a distinct 1,016 × 38 historical reference, SHA-256 `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`, used only for saved results and metadata.

The `Retention_Final` target semantics and units remain unresolved. ACR means `100 × C_cooked / C_raw`, an apparent concentration ratio; it is not total-mass retention. Source-specific units/bases, assay compatibility, replicate independence, and external validation remain limitations. The application reads saved evidence and does not train, predict, or recalculate metrics.
