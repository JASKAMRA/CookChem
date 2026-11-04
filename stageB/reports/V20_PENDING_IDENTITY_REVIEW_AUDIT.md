# Stage B V20 — pending identity audit

**Status: 13 compound identities remain pending; no independent chemistry approval is claimed.** This report audits the current V20 registry and its 36-row adjudication ledger. It does not revise identifiers or statuses.

## Reconciled counts

- Compound registry: **143** rows.
- V20 adjudication ledger: **36** reviewed candidate rows.
- Ledger outcomes: 23 `RESOLVED`, 11 `PARTIALLY_RESOLVED`, 2 `MANUAL_REVIEW_REQUIRED`.
- Registry identity status: **130 identity-complete, 13 pending**. The 13 pending are the 11 partial plus 2 manual-review-required outcomes.
- V20 calls the work desk adjudication; independent human chemistry review is explicitly not represented.

## Record-level pending cases

| Compound ID | Name | CID | V20 ledger outcome | Current unresolved identity question | Required next evidence/review |
|---|---|---:|---|---|---|
| `MOL-V11-CID-72941753` | Paradisin A | 72941753 | `MANUAL_REVIEW_REQUIRED` | PubChem record is a complex limonoid glycoside. Exact stereochemical and linkage-level identity was not independently established against a primary isolation/structure report in this review. Keep all identifiers and pending status unchanged. | Obtain primary structure/isomer/form evidence and specialist review before changing identity status. |
| `MOL-V11-CID-24788952` | Paradisin C | 24788952 | `MANUAL_REVIEW_REQUIRED` | PubChem record is a complex limonoid glycoside. Exact stereochemical and linkage-level identity was not independently established against a primary isolation/structure report in this review. Keep all identifiers and pending status unchanged. | Obtain primary structure/isomer/form evidence and specialist review before changing identity status. |
| `MOL-V11-CID-1268142` | Nootkatone | 1268142 | `PARTIALLY_RESOLVED` | PubChem CID 1268142 identifies the stereospecific (+)-nootkatone (4R,4aS,6R), whereas the canonical target name “Nootkatone” does not specify that stereochemistry. CID and structure are internally consistent, but the source-level name does not establish the stereospecific entity. | Retain pending; resolve stereochemistry, positional form, mixture/salt or identifier discrepancy with primary evidence before counting complete. |
| `MOL-V11-CID-9946625` | Epoxybergamottin | 9946625 | `PARTIALLY_RESOLVED` | PubChem identifies the E-alkene geometry, but the epoxide stereocenter is not specified in the standardized structure. Preserve pending status until the target form is supported. | Retain pending; resolve stereochemistry, positional form, mixture/salt or identifier discrepancy with primary evidence before counting complete. |
| `MOL-V12-CID-5702287` | 18β-Glycyrrhetinic acid | 5702287 | `PARTIALLY_RESOLVED` | CID and name match, but the current PubChem InChI encodes two undefined stereocenters. Do not treat the structure as fully stereochemically adjudicated. | Retain pending; resolve stereochemistry, positional form, mixture/salt or identifier discrepancy with primary evidence before counting complete. |
| `MOL-V13-CID-5281858` | Ginkgolic acid C15:1 | 5281858 | `PARTIALLY_RESOLVED` | PubChem CID identifies a specific (8Z) C15 monoene. The target/source shorthand C15:1 does not establish double-bond position or geometry; retain pending status. | Retain pending; resolve stereochemistry, positional form, mixture/salt or identifier discrepancy with primary evidence before counting complete. |
| `MOL-V13-CID-5469634` | Ginkgolic acid C17:1 | 5469634 | `PARTIALLY_RESOLVED` | PubChem CID identifies a specific (10Z) C17 monoene. The target/source shorthand C17:1 does not establish double-bond position or geometry; retain pending status. | Retain pending; resolve stereochemistry, positional form, mixture/salt or identifier discrepancy with primary evidence before counting complete. |
| `MOL-V14-CID-5469424` | Demethoxycurcumin | 5469424 | `PARTIALLY_RESOLVED` | CID 5469424 is the (1E,6E) geometric form, but the canonical target/source label does not specify E/Z geometry. Retain pending status. | Retain pending; resolve stereochemistry, positional form, mixture/salt or identifier discrepancy with primary evidence before counting complete. |
| `MOL-V14-CID-5315472` | Bisdemethoxycurcumin | 5315472 | `PARTIALLY_RESOLVED` | CID 5315472 is the (1E,6E) geometric form, but the canonical target/source label does not specify E/Z geometry. Retain pending status. | Retain pending; resolve stereochemistry, positional form, mixture/salt or identifier discrepancy with primary evidence before counting complete. |
| `MOL-V14-CID-33258` | Allura Red AC (FD&C Red No. 40) | 33258 | `PARTIALLY_RESOLVED` | The disodium salt connectivity is identified, but the registered color additive includes isomer/subsidiary-color composition and the CID does not specify azo geometry. Retain pending until an exact analyte form is established. | Retain pending; resolve stereochemistry, positional form, mixture/salt or identifier discrepancy with primary evidence before counting complete. |
| `MOL-V15-CID-19700` | Brilliant Blue FCF | 19700 | `PARTIALLY_RESOLVED` | CID 19700 is the disodium salt, but authoritative descriptions also include isomeric and subsidiary-color material and alternative salt forms. Keep pending for exact analyte-form equivalence. | Retain pending; resolve stereochemistry, positional form, mixture/salt or identifier discrepancy with primary evidence before counting complete. |
| `MOL-V15-CID-19118` | Azorubine (carmoisine) | 19118 | `PARTIALLY_RESOLVED` | Disodium salt connectivity and synonyms match, but azo geometry is unspecified in the CID structure. Keep pending for exact isomer-level identity. | Retain pending; resolve stereochemistry, positional form, mixture/salt or identifier discrepancy with primary evidence before counting complete. |
| `MOL-V15-CID-164825` | Tartrazine | 164825 | `PARTIALLY_RESOLVED` | The current PubChem record reports a different InChIKey from the archived V19 capture for the same CID/InChI. The identifier was reconciled in V20 to the current official key, but azo geometry remains unspecified; keep pending. | Retain pending; resolve stereochemistry, positional form, mixture/salt or identifier discrepancy with primary evidence before counting complete. |

