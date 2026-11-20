# CookRisk Phase 2 — Dataset Provenance and AR-01 Report

**Execution date:** 2026-11-20  
**Scope:** Read-only provenance investigation and report creation  
**AR-01 status:** **FOUND AND HASH-MATCHED**

## Executive summary

The saved Stage A validation summary records `input_sha256` as `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`. The current Batch021 dataset at its manifest/checksum path independently hashes to that exact value, and the Batch021 `SHA256SUMS.txt` records the same digest for `updated_master_dataset.csv`. The saved input identity is therefore found and hash-matched to the current 1,016-row, 38-column Batch021 file. This establishes the input-byte identity recorded by the saved validation evidence; it does **not** reproduce or independently validate the historical model metrics.

The earlier `d866d0ff…d5d3c1` value remains an unresolved historical documentation/provenance discrepancy: it appears as a former “current Batch021” claim in demonstrator audit material, but no inspected Stage A manifest, checksum, or validation record associates it with an input file. Its originating artifact or version was not located in the scoped evidence. The old Reconstruction pin `16dbbd9c…52be99` likewise was not located as a file or digest in the inspected Stage A package; the current approved Reconstruction file is intact at `f9391233…f083b0`.

Current Reconstruction and Batch021 are distinct approved dataset roles: Reconstruction is approved for live demonstrator exploration only; Batch021 remains the separate historical evaluation evidence family. Reconstruction has the same 1,016 observation IDs and 38 shared columns as Batch021, plus five documented verification/provenance fields. Fifteen `target_value_percent` cells differ in serialized representation, with maximum absolute numeric difference `2.842170943040401e-14`. Its manifest does not record build-time input/output hashes, and its builder uses absolute paths from a different Windows machine; independent construction was not rerun. No canonical scientific designation was found or granted.

`Retention_Final` remains scientifically unresolved. Documentation records historical dimensions and two hashes, but equation, units, scale, and measurement basis are not established. It is not interchangeable with ACR, and total-mass retention cannot be inferred without compatible paired food masses or validated yield.

## Scope and safety boundaries

This was a read-only audit of the named demonstrator reports/docs and specifically relevant Stage A manifests, datasets, builders, checksums, and saved validation records. The only new files are the five deliverables in this isolated report directory. No datasets, predictions, model artifacts, scientific calculations, registry pins, dependencies, or historical outputs were changed. No Git write operation, build, model run, or dependency installation was performed.

Stage B and restricted Stage C/D source materials were not accessed. `research/EXISTING_RESULTS_METRICS_CATALOG.csv` was not read, searched, hashed, copied, or otherwise accessed. No broad repository scan was performed. The specifically referenced Phase 0 inventory path was checked and is absent at that path; this is not a claim that no inventory exists elsewhere.

## Files inspected and relevance

| File | Why it was inspected |
|---|---|
| `research/CookRisk_Interactive_Research_Demonstrator/reports/application_repair_and_final_qa_2026-11-19/FINAL_REPORT.md` | Phase 1 status and recorded approved application behavior. |
| `research/CookRisk_Interactive_Research_Demonstrator/reports/provenance_reconciliation_2026-11-19/COOKRISK_DATASET_IDENTITY_PROVENANCE_RECONCILIATION.md` | Phase 0 hash, lineage, prior AR-01-related discrepancy, and owner-decision evidence. |
| `research/CookRisk_Interactive_Research_Demonstrator/reports/diagnostic_audit_2026-11-19/COOKRISK_APPLICATION_DIAGNOSTIC_AUDIT.md` | Exact former pins and dataset role descriptions. |
| `research/CookRisk_Interactive_Research_Demonstrator/docs/EVIDENCE_AND_DATA_SELECTION.md` | Documented limited Reconstruction approval and Batch021 separation. |
| `research/CookRisk_Interactive_Research_Demonstrator/README.md` | Application-facing data and evidence context. |
| `research/CookRisk_Interactive_Research_Demonstrator/dataset_registry/datasets.json` | Registered IDs, pins, dimensions, targets, lineage, and approval scope. |
| `stageA/verified_concentration_ratio_reconstruction/README.md` | Reconstruction purpose, target semantics, and limitations. |
| `stageA/verified_concentration_ratio_reconstruction/manifest.json` | Declared inputs/outputs and build summary. |
| `stageA/verified_concentration_ratio_reconstruction/build_reconstruction.py` | Declared transformation and paths; inspected only, not executed. |
| `stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv` | Current Reconstruction digest, dimensions, schema, IDs, and shared-column comparison. |
| `stageA/dataset_expansion_1000/batch_021/manifest.json` | Batch021 parent digest and row-count lineage. |
| `stageA/dataset_expansion_1000/batch_021/SHA256SUMS.txt` | Batch021 dataset checksum record. |
| `stageA/dataset_expansion_1000/batch_021/reproduction_instructions.md` | Batch021 build/evaluation provenance context. |
| `stageA/dataset_expansion_1000/batch_021/dataset_expansion_report.md` | Batch021 expansion evidence context. |
| `stageA/dataset_expansion_1000/batch_021/build_batch_021.py` | Parent/build/checksum behavior; inspected only, not executed. |
| `stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv` | Current Batch021 digest, dimensions, schema, IDs, and comparison source. |
| `stageA/dataset_expansion_1000/batch_020/updated_master_dataset.csv` | Candidate parent bytes named by the Batch021 manifest. |
| `stageA/molecular_vs_source_validation_audit/README.md` | Saved validation design and interpretation context. |
| `stageA/molecular_vs_source_validation_audit/validation_summary.json` | Historical validation input digest, target, row count, and saved results metadata. |
| `stageA/molecular_vs_source_validation_audit/fold_metrics.csv` | Saved fold-output identity and dimensions. |
| `stageA/molecular_vs_source_validation_audit/SHA256SUMS.txt` | Saved validation artifact checksum records. |
| `stageA/molecular_vs_source_validation_audit/validation_comparison.py` | Input hashing and evaluation protocol implementation; inspected only, not executed. |

