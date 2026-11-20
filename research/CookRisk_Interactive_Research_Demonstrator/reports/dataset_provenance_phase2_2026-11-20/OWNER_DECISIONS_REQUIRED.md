# Owner Decisions Required — CookRisk Phase 2

**Prepared:** 2026-11-20  
This page distinguishes documented approvals from decisions that remain with the owner. It does not make scientific or governance decisions on the owner's behalf.

## Existing documented approvals

| Topic | Existing documented position | Scope limit |
|---|---|---|
| Reconstruction | Approved for live record-level demonstrator exploration at the current verified `f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0` snapshot. | Not canonical; not independently scientifically validated; does not approve broader scientific claims. |
| Batch021 | Preserved as a separate historical ML evidence family at current verified `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`. | Historical artifacts/metrics remain untouched; current input identity does not mean a fresh metric reproduction. |
| Dataset family separation | Live Reconstruction exploration and historical Batch021 results remain separate. | No merge or silent fallback is approved. |
| ACR meaning | `100 × C_cooked / C_raw`, an apparent concentration ratio. | Not total-mass retention without compatible paired food masses or validated yield. |

These positions are documented in the demonstrator evidence/data-selection documentation and registry, and are also stated in the current task's approved references.

## Pending decisions and evidence requests

### 1. Historical `d866…` Batch021 claim

**Question:** Can the owner identify the exact file, release, or report version that produced `d866d0ffab8c335e0469f2815c3cdf518b3d019be1bdf2e37ba2ced2e7d5d3c1`? If not, may the demonstrator documentation label it as an unverified stale historical claim relative to the currently verified Batch021 file?

**Current evidence:** The full value appears in prior demonstrator audit/provenance material. The inspected Batch021 manifest/checksum and saved validation input record support `111064…669c8`; no inspected Stage A file is linked to `d866…`.

**Until decided:** Retain the discrepancy in the gap register. Do not substitute the `d866…` value into current pins or claim its origin is known.

### 2. Old Reconstruction snapshot `16db…`

**Question:** Is recovery of the exact former `16dbbd9c38a21675a2644b415289004e5a8eb7091e97a96dae645ed2bf52be99` bytes required? If yes, what authorized archive or artifact location contains them?

**Current evidence:** The current Reconstruction at its documented path hashes to `f939…`; exact old bytes were not located in the scoped inspected Stage A artifacts.

**Until decided:** Keep the current, previously approved limited exploration snapshot. Do not claim a byte-for-byte historical comparison or global absence of the old file.

### 3. Reconstruction build-time provenance gap

**Question:** Is the missing build-time input/output hash record an accepted historical limitation, or should the owner authorize a future, separately scoped provenance-rich rebuild/recording effort?

**Current evidence:** The builder and manifest document a Batch021-based derivation and list inputs/outputs, but no build-time input or output hashes are recorded; builder paths are absolute paths from another machine. Independent reproduction was not performed.

**Until decided:** Do not rebuild or regenerate scientific artifacts under this Phase 2 task; continue to describe lineage as documented, not independently reproduced.

### 4. AR-01 historical evaluation claims

**Question:** Is it acceptable to retain the saved historical results with the explicitly limited statement that the recorded input hash is matched, while independent metric reproduction remains unverified? Any future rerun or metric update needs separate authorization.

**Current evidence:** The saved `validation_summary.json` input digest, current Batch021 file digest, and Batch021 checksum sidecar all match `111064…669c8`. This resolves input identity as **FOUND AND HASH-MATCHED** under the required status scheme. No training or evaluation was run in this audit.

**Until decided:** Display historical results only with their saved provenance. Never describe the metrics as independently reproduced based on this hash match.

### 5. `Retention_Final` definition and scientific interpretation

**Question:** Can the owner provide or approve primary-source adjudication for the equation, units, scale, measurement basis, and intended interpretation of `Retention_Final`?

**Current evidence:** The inspected registry/prior report document dimensions and historical/current digests, but equation, units, scale, and basis remain unknown. The source CSV was not read or hashed in this audit.

**Until decided:** Keep `Retention_Final` separate from ACR and do not infer total-mass retention or fill missing values with zero.

### 6. Dataset family separation

**Decision state:** No pending decision for the current architecture. Separation is already documented and approved: Reconstruction for live exploration; Batch021 for historical ML evidence.

**New authorization needed only if:** Someone proposes merging the families, using Batch021 as a live fallback, presenting Reconstruction as the historical model input, or changing the established roles.

### 7. Scientific approval and canonical designation

**Question:** Is any broader scientific use or canonical ACR dataset designation intended? If so, which exact snapshot, target semantics, provenance package, and independent validation standard should govern it?

**Current evidence:** No explicit canonical designation was found. Existing Reconstruction approval is demonstrator-only; Batch021 is a separate historical evidence family.

**Until decided:** Make no canonical, independent-validation, causal, or deployment claim. Phase 3 may proceed with presentation-only UI work under current role labels and fail-closed checks.

## Summary of who must act

- **No owner action is needed** to continue using the already approved current dataset roles and keep the families separate.
- **Owner input is needed** to identify the `d866…` origin, to recover `16db…` if that old snapshot is required, and to adjudicate `Retention_Final` semantics.
- **Explicit authorization is needed before** any scientific rebuild/rerun, historical metric update, canonical designation, or broader scientific use.
