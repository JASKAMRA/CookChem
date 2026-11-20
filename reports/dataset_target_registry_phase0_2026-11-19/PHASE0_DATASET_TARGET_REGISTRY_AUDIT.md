# CookRisk Phase 0 — Dataset & Target Registry Audit

**Audit date:** 2026-11-19  
**Repository root:** current workspace (`CookChem`)  
**Status:** READ-ONLY AUDIT COMPLETE; REGISTRY IMPLEMENTATION BLOCKED pending explicit owner designation.

## Executive result

No reviewed decision record explicitly designates a canonical or demonstrator-approved ACR snapshot. The existing record-level loader remains correctly fail-closed: it expects the reconstruction file hash `16dbbd9c38a21675a2644b415289004e5a8eb7091e97a96dae645ed2bf52be99`, but the file at that path is currently `f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0`. The intended `16db…` bytes were not found among the permitted, inventoried dataset artifacts. No loader, pin, dataset, application, Stage A source, or historical artifact was changed.

**The evidence supports candidate identities and lineage, but not the owner’s intended dataset choice.** Batch021 is the best-supported current full ACR master by checksum and parent lineage; this is an evidence ranking only, not an approval. The reconstruction is a closely matching enriched derivative with a missing build-time hash chain. The 439-row prototype has a verified parent/output link but is a subset. Historical `Retention_Final` remains a separate target with unresolved scale and units.

## Owner-decision check

| Decision required | Evidence checked | Result |
| --- | --- | --- |
| Approve Batch021 (`111064…669c8`) as the demonstrator record-level dataset | Dataset-selection docs, reconciliation report, Stage A handoff/state and Batch021 records | **NOT FOUND.** The hash is strongly corroborated for the present file, but no owner selection is recorded. |
| Approve the enriched reconstruction (`f939…f083b0`) instead | Same records plus reconstruction manifest/build materials | **NOT FOUND.** Its present identity is known; its intended byte-version is not established. |
| Recover and use the pinned `16db…52be99` bytes | Permitted dataset inventory, manifest/checksum references, exact-hash check | **NOT FOUND.** The value appears as an application/documentation pin, but no inventoried dataset has that SHA-256. |
| Approve correcting the Batch021 “current” hash and provenance wording | Demonstrator references compared with Batch021 sidecar/state/validation input | **NOT FOUND.** Current file hash `111064…669c8` is corroborated; displayed `d866d0…d5d3c1` is unsupported by the inspected Stage A records. |
| Approve current 439-row prototype scripts for future reruns | Prototype sidecar and prior provenance reconciliation | **NOT FOUND.** Dataset parent/output linkage is verified; three code-file hashes differ from the saved sidecar. |
| Approve canonical semantics/units for historical `Retention_Final` | Reviewed historical benchmark and documentation | **NOT FOUND.** Preserve as a separate target; its original equation, scale and units remain unresolved. |

The Stage A `STAGE_A_RF01_RF15_HUMAN_DECISION_HANDOFF_2026-11-04.md` records **0 of 15 decisions approved** and does not identify a scientific owner/reviewer. The unrelated M1 authorization request is explicitly not an ACR dataset choice. Recommendations in reports were treated as recommendations, not approvals.

## Ranked candidate evidence

Ranks express **evidence for a dataset’s stated role**, never canonical authority. The detailed candidate table contains 138 candidate/related tabular artifacts, with hashes, row/column counts, schema, ID-set fingerprints, target fields, Batch021 comparisons, sidecar status, and a per-file rationale. The 570-file inventory includes supporting manifests, checksums and metadata as well as datasets.

