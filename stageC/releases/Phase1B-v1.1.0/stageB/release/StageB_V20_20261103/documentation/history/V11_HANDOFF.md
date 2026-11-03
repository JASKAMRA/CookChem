# CookRisk Stage B V11 handoff

**Release status: PASS_WITH_WARNINGS**  
**Release path:** `C:\Users\dakshant\Documents\CookChem\stageB\release_v11_20261030`  
**Scope:** Stage B literature evidence only. No exposure estimates, retained doses, patient-specific risk scores, or Stage A model changes.

## Dataset status

V10 was independently recalculated at 100 anchors, 263 interaction records, 117 drug/probe labels, 140 PMIDs, and 136 nonblank DOIs. The V10 evidence classes are 70 human pharmacokinetic, 4 controlled clinical, 51 animal, and 138 in-vitro rows. V10 has 35 warning rows across 33 codes. One noncritical baseline finding: 60 anchors lack explicit rows in V10's selection-decision table; V11 adds retrospective traceability rows without inventing historical dates. DOI blanks remain for six evidence rows from five publications; PubMed metadata supplied no DOI for these.

V11 contains **105 anchors**, **272 evidence records**, **121 drug/probe labels**, **144 PMID publications**, **141 distinct nonblank DOIs**, and 146 bibliography entries. Evidence classes: Animal 51, Controlled clinical 4, Human pharmacokinetic 70, In vitro 147. Five anchors and nine in-vitro records were added. The 120-anchor stretch target remains 15 anchors away.

## Testing and validation

- V11 automated checks including clean-copy rebuild: **45/45 passed; 0 failed**. The clean copy reproduced 12/12 core outputs byte-for-byte and its validator passed 43/43 automated assertions. **6 manual checks remain unexecuted** and are not counted as passes.
- Adversarial mutation tests: **23/23 detected (100%)** across distinct integrity rules in isolated temporary copies.
- Regression: all 100 inherited anchor rows and all 263 inherited evidence rows are byte/field-identical; the cooking-retention table remains byte-identical. V10 checksums match its existing manifest.
- V10 baseline validation report itself says PASS 21/21 and 10/10 mutations; V11 independently reproduced its counts. Independent audit found the selection-decision coverage gap described above.

## Scientific and source review limits

The V11 claims table retains conservative source-status labels. Added PMID-linked results are abstract-level and have not been re-extracted from full-text tables; Paradisin C remains a DOI-only qualitative record. No inherited claims were upgraded. The broad inherited source-to-claim review, full-text numerical/table verification, one-by-one inherited food-occurrence review, expert chemical-form/stereochemistry adjudication, and cohort overlap review are not complete. Numeric screens surfaced 156 endpoint/unit candidates in V11; that count is a triage measure, not proof that all values are correct. Existing resveratrol holds remain. These gaps preclude an unqualified PASS.

## Expansion and warning state

Added Paradisin A, Paradisin C, nootkatone, epoxybergamottin, and amentoflavone. Paradisin A/C, nootkatone, and epoxybergamottin have grapefruit context; amentoflavone is explicitly supplement/medicinal-botanical context and is not represented as ordinary-food exposure. Candidates GF-I-1, GF-I-4, Paradisin B, and imperatorin were deferred because identity or target attribution was not adequately resolved.

The 35 inherited warning rows remain unchanged. V11 adds six visible warning rows; no inherited scientific warning was closed. The combined ledger has 41 rows across 39 codes (25 unresolved, 13 partial, 1 resolved, 2 not applicable). See the transition report and warning ledger.

## Rebuild and deliverables

The build uses adjacent V10 inputs plus captured PubChem/PubMed/Crossref metadata and Python's standard library; no network access is needed. It accepts a release-directory argument and is intended to run from a clean copy. Clean-copy rebuild comparison is complete: 12/12 core outputs match byte-for-byte and the clean-copy validator passes 43/43 automated checks. Results are in `audit/v11_clean_rebuild_comparison.csv` and `audit/v11_reproducibility_test_results.csv`.

Primary tables are under `outputs/`: `compound_registry_v11.csv`, `stageB_food_drug_interactions_v11.csv`, `drug_probe_registry_v11.csv`, `study_registry_v11.csv`, `source_bibliography_v11.csv`, `identity_structure_audit_v11.csv`, `selection_decisions_v11.csv`, `candidate_screening_log_v11.csv`, `source_audit_v11.csv`, `claim_support_and_verification_v11.csv`, and `warning_resolution_ledger_v11.csv`. Test plan, results, coverage, mutation, regression, and rebuild records are under `audit/`.

**Final assessment:** PASS_WITH_WARNINGS. Structural/reference/inherited-row checks and the mutation suite pass. Scientific review remains incomplete, notably source-to-claim/table verification and inherited food-context review. Treat this as a literature evidence resource, not clinical decision support.
