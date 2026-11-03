# Phase 2 closeout and Phase 3 foundation — progress checkpoint

Updated: 2026-11-03

## Completed modules

### Milestone 1 and Phase1B

- Restored the two verified root Batch 106 snapshot files from commit `1c51885`; preserved NHDC evidence in the V20 versioned Phase1B package.
- Added `.gitattributes` rule `stageC/releases/** -text` for exact release-byte handling. No historical release contents were rewritten.
- Built Phase1B-v1.3.1 from the archived v1.3.0 release bytes. Counts were independently derived from the packaged food, mapping, coverage, and V20 identity tables:
  - 584 total records and mappings: 335 ordinary food, 221 ingredients, 28 beverages.
  - 130 raw-mapped IDs; 125 identity-complete and 5 pending in V20.
  - 121 accepted mappings; 116 scientifically eligible quantitative compounds across all classes and 80 in ordinary food.
  - The 125 figure in v1.3.0 was identity-complete mapped coverage, not quantitative eligibility. The earlier user-authorized closeout remains historically recorded; the corrected eligibility count does not meet the approximate 120 or 130 target.
- The release reconciles 11 stale identity flags against V20 without changing values or mappings, preserves nine raw mapping rows that were not accepted, and contains the new checkpoint, report, and reconciliation tests.
- Phase1B-v1.3.1 package manifest verified: 1,324 artifacts; SHA-256 `ad0d4a03e27022d8efade756c48ccd1d792d40608f9dd9674bc55190e1851da8`.

### Phase 2

- Corrected the 33 turmeric `measurement_unit` labels to the primary table wording “mg/g plant material”; no numeric values changed. The cooked-sample denominator remains documented as unresolved.
- Independently rebuilt the 117-pair source audit: 117 records, 0 audit errors, 33 basis-limited turmeric rows, and ratios recomputed from reported group means.
- Reviewed all 63 source-condition candidates: 30 `PENDING_SOURCE_BASIS`, 33 `PENDING_MATRIX_COMPATIBILITY`.
- Finalized all 22 compatibility combinations: 10 `PENDING_SOURCE_BASIS`, 11 `PENDING_MATRIX_COMPATIBILITY`, 1 `QUALITATIVE_ONLY`.
- Finalized all 584 applicability rows: 569 with no linked evidence, 10 pending source basis/matrix, 1 pending matrix, and 4 qualitative-only.
- Reviewed all 197 identity crosswalk rows: 19 strict accepted, 1 existing Curcumin manual match with CID warning, 27 structure-equivalence pending, 9 name/structure pending, 9 manual source adjudications, 127 no Stage B CID match, and 5 no CID.
- Kept cooked-concentration output at zero. Two missing historical log files are named and explained in the successor manifest; no logs were reconstructed.
- Released Phase2-v0.3.0 as `COMPLETE_WITH_DOCUMENTED_LIMITATIONS`, linked to Phase1B-v1.3.1 manifest SHA `ad0d4a03e27022d8efade756c48ccd1d792d40608f9dd9674bc55190e1851da8`. Release manifest SHA: `2d1ca237cbf0f74233e48eddc0a0acea67b7797dffee33adc3ba723745842f65`.

### Phase 3

- Added the recipe/meal architecture, JSON Schemas, and `stage_c.recipe_engine` with JSON save/load, validation, explicit per-ingredient and recipe mass balance, quantity conversion, raw ingredient exposure, compatible Phase 2 interval application, recipe/meal aggregation, provenance, and direct-food/recipe double-count protection.
- Raw food calculations reuse the Phase 1 exposure engine. Volume/mass conversion requires verified density; beverages can use mg/L × explicit volume. Cooked output requires all four Phase 2 compatibility gates and measured cooked mass/volume; without them the raw reference amount remains clearly separate and cooked exposure is incomplete.
- Clinical interpretation and Stage A inference are excluded.

## Tests

- Phase1B v1.3.1 reconciliation package: 3/3 passed.
- Targeted Phase1B regression modules: 36/36 passed.
- Phase2 v0.3.0 bundled release tests: 7/7 passed.
- Phase2 source audit, integration, retention arithmetic, and Phase3 recipe/meal modules: 24/24 passed.
- Full `stageC/tests` regression suite: 132/132 passed.
- The initial full-suite run exposed one obsolete test assertion expecting `NOT COMPLETE`; it was updated to assert the completed-with-limitations decision and the reviewed record counts, then the full suite passed. Initial Phase2/Phase3 test attempts also exposed assertion precision/path issues; those tests were corrected and final focused/bundled runs pass.