| Evidence rank | Candidate | Current bytes and structure | Evidence and suitability | Authorization |
| --- | --- | --- | --- | --- |
| A1 — strongest full ACR identity | `stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv` | SHA-256 `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`; 1,016 × 38; 1,016 unique `observation_id`s | Its digest matches Batch021 `SHA256SUMS.txt`, Stage A recovery state, and saved validation `input_sha256`. Its parent digest matches Batch020 (`31c205…cb0d`, 938 rows); the manifest records 78 new rows. Target is `apparent_concentration_ratio_percent`, `100 × C_cooked / C_raw`. Strongest current full-master identity evidence; experimental and not owner-designated. | **NOT APPROVED** |
| A2 — enriched full ACR derivative | `stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv` | SHA-256 `f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0`; 1,016 × 43; 1,016 unique IDs | Same observation-ID set and 38 shared columns as Batch021, plus five verification/provenance fields. The 15 serialized shared target differences have maximum absolute difference `2.842170943040401e-14`; the target remains ACR. Builder reads Batch021 and adds verification fields, but its manifest has no input/output hashes. Consistent with a derivative; cannot establish whether `f939…` is an intended newer release or an unrecorded rewrite. `16db…` is absent. | **NOT APPROVED** |
| B1 — linked prototype output | `stageA/final_prototype_2026_11_10/final_modelling_dataset.csv` | SHA-256 `1fea513ac44777411357df6ac7d084eecd97cd08f956d3ac23e38695552554d1`; 439 × 35; 439 unique IDs | Sidecar hash matches; all 439 parent IDs and 34 parent columns/values match the parent copy; one added eligibility field. ACR target. A valid linked saved output for its limited prototype cohort, not a full ACR master. Three current prototype scripts differ from their sidecar hashes; this limits rerun reproducibility claims. | Dataset link verified; no owner designation |
| B2 — prototype parent | `stageA/recovery_v1_0_0_2026_11_10/expanded_clean_stageA_dataset.csv` | SHA-256 `d3960dc6ec808ca1783cbb2c57d35fb4676da04feeff675280c1f07eb072005a`; 439 × 34; 439 unique IDs | Exact hash is recorded in the recovery/prototype manifests and checksum records; the prototype’s packaged parent copy is byte-identical. This is a subset with a verified lineage, not the complete 1,016-row master. | **NOT APPROVED** |
| B3 — strict source-verified subset | `stageA/989_observation_recovery_audit/expanded_verified_original_subset.csv` | SHA-256 `a315dbb632d3dc3c62ecdc60bddec4cb26d3cbb6fb229661825e2553be8415f8`; 338 × 48; 338 unique `Record_ID`s | IDs match the 338-row strict sensitivity cohort and map to the corresponding Batch021 `original_record_id`s. This is a filtered source-verified historical subset, not a full master. The separate `strict_338.csv` is 338 × 51 with the same ID set but different columns/bytes; do not treat the files as byte-equivalent. | **NOT APPROVED** |
| C1 — sequential experimental ACR masters | `stageA/dataset_expansion_1000/` batch master files | Batch001: 451 rows, `7c0e…3ab8`; Batch002–021 hashes and counts are in the lineage CSV | Available manifests chain parent digests from the 439-row `d396…005a` parent through Batch021. Batch014 and Batch017 directories are absent, but Batch015 and Batch018 parent hashes connect to the preceding extant outputs. These are successive experimental snapshots; recency does not establish approval. | **NOT APPROVED** |
| C2 — recovery versions | `stageA/recovery_v0_2_0_2026_11_10/` through `recovery_v1_0_0_2026_11_10/` | v0.2: 117 × 32 (`b5a5…6c22`); v0.3: 338 × 34 (`9476…9f24`); v0.4: 374 × 34 (`60ba…e8db`); v0.5/v0.6 same 379 × 34 bytes (`72b1…9cc0`); v0.7: 407 × 34 (`9af2…ffba`); v0.8/v0.9/v1.0 same 439 × 34 bytes (`d396…005a`) | ACR experimental versions. v0.7→v0.8 and v0.8→v0.9/v1.0 have recorded parent-hash lineage. v0.3–v0.6 have no adjacent manifest parent digest in the inventoried files. Earlier versions and duplicate bytes are not additional independent datasets. | **NOT APPROVED** |
| H1 — historical benchmark, kept separate | `stageA/input/cookchem_molecular_retention_preprocessed.csv` and `data/preprocessing/final/cookchem_molecular_retention_preprocessed.csv` | Both SHA-256 `cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27`; 1,124 × 47; exact byte duplicates | Target is `Retention_Final`; it is not established as ACR. A separately documented historical hash `750124…5f89` does not match current bytes. Do not use for ACR views or infer equation/units from the column name. | Historical role documented; current canonical designation/semantics not resolved |
| H2 — mixed sensitivity/final tables | `data/final/stageA_final_dataset.csv` (1,104 × 51, SHA `f0fbe50e…d5a24a`), plus `stageA/dual_dataset_sensitivity_analysis/{strict_338,extended_948,exploratory_989}.csv` | IDs and targets differ by table; see candidate CSV | These tables contain historical `Retention_Final` and calculated-ratio/target fields with distinct inclusion rules. `stageA_final_dataset.csv` has 948 historical IDs in common, 156 IDs not in the 1,124-row benchmark and omits 176; its `target` equals the calculated ratio in this file. Not a canonical substitute for either master. | **NOT APPROVED** |