## Identity status rules

- A CID/name/structure cross-check in V20 is a desk-level registry review, not an independent chemistry sign-off.
- Preserve machine/CID-resolved, literature-supported, manually reviewed, expert-approved, and unresolved states as separate concepts.
- No pending identity is promoted in this audit. The 13 cases above remain pending because the registered target name or analyte form does not establish the exact stereochemical, geometric, positional, salt/mixture, or source-specific identity.
- The decision ledger contains 36 rows, but this does not mean 36 independent expert approvals.

## Evidence and limitations

Source files are `stageB/release/StageB_V20_20261103/data/compound_registry.csv`, `identity/adjudication/V20/identity_adjudication_decisions.csv`, and `RELEASE_STATUS.md`. V20 records PubChem references and desk-review rationale. This audit did not independently re-extract every PubChem record or revisit primary isolation papers, so it does not resolve any remaining identity issue. The correct next action is qualified independent review of these 13 cases, prioritizing the two complex limonoid glycosides and cases with explicit stereochemistry/isomer/salt-form ambiguity.

## Decision

Keep registry status at 130 complete / 13 pending. Do not change Stage B or Phase1B records until a qualified reviewer documents supporting source evidence and an additive, versioned successor is justified.

## 2026-11-04 continuation integrity recheck

- Registry recount: **143 rows; 130 non-pending; 13 pending**. No identity fields or decisions were changed.
- StageB V20 manifest: **839 entries / 839 files, exact-byte verification PASS**; no missing, unexpected, or mismatched entries in exact mode.
- Canonical-text verification reports one line-ending normalization difference for `validation/final_validation_results.csv`. Its current raw SHA-256 matches the manifest (`9494588fa341142fa98c34d0991c5b53321f0d28235a07ff9b45e4cd82e493b2`); LF-normalized SHA-256 is `d4172d01804bed6466d9868007b70733a752e67a8e3531edd63e21c9aa35b3c9`. The frozen release's `build_v20_manifest.py` specifies exact raw-byte hashing, while its integrity-policy prose describes canonical-text hashing. This is a documentation/verification-mode inconsistency; the manifest and artifact were not changed.
- `Phase1B-v1.3.2` outer manifest verification: **PASS, 1,324 artifacts**. Phase2-v0.3.1 manifest verification: **PASS, 50 artifacts**. The complete Stage B test suite passes 46/46 using `PYTHONDONTWRITEBYTECODE=1`; no `.pyc` files were created in the frozen V13 release tree.
