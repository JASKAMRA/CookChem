# Phase 4-v0.1.2 integrity incident report

**Formal disposition: UNRECOVERABLE from the repository and documented/accessibly reachable sources searched on 2026-11-04.** No original release bytes or trusted release metadata were recovered. This is not a claim that an undocumented owner-held archive cannot exist; no such location is identified in project documentation and external GitHub access failed. The three existing Phase 4 release folders and their manifests remain unchanged.

## Preservation and repository state

- Read-only Git state at inspection: `main`, HEAD `067c6d117bdcf4f9274606499150a859b7c791c6`; working tree was clean before this report and the evidence snapshot were created.
- Current v0.1.2 package preserved byte-for-byte under [`evidence_snapshot/Phase4-v0.1.2_observed`](evidence_snapshot/Phase4-v0.1.2_observed).
- Snapshot inventory: [`observed_snapshot_inventory.json`](evidence_snapshot/observed_snapshot_inventory.json), SHA-256 `c3103fb6ee085a395f866eb9b8ee0cdf04bf4258d30d9da56b644a6ac1332393`.
- This snapshot is evidentiary only; it is not a corrected package or a recovery candidate.

## v0.1.2 manifest and sidecar

- Manifest declares 18 release artifacts (20 observed files include the two manifest files).
- Declared detached-manifest SHA-256: `9d6a3a13d6567a872bfb890cf02ea118648a8572c92ebdd8e33b970d0f889fba`.
- SHA-256 of the current `release_manifest.json`: `978a706ac4c9bb0fbc69a95bb097bdb7b4d743795ab135eb66100e13c6cd2752`.
- The detached sidecar therefore does not verify the current manifest.
- Of 18 listed artifacts, 8 match both declared byte count and SHA-256; 10 do not.

## File-by-file v0.1.2 comparison

| Path | Manifest bytes | Observed bytes | Manifest SHA-256 | Observed SHA-256 | Result |
|---|---:|---:|---|---|---|
| `CHANGELOG.md` | 1011 | 1011 | `9b461c3ebe6f28ac2969d4d01855523096ac2d27ab52ecd9ea36acf724f3ec30` | `9b461c3ebe6f28ac2969d4d01855523096ac2d27ab52ecd9ea36acf724f3ec30` | **MATCH** |
| `PROPOSED_SCOPE.md` | 2482 | 2459 | `87bdf2ccee391d10d5ea4231a92c5a7c97b16f6108579c1685426620fe6ea322` | `1c80f867f0e8766cfe1cfb66f577c9f052494e69a6d1c7adcee97cbb88f80497` | **MISMATCH** |
| `README.md` | 1833 | 1816 | `125844bb765f185147bf36982c2cdd4e17ca7858e4740ae82cf78b973158b3ba` | `1f2557adcfbc603700ffc39d4196bd7f245d1f07878fe927770418a916606f86` | **MISMATCH** |
| `data/evidence_registry.json` | 38416 | 37869 | `90503d55928b5e0314680d0611b4f4b5d4eb7947dd8f38cbcd3f7a0333a503d3` | `6e359bfe453a02cf20fb5472529feb64477d3d791cf4d27c962772e6549ed72c` | **MISMATCH** |
| `data/source_registry.json` | 1315 | 1282 | `ea250cd1dd9181ed5869927cf0326b8f4a4dd5f8dd3342ae8e5be36a446ab482` | `a117dfc8d740aef19dac9925a326007fb3bc030b31e57089942d52f7d3bd35ed` | **MISMATCH** |
| `release_info.json` | 1900 | 1859 | `08ed6fd39e220d9a33c9b7deda2674cbc978c47f5bb5d9664a5dedbf0cff2d67` | `adfab3b71d3cc702deb9b56f15b6c119ac346372e6c35c7e284d23a5979b71bb` | **MISMATCH** |
| `reports/extraction_report.md` | 2863 | 2832 | `b92ae2218369d652b04b11abdaa4b828e12886afbf9394fb723065f8229aed8c` | `41927c34f6aa505bf0e0fc032cc06bf62a7de818ba7e5c7ee0b39a9c07918826` | **MISMATCH** |
| `reports/identity_applicability_review.md` | 1890 | 1866 | `8e717d20fb64cb1db0fe523d49b685d5f5d1bba52b2be6dead61566bf72ef443` | `3ed945d240fa0c8d317ddee223b3ce89e7ef0d57aad5f945fd2a772f48c9df41` | **MISMATCH** |
| `reports/pending_evidence_register.csv` | 2605 | 2598 | `76abc471a2e960f67412cf50c5e8738e1726add43276c497e3af8835eb187a22` | `1e8d25e2bf09d8b9736d60dc1c695b0a07b238c8e5a936b36a535d758d75bf5a` | **MISMATCH** |
| `reports/source_bibliography.csv` | 649 | 647 | `cb44cc16b7f76f57b92af7897c5c780100ff9868a245bb05465c96952f1026ff` | `bcb03eca7dbb70fcef1be7ba12e8a1897304f3d95c30162126dbbbade9cec7b8` | **MISMATCH** |
| `reports/validation_report.md` | 993 | 985 | `000266f34469a71137b72948a08b5726b6120620c929bccf613e8ebbb7f54934` | `d7c809a4f21c4ead2a6b6c6a28e49834256363a6c3b94200e7864f72e7a7ac62` | **MISMATCH** |
| `requirements-dev.txt` | 103 | 103 | `0234ec3d247779dd0c2dbf4caee15bd42fa394dc495250d5eeca2decc0663224` | `0234ec3d247779dd0c2dbf4caee15bd42fa394dc495250d5eeca2decc0663224` | **MATCH** |
| `schemas/evidence.schema.json` | 5300 | 5300 | `511867d60ccdc09395b7ac1ea6303c1901d125ddb514ad0cc6c6bcac4650a7dd` | `511867d60ccdc09395b7ac1ea6303c1901d125ddb514ad0cc6c6bcac4650a7dd` | **MATCH** |
| `schemas/source.schema.json` | 1884 | 1884 | `12f8206dfe478fdb27bdfd0ab8ea973fd341ead1fb6a784ca4cb4476161dee2b` | `12f8206dfe478fdb27bdfd0ab8ea973fd341ead1fb6a784ca4cb4476161dee2b` | **MATCH** |
| `scripts/build_release.py` | 4777 | 4777 | `4b1e1da431aa6c848f9122831c141c72cbc318fd840199e57c12e09ea46ac195` | `4b1e1da431aa6c848f9122831c141c72cbc318fd840199e57c12e09ea46ac195` | **MATCH** |
| `scripts/extract_white2016_full_text.py` | 21415 | 21415 | `755e4ad6e39bbbe3ca0d01d03626872f6da95f754a919e66f0eaba16e0ddf7b5` | `755e4ad6e39bbbe3ca0d01d03626872f6da95f754a919e66f0eaba16e0ddf7b5` | **MATCH** |
| `src/phase4_registry.py` | 5898 | 5898 | `52a6e690d8541a22419a0fc81ca828fbc037f309c861e7d3aa04b7a19c4f105a` | `52a6e690d8541a22419a0fc81ca828fbc037f309c861e7d3aa04b7a19c4f105a` | **MATCH** |
| `tests/test_phase4_registry.py` | 7025 | 7025 | `dc6aefca61269753d26e72b6996a5b3bb9b51ed9afa50730350af21bc048443c` | `dc6aefca61269753d26e72b6996a5b3bb9b51ed9afa50730350af21bc048443c` | **MATCH** |

