# Stage D — Qualified Review and Protected-Source Integration Handoff

**Status:** PREPARATION ONLY — no protected source was accessed and no human review was performed.  
**Scope basis:** Official Stage D roadmap, Stage D closure register dated 2026-11-04, and Stage D identity-provider deployment checklist.

## Authorized inputs required from the custodians

Provide these only through the organization's approved controlled environment. This handoff contains no Stage B records or source payloads.

1. **Protected evidence source:** the owner-designated immutable Stage B release, its release-manifest identifier and exact-byte SHA-256, the authorized evidence file, expected row count, and permitted evidence IDs. The authorized custodian must verify the source digest and record the verification output; this workspace must not receive or inspect the protected source.
2. **Stage D integration inputs:** owner-designated Stage D queue and mechanism-registry versions, their exact manifest digests, and a source-to-registry reconciliation result produced by an authorized environment. Do not substitute a prior embedded snapshot or an unverified local copy.
3. **Stage C exposure input when a comparison is actually supportable:** owner-approved Phase 3 release ID and manifest digest, one exact recipe/ingredient estimate ID, source food/mapping references, and upstream release provenance. Current Stage C evidence records zero accepted cooked-concentration outputs; no cooked estimate may be asserted until Stage C scientific gates pass. Raw-reference amounts must remain explicitly raw.
4. **Primary literature access:** reviewer-authorized full text or abstract, bibliographic identity, exact page/table/figure locator, and any supplementary material needed for the record. Record access level honestly; abstract-only review cannot be represented as full-text review.
5. **Identity and assignment service:** approved issuer, issuer-bound trusted key source, reviewer roster and roles, credential expiry, key rotation/revocation source, reviewer resolution, assignment authorization, and deployment-owner approval, as required by `identity_provider_deployment_checklist.md`.
6. **Independent checkpoint service:** service owner, endpoint/configuration version, trust-key or attestation method, retention policy, access control, and receipt/reference format. It must be administered separately from the local audit-log storage trust domain.
7. **Persistence environment:** documented filesystem/store, locking and fsync guarantees, backup/restore policy, and owner approval for the deployment location.

## Required reviewer actions

### Evidence records

For each of the 317 queued records, an authorized reviewer must inspect the authorized source record and primary source; confirm record-to-source identifiers and locators; preserve source language; record study type, model/population, route, dose basis, timing, preparation/matrix, outcomes, limitations, and contradictions; and enter a cited rationale and explicit disposition. Null, negative, positive, mixed, and conflicting outcomes remain distinct and scoped to tested conditions. A reviewer must not infer missing values, identity, mechanism, ordinary-food exposure, or clinical risk.

### Mechanism candidates

For each of the 25 candidates, an appropriately qualified reviewer must confirm the source locator and access level; assess compound/target identity, assay type and context, directness, concentration/dose, study design/confounding, endpoint meaning, independent replication, food context, human exposure relevance, and clinical interpretation boundary; and document supporting and contradicting findings, uncertainties, rationale, and disposition. Do not promote a candidate automatically. Preserve unresolved target mappings and source conflicts.

### Six-gate comparability and interpretation

A qualified reviewer must review each proposed comparison's compound identity, route, units/basis, time window, population/model, and preparation/matrix. Software `READY_FOR_REVIEW` is not an approval. Record the reviewer, source locator, rationale, limitations, and explicit outcome. An absent or noncomparable Stage C exposure remains pending/blocked.

### Authorization and audit

- Reviewer actions must be authenticated by the approved provider and authorized from its roster; no self-declared name, role, or key is acceptable.
- Review and assignment events must use the append-only local chain and be independently checkpointed. Preserve checkpoint receipts and verification output outside the local audit-log storage trust domain.
- Any provider, assignment, chain, or checkpoint failure stops the affected review action and is recorded without writing a fabricated approval.

## Review return template

```text
Protected-source integration and qualified-review return

Authorized source custodian:
Approved controlled environment/reference:
Source release ID:
Owner-provided manifest SHA-256:
Authorized file digest verification output:
Expected/observed source row count:
Permitted record identifiers or assignment reference:
Stage D queue/registry release IDs and manifest digests:
Stage C Phase 3 release and estimate reference (if applicable):
Primary-source access level and citation/locator for each reviewed record:
Identity-provider issuer/configuration version:
Reviewer roster reference and assigned reviewer IDs:
Review records completed / pending / rejected:
Supporting findings and locators:
Contradicting findings and locators:
Uncertainty, limitations, and unresolved conflicts:
Comparability gate decisions and rationale:
Authenticated action-log verification result:
Assignment-ledger verification result:
Independent checkpoint service/version and receipt:
Checkpoint verification result:
Persistence/backup environment and approval:
Reviewer name/role, credential identity reference, and review date:
Scientific owner disposition (if required):
Outstanding issues:
```

**No reviewer records are completed by this template.** The 317 and 25 counts are workflow totals from the existing Stage D closure evidence, not an assertion that any review has occurred.
