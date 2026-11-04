# C1B-02 Runtime Provisioning Checklist

**Purpose:** Custodian checklist for completing the runtime-input handoff after the owner designates an archive and approves controlled provisioning. This does not authorize Codex to obtain, inspect, hash, or package protected inputs.

## Required custodian actions

### Stage C release custodian

- [ ] Confirm release ID and immutable source location for the complete `Phase1B-v1.3.2` package.
- [ ] Supply its complete manifest and verifier result for all **1,324** listed artifacts. Existing recorded manifest SHA-256: `df3a95ae0957b68a89e38098c0824877196aa74ef7dd92573e6ab1f37e39b9b5` (manifest digest only; custodian must separately record the delivered package/archive digest).
- [ ] Confirm the exact `Phase2-v0.3.1` package bytes and all **50** artifact checks; provide the owner-approved expected manifest and package/archive digests. Both expected digests are currently **UNASSIGNED** in the reviewed handoff evidence.
- [ ] For `Phase4-v0.1.2`, record the actual supplied artifact identity and digest, and report the integrity failure/degraded state without repairing or regenerating it. Do not call it verified; the handoff requires the app to remain fail-closed and show `DEGRADED_PHASE4_CONTEXT_UNAVAILABLE`.

### Protected Stage B source custodian

- [ ] Keep the protected interaction-evidence input in the authorized controlled environment.
- [ ] Supply it to the authorized partner only through the approved provisioning route; do not send it to this workspace or include it in the Stage C-only archive.
- [ ] Record its authoritative release/input identifier, exact-byte SHA-256, expected row count, verification command/output, custodian identity/role, and provisioning receipt in the controlled owner record. All of these fields are currently **UNASSIGNED** here.

### Stage D runtime custodian

- [ ] Identify the exact deployed `stageD/src/` revision/package and provide its exact-byte digest and owner-approved provisioning route.
- [ ] Identify `stageD/data/mechanism_evidence_registry.json` and provide its exact-byte SHA-256 and controlled provisioning record.
- [ ] Keep each input separately identifiable; do not merge or rewrite source files to fit the candidate archive. Current expected digests and custodian identity are **UNASSIGNED** in reviewed Stage C handoff evidence.

## Owner/coordinator handoff controls

- [ ] Confirm the exact candidate manifest approval and SHA-256: `c2e809c8bbda167c0fd20c7b99d86fb9c22331427d7ccb5c16771c33937b805b`.
- [ ] Designate current archive/revision, authorized creator, output location, partner recipient, and archive SHA-256 in the owner designation record.
- [ ] Confirm the partner receives the same candidate manifest and separately provisioned runtime inputs, each with an owner-supplied digest.
- [ ] Preserve exact bytes; do not normalize, edit, or repackage an already designated archive after hashing.

## Partner verification and return

- [ ] Verify the owner-designated archive and manifest using the PowerShell `Get-FileHash -Algorithm SHA256` commands in `C1B_02_PARTNER_WINDOWS_VERIFICATION.md` before extraction.
- [ ] Verify every manifest-listed file size and exact-byte SHA-256 after extraction.
- [ ] Verify every separately provisioned runtime input against its custodian-supplied identifier and digest. Stop and report BLOCKED on any absent input or mismatch.
- [ ] Record Windows edition/build, PowerShell/Python/browser versions, full startup output, API status/body, visible degraded Phase 4 behavior, disabled review submission, browser errors, and exact verifier results.
- [ ] Return the completed partner template and evidence to the owner. Partner recipient and return route are **UNASSIGNED**.

## Current provisioning state

No archive is designated; no authorized archive creator/output location or partner recipient is recorded. Runtime custodian assignments and most package digests are **UNASSIGNED**. No archive should be created and no partner test should begin until the owner and custodians complete the applicable fields above. Stage B remains inaccessible to Codex.