## Remaining modules and scientific limitations

- Phase 2 numerical cooked estimates remain unavailable until source denominator, matrix, conditions, and cooked-yield evidence satisfy compatibility. No current estimate is withheld solely by software.
- Identity adjudication remains open for the 27 structure-equivalence, 9 name/structure, 9 within-group CID conflict, 127 no-Stage-B-CID, and 5 no-CID groups. They remain visible and cannot be joined automatically.
- Phase 3 has a tested software foundation but no end-user interface, large recipe library, or Phase 2 numeric retention factor to demonstrate cooked estimates against.
- The environment has no `jsonschema` package. Schema files parse as JSON and the standard-library validators and fixtures pass; formal Draft 2020-12 metaschema validation was not available.
- Exact historical test logs referenced by Phase2-v0.2.0 could not be recovered; their absence is recorded in Phase2-v0.3.0.

## Known workspace/tooling blockers

- Git metadata is read-only here: creating the requested work branch and writing the index were denied. Work is preserved on `main`; nothing was committed. New packages and `.gitattributes` are present in the workspace and manifest-verified.
- An archived-byte comparison found Phase1B-v1.3.0 (1,323 files), Phase2-v0.1.0 (20 files), and Phase2-v0.2.0 (44 files) byte-identical to Git archive blobs. Phase1-v1.3.0 has 877 newline-only differences in the current worktree; its Git archive blobs remain intact and the attributes rule is set for future checkouts. No historical package was rewritten.
- Stage A model/input files were not accessed, changed, retrained, or run. Stage B was not modified.

## Next concrete work

1. When Git metadata is writable, create a `codex/` branch and commit the already-validated workspace changes without rewriting historical releases.
2. Add a Draft 2020-12 validator to the environment or CI and validate both Phase3 schemas against it.
3. When scientifically compatible cooking evidence and measured cooked yield become available, test the Phase3 cooked interval path against that specific evidence. Until then, keep cooked results unavailable.

## Latest continuation — release-chain verification

This section supersedes the earlier test summary and next-action list above where they differ.

### Completed in this continuation

- Regenerated the recipe and meal example outputs from the final Phase3 CLI. The apple recipe reports a raw-reference total of 11.2950 mg; the apple+cocoa meal reports 21.11650 mg. Both use zero Phase2 quantitative cooking records and are not cooked-dose estimates. Recipe mass balance remains `INCOMPLETE` because the illustrative recipe does not provide the required measured batch-yield inputs.
- Corrected the repository-level Phase2 verifier to resolve the release directory when invoked from `stageC/scripts/`. Both the repository command and the packaged Phase2 command now report `PASS`.
- Verified Phase1B-v1.3.1's outer manifest (1,324 artifacts; SHA-256 `ad0d4a03e27022d8efade756c48ccd1d792d40608f9dd9674bc55190e1851da8`) and its dedicated reconciliation tests (3/3 passed).
- Verified Phase2-v0.3.0's manifest and all 49 files; release tests pass 7/7. Manifest SHA-256 remains `2d1ca237cbf0f74233e48eddc0a0acea67b7797dffee33adc3ba723745842f65`.
- Verified Phase3-v0.1.0's 26-artifact manifest; SHA-256 `2f63783dae14680a50b57b88f09785f836225a128a56778c22e95085d39f1477`. Its isolated package suite ran 26 tests (23 passed, 3 schema tests skipped); recipe/meal release integration tests pass 5/5.
- Full `stageC/tests` regression suite: 154 tests run, 151 passed, 3 skipped, 0 failed (82.6 seconds). The skipped tests require the unavailable `jsonschema` dependency for formal Draft 2020-12 validation.
- No Stage A or root Stage B files were changed. No Git metadata operation was performed. Historical releases remain unchanged.

### Phase1B nested dependency integrity blocker

