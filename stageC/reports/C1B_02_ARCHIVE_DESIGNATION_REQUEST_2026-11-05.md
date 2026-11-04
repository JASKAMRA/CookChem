# C1B-02 — Owner Archive Designation Request

**Purpose:** Complete the remaining owner designations under the already selected original acceptance route. This supplements the earlier decision record; it does not change the approved scope or acceptance criteria.

## Reconciled current decisions

- Exact-byte SHA-256 policy: **APPROVED**; hash original bytes without normalization.
- Candidate content and exclusions: **APPROVED** for the exact 46-file manifest recorded in `C1B_02_OWNER_CONTENT_APPROVAL_RECORD_2026-11-05.md`.
- Approved manifest SHA-256: `c2e809c8bbda167c0fd20c7b99d86fb9c22331427d7ccb5c16771c33937b805b`.
- C1B-02 disposition: **A — Original acceptance**. The historical owner request showing `PENDING` was superseded by the later portability decision record selecting A; the original partner criteria remain in force.
- Current eligible archive/revision: **UNASSIGNED**. The recorded older revision `067c6d117bdcf4f9274606499150a859b7c791c6` is explicitly ineligible because it predates the continuation changes.
- Archive, Windows/browser result, and partner sign-off: **NOT AVAILABLE**.

## Owner designations required

Please supply each field without changing the approved manifest:

1. **Authoritative handoff input:** choose one:
   - Current immutable revision ID: ____________________
   - Or owner-designated archive filename: ____________________
2. **Authorized archive creator:** identity and role: ____________________
3. **Explicit archive-creation authority:** approval/reference for that creator: ____________________
4. **Approved output location:** controlled path or delivery location: ____________________
5. **Archive identity after authorized creation:** filename, byte size, creation date, and exact-byte SHA-256: ____________________
6. **Runtime-input custodians:** name/role and controlled provisioning route for each item in `C1B_02_RUNTIME_PROVISIONING_CHECKLIST.md`: ____________________
7. **Partner handoff:** recipient identity/team, secure delivery route, and return contact/deadline: ____________________

Do not fill archive digest fields until the authorized creator has created the archive from exactly the approved candidate bytes and computed SHA-256 over the resulting original archive bytes. The manifest digest above is not an archive digest.

## Runtime inputs requiring custodian records

The runtime inventory and per-input verification steps are in `C1B_02_RUNTIME_PROVISIONING_CHECKLIST.md`. The known Stage C Phase1B release-manifest digest is `df3a95ae0957b68a89e38098c0824877196aa74ef7dd92573e6ab1f37e39b9b5`; it is not a package/archive digest. Expected package digests and/or custodians remain **UNASSIGNED** for Phase1B delivery, Phase2-v0.3.1, Phase4-v0.1.2, protected Stage B interaction evidence, `stageD/src/`, and the Stage D mechanism registry. Protected Stage B inputs must be provisioned only by their authorized custodian in the approved controlled environment; Codex must not access or package them.

## Partner execution after designation

The existing reproducible procedure is `C1B_02_PARTNER_WINDOWS_VERIFICATION.md`. It specifies exact-byte archive and manifest checks with `Get-FileHash -Algorithm SHA256`, file size/hash checks after extraction, Python startup, health API request, browser checks, expected degraded Phase 4 behavior, disabled review submission, and a results-return template. The partner must stop and report BLOCKED if any designated input or digest is absent or mismatched. The partner must return actual outputs and errors; instructions alone do not verify portability.

## Stop condition

No archive was created or designated by this request. Do not create one until the owner fills the creator authority, output location, authoritative handoff input, and custodian/provisioning fields above. Do not begin partner testing until the partner has the owner-designated handoff and complete required runtime inputs with owner-supplied digests. C1B-02 remains **BLOCKED** until the partner returns genuine Windows/browser evidence under the original acceptance criteria.