The previously referenced `research/CookRisk_Interactive_Research_Demonstrator/reports/dataset_target_registry_phase0_2026-11-19/DATASET_FILE_INVENTORY.csv` was checked and is not present at that exact path. No contents were read from any other inventory candidate.

## Dataset identity evidence

| Item | Expected/documented SHA-256 | Freshly measured SHA-256 | Dimensions / identity | Result |
|---|---|---|---|---|
| Reconstruction current CSV | Approved pin `f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0` | `f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0` | 1,016 × 43; 1,016 unique, nonblank `observation_id` values | Pin matches; demonstrator-only live exploration approval. |
| Batch021 current CSV | Approved pin and validation input `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8` | `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8` | 1,016 × 38; 1,016 unique, nonblank `observation_id` values | Pin and saved validation input digest match. |
| Batch020 parent CSV | Batch021 manifest parent pin `31c2059e3f90f8733461e7ba263856ee2b86a5da24537fdf035ee3648d95cb0d` | `31c2059e3f90f8733461e7ba263856ee2b86a5da24537fdf035ee3648d95cb0d` | 938 × 38; 938 unique, nonblank `observation_id` values | Parent digest matches manifest; Batch021 records 78 added rows. |
| Saved validation summary JSON | Batch021 checksum sidecar: `0d7563a63f6bca310ab5d16d4b15e07ba4cc78388a4dc7443c4e9ba8851cc662` | `0d7563a63f6bca310ab5d16d4b15e07ba4cc78388a4dc7443c4e9ba8851cc662` | JSON metadata; records 1,016 rows, `target_value_percent`, equation `100 * cooked_concentration / raw_concentration`, input SHA `111064…669c8` | Saved evidence artifact hash matches sidecar. |
| Saved fold metrics CSV | Validation checksum sidecar: `21d8925e0349b994ea5b58c6875a952c00ee5e99db04e0663ffb7e400acfac65` | `21d8925e0349b994ea5b58c6875a952c00ee5e99db04e0663ffb7e400acfac65` | 10 × 11; fold/strategy metrics, no observation ID field | Saved artifact hash matches sidecar; not an observation-level input. |
| Former Reconstruction expected snapshot | Historical demonstrator pin `16dbbd9c38a21675a2644b415289004e5a8eb7091e97a96dae645ed2bf52be99` | NOT LOCATED in the scoped inspected evidence | No file with this digest was identified among the named Reconstruction, Batch021, or validation artifacts | Prior pin remains unexplained; do not infer global absence. |
| Former Batch021 “current” claim | Prior demonstrator claim `d866d0ffab8c335e0469f2815c3cdf518b3d019be1bdf2e37ba2ced2e7d5d3c1` | NOT LOCATED as an inspected Stage A dataset/checksum digest | No associated file identity or dimensions established | Originating artifact/version remains unresolved. |
| Historical `Retention_Final` source | Prior documentation records current `cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27` and historical `750124efc8b89dff1f67764064b1049b5db51fb1b2f222d4f91cd94c56945f89` | NOT MEASURED; source CSV was not read or hashed in this audit | 1,124 × 47 is documented, not freshly measured | Equation, units, and measurement basis remain unresolved. |

Machine-readable evidence is in `DATASET_IDENTITY_AND_HASH_EVIDENCE.csv`.

## Task A — Existing project evidence