- The dedicated Phase1B-v1.3.1 reconciliation tests and outer package manifest pass, but a separate full discovery run inside its embedded `stageC/tests` suite ran 86 tests and reported 7 failures and 19 errors. Failures include tests asserting earlier historical counts/checkpoints; integration errors include `StageB exact manifest verification failed`.
- The embedded StageB_V20 manifest lists 839 artifacts. In the current Windows working copy, 829 have CRLF-only hash mismatches; the remaining 10 match exactly. All 839 manifest-listed raw Git blobs in the unchanged Phase1B-v1.3.0 predecessor were independently checked against the embedded StageB manifest and match exactly. The new Phase1B-v1.3.1 copy remains CRLF-converted in this working tree, so the attribute rule alone does not repair its current bytes.
- The StageB source package was not modified. The Phase1B successor itself needs a byte-exact packaged dependency and refreshed checksums, followed by coordinated Phase2/Phase3 dependency-hash successors. Keep v1.3.1 and v0.3.0 immutable while doing that. The user handles Git writes, so clean-checkout verification must follow once the corrected package and attributes are committed by the user.

### Exit assessment and next action

- Phase2 scientific review is complete for the frozen 117 observations, all 63 candidates, all 22 combinations, all 584 applicability rows, and all 197 identity crosswalk rows. Zero cooked-concentration estimates are justified. However, under the prompt's release-integrity criterion, Phase2 is **BLOCKED** until the Phase1B embedded dependency discrepancy is resolved and the corrected release chain is verified.
- Phase3 recipe/meal engineering is implemented and tested for raw-reference exposure and explicit mass/volume accounting. Its cooked path correctly remains unavailable without eligible Phase2 evidence. Schema JSON parses and custom validation passes; formal Draft 2020-12 validation is still skipped because `jsonschema` is not installed.
- Next: prepare a byte-exact Phase1B patch successor from the authoritative raw Git blobs (without editing StageB or v1.3.0), then create Phase2 and Phase3 patch successors with the new upstream hashes. Run the targeted package suites and one final full Stage C suite after that chain is stable.

## Final continuation — corrected release chain

This section supersedes the blocker and next-action statements immediately above.

- Created Phase1B-v1.3.2 as a patch successor, preserving v1.3.1. Its embedded StageB_V20 copy was restored from raw Git blobs without changing the StageB source or any scientific values. All 839 internal manifest entries match. Outer manifest: 1,324 artifacts; SHA-256 `df3a95ae0957b68a89e38098c0824877196aa74ef7dd92573e6ab1f37e39b9b5`. The four reconciliation/byte-integrity tests pass.
- Phase1B's inherited embedded suite still reports 70 passed, 11 failed, and 5 errors out of 86. The remaining cases expect historical snapshot paths, checkpoint fields, counts, release IDs, and batch states; no StageB V20 hash mismatch remains. The current repository Stage C suite is green.
- Created Phase2-v0.3.1, preserving v0.3.0, and pinned it to Phase1B-v1.3.2 manifest `df3a95ae0957b68a89e38098c0824877196aa74ef7dd92573e6ab1f37e39b9b5`. Its 50-artifact manifest verifies at SHA-256 `2b72e4df095002952fcf2eef2af3381425384317d6ea259b81676ed8c243746e`; all 7 package tests pass.
- Created Phase3-v0.1.1, preserving v0.1.0, with the corrected Phase1B-v1.3.2 and Phase2-v0.3.1 pins. Its 26-artifact manifest verifies at SHA-256 `546286e6c409048a7b5abba33f4c3be7c2cf9ec424c37991b0cb8d82ab37c31b`. The package suite ran 26 tests (23 passed, 3 schema checks skipped); pinned release integration tests pass 5/5.
- Regenerated recipe and meal CLI examples against the corrected release chain. The apple raw-reference total is 11.2950 mg and the apple+cocoa total is 21.11650 mg. Both report zero quantitative Phase2 cooked records and zero Phase4 context records; the outputs do not claim cooked-dose estimates.
- Final `stageC/tests` run: 154 tests, 151 passed, 3 skipped, 0 failed. The skipped cases require the unavailable `jsonschema` package for formal Draft 2020-12 validation.

### Final decision