`DATASET_CANDIDATE_RANKING.csv` is the per-artifact table. Its “rank” is a role/evidence tier, not a recommendation to deploy that candidate. No candidate is owner-approved for the demonstrator.

## Exhaustive discovery scope and results

The structured inventory covers the permitted Stage A, data, Stage A experiment, EDA, molecular-feature, computational-prototype, demonstrator documentation/report, and project research-report areas. It records **570 files**: 481 CSV/TSV, 53 JSON metadata files, one XLSX, and 35 checksum sidecars. The tabular files were hashed and parsed for row count, column count/schema, available IDs and target fields; no parse errors were recorded. The XLSX was inventoried by workbook/sheet metadata. `DATASET_FILE_INVENTORY.csv` preserves the per-file results. `ACR_MASTER_LINEAGE.csv` records exact manifest parent digests and resolves them to current dataset hashes when possible.

The expected reconstruction hash `16db…52be99` is absent as an actual SHA-256 among the inventoried artifacts. Its textual appearances are in the demonstrator pin and documentation. No permitted project archive/backup or non-CSV columnar dataset candidate was identified outside the demonstrator’s local dependency environment. The local environment contains third-party package test fixtures, not CookRisk dataset versions.

Checksum summary from inventoried files: **379 sidecar entries match; 8 are mismatched**; the rest have no sidecar entry. The mismatches concern five Batch021 analysis outputs, two Stage A expansion support CSVs, and a checksum file’s self-entry. The Batch021 master dataset itself matches its sidecar. The reconstruction has no output sidecar. For the prototype, the saved parent and dataset-output hashes match, while the prior reconciliation identified three code-file hash mismatches and a missing `run.log`.

**Scope exception, recorded transparently:** A final broad extension sweep calculated read-only hashes for some extra repository paths before recognizing their scope. It touched `research/EXISTING_RESULTS_METRICS_CATALOG.csv`, which may contain cross-stage/restricted material, and `research/CookRisk_Interactive_Research_Demonstrator/.audit-venv-20261119/Lib/site-packages/` package fixtures. It did not parse or use the catalog contents, and it will not be inspected further. The protected `stageB/`, `stageC/`, and `stageD/` directories were pruned from that walk. The aggregate catalog’s bytes were nevertheless read to compute its hash; therefore this audit cannot claim a perfectly maintained no-access boundary. No protected-stage source data was used as evidence, and no files were changed by the scan.

Two additional root-level CSV names were seen in the same pass: `ACADEMIC_REVIEW_ISSUES.csv` and the cross-stage catalog above. Their contents were not parsed or included in the candidate ranking. The candidate ranking is exhaustive for the reviewed Stage A dataset families and the initial permitted inventory, with this explicit limitation on unrelated or potentially protected aggregate material.

## Proposed dataset/target registry specification

The IDs below are **proposed stable identifiers only**. They must not become active registry selections until their designation is approved. Every record should carry the following fields: stable dataset ID; repository-relative path; SHA-256; row and column counts; schema reference; target field; target equation and scientific meaning; measurement basis and units where known; parent dataset ID; source/input hashes where available; provenance status; owner designation status; allowed application uses; and explicit restrictions/unresolved issues.

