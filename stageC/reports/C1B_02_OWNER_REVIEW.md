# C1B-02 Candidate Handoff — Owner Review

**C1B-02 disposition:** Option A selected — original acceptance remains in force.  
**Candidate-content review state:** PENDING — no approval of these exact files is claimed.  
**Hash policy:** Exact-byte SHA-256 over original bytes; no canonicalization or newline normalization.

## Candidate manifest

- File: `stageC/reports/C1B_02_CANDIDATE_HANDOFF_MANIFEST.json`
- Manifest SHA-256: `c2e809c8bbda167c0fd20c7b99d86fb9c22331427d7ccb5c16771c33937b805b`
- Entries: 46 explicitly listed Stage C candidate files; each entry records relative path, byte size, and exact-byte SHA-256.
- The hash above identifies the manifest bytes, not a ZIP archive. No ZIP archive has been created.

## Scope proposed for review

The candidate contains only:

- Stage C app server, README, and static browser assets.
- Stage C Python modules under `stageC/src/stage_c/`.
- Stage C JSON schemas under `stageC/schemas/`.
- `stageC/tests/test_app_api.py`, for named isolated tests only.

The JSON manifest identifies the release identifiers and runtime dependencies that are **not included**. The app requires the separately provisioned Stage C Phase1B-v1.3.2, Phase2-v0.3.1, and Phase4-v0.1.2 runtime packages, protected Stage B interaction-evidence input, and Stage D source/mechanism registry. An authorized owner/partner must provision those separately. Their bytes were not accessed or hashed in preparing this candidate.

## Missing authoritative handoff input

No current owner-reviewed archive or immutable revision has been designated. The prior partner handoff's revision `067c6d117bdcf4f9274606499150a859b7c791c6` predates local continuation changes and is not acceptable for this verification. The owner must supply/designate either:

- the current immutable revision identifier and the partner's authorized access path, or
- the owner-created `CookRisk-reviewed.zip`, its exact-byte SHA-256, and the matching approved candidate manifest.

For the original acceptance selected by the owner, the partner must receive the complete required runtime inputs through an authorized environment. At minimum these include the complete Phase1B-v1.3.2 package, Phase2-v0.3.1 and Phase4-v0.1.2 packages, the protected Stage B interaction-evidence runtime input, and the Stage D source modules plus mechanism-evidence registry. The owner/authorized partner must provide the exact identifiers and byte digests for every provisioned input. The Stage C-only candidate archive does not contain these dependencies and cannot run the app alone.

## Exclusions and limits

- No Stage B file or embedded Stage B snapshot is in the candidate or was accessed by Codex.
- No Stage D file, Stage A model/data, scientific source dataset, Phase 2 observation, frozen release directory, manifest, or historical output is included.
- Phase4-v0.1.2 remains integrity-degraded and must continue to fail closed.
- The Phase1B full-package verifier cannot be called passing unless the complete owner-provisioned package is present and its verifier actually passes. A source-only candidate archive is not a complete runnable app package.
- Windows/browser portability remains unverified until the partner executes the approved procedure.

## Exact-byte verification

Before extracting an owner-created archive, the partner must run:

```powershell
Get-FileHash .\CookRisk-reviewed.zip -Algorithm SHA256
```

Compare all 64 hexadecimal characters against the digest the owner records for that exact archive. Hash the manifest itself with the same algorithm and compare it to the manifest SHA-256 above. Do not normalize or repackage files before checking. After extraction, check every manifest-listed file's SHA-256 and byte size. The partner procedure is in `stageC/reports/C1B_02_PARTNER_WINDOWS_VERIFICATION.md`.

## Owner approval confirmation

Complete this section only after reviewing the candidate manifest and deciding who will create and designate the archive and provision external runtime dependencies.

The project owner selected **A — original acceptance** for the portability-gate disposition. That selection does not by itself approve this candidate manifest, designate a current archive, or constitute partner verification.

- [ ] I approve the exact candidate contents and exclusions in the manifest.
- [ ] I authorize the following person/team to create the archive from these exact bytes: ____________________
- [ ] I have arranged authorized separate provisioning of the required runtime dependencies.
- [ ] I confirm the exact-byte SHA-256 policy remains in force.
- [ ] I designate this archive for partner verification:
  - Filename: ____________________
  - Archive SHA-256: ____________________
  - Creation date: ____________________
- Owner/authorized maintainer name and role: ____________________
- Approval date: ____________________
- Signature or approval record reference: ____________________

**C1B-02 remains BLOCKED until** the owner completes the applicable approvals, designates the current handoff input, and the partner returns genuine Windows/browser evidence. This preparation does not change acceptance criteria or claim owner approval.
