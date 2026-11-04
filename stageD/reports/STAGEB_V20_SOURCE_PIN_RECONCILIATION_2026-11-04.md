# StageB V20 source pin reconciliation — 2026-11-04

**Status: RECONCILED IN STAGE D WORKING CODE.** Stage B source files were not modified. This is a derived-queue/provenance correction; it is not a scientific review decision.

## Finding

- StageB V20 manifest `stageB/release/StageB_V20_20261103/manifests/SHA256SUMS.json` lists `data/interaction_evidence.csv` as SHA-256 `5c095c6ee22d8d998888d3d47bc4ae2fcabf17faf4df0bee8aad7d6bb9af1cec`.
- The current CSV is 529728 bytes and hashes to `5c095c6ee22d8d998888d3d47bc4ae2fcabf17faf4df0bee8aad7d6bb9af1cec`. The 839 entries in the V20 manifest all verify against current bytes.
- Stage C/Stage D working code and derived review artifacts were still pinned to `358665c339e0ab673bb846d16d30e75dbed2b9587ae4df91baddfb5493a3b8e6`. The old digest was therefore stale for the current StageB V20 file and made Stage D queue rebuilds and the application health load fail closed.
- Parsing current CSV rows and comparing every field against the prior 317-record queue showed **317/317 exact row matches**, with no changed Evidence_ID or source field. This establishes row-data continuity, not byte-level continuity.
- The append-only human review action log did not exist at reconciliation time. Existing queue and reviewer artifacts were preserved before regeneration in [`pre-rebind snapshot`](source_integrity_incident/stageb_v20_pre_rebind_snapshot/).

## Correction performed

- Updated the Stage D queue source SHA and Stage C app StageB input pin to the hash already recorded by the read-only V20 package manifest.
- Rebuilt the 317-record queue, 25-row mechanism registry, unassigned 317-record reviewer export, and coverage dashboard from the verified CSV.
- Stable review IDs and assignment ID changed because they are hash-scoped. No prior human actions existed to migrate. All 317 records remain `NOT_REVIEWED`; source verification remains `NOT_PERFORMED`; no decision or negative inference was added.
- Stage C app now reports the corrected StageB hash and continues to enforce the Phase4 integrity gate. Phase4 context remains withheld; this correction does not weaken or bypass its hash checks.

## Verification

- StageB V20 source SHA-256: `5c095c6ee22d8d998888d3d47bc4ae2fcabf17faf4df0bee8aad7d6bb9af1cec`; V20 listed artifact hashes: 839/839 pass.
- Rows: 317; all prior queued source-record dictionaries equal current CSV row dictionaries.
- Regenerated queue: 317 records; machine triage categories retained; human state 317 `NOT_REVIEWED`.
- Regenerated mechanism registry: 25 records with source file hash `5c095c6ee22d8d998888d3d47bc4ae2fcabf17faf4df0bee8aad7d6bb9af1cec`.
- Reviewer assignment: 317 rows, `decisions_created: false`.
- Review action history: absent before regeneration; no events imported or fabricated.
- Focused and full software tests are recorded separately in the continuation report after the code change.

## Limits

The earlier SHA `358665c339e0ab673bb846d16d30e75dbed2b9587ae4df91baddfb5493a3b8e6` was already embedded in the prior committed Stage D code/artifacts. The current Git history provides no separate earlier StageB V20 CSV copy at that digest from which to infer why the pin became stale. The V20 manifest and present CSV establish the source bytes used for this rebind. StageB identity/source semantics and all human review states were left unchanged.
