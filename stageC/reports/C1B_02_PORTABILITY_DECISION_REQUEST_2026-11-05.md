# C1B-02 — Formal Portability-Gate Decision Request

**Decision status:** OPTION A SELECTED; ORIGINAL ACCEPTANCE REMAINS IN FORCE  
**Purpose:** Select the legitimate disposition of the C1B-02 Windows/browser portability gate.

## Existing approval evidence

The project owner has explicitly approved **exact-byte SHA-256** verification. This remains mandatory under every option below. No normalization is permitted, and no release bytes or manifest hashes are to be rewritten to accommodate a mismatch.

The task record identifies no current owner-reviewed revision/archive containing the continuation changes and no partner Windows/browser result. Existing evidence does not establish approval to waive or defer that partner check. Therefore the portability gate is still open.

## Owner decision

Select exactly one outcome:

### A — Complete original acceptance

The owner designates a current immutable revision or archive, approves its contents, and arranges genuine partner Windows/browser verification against that exact input. Exact-byte SHA-256 and original package checks remain required. The partner returns the recorded environment, digest, commands, output, browser result and failures.

### B — Amend acceptance to defer portability

The owner formally amends C1B-02 to permit Stage C engineering acceptance while Windows/browser portability remains **UNVERIFIED / DEFERRED**. The amendment must preserve exact-byte SHA-256 requirements, identify an owner and due condition for the future partner check, state which checks can be run on the current approved platform, and prohibit claims of Windows compatibility until partner evidence arrives. Any split Stage C handoff must exclude Stage B files/snapshots; protected runtime dependencies remain separately provisioned by the owner/authorized partner. The original full-package check must not be claimed as passing if its inputs were excluded.

This is an acceptance-criteria amendment and requires explicit approval by the project owner or a documented authorized maintainer. No such approval is recorded in the reviewed evidence.

### C — Keep C1B-02 blocked

If A is not completed and B is not explicitly approved, keep C1B-02 **BLOCKED**. Do not change task status or acceptance criteria.

## Approval record

- Selected outcome: **A — Complete original acceptance**
- Decision evidence: user selected “A — Original acceptance” in response to the owner/authorized-maintainer decision request.
- Approver name/role: **NOT RECORDED**
- Decision date: **2026-11-05** (conversation record)
- Acceptance amendment: **NONE**; exact-byte SHA-256 and genuine partner Windows/browser evidence remain required.

## Effect on overall Stage C

Option A preserves the original portability acceptance. The current reviewed handoff and partner Windows/browser evidence are still required. C2-01 remains blocked by missing compatible scientific evidence/required decisions; subsequent phases and C7-01 final release acceptance remain gated by their registered prerequisites. Stage C must remain **NOT COMPLETE** until those mandatory criteria are satisfied.

No partner was contacted. No archive was created. No Stage B material was accessed or packaged. No release, manifest, dataset, or historical output was changed. No Git or remote operation occurred.
