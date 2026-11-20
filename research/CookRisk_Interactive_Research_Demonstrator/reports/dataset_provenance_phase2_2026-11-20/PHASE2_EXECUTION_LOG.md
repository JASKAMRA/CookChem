# Phase 2 Execution Log

**Date:** 2026-11-20  
**Mode:** Read-only evidence inspection plus creation of the five requested report deliverables.  
**Overall:** Complete for the authorized scoped audit; listed provenance/scientific gaps remain open.

## Work completed

1. Read the Phase 2 master directive and reviewed the Phase 1 final QA report, prior provenance and diagnostic reports, demonstrator README, evidence/data-selection documentation, and dataset registry.
2. Inspected the specifically relevant Stage A Reconstruction and Batch021 manifests, builders, readmes/reports, checksum sidecars, saved validation summary and fold metrics. Builders were read only and not executed.
3. Recomputed full SHA-256 and dimensions for the current Reconstruction, Batch021, and Batch020 parent CSVs. Recomputed SHA-256 for the saved validation summary and fold metrics. Compared observation ID coverage and the shared columns in Reconstruction and Batch021.
4. Checked the exact former `16dbbd9c38a21675a2644b415289004e5a8eb7091e97a96dae645ed2bf52be99` and `d866d0ffab8c335e0469f2815c3cdf518b3d019be1bdf2e37ba2ced2e7d5d3c1` references within the named reports and permitted Stage A evidence. The old Reconstruction bytes and a Stage A file tied to `d866…` were not located within that scope.
5. Assigned AR-01 the required status **FOUND AND HASH-MATCHED**, because the saved validation summary input digest, current Batch021 dataset hash, and Batch021 checksum-sidecar entry are an exact full-digest match.
6. Checked the exact referenced Phase 0 inventory path; it is absent there. Did not broaden the inventory search.
7. Created the four report/evidence files and this log inside the new isolated report directory.

## Verified identity values

| Artifact | Fresh SHA-256 | Dimensions / metadata |
|---|---|---|
| `stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv` | `f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0` | 1,016 × 43; 1,016 unique observation IDs |
| `stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv` | `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8` | 1,016 × 38; 1,016 unique observation IDs |
| `stageA/dataset_expansion_1000/batch_020/updated_master_dataset.csv` | `31c2059e3f90f8733461e7ba263856ee2b86a5da24537fdf035ee3648d95cb0d` | 938 × 38; parent digest matches Batch021 manifest |
| `stageA/molecular_vs_source_validation_audit/validation_summary.json` | `0d7563a63f6bca310ab5d16d4b15e07ba4cc78388a4dc7443c4e9ba8851cc662` | Input digest `111064…669c8`; recorded dataset rows 1,016 |
| `stageA/molecular_vs_source_validation_audit/fold_metrics.csv` | `21d8925e0349b994ea5b58c6875a952c00ee5e99db04e0663ffb7e400acfac65` | 10 × 11 |

## Report verification

- Reopened all four report/evidence files after creation and confirmed they are nonempty.
- Parsed both CSV deliverables with Python's standard CSV reader: 8 data rows each; every row has the declared field count.
- Confirmed the main report includes the exact AR-01 status and the full Reconstruction, Batch021, old `16db…`, and `d866…` digests; it also covers `Retention_Final` and Phase 3 boundaries.
- Confirmed the isolated directory contains only the five requested deliverables after this log was added.
- Final report paths:
  - `research/CookRisk_Interactive_Research_Demonstrator/reports/dataset_provenance_phase2_2026-11-20/PHASE2_DATASET_PROVENANCE_AND_AR01_REPORT.md`
  - `research/CookRisk_Interactive_Research_Demonstrator/reports/dataset_provenance_phase2_2026-11-20/DATASET_IDENTITY_AND_HASH_EVIDENCE.csv`
  - `research/CookRisk_Interactive_Research_Demonstrator/reports/dataset_provenance_phase2_2026-11-20/PROVENANCE_GAP_REGISTER.csv`
  - `research/CookRisk_Interactive_Research_Demonstrator/reports/dataset_provenance_phase2_2026-11-20/OWNER_DECISIONS_REQUIRED.md`
  - `research/CookRisk_Interactive_Research_Demonstrator/reports/dataset_provenance_phase2_2026-11-20/PHASE2_EXECUTION_LOG.md`

## Tests and validation

- No application test suite was run: this task audits provenance and creates reports; no application code changed.
- Read-only integrity checks passed for the reported file digests, dimensions, ID coverage, parent digest, checksum-sidecar agreement, and report CSV structure.
- Historical model evaluation was not rerun. This is intentional; saved metrics remain historical evidence only.

## Preservation and boundaries

- The only writes made were creation of the five files listed above in this new report directory. No existing source, dataset, prediction, historical metric, model artifact, registry pin, dependency, or lockfile was edited by this work.
- No Git write operation, dependency installation, model training, or build was performed.
- Stage B and restricted Stage C/D content were not accessed. `research/EXISTING_RESULTS_METRICS_CATALOG.csv` was not accessed. No broad repository scan was performed.
- The `Retention_Final` source CSV was not read or hashed; documentary values remain explicitly documentary.

## Remaining open work

- Identify the origin/version behind the old `d866…` Batch021 claim, if an owner-held artifact exists.
- Locate the former `16db…` Reconstruction bytes only if historical byte comparison is required.
- Obtain owner/source adjudication for `Retention_Final` semantics.
- Obtain separate authorization before any rebuild, historical metric rerun/update, canonical designation, or scientific scope expansion.
