# C1B-02 Owner Designation Record

**Status:** PARTIALLY DESIGNATED — candidate contents approved; archive, creator, runtime-input custodians, recipient, and partner execution remain unassigned. This record captures existing evidence and does not invent missing designations.

## Approved candidate

| Field | Recorded value |
|---|---|
| Candidate manifest | `stageC/reports/C1B_02_CANDIDATE_HANDOFF_MANIFEST.json` |
| Manifest SHA-256 (exact bytes) | `c2e809c8bbda167c0fd20c7b99d86fb9c22331427d7ccb5c16771c33937b805b` |
| Candidate entries | 46; all paths are within `stageC/` |
| Owner content approval | Recorded in `C1B_02_OWNER_CONTENT_APPROVAL_RECORD_2026-11-05.md`; applies to the exact candidate only |
| Current authoritative archive/revision ID | **UNASSIGNED** |
| Authorized archive creator identity and role | **UNASSIGNED** |
| Archive output location | **UNASSIGNED**; `CookRisk-reviewed.zip` is the procedure's expected filename, not a designated existing archive |
| Archive SHA-256 | **UNASSIGNED**; no archive is present/designated |
| Partner recipient | **UNASSIGNED** |
| Partner verification responsibility | Execute the approved Windows/PowerShell, startup, API, browser, and degraded Phase 4 checks; return exact outputs using `C1B_02_PARTNER_WINDOWS_VERIFICATION.md` |

The Stage C owner review records prior revision `067c6d117bdcf4f9274606499150a859b7c791c6` as an older baseline that excludes continuation changes; it is **not eligible** for this handoff. No Git operation was used to identify or designate a replacement.

## Runtime inputs requiring separate controlled provisioning

| Required input | Existing Stage C record | Expected exact-byte digest | Custodian | Provisioning status |
|---|---|---|---|---|
| Complete `Phase1B-v1.3.2` runtime package (1,324 manifest-listed artifacts) | Release manifest digest recorded as `df3a95ae0957b68a89e38098c0824877196aa74ef7dd92573e6ab1f37e39b9b5` | Package/archive digest **UNASSIGNED**; the listed value identifies the release manifest, not a package archive | **UNASSIGNED** | Not provisioned for partner handoff |
| `Phase2-v0.3.1` runtime package (50-artifact release) | Release identifier and artifact count recorded | Package/archive digest **UNASSIGNED** in the reviewed handoff evidence | **UNASSIGNED** | Not provisioned for partner handoff |
| `Phase4-v0.1.2` runtime package | Handoff records this release as integrity-degraded; Stage C closure records it as unrecoverable in investigated sources | Accepted runtime digest **UNASSIGNED**; do not repair, regenerate, or treat the package as verified | **UNASSIGNED** | Not provisioned; expected app behavior is fail-closed degraded Phase 4 context |
| Protected Stage B interaction-evidence runtime input | Explicitly required by the Stage C handoff | **UNASSIGNED**; must be supplied and verified by its authorized custodian outside this workspace | **UNASSIGNED** | Not accessed or provisioned here |
| `stageD/src/` runtime modules | Explicitly required by the Stage C handoff | **UNASSIGNED** in reviewed Stage C handoff evidence | **UNASSIGNED** | Not provisioned for partner handoff |
| `stageD/data/mechanism_evidence_registry.json` | Explicitly required by the Stage C handoff | **UNASSIGNED** in reviewed Stage C handoff evidence | **UNASSIGNED** | Not provisioned for partner handoff |

All values marked **UNASSIGNED** require the responsible custodian to identify the exact immutable bytes and return their SHA-256 before provisioning. Release-manifest hashes must not be represented as archive/package hashes. Protected Stage B material must never be sent to this workspace.

## Owner completion fields

- [ ] Designate current authoritative revision or archive identifier: ____________________
- [ ] Authorize archive creator (identity and role): ____________________
- [ ] Designate archive output location: ____________________
- [ ] Record archive filename and exact-byte SHA-256 after creation: ____________________
- [ ] Name each runtime-input custodian and approve the controlled provisioning route: ____________________
- [ ] Name the partner recipient and confirm the verification deadline/contact route: ____________________

## Current stop condition

**Do not create an archive.** Creation remains unauthorized until an authorized creator and output location are designated, all required inputs have verified exact-byte identifiers/digests, and protected inputs are handled solely by their authorized custodians. C1B-02 remains blocked pending partner execution and returned evidence under the original acceptance criteria.
