# C1B-02 — Owner Decision Request: Split Stage C Partner Handoff

**Status:** Awaiting owner decision; C1B-02 remains BLOCKED  
**Date:** 2026-11-05  
**Policy already approved:** SHA-256 over exact original bytes; no normalization.

## Decision required

The existing partner instructions require a full repository checkout, the full Phase1B-v1.3.2 package (1,324 manifest-listed artifacts), and runtime inputs outside Stage C. The available partner handoff names revision `067c6d117bdcf4f9274606499150a859b7c791c6`, which predates local continuation changes. No current owner-reviewed revision/archive or partner Windows/browser result is recorded. This report does not inspect or package protected Stage B material.

The project owner must select one option:

- **A — Owner/partner full-package route.** The owner and authorized partner arrange the complete required package and protected runtime inputs through their approved environment. Codex does not access, inspect, or package Stage B. The partner returns verification evidence against the owner-designated revision/archive.
- **B — Formally approve a split handoff.** The owner revises C1B-02 handoff and acceptance criteria to permit a reviewed Stage C-only archive, while protected runtime dependencies are provisioned separately by the owner/authorized partner in their approved environment. The partner reports the identity and exact-byte digests of separately provisioned inputs and confirms which checks were run. The original Phase1B manifest's 1,324-artifact check must not be represented as passing if protected entries are absent; the owner must define the permitted split validation and acceptance evidence before the partner run.
- **C — Retain the existing gate.** If A is not arranged and B is not approved, keep C1B-02 BLOCKED pending the current owner-reviewed complete handoff and partner Windows/browser verification.

**Owner decision:** `PENDING`  
**Approving owner/maintainer:** to be named by the project owner.  
**Acceptance-procedure revision (if B):** required before treating a split run as C1B-02 acceptance.

## Stage C-only archive candidate manifest (not an archive)

This is a boundary-safe candidate allowlist for owner review, not a complete, approved manifest and not proof that the app can run by itself:

1. `stageC/app/server.py`
2. `stageC/app/static/index.html`
3. `stageC/app/static/app.js`
4. `stageC/app/static/style.css`
5. `stageC/app/README.md`
6. `stageC/src/stage_c/*.py` (Stage C application modules only; no scientific data is added by this list)
7. `stageC/tests/test_app_api.py` (only if the owner wants the isolated API regression check included)
8. `stageC/releases/Phase1B-v1.3.2/`, `stageC/releases/Phase2-v0.3.1/`, and `stageC/phase4/releases/Phase4-v0.1.2/` only after an authorized owner/packager has classified the archive contents and excluded every Stage B file, embedded Stage B snapshot, and protected Stage B-derived bundle.
9. This handoff procedure and the applicable Stage C task reports, if needed for partner context.

**Mandatory exclusions:** every `stageB/` path; every embedded Stage B snapshot or copy; Stage D source/data; Stage A models/data; unrelated releases and historical outputs. Do not infer that a Stage C release directory is safe to include merely from its parent directory name. The candidate release directories require a boundary review by an authorized packager; this task did not enumerate or open their contents.

The Stage C app guide says the app consumes repository-relative releases and non-Stage-C runtime inputs. Therefore this allowlist is not independently runnable until the owner/partner provisions required protected runtime dependencies separately. The existing full Phase1B verifier expects its complete package; a split archive that omits protected entries cannot claim the original 1,324-artifact verification passed.

## Exact-byte archive digest procedure

After the owner approves the exact archive contents and the archive is created in the approved environment:

1. Record the exact filename, byte size, creation date, owner-approved content-manifest version, and full SHA-256 digest in the handoff record.
2. On Windows, before extraction, the partner runs:

   ```powershell
   Get-FileHash -LiteralPath .\CookRisk-StageC-reviewed.zip -Algorithm SHA256
   ```

3. Compare all 64 hexadecimal characters to the owner-provided digest. Any difference stops verification. Do not unzip/re-zip, normalize text, or substitute a canonical-text digest.
4. Record the command output and the digest in the partner result. After extraction, record the archive filename and the reviewed content-manifest version used. Any separately provisioned dependency must be identified and checked against its owner-provided exact-byte digest using the same method.
5. Report the split nature of the handoff. Do not claim the original full-package verifier passed when protected entries were intentionally not in the archive.

The outer archive hash establishes that the received archive bytes match the owner-designated archive. It does not certify scientific validity, completeness of an unapproved allowlist, or integrity of separately provisioned dependencies.

## Required approval and partner evidence

**Owner/maintainer must provide:** selected option A/B/C; full immutable revision ID or archive filename plus SHA-256; approved content manifest; named approver; and, for B, the revised C1B-02 acceptance procedure and the approved method for separately provisioning protected runtime inputs.

**Partner must return:** checked revision or archive name; pre-extraction SHA-256 command and output; Windows edition/build; Python version; browser name/version; exact approved package/check commands and outputs; app startup/browser result; whether the degraded Phase 4 notice appeared; all failures/tracebacks; and, for B, identifiers/digests and verification results for separately provisioned dependencies. No human review or scientific validation is implied by a successful software smoke check.

## Disposition

C1B-02 remains **BLOCKED** until the owner supplies the reviewed handoff input and the partner returns the required Windows/browser evidence under the currently approved or formally revised procedure. No release archive was created or changed. No protected Stage B file or embedded snapshot was accessed.
