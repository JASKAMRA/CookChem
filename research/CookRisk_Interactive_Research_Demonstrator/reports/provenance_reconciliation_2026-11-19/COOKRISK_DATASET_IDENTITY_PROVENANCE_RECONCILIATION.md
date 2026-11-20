# CookRisk Dataset Identity and Provenance Reconciliation

**Audit date:** 2026-11-19  
**Purpose:** Resolve the documented reconstruction, Batch021, and 439-row prototype identity/provenance discrepancies before changing any application loader configuration.  
**Method:** Read-only review of manifests, build/validation scripts, checksum sidecars, saved reports/state, and row/schema comparisons. No build, model, or data-generation scripts were executed. No existing file was changed. Stage B and restricted Stage C/D source material were not accessed; no Git write operation or dependency installation was performed.

## Reconciliation table

| Dataset | Expected hash | Actual hash | Identity established? | Provenance status | Owner decision needed? |
|---|---|---|---|---|---|
| Verified concentration-ratio reconstruction (`final_verified_master_dataset.csv`) | Demonstrator pin: `16dbbd9c38a21675a2644b415289004e5a8eb7091e97a96dae645ed2bf52be99` | `f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0` | **Underlying observation identity: yes** — same 1,016 observation IDs and 38 source columns as current Batch021. **Exact intended byte-version: no.** | Current file is consistent with the reconstruction builder’s stated operation: copy Batch021 and add five verification/provenance columns. Fifteen `target_value_percent` values differ from Batch021 only by floating-point serialization (max absolute delta `2.842170943040401e-14`). The reconstruction package has no output checksum file and its manifest records no input or output hashes; the expected `16db…` bytes were not found in the inspected Stage A artifacts. | **Yes.** Choose whether the demonstrator should use this 43-column derivative and its current hash, the Batch021 base file, or a separately preserved historical reconstruction byte snapshot. No explicit canonical ACR owner designation was found. |
| Batch021 ACR master (`updated_master_dataset.csv`) | Demonstrator's documented “current” value: `d866d0ffab8c335e0469f2815c3cdf518b3d019be1bdf2e37ba2ced2e7d5d3c1`; Batch021's recorded current/input digest: `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8` | `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8` | **Yes for the present file and its current audit-input identity.** Its digest matches Batch021 `SHA256SUMS.txt`, `CONTINUOUS_RECOVERY_STATE.json`, and the molecular/source validation summary's `input_sha256`. Its 938-row parent digest also matches Batch020. | The `d866…` value appears in the demonstrator configuration/docs but not in the inspected Stage A checksum, manifest, state, or validation records. Its originating file/version could not be established; it is unsupported as the present file's hash. | **Yes before changing app/docs.** Owner should approve updating the displayed current hash/status to the verified `111…` value and decide what attribution statement the saved validation artifacts support. |
| 439-row parent (`recovery_v1_0_0/expanded_clean_stageA_dataset.csv`) | Prototype manifest and recovery checksum: `d3960dc6ec808ca1783cbb2c57d35fb4676da04feeff675280c1f07eb072005a` | `d3960dc6ec808ca1783cbb2c57d35fb4676da04feeff675280c1f07eb072005a` | **Yes.** | Current parent matches the manifest digest and recovery package checksum. The prototype's `authoritative_v1_dataset_copy.csv` also has this exact digest, independently linking the packaged copy to the parent bytes. | **No** to establish this parent link. Owner decision is needed only before accepting/re-running the prototype's drifted build/validation scripts as the reproducible recipe. |
| 439-row prototype output (`final_modelling_dataset.csv`) | Prototype `SHA256SUMS.txt`: `1fea513ac44777411357df6ac7d084eecd97cd08f956d3ac23e38695552554d1` | `1fea513ac44777411357df6ac7d084eecd97cd08f956d3ac23e38695552554d1` | **Yes for the saved dataset artifact and its parent-record linkage.** | Sidecar digest matches current output. It contains the same 439 unique observation IDs and all 34 parent columns/values; the one added column is `eligibility_reason`. Target name/equation/semantics agree with the parent: apparent concentration ratio, `100 * C_cooked / C_raw`, not total-mass retention. The adjacent saved `model_comparison.csv` hash also matches its sidecar. Some code-file checksums do not match the sidecar and `run.log` is absent, limiting exact recipe reproducibility, but not the observed parent/output dataset link. | **No** for dataset parent/output identity. **Yes** before claiming the current scripts reproduce these saved outputs or authorizing a new run. |
| Historical `Retention_Final` input listed as a reconstruction input | Historical digest documented in demonstrator evidence text: `750124efc8b89dff1f67764064b1049b5db51fb1b2f222d4f91cd94c56945f89`; not recorded in the reconstruction manifest | `cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27` | **Current file identity: yes; historical byte identity: no.** | This is one of the reconstruction builder's declared inputs, used to map historical `Record_ID`/DOI/molecule records. The manifest supplies an absolute path from another Windows machine, but no input digest. Present bytes differ from the separately documented historical digest. It remains `Retention_Final`, not ACR. | **Yes** if the owner wants the 338 historical mappings attributed to a particular historical benchmark snapshot. Do not equate its target with ACR. |
| v0.1 source-to-target mapping ledger listed as a reconstruction input | None recorded in reconstruction manifest | `b4b05438252cf95b3d27d4998c250a26175b91f9b198493fb53f626d3717a408` | **Current file identity: yes; build-time byte identity: no.** | Declared input for adjudicating historical mapping/exclusion statuses; current repository-relative file exists. The reconstruction manifest records neither its digest nor a portable relative path. | **Yes** if the owner needs the 338 mapping decisions attributed to the exact ledger snapshot used at build time. |