| Proposed dataset ID | Path / current hash / shape | Target and scientific meaning | Lineage / provenance | Proposed allowed use and restriction |
| --- | --- | --- | --- | --- |
| `STAGEA-HIST-RETENTION-1124-CD51` | `stageA/input/cookchem_molecular_retention_preprocessed.csv`; `cd51…8c27`; 1,124 × 47 | `Retention_Final`; original equation, scale, and units **unresolved**; do not call ACR. | Current bytes exactly duplicate the `data/preprocessing/final/` file. Historical documentation also names a nonmatching `7501…5f89` hash. | Historical benchmark/metrics only under its documented historical interpretation. No record-level ACR use; retain separate until target is adjudicated. |
| `STAGEA-ACR-BATCH021-1016-111064` | `stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv`; `111064…69c8`; 1,016 × 38 | `target_value_percent`; `apparent_concentration_ratio_percent = 100 × C_cooked / C_raw`; an apparent concentration ratio, not total-mass retention. | Parent Batch020 is 938 rows, `31c205…cb0d`; current output hash corroborated by sidecar, Stage A state and saved validation input. | Candidate for record-level ACR only after explicit owner approval. Not canonical by inference; do not infer total-mass retention or reconcile source-specific bases silently. |
| `STAGEA-ACR-RECON-1016-F939` | `stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv`; `f939…83b0`; 1,016 × 43 | ACR target plus verification/provenance fields; same ACR equation. | Same observation set as Batch021; current builder reads Batch021 plus historical input and a mapping ledger, but build-time input/output hashes are absent. Expected `16db…` bytes not found. | Candidate only after owner selects exact bytes and they are provenance-bound. No silent pin update or fallback. |
| `STAGEA-ACR-STRICT338-VERIFIED` | `stageA/989_observation_recovery_audit/expanded_verified_original_subset.csv`; `a315…15f8`; 338 × 48 | `verified_concentration_ratio_percent` alongside historical `Retention_Final`; ACR remains `100 × C_cooked / C_raw`. | 338 IDs match the strict cohort and map to Batch021 original records. Related `strict_338.csv` is a distinct 338 × 51 file with its own hash. | Subset/sensitivity use only, after approval; label inclusion and target explicitly. Never present as the full master. |
| `STAGEA-ACR-PROTOTYPE439-1FE` | `stageA/final_prototype_2026_11_10/final_modelling_dataset.csv`; `1fea…54d1`; 439 × 35 | ACR, `100 × C_cooked / C_raw`. | Output hash and parent link to `d396…005a` are verified. Current scripts have checksum drift. | Existing saved prototype outputs may be referenced with their scope. Do not claim exact rerun reproducibility or use as a full master without approval. |

`Schema_name_type` and exact column lists are in the inventory and candidate CSV. The inventory does not create approval or resolve source-specific analytical basis. For every proposed use, the registry must explicitly distinguish **verified identity** from **owner designation**.

### Scientific target contract

- **ACR:** `100 × C_cooked / C_raw`. It is a concentration ratio, not true total-mass retention. It can exceed 100%; that does not establish mass gain or retention.
- **True total-mass retention:** requires compatible raw/cooked concentration measurements and paired food masses, or a validated compatible yield. These conditions are not established for the ACR master as a whole.
- **Historical `Retention_Final`:** remains its own target; do not rename, convert, merge, or assign units/equation without authoritative evidence.
- **Model metrics:** saved results remain keyed to their recorded dataset, target, split design and provenance. A dataset selection must not rewrite, pool, or freshly recalculate historical metrics.

## Proposed fail-closed loader contract

When owner designation exists, the loader should accept a stable dataset ID from an approved registry and then:

1. Reject unknown IDs, unapproved entries, missing files, unexpected hashes, row-count changes, and absent/unknown target definitions with explicit errors.
2. Verify exact SHA-256 before reading any record-level data; do not search alternative paths or fall back to another CSV.
3. Display dataset ID, relative path, exact hash, target field/equation, measurement basis where established, provenance/designation status, and restrictions.
4. Keep saved model metrics in their own recorded result families, independent of the record-level selection.
5. Preserve the ACR/total-mass-retention distinction and historical `Retention_Final` isolation.

The current `research_data.load_acr_dataset()` already checks the exact reconstruction hash and the 1,016-row count and raises an integrity error on mismatch. The UI reports the record-level ACR views unavailable; the documented behavior is fail-closed, with no alternate dataset selected. The current loader pin is stale for the bytes at its path, but must remain unchanged until the owner selects an exact snapshot. The diagnostic report recorded the exact visible error; this audit read that report but did not freshly exercise the running application.

## Decision matrix and exact owner choices required

1. **Choose the record-level dataset** by stable ID, repository-relative path and exact SHA-256: Batch021 `111064…69c8`; reconstruction `f939…83b0`; or provide authorized access to the exact `16db…52be99` bytes. State whether this is a demonstrator browsing selection only or a canonical designation.
2. **Approve the scientific target contract:** confirm the displayed field and ACR equation, measurement basis/units to expose, and explicit statement that ACR is not total-mass retention. Identify any records that must be excluded and the documented inclusion rule.
3. **Approve Batch021 provenance correction:** whether the demonstrator may replace the unsupported `d866…d5d3c1` current-hash wording with the corroborated `111…69c8`, and whether saved validation results may be described as hash-matched to that input (without calling them independently reproduced).
4. **For a reconstruction selection:** identify/approve the exact release and its input snapshots; alternatively supply the preserved `16db…52be99` bytes. Record hashes for historical input, mapping ledger, Batch021 input, output, and build script before changing a pin.
5. **For future prototype reruns:** explicitly approve the current versions of `prediction_interface.py`, `run_final_prototype.py`, and `validate_final_prototype.py` whose bytes differ from the sidecar, or provide the intended matching versions.
6. **For historical benchmark display:** designate which 1,124-row byte snapshot applies and provide authoritative `Retention_Final` target equation, scale and units if those semantics are to be displayed as verified.