**Phase2 evidence-release scope: COMPLETE_WITH_DOCUMENTED_LIMITATIONS; Phase 2 roadmap: IN_PROGRESS.** All 117 observations, 63 candidates, 22 compatibility combinations, 584 applicability rows, and 197 identity crosswalk rows are reviewed; no candidate qualifies for a cooked-concentration estimate, so the output remains zero rows. The Phase2-v0.3.1 and Phase1B-v1.3.2 release manifests and targeted suites verify. Deployment closure remains open until the Stage A owner supplies the approved model/serving decisions, target denominator and basis, hashed model/runtime package, output contract, and scientific compatibility acceptance. No model inference is authorized or required for this checkpoint.

**Phase3: foundation implemented and tested, COMPLETE_WITH_DOCUMENTED_LIMITATIONS.** Raw-reference recipe/meal calculations, explicit mass and volume accounting, provenance, leftovers/consumed portions, schemas, CLI, examples, and release adapters are in place. Cooked exposure remains unavailable without compatible Phase2 evidence and measured cooked yield. No clinical interpretation is implemented.

Stage A, the StageB source release, and historical Phase1B/Phase2/Phase3 packages were left unchanged. No branch, index, commit, or other Git metadata was written. Remaining limitations are the inherited non-green embedded Phase1B historical suite, three skipped formal schema tests, unresolved Phase2 scientific basis/yield/identity cases, and two unrecoverable historical Phase2 logs. Next: user-side clean-checkout verification of the corrected `-text` release rule, followed by formal JSON Schema validation when `jsonschema` is available.

## Advanced execution continuation — 2026-11-04

This section supersedes earlier test summaries and next-action statements above where they differ. Full roadmap status is in [ADVANCED_EXECUTION_REPORT.md](reports/ADVANCED_EXECUTION_REPORT.md).

### Completed and verified

- Formal Draft 2020-12 validation is enabled with pinned `jsonschema==4.26.0` and pinned transitive dependencies. All seven active Stage C schemas pass metaschema validation; recipe/meal positive and negative fixtures run without skips.
- Corrected recipe and meal string-decimal constraints that previously allowed out-of-range fractions, and tightened runtime identifier/type validation. Added explicit tests for missing food mapping and missing batch yield.
- Added `stageC/src/stage_c/cooking_integration.py` and `stageC/schemas/stage_a_prediction.schema.json`. The adapter requires input/code/model/output provenance, exact food/compound IDs, eight explicit compatibility gates, semantic labels, and a review state. Current Stage A model output remains blocked because no serialized artifact/hash or target denominator/basis is available. No inference was run.
- Added Stage C Phase 4 interval uncertainty/sensitivity support and Phase 5 independent arithmetic/reference-validation framework. Intervals preserve source type; missing uncertainty stays explicit. No published-data or external validation was conducted.
- Added Stage D architecture and comparability contracts plus a 3-record mechanism-candidate registry drawn from two primary studies. Stage B rows are preserved verbatim and source-file hash is pinned. All scientific interpretation and identity review remains pending; an endpoint discrepancy in one article is preserved for manual reconciliation.
- Built and verified immutable Phase3-v0.1.2: 47 artifacts, manifest SHA-256 `8a0d532ff35cc8ac88d5cedc0231caf35b94aebac6501c30c55b5db48ff1a9ec`. Isolated package tests pass 79/79.

### Final test checkpoint

- Stage C working-tree suite: 199 passed, 0 failed, 0 skipped.
- Stage C Phase 4 registry: 13 passed, 0 failed, 0 skipped.
- Stage D normalization/comparability/mechanism suite: 18 passed, 0 failed, 0 skipped.
- Phase3-v0.1.2 isolated package: 79 passed, 0 failed, 0 skipped.
- Historical Phase1B-v1.3.2, Phase2-v0.3.1, and Phase3-v0.1.1 releases remain preserved. Existing pinned Phase 2 data still has zero quantitative cooked estimates.

### Remaining work and blockers

- Stage C Phase 2 remains in progress until an approved, deployable Stage A artifact and target measurement semantics exist. Do not run Stage A or treat model output as measured retention.
- Stage C Phase 4 can only quantify uncertainty when sourced concentration, quantity, serving, and yield bounds are present. Current inputs often remain point-estimate-only.
- Stage C Phase 5 has no published reference comparison or external validation yet.
- Stage D mechanism, identity, and evidence-quality assessments require expert review; no automatic evidence score or clinical conclusion is available.
- Stage C and Stage D user-facing applications and final integration remain outstanding.
- Git was not modified; the user retains branch, commit, and publishing operations.