The scoped reports, registry, README, Stage A manifests, checksum sidecars, build descriptions, and saved validation artifacts listed above were reviewed. They agree that the current Reconstruction file is a 43-column derivative of the 38-column Batch021 family, and that historical evaluation evidence is saved separately. The cited Phase 0 inventory CSV is missing at its referenced path, so no evidence from it is claimed. No broader inventory search was performed.

## Task B — AR-01 historical validation input investigation

### Status: FOUND AND HASH-MATCHED

The full 64-character hashes were checked in the named prior provenance and diagnostic reports and in the specific Stage A records relevant to this lineage: Reconstruction `manifest.json`; Batch021 `manifest.json` and `SHA256SUMS.txt`; validation `validation_summary.json` and `SHA256SUMS.txt`. The exact `111…` digest is recorded as the validation input and Batch021 CSV digest. The exact `d866…` digest is not recorded by those inspected Stage A provenance/integrity files. The exact `16db…` digest is documented as a former demonstrator pin, not as a digest in the inspected Stage A Reconstruction manifest/checksum evidence.

Evidence chain:

1. `stageA/molecular_vs_source_validation_audit/validation_summary.json` records the full `input_sha256` `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`, dataset row count 1,016, target `target_value_percent`, and equation `100 * cooked_concentration / raw_concentration`.
2. The saved summary itself hashes to `0d7563a63f6bca310ab5d16d4b15e07ba4cc78388a4dc7443c4e9ba8851cc662`, matching the validation `SHA256SUMS.txt` entry.
3. The current documented candidate, `stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv`, freshly hashes to the exact recorded input digest and has 1,016 rows × 38 columns.
4. `stageA/dataset_expansion_1000/batch_021/SHA256SUMS.txt` independently lists the same exact digest for `updated_master_dataset.csv`.

This establishes the saved evaluation's input-byte identity by its recorded SHA-256 and the matching current Batch021 candidate. It does not establish a fresh rerun, reproduce the saved metrics, or prove scientific validity. No training or evaluation script was executed.

### Reconciliation of `d866…` and `111…`

The full `d866d0ffab8c335e0469f2815c3cdf518b3d019be1bdf2e37ba2ced2e7d5d3c1` appears in prior demonstrator audit/provenance material as a then-current Batch021 value. It is not the digest listed in the inspected Batch021 manifest/checksum and is not the `input_sha256` in the saved validation summary. No Stage A file bearing that digest or a record explaining its origin was identified in the scoped search. The current `111…` value is confirmed for the current Batch021 file and saved evaluation input; the historical source/version behind `d866…` remains unresolved. Calling the `d866…` claim stale relative to current inspected bytes is supported; claiming its exact origin or the historical date it changed is not.

### Reconciliation of old Reconstruction pin `16db…`

The full `16dbbd9c38a21675a2644b415289004e5a8eb7091e97a96dae645ed2bf52be99` is present as the previous demonstrator pin in the scoped reports. The current Reconstruction CSV is `f939…`, and no file or Stage A manifest/checksum in the scoped inspected package links to the old digest. The exact `16db…` bytes were **not located within the inspected scope**; this is not a claim that they do not exist elsewhere.

## Task C — Reconstruction provenance

- **Current file integrity:** verified; full SHA matches approved pin `f9391233…f083b0`.
- **Current shape and identifiers:** 1,016 rows × 43 columns; all 1,016 `observation_id` values are nonblank and unique.
- **Relationship to Batch021:** same 1,016 observation IDs; 38 shared columns; five added fields: `verified_concentration_ratio_percent`, `target_verification_status`, `original_retention_final_provenance`, `calculated_ratio_percent`, and `ratio_calculation_abs_difference`.
- **Shared-column comparison:** only `target_value_percent` differs in serialized text across shared fields, for 15 observations; maximum numeric absolute difference is `2.842170943040401e-14`. This tiny serialization-level difference is not evidence of an independently validated scientific correction.
- **Documented derivation:** the builder reads Batch021 plus historical source/ledger inputs, starts its final table from the Batch021 data, then appends the five fields. The manifest lists the inputs and outputs and reports 1,016 final rows. Its paths are absolute paths rooted under `C:\Users\kamra\Desktop\BTP\CookChem\stageA`, not portable repository-relative inputs.
- **Build hashes:** the Reconstruction manifest has no build-time input hashes or output hash; the inspected package has no Reconstruction output checksum sidecar establishing the old `16db…` bytes.
- **Independent reproduction:** NOT PERFORMED. Current hash and derivation description are verified separately; they do not show that the construction was independently rebuilt from the exact historical source bytes.
- **Canonical status:** not designated canonical. Existing approval is limited to live demonstrator exploration.

The evidence supports current file integrity and documented derivation, but not a definitive classification of the `16db…` → `f939…` byte change as a legitimate new release versus an unrecorded rewrite. Do not promote the Reconstruction beyond its existing limited role.

