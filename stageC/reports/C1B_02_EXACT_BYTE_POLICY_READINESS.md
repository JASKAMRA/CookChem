# C1B-02 — Approved Exact-Byte Policy and Windows Readiness

**Task:** C1B-02 — Phase 1B release hashing policy / Windows reproduction  
**Status:** **BLOCKED — policy approved; current reviewed handoff and partner verification are missing**  
**Date:** 2026-11-05

## Approved policy

The project owner explicitly approved **exact-byte SHA-256** for release verification on 2026-11-05. Hash the original file bytes; do not normalize line endings, encoding, Unicode, or other text content. No release file is to be rewritten to accommodate the policy.

## SHA-256 method and existing verification evidence

The Stage C `Phase1B-v1.3.2/verify_release.py` implementation uses `hashlib.sha256(path.read_bytes()).hexdigest()` for each manifest artifact. This hashes the original bytes and performs no text normalization. The manifest digest is also computed over the original bytes of `CHECKSUMS.json`.

Existing Stage C evidence, not rerun in this task:

- `STAGE_C_MASTER_EXECUTION_CYCLE_1_REPORT.md` records exact-byte verification of the embedded dependency as **839/839 passing** and Phase1B-v1.3.2 package verification as **1,324 artifacts passing**.
- The same report preserves canonical-text verification as **838 matches and one mismatch**, caused by the newline-normalized `validation/final_validation_results.csv`. That is historical evidence under the unapproved canonical policy; the file and its hashes remain unchanged.

No dependency, snapshot, release verifier, or release package was executed or opened for re-verification here. The implementation method and prior results were checked from Stage C code/report evidence only.

## Exact partner input required

The partner must receive one owner-designated, reviewed input that represents the current intended checkout:

1. A reviewed revision identified by its full immutable revision ID, **or**
2. A reviewed archive identified by its filename and SHA-256.

It must include the complete Stage C app and the full Phase1B-v1.3.2 package, including all 1,324 manifest-listed artifacts and required local inputs. The partner verification package requires recording the checked revision, Windows edition/build, Python version, browser/version, exact-byte verification output, and actual local app/browser result.

The last revision named in the Stage C partner handoff is `067c6d117bdcf4f9274606499150a859b7c791c6`. That handoff explicitly says the local continuation changes are not present at that revision and are not confirmed on a partner checkout. It is therefore not an acceptable reviewed revision for this run. The Stage C reports contain no owner-designated replacement revision or reviewed archive. They also record that no partner Windows clone/browser run has occurred.

## Prerequisite disposition

| Prerequisite | Status | Evidence |
|---|---|---|
| Owner selects exact-byte or canonical-text policy | **SATISFIED** | Explicit owner approval recorded above; exact-byte SHA-256 selected. |
| Existing package can be checked over original bytes | **SATISFIED by existing evidence** | Stage C verifier uses `read_bytes()`; Cycle 1 records exact-byte results, 839/839 nested entries and 1,324/1,324 Phase1B artifacts. Not rerun. |
| Current owner-reviewed revision or archive supplied | **MISSING** | Partner handoff identifies only an older baseline that excludes local continuation changes; no reviewed archive is recorded. |
| Partner Windows/browser verification result | **MISSING** | Partner verification package is marked PENDING; no Windows partner run is documented. |

**C1B-02 remains BLOCKED.** The required next external input is the owner-designated reviewed revision or archive, followed by the partner’s Windows/browser verification evidence against that exact input. Do not claim C1B-02 complete before those results arrive.

## Scope and preservation

Only this C1B-02 evidence report was created. No release file, manifest, hash, scientific dataset, Stage A file, Stage B source or embedded snapshot, Stage D file, or Phase 2 observation was read or modified. No Windows verification was performed. No Git operation or remote access occurred.