Until these decisions are recorded, the candidate statuses remain **PROPOSED/REPORTED/BLOCKED**, not owner-approved. No application behavior should change.

## Proposed implementation layout and tests (not created or run)

After owner designation, the narrow change set can be:

- `research/CookRisk_Interactive_Research_Demonstrator/data_registry/datasets.json` — approved dataset/target metadata only; no copied datasets.
- `research/CookRisk_Interactive_Research_Demonstrator/tests/test_dataset_registry.py` — isolated registry/gate tests using synthetic temporary CSVs, not project data mutation.
- Minimal `research_data.py` integration and a focused selection/provenance documentation update, with old fail-closed behavior preserved until the approved registry entry is active.

Planned tests:

1. Approved dataset ID with matching file hash loads.
2. Hash mismatch is rejected before record access.
3. Unknown dataset ID is rejected.
4. Missing file is rejected without fallback.
5. Missing or unknown target definition is rejected.
6. No fallback occurs when the approved file is unavailable or malformed.
7. ACR is labeled as concentration ratio and cannot satisfy a true-total-mass-retention target.
8. Historical `Retention_Final` remains isolated from ACR records and labels.
9. Saved ML metrics remain unchanged and independent of record-level selection.

Synthetic mutation fixtures should cover altered bytes, deleted file, unknown target, and unapproved ID. Tests are **PROPOSED; not executed**, because implementation is blocked and no selected dataset is approved.

## Verification actually performed

- **VERIFIED:** current SHA-256 values, tabular row/column counts, schema/available ID and target summaries recorded in the inventory; exact expected `16db…` hash absent from those file hashes.
- **VERIFIED:** Batch021 hash supported by checksum/state/saved validation input; parent hash connects it to Batch020.
- **VERIFIED:** reconstruction and Batch021 have identical 1,016 observation IDs; 15 tiny serialized target differences, maximum absolute difference `2.842170943040401e-14`.
- **VERIFIED:** 439-row prototype output and parent bytes have the documented exact hashes; all parent IDs/34 shared fields match.
- **VERIFIED:** historical preprocessed files are exact byte duplicates of one another; their current hash differs from the documented historical input hash.
- **VERIFIED:** existing sidecars for 379 inventoried files match; eight inventoried entries are mismatched as described above.
- **REPORTED, not freshly re-run:** prior UI diagnostic found Evidence Explorer, ACR Analysis and Cooking & Compound Patterns blocked by the reconstruction hash mismatch.
- **NOT RUN:** application tests, loader tests, or full suite. No source code changed and no owner-approved dataset exists to test as active.
- **NOT MODIFIED:** no application, dataset, manifest, model artifact, Stage A source record, historical release, dependency file or Git state.

## Files created for this audit

- `reports/dataset_target_registry_phase0_2026-11-19/PHASE0_DATASET_TARGET_REGISTRY_AUDIT.md` — this decision and registry-design report.
- `reports/dataset_target_registry_phase0_2026-11-19/DATASET_FILE_INVENTORY.csv` — per-file structured inventory.
- `reports/dataset_target_registry_phase0_2026-11-19/DATASET_CANDIDATE_RANKING.csv` — detailed evidence-ranked candidate table.
- `reports/dataset_target_registry_phase0_2026-11-19/ACR_MASTER_LINEAGE.csv` — parent hash, current child hash and path resolution for master/version candidates.

These files are all inside the newly created isolated report directory. No existing file was edited.

## Remaining blockers and recommended next task

**Blocker:** explicit owner decisions listed above, first of which is selection of exact record-level dataset bytes and target/inclusion contract. The evidence cannot determine whether the intended source is Batch021, the current enriched reconstruction, or a preserved `16db…` snapshot.

**Recommended next task:** obtain one written owner decision selecting the exact path/hash and target contract, and state whether the selection is canonical or demonstrator-only. Keep the current gate unchanged until that decision is recorded. Then implement only the approved registry entry and its focused tests.