## Task D — Batch021 historical evidence

Batch021 is the 1,016 × 38 historical evidence family. Its current bytes match both the approved pin and saved validation `input_sha256`. Its manifest records a 938-row parent with SHA `31c2059e…95cb0d`, 78 new rows, and 1,016 total rows; the named Batch020 parent file independently matches the recorded parent hash and has 938 × 38 rows. The Batch021 checksum sidecar includes the current master CSV digest.

The saved validation summary and fold metrics are preserved artifacts with checksum-matched identities. The validation summary records the input digest, target, and evaluation metadata; the saved fold metrics comprise 10 rows × 11 columns. This evidence supports an exact recorded input-byte identity and saved outputs, not independent metric reproduction. No model was trained and no historical artifact was regenerated or changed.

## Task E — `Retention_Final` status

The inspected registry and prior provenance report document a historical source with 1,124 rows × 47 columns, a previously documented current digest `cd51de…0358c27`, and a historical digest `750124…6945f89`. These are documentary values only in this audit: the source CSV was not read or hashed. The Reconstruction builder lists a historical input at an absolute path and retains a provenance mapping, but the build manifest does not record that input's digest.

The equation, units, scale, and measurement basis for `Retention_Final` remain UNKNOWN. Its equivalence to ACR is NOT ESTABLISHED. ACR is an apparent concentration ratio, `100 × C_cooked / C_raw`; total-mass retention requires compatible paired food masses or validated yield in addition to concentration information. No such inference is made here.

## Evidence-strength distinctions

| Evidence level | What is established | What is not established |
|---|---|---|
| Current file integrity | Exact SHA-256 and dimensions for current Reconstruction, Batch021, and Batch020 candidate files. | Correctness of the underlying scientific measurements by hash alone. |
| Saved historical input identity | Validation summary records `111…`; current Batch021 candidate and checksum sidecar match. | A newly rerun evaluation or independent verification of saved metrics. |
| Documented lineage | Batch021 manifest names Batch020 parent hash; Reconstruction docs/builder describe Batch021-based derivative and five added fields. | Exact Reconstruction build-time input bytes, complete portable lineage, or an independently repeated build. |
| Scientific validation | Reconstruction target labels ACR and records concentration measurements; saved validation design metadata is available. | Canonical designation, independent scientific validation of Reconstruction, causal inference, or total-mass retention. |

## Provenance gaps and owner decisions

See `PROVENANCE_GAP_REGISTER.csv` and `OWNER_DECISIONS_REQUIRED.md` for the complete structured list. Key unresolved items are the origin of `d866…`, the unlocated old `16db…` Reconstruction bytes, missing Reconstruction build-time digests, unresolved `Retention_Final` semantics, and no independent rerun of historical metrics. Existing owner approval remains limited to Reconstruction live exploration and Batch021 historical evidence separation.

## Risks and limitations

- A matching SHA-256 establishes byte identity with the recorded digest, not validity of measurements or model conclusions.
- The stale `d866…` value cannot be tied to a permitted file/version; do not substitute it for the verified current Batch021 digest.
- Reconstruction's matching observation IDs do not make it the same dataset snapshot or make its additional fields independently validated.
- Tiny target serialization differences are recorded, not treated as scientific recalculation or correction.
- Historical `Retention_Final` must remain separate from ACR until primary-source or owner adjudication establishes its definition and units.
- The Phase 0 inventory path is missing; this report's scope is the explicit evidence list above, not an exhaustive repository inventory.

## Phase 3 readiness and exact next steps

Phase 3 presentation/UI work can safely begin **only as a presentation-only phase** while preserving the current dataset-family separation and integrity gates. Keep Reconstruction labeled as limited demonstrator exploration at its verified `f939…` digest, and keep Batch021 historical results labeled with their original dataset, target, split, and saved provenance. Do not make fresh-reproduction, canonical-dataset, causal, or total-mass-retention claims.

Before any scientific scope expansion or provenance repair:

1. Ask the owner to supply or identify the artifact/version behind the historical `d866…` claim and, if required, the exact prior `16db…` Reconstruction snapshot.
2. Record whether the Reconstruction's missing build-time hashes are an accepted historical limitation or whether a future, separately authorized provenance-rich rebuild is desired.
3. Obtain source/owner adjudication for `Retention_Final` equation, units, scale, and measurement basis before showing it as a scientific target.
4. Obtain explicit scientific approval before canonical designation, model reruns, metric updates, or uses beyond the documented demonstrator role.
5. Preserve the current matched AR-01 status as input identity evidence only; any independent reproduction must be a separately authorized, controlled task.

No owner decision is needed to maintain the already documented separation of live Reconstruction exploration and historical Batch021 evidence. Any departure from that separation requires a new explicit decision.