## Findings and evidence

### 1. Reconstruction is an enriched Batch021 derivative, not an independent row set

The reconstruction builder's `main()` reads the historical benchmark, the v0.1 source-to-target ledger, and `batch_021/updated_master_dataset.csv`. It verifies historical records by exact record ID, DOI, and canonical molecular ID, then sets the final table from the Batch021 table and appends five fields: `verified_concentration_ratio_percent`, `target_verification_status`, `original_retention_final_provenance`, `calculated_ratio_percent`, and `ratio_calculation_abs_difference`.

The current files confirm that lineage at the record level:

- Both files contain 1,016 rows and 32 DOI families. Batch021 has 38 columns; the reconstruction has 43.
- All Batch021 observation IDs are present in the reconstruction. All 38 shared columns match except 15 tiny changes in the serialized `target_value_percent`; the largest numerical change is about `2.84e-14`. The other fields are semantically identical.
- The target label/equation in both files are `apparent_concentration_ratio_percent` / `100 * C_cooked / C_raw`. The reconstruction adds verification status/provenance; its manifest summary reports 338 `verified_unchanged` historical mappings and 678 `new_primary_source_verified` records. “New” here is a status relative to mapping the historical 1,124-row set; these 678 records are already in Batch021, not an additional 678 rows beyond it.
- The reconstruction records a maximum difference of `0.004822448472793894` percentage points between its stored ratio and a direct formula calculation, consistent with stored source rounding. This does not change the target to total-mass retention.

These findings support the reconstruction file being a generated/re-exported derivative of Batch021, rather than an unrelated or obviously misselected dataset. They do **not** prove that its current bytes are the exact intended release. Its manifest lists output filenames but no input/output SHA-256 values; no `SHA256SUMS.txt` is present; the expected `16db…` artifact was not found among the inspected Stage A files. The manifest and builder also retain absolute paths under `C:\Users\kamra\Desktop\BTP\CookChem`, which do not resolve in this checkout. The builder's current declared input paths exist as equivalent repository-relative files, but their exact hashes at the time the current reconstruction was generated are not recorded.