## History and recovery search

- `git log --all -- <Phase4-v0.1.2 package path>` shows the package path first appears in commit `067c6d117bdcf4f9274606499150a859b7c791c6`; no earlier v0.1.2 package revision is available in reachable history. All Phase4 v0.1.0, v0.1.1, and v0.1.2 release folders also first appear in that same commit.
- A full same-basename/same-size search of current repository files found no file matching any of the ten manifest-expected hashes.
- A search of 6,290 reachable Git objects, filtered by the ten expected sizes and checked by SHA-256, found no exact expected blob. `git fsck --full --unreachable --no-reflogs` reported no unreachable objects.
- Earlier packages do not provide a verified recovery source: v0.1.0 has 1/15 listed artifact hash/size mismatch and a bad sidecar; v0.1.1 has 10/17 listed mismatches and a bad sidecar. v0.1.2 has 10/18 and a bad sidecar.
- The v0.1.1 and v0.1.2 current bytes for several affected artifacts are identical, but neither release manifest validates those bytes. This establishes repeated package-state inconsistency, not the provenance of the expected content.

## Current-source reproduction check and per-file classification

Compared all 18 observed package artifacts against both the preserved observed-byte snapshot and the current canonical `stageC/phase4/` source tree. All 18 snapshot entries match the current package bytes. For 9 manifest-mismatching files, the current canonical source file is byte-for-byte identical to the release artifact; the release builder's `INCLUDED` list copies those same relative paths into a package. This supports a **verified regeneration of the observed bytes from the current source tree**, but it does not recover the different bytes declared by the v0.1.2 manifest, nor independently authenticate that manifest. `release_info.json` has no canonical source counterpart and remains untraced.

Per-file machine-readable result: [`phase4_v0_1_2_file_classification.json`](phase4_v0_1_2_file_classification.json).

| Classification | Count | Meaning here |
|---|---:|---|
| `VERIFIED_REGENERATION` | 9 | Manifest-mismatching observed artifact equals current canonical source bytes and is in the builder's copy set. Not a recovered original. |
| `UNRESOLVED` | 8 | Artifact matches the manifest's declared size and digest, but the manifest sidecar fails and no independent manifest provenance exists. |
| `UNKNOWN_OR_CORRUPTED` | 1 | `release_info.json` disagrees with its manifest entry and has no canonical source counterpart or trusted recovery source. |
| `RECOVERED_FROM_TRUSTED_SOURCE` | 0 | No trusted external/recovery source found. |
| `MODIFIED_WITH_VERIFIED_PROVENANCE` | 0 | No provenance record establishing authorized modification found. |

