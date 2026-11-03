# Cycle 5 — cross-stage lineage and release readiness

**Status: IN_PROGRESS.** This is a read-only integrity review plus synthetic integration coverage. It does not certify scientific validity or complete Stage C/Stage D release readiness.

## Pinned data lineage

| Layer | Pinned artifact | Integrity / coverage result | Boundary |
|---|---|---|---|
| Stage B source evidence | `stageB/release/StageB_V20_20261103/data/interaction_evidence.csv` | SHA-256 `358665c339e0ab673bb846d16d30e75dbed2b9587ae4df91baddfb5493a3b8e6`; 317 source rows | Read-only input for Stage D queue and mechanism registry. |
| Stage C food composition | `Phase1B-v1.3.2` | 1,324 packaged artifacts verified; manifest SHA-256 `df3a95ae0957b68a89e38098c0824877196aa74ef7dd92573e6ab1f37e39b9b5`; 584 food rows, 584 mappings | Benchmark comparators and app catalog use the pinned release. Working-copy differences are not treated as release data. |
| Stage C cooking integration | `Phase2-v0.3.1` | 50 packaged artifacts verified; manifest SHA-256 `2b72e4df095002952fcf2eef2af3381425384317d6ea259b81676ed8c243746e` | Zero accepted cooked-concentration estimates; the app reports unavailable cooked values when evidence is not compatible. |
| Stage C recipe/meal engine | `Phase3-v0.1.2` | 47 packaged artifacts verified; manifest SHA-256 `8a0d532ff35cc8ac88d5cedc0231caf35b94aebac6501c30c55b5db48ff1a9ec` | Raw-reference results are retained distinctly from cooked estimates; transient outputs are not eligible for evidence comparison. |
| Stage C mechanism evidence | `Phase4-v0.1.2` | 18 packaged artifacts verified; manifest SHA-256 `9d6a3a13d6567a872bfb890cf02ea118648a8572c92ebdd8e33b970d0f889fba` | Evidence candidates remain unapproved and must not be read as accepted mechanisms. |
| Stage D review | derived queue | 317 unique `Evidence_ID`s retain source rows and source hash; 317 remain `NOT_REVIEWED` | Machine routing is separate from source verification and human decisions. The action log remains empty in the current workspace. |

The four current package manifests were checked against their listed file hashes, byte counts, artifact counts and manifest-digest sidecars. The Phase1B release's own verifier independently returned `PASS` for all 1,324 artifacts. Historical release folders were not edited or replaced. The Phase3-v0.1.2 isolated test suite passes against the pinned package.

## Cross-stage synthetic integration

`stageC/tests/test_cycle5_integration.py` exercises recipe calculation → meal aggregation → uncertainty coverage. It checks explicit Stage B provenance and blocks a comparison when the Phase3 result comes from a transient, unverified release. Application API tests separately verify raw-reference and consumed amount fields in exports, no cooked number without compatible evidence, provenance in catalog and evidence records, and that a pending comparison cannot create a clinical interpretation.

All inputs in this integration fixture are synthetic. These tests verify software contracts, not scientific performance. Missing intervals remain missing; compound totals stay separated; no cross-compound addition or source-free evidence link is allowed.

## Application persistence and exposure

The local prototype binds only to loopback. Its reviewer log is separate from Stage B source records, append-only, hash-chained, and schema-checked. The action schema is version 1.0.0; there were no prior events to migrate, and future schema changes require an explicit migration before old actions are reused. Successful reviewer actions receive a versioned cumulative backup snapshot; a backup failure is surfaced while leaving the already-appended action trace intact. The repository currently has no real reviewer actions. Synthetic API mutation tests use temporary files and clean them up.

The review corpus is 317 records. The application uses local JSON/CSV reads and an append-only JSONL action log; there is no database service or remote endpoint. No performance bottleneck has been demonstrated at this corpus size, so profiling and optimization were not justified. No production-scale, concurrency, load, security, privacy, or accessibility qualification is claimed.

## Integrity and remaining gates

- `git status --short -- stageA stageB` was empty; Stage A and Stage B tracked source content is unchanged.
- Repository HEAD remained `8545029a4bae1bc923fdc840bbfe681b2d7bef03`; no branch, index, commit, or history operation was performed.
- All active Stage C, Stage C Phase 4, and Stage D JSON schemas passed Draft 2020-12 metaschema validation: **33 valid**.
- Synthetic end-to-end recipe/meal/uncertainty and transient-release refusal test: **1 passed**.
- Release hash checks establish byte integrity only. They do not establish that source observations are correct or that any model is validated.
- Remaining gates include Stage A owner decisions and an approved package; source-compatible cooked measurements; independent human review of Stage D evidence; expert-approved interpretation policy; and broader scientific validation against genuinely commensurate cooked observations and model outputs.

No evidence of a performance bottleneck arose during the limited local tests. A profiler or load test was not warranted by this 317-record scope, and calculation semantics and architecture were not changed for speed.