Therefore the available evidence cannot conclusively classify the `16db…` → `f939…` byte change as a legitimate newer release versus an unrecorded rewrite. It does show that the current file's observation set and scientific target align with the builder's Batch021-based construction. No explicit owner-designated canonical ACR dataset was found; Stage A state calls the target experimental, and the demonstrator explicitly says its selection is not canonical.

### 2. The two Batch021 hashes refer to different claims

- `111064…669c8` is the current SHA-256 of `stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv`. It is also the file's entry in Batch021 `SHA256SUMS.txt`, the current `dataset_sha256` in Stage A `CONTINUOUS_RECOVERY_STATE.json`, and the `input_sha256` in the saved molecular/source validation summary.
- Batch021 `manifest.json` declares its parent digest as `31c205…cb0d`; this equals the current Batch020 master digest and Batch021's parent digest. Batch021's own checksum list verifies its present output digest as `111064…669c8`.
- `d866d0…d5d3c1` is the demonstrator's configured/documented “current Batch021 CSV” value. No matching source digest was found in the inspected Stage A manifest, checksum, state, or validation artifacts. Its exact source/version is unknown. The evidence supports calling it a stale demonstrator value, not the current Batch021 file hash.

Thus the saved validation summary is tied by digest to the current Batch021 input path. That match alone does not freshly reproduce the saved metrics or validate every downstream result. Any revised attribution text should retain the distinction between “same input bytes” and “metrics independently reproduced.”

### 3. The 439-row parent and data-output link are established; package code provenance is not fully clean

The v1.0 recovery manifest declares parent dataset digest `d3960…005a`, which matches the present 439-row parent and its `SHA256SUMS.txt`. The prototype manifest records that same parent digest and includes `authoritative_v1_dataset_copy.csv`; the copy's current digest is also `d3960…005a`. The prototype `SHA256SUMS.txt` lists the current final modelling dataset as `1fea…554d1`, which matches the file, and the current model-comparison output hash also matches its entry.

The prototype manifest's parent path is an absolute path under `C:\Users\kamra\Desktop\BTP\CookChem` and is unavailable in this checkout. The exact-byte packaged copy resolves that path problem for dataset identity. Parent and final model output each have 439 unique IDs; all parent IDs occur in the output, the 34 shared columns have identical numeric values, and the final output adds `eligibility_reason`. Its validation script checks 439 rows, 10 DOI families, the apparent-ratio target name, and no saved model or Stage C integration authorization.

The prototype sidecar is not a clean checksum of every current package file: 34 entries matched, while `prediction_interface.py`, `run_final_prototype.py`, and `validate_final_prototype.py` differed from their listed hashes and `run.log` was missing. The two dataset artifacts and model-comparison file just described did match their entries. This is a code/reproduction-package drift warning; it does not negate the verified dataset parent/output digest links.

## Confirmed findings

- The current Batch021 CSV is byte-identical to the file identified by `111064…669c8`; `d866d0…d5d3c1` is not supported as its present digest by the Stage A records inspected.
- The current reconstruction is the same 1,016-row observation set as Batch021 with five added verification/provenance columns. Its 15 shared target-string differences are at floating-point serialization precision, not meaningful scientific changes.
- The reconstruction build package lacks hashes for its inputs and outputs, and its old absolute input paths prevent a faithful replay from this checkout without path adaptation. The expected `16db…` file itself was not found in the inspected Stage A artifacts.
- The 439-row parent relation is confirmed by an exact SHA-256 match, including a packaged parent copy. The final model dataset's saved checksum matches current bytes and its rows/target align with the parent.
- No explicit owner-designated canonical ACR dataset appears in the inspected records. Stage A says the target is experimental and not authorized for Stage C integration; the demonstrator says no canonical designation is established.

## Unresolved discrepancies