No file is represented as the authenticated historical original. The 9 source-matching files can be rebuilt from current source inputs into a **new** version if release ownership and source provenance are approved; this investigation alone does not justify doing so.

## Independent provenance locations checked in this disposition cycle

| Location | Search and result | Provenance conclusion |
|---|---|---|
| Local Git refs and checkpoint trees | `main` and `origin/main` point to `067c6d1`; no tags exist. Two `refs/codex/turn-diffs/...` refs point to tree `d5781bbfcfc4f48e805c1aa3bd669d018036c0fb`. That tree contains the same v0.1.2 observed files and the same bad manifest digest; it has no different copy of the 10 expected artifacts. | Not an independent recovery; no missing expected bytes found. |
| Remote Git refs | `git ls-remote origin refs/heads/main 'refs/tags/*'` failed because `github.com` could not be resolved. GitHub CLI is absent; browser/search access returned no repository artifact data. | Remote refs, tags and release assets could not be queried. |
| CI configuration/artifacts | No GitHub Actions, GitLab, Jenkins, Dockerfile, Compose, environment-lock or CI workflow files are in the repository. No `gh` CLI is installed. | No local CI artifact locator; hosted CI artifacts inaccessible in this environment. |
| Repository release archives | Prior scoped archive search found Stage B historical archives and Phase 1B source-data archives, but no Phase 4-v0.1.2 archive. Phase 4 v0.1.0/v0.1.1 are present but their own manifests fail verification. | No trusted Phase 4 archive. |
| User backup/download locations | Searched `Downloads`, `Documents`, and `Desktop` for Phase4-v0.1.2/Phase4 backup/archive names; no candidate returned. | No candidate found in searched locations. |
| Documented external storage/backup | Project documentation names only local Stage D reviewer-action snapshots, unrelated to Phase 4. No Phase 4 external storage, cloud bucket, or backup location is documented; no connected storage integration is available in this session. | No documented external source to query. |

The two local Codex checkpoint refs were examined once as a distinct local history source. Their contents equal the already preserved observed package and add no independent authenticity. They were not treated as a trusted backup.

## Root-cause assessment

**Root cause is undetermined.** The mismatching bytes and stale sidecars are already present in the first Git commit that introduced all three Phase4 release directories; the repository history does not contain a prior v0.1.2 state for comparison. Current artifacts are not explained by CRLF-to-LF conversion. The available evidence cannot distinguish an incorrect historical manifest from post-generation replacement or incomplete packaging before the initial commit. Do not attribute this to a specific person, machine, or process without further evidence.

## Recovery decision

**UNRECOVERABLE** for the original v0.1.2 package from the sources searched. No byte-exact source for the manifest-declared mismatches or trusted release metadata was found. Do not regenerate its manifest, copy predecessor files into it, or represent current source matches as the original. If the owner later supplies a separately authenticated archive or backup, reopen this disposition and verify it before use.

### Separate successor-release plan (not executed)

No successor has been built or published. If the project owner approves a new release:

1. Create a new version (proposed `Phase4-v0.1.3`) and explicitly state that v0.1.2 is unrecoverable/unverified; never call it a restoration.
2. Start from the canonical `stageC/phase4/` tree and record source commit/tree IDs and every input hash. The 9 source-matching artifacts are reproducible inputs, not independent scientific provenance. Recheck the six evidence records against the cited primary publication and supplementary material; preserve all pending/zero-accepted statuses until a qualified reviewer signs off.
3. Author `release_info.json` specifically for the new version, recording the actual source revision, generator, upstream Phase1B-v1.3.2 and Phase2-v0.3.1 identities/hashes, and all limitations. Do not copy or fabricate v0.1.2 metadata.
4. Obtain owner scope approval and independent extraction, chemical-identity, and applicability reviews. Keep accepted evidence at zero unless all release criteria are met.
5. Build into a new directory using a versioned builder; validate source registries, formal schemas, focused tests and package contents before generating the new manifest. Verify all artifact hashes and detached sidecar independently, then validate a clean copy.
6. Update the app's pinned release/hash only after the successor passes those checks; test both verified-load and fail-closed paths. Publish only after explicit owner release approval.

Until those conditions are met, the application must continue to withhold Phase 4 context.

## Verification commands and results

- SHA-256 and byte counts were recomputed for every manifest-listed v0.1.2 file; result: 8 match, 10 mismatch.
- The sidecar was checked against SHA-256 of the current manifest; result: mismatch.
- Git history was inspected read-only; all Phase4 release directories were first introduced in the current parent commit; no prior Phase4-v0.1.2 revision exists.
- Repository file search and Git object search found no exact copies of the ten expected file contents.
- Independent-source disposition search: local Codex checkpoint tree equals current observed package; remote Git query failed DNS; no local CI workflow/artifact setup or Phase 4 archive was identified; searched user Downloads/Documents/Desktop yielded no Phase 4 backup/archive candidate; no external Phase 4 storage location is documented.
- No test was run for this report; this is an integrity/provenance investigation, not a code change.
