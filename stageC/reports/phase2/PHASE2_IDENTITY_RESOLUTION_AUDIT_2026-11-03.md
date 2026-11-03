# Phase 2 Identity Resolution Audit — 2026-11-03

## Outcomes

The Stage A/B crosswalk covers 197 Stage A molecular groups:

| Outcome/status | Count | Treatment |
|---|---:|---|
| `STRICT_MATCH` | 19 | Accepted on matching CID, canonical name, and canonical SMILES. |
| `MATCH_AFTER_MANUAL_REVIEW` | 1 | Curcumin only; stable ID/name/structure are linked while the Stage A CID discrepancy is retained as a warning. |
| `CID_MATCH_REQUIRES_STRUCTURE_REVIEW` | 36 | Not accepted. Stage A group-level resolved CID is blank; reported CID agreement and names are candidate evidence, not structural equivalence proof. |
| `INTRA_GROUP_CID_CONFLICT` | 9 | Not accepted; multiple Stage A CIDs conflict within a grouped molecular ID. |
| `NO_CID` | 5 | No CID-based candidate; not accepted. |
| `NO_STAGEB_CID_MATCH` | 127 | No candidate Stage B CID match; retained as unmapped. |

The focused review ledger contains **45 candidate groups**: 27 `POSSIBLE_MATCH`, 9 `IDENTITY_CONFLICT`, and 9 `UNRESOLVED`. No candidate was promoted. The row-level evidence, original identifiers, names, SMILES, candidate CID comparison, Stage A CID-resolution state, existing disposition, and reason are in [identity_resolution_audit_2026-11-03.csv](identity_resolution_audit_2026-11-03.csv).

## Curcumin

Curcumin is the single manual acceptance. The stable Stage A molecular group ID and canonical name/SMILES agree with the Stage B candidate; the Stage A PubChem CID does not. The join is therefore made on the structure-backed stable identity and carries a visible CID discrepancy warning. Neither raw CID is silently rewritten.

## Why the other candidates remain pending

The Phase 2 environment has no RDKit, Open Babel, or comparable molecular graph toolkit. More importantly, Stage A's `PubChem_CID_Resolved` is blank for candidate groups; the Stage A reported CID alone does not prove the source compound assignment. Stage B's candidate structure audit helps identify a candidate but cannot, without verification of the Stage A source structure and its stereochemistry/form/parent status, certify equivalence. Canonical SMILES strings also differ in serialization and sometimes in stereochemical specificity; string inequality alone is not proof of a different molecule, and string/name equality alone is not proof of the same registered analyte.

To resolve candidates safely, obtain the source-level structure or identifier provenance for each Stage A group; normalize both structures with a documented cheminformatics version; compare isomeric structures, formula, charge, InChI/InChIKey and parent/salt/glycoside distinctions; record the authoritative record/version and reviewer rationale; then issue a versioned crosswalk successor. Until then, candidates remain unmapped and do not contribute to cooked-concentration calculations.