- Which exact bytes the demonstrator's `16db…` reconstruction pin was intended to identify, and whether those bytes can be recovered from an authorized archive.
- Whether the current `f939…` enriched derivative should be the demonstrator's selected record-level representation or whether the owner prefers the underlying Batch021 CSV.
- The origin of the stale `d866…` Batch021 value and whether the owner approves updating application/documentation status to the verified `111…` value.
- Which precise historical benchmark/ledger snapshots were used when the reconstruction output was built; its manifest has no input hashes.
- Whether the current prototype scripts whose hashes differ from its sidecar are intentional edits, and whether they are acceptable for future reproducibility claims.

## Exact owner decisions required

1. **Record-level dataset designation:** Select the intended application input by repository-relative path and SHA-256: Batch021 (`111064…669c8`) or the enriched reconstruction (`f939…f083b0`), or supply the preserved bytes corresponding to `16db…52be99`. Confirm target field name/equation and that the selection is not being designated canonical unless that is explicitly intended.
2. **Batch021 status text:** Approve using `111064…669c8` as the present Batch021 digest in app metadata and confirm whether the saved validation summaries may be labeled as using that same input snapshot (without calling them freshly reproduced).
3. **439-row future reproduction:** Decide whether the three current scripts that disagree with the prototype checksum sidecar are approved versions before anyone reruns them or claims exact computational reproducibility.

## Safest next implementation step

Do not change loader pins yet. Obtain the owner’s written snapshot choice and, for the reconstruction choice, bind the accepted file to a new provenance record containing its repository-relative path, digest, row/column counts, target semantics, and hashes of its exact source inputs. If the owner selects a preserved `16db…` snapshot, they must identify where to retrieve those exact bytes. Keep current fail-closed behavior until that decision is recorded. Separately, after approval, correct the stale Batch021 hash claim and distinguish digest-matched historical input from independently reproduced model results.

## Files inspected

- Prior diagnostic: `research/CookRisk_Interactive_Research_Demonstrator/reports/diagnostic_audit_2026-11-19/COOKRISK_APPLICATION_DIAGNOSTIC_AUDIT.md`
- Demonstrator source/config/docs: `research/CookRisk_Interactive_Research_Demonstrator/research_data.py`, `app.py`, `README.md`, `docs/EVIDENCE_AND_DATA_SELECTION.md`, and `DEMONSTRATOR_COMPLETION_REPORT.md`
- Reconstruction: `stageA/verified_concentration_ratio_reconstruction/manifest.json`, `build_reconstruction.py`, `README.md`, `final_verified_master_dataset.csv`, `original_1124_observation_audit.csv`, `target_calculation_audit.csv`, and `source_provenance_manifest.csv`
- Batch021 and parent: `stageA/dataset_expansion_1000/batch_021/manifest.json`, `SHA256SUMS.txt`, `updated_master_dataset.csv`, `validate_batch_021.py`; Batch020 `updated_master_dataset.csv` and `SHA256SUMS.txt`; `stageA/CONTINUOUS_RECOVERY_STATE.json`; `stageA/molecular_vs_source_validation_audit/validation_summary.json` and `fold_metrics.csv`
- 439-row lineage: `stageA/recovery_v1_0_0_2026_11_10/manifest.json`, `SHA256SUMS.txt`, `expanded_clean_stageA_dataset.csv`; `stageA/final_prototype_2026_11_10/manifest.json`, `SHA256SUMS.txt`, `authoritative_v1_dataset_copy.csv`, `final_modelling_dataset.csv`, `model_comparison.csv`, and `validate_final_prototype.py`
- Reconstruction-declared historical inputs: `stageA/input/cookchem_molecular_retention_preprocessed.csv` and `stageA/recovery_v0_1_0_2026_11_10/source_to_target_ledger.csv`

**Files changed:** This new reconciliation report only. No existing file, dataset, manifest, application loader, or historical artifact was modified.
