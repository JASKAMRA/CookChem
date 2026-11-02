# CookRisk Stage C — Phase 1B Final Completion and Release

**Exit decision: COMPLETE WITH DOCUMENTED LIMITATIONS.** Phase 1B source screening, accepted-data reconciliation, final contextual review, validation, and release packaging are complete. This does not mean every Stage B target has an ordinary-food concentration.

## A. Executive summary

Phase 1B expanded the active Stage C data layer from the initial USDA tables to a provenance-tracked set of **511 accepted quantitative ordinary-food records** and **511 compound-food mappings**. Coverage is **109/119 Stage B compounds (91.60%)**. All 119 compounds are represented in the priority and search registers; ten have no accepted ordinary-food measurement. The 100 numbered batch folders retain source findings, candidate data, decisions, and limitations.

Batch 100 separately reconciles numerical plant-context evidence for eight of those ten targets. Seven targets have primary quantitative botanical measurements, one (irilone) has a secondary-source numeric lead held pending primary-table verification, and two still lack exact quantitative matrix values. No contextual values were inserted into the ordinary-food dataset.

## B. Quantitative coverage

| Evidence class | Actual count | Treatment |
|---|---:|---|
| Stage B targets | 119 | Current checksummed Stage B registry |
| Accepted ordinary-food measurements | 511 records | Kept in `data/food_composition/food_composition.csv` |
| Accepted ordinary-food mappings | 511 rows | Kept in `data/compound_food_mapping/compound_food_mapping.csv` |
| Compounds with ordinary-food quantitative coverage | 109/119 | Recomputed from the data and mapping files; 10 remain uncovered |
| Contextual primary quantitative leads among final 10 | 7 compounds | Six *Scutellaria* root compounds and amentoflavone in *Viburnum* vegetative tissues; held outside food coverage |
| Secondary-only contextual lead among final 10 | 1 compound | Irilone, 0.06 mg/g dry weight as transcribed in a secondary monograph; held |
| Final targets with no verified exact quantitative matrix value | 2 compounds | 7-methoxyflavanone and 5,4′-dihydroxy-3,6,7,8,3′-pentamethoxyflavone |
| Central candidate register | 23 rows | 22 pending manual review; one resolved by an accepted alternate measurement |
| Explicit rejected source outcomes in batch screening | 2 | One matrix-incompatible, one incompatible analyte |

Accepted source classes comprise **491 primary analytical measurements, 15 authoritative food-composition database records, and 5 peer-reviewed secondary-source records**. All 511 active records have a source URL, title, quantitative value/unit, basis/method descriptions, and source-verification status. The 61 source titles/URLs are represented in the dataset and batch notes.

## C. Source discovery and screening

The project has 100 numbered batch folders and a cumulative search log with **411 source/compound events across all 119 Stage B IDs**. Batch candidate files contain **618 candidate-food rows across 51 CSVs**; these remain separate from accepted rows. Sources include USDA Flavonoid and Isoflavone databases, USDA FoodData Central/SR Legacy, NIST reference materials, and peer-reviewed analytical studies. Batch notes retain table/page/section locators, units, food and plant identity, state, methods, uncertainty, sample basis, and acceptance rationale.

The active dataset includes both food-composition database aggregates and primary papers that report explicitly quantified or labeled semi-quantified values. Semi-quantitative methods, dried/frozen/sample-weight bases, analytical rather than biological replicates, study-specific treatments, and other source limits remain documented; measurements are not presented as market or population averages.

## D. Contextual reconciliation of the final ten

The separate Batch 100 contextual table includes six primary HPLC measurements from medicinal *Scutellaria baicalensis* root studies: baicalein, baicalin, scutellarein, wogonin, wogonoside, and oroxylin A. It also retains three *Viburnum* amentoflavone tissue values from one primary paper: *V. lantana* leaves 0.1104 ± 0.0006%, branches 0.0061 ± 0.0005%, and *V. opulus* leaves 0.0066 ± 0.0002% on dried powdered plant material (Table 3, n=3 analytical measurements). These are contextual matrices and do not establish ordinary-food dietary concentrations.

The secondary red-clover monograph reports irilone at 0.06 mg/g dry weight after hydrolysis and attributes the value to Tsao et al. (2006). The primary paper confirms red-clover cultivar/plant-part HPLC profiling, but its exact numerical row and statistical meaning were not independently verified; the value remains held and is not treated as primary evidence.

Focused exact-name/CID/CAS searches did not locate a verified, matrix-specific quantitative result for 7-methoxyflavanone (PubChem CID 2825024) or the exact pentamethoxyflavone (PubChem CID 100625). Occurrence reports, aggregate PMF totals, other PMFs, structurally similar analogues, isolation yields, and qualitative non-detections were not converted into concentrations.

The complete values and dispositions are in `batches/batch_100_contextual_reconciliation/CONTEXTUAL_QUANTITATIVE_SCREEN.csv` and `CONTEXT_COVERAGE.json`.

## E. Scientific limitations

Medicinal roots, botanical supplements, extracts, and vegetative plant tissues are not interchangeable with consumer foods. Their preparation, dose, edible status, denominator, and intended use can differ. Contextual values therefore cannot support ordinary dietary exposure without an explicitly supported consumption matrix and preparation model. The two unresolved values remain missing, not zero.

Phase 1B does not apply Stage A cooking-retention predictions. It does not establish recipe-level or population dietary exposure, food-retention estimates, bioavailability, clinical effects, or health risk. Study-specific values must not be generalized beyond their source matrices and conditions.

## F. Validation and testing

- Full Stage C suite: **61/61 passed**, 0 failures, 0 blocked.
- Focused mapping, food-composition, unit-conversion, exposure, and integration suite: **48/48 passed**; both CLI portability tests passed as well (50/50 across focused modules).
- Phase 1 data validation: **PASS**, 511 food records, 511 mappings, zero mapping/orphan/integrity errors.
- Independent mapping rebuild: **byte-for-byte match** with the active mapping CSV; recomputed coverage is 109/119.
- Stage B connector: **PASS**, 710 manifest entries, 119 compounds.
- Stage B portable validator: **16/16 checks passed**, 0 errors, **313 existing warnings**; warnings remain documented and were not suppressed.
- Clean-copy test and validation results are recorded with the versioned release.
- Initial full-suite runs exposed one stale integration-test expectation (99 rather than the active dataset size); that assertion was corrected. A portable report-path check was added, and the final suite passed.

## G. Reproducibility and release

Versioned release: `stageC/releases/Phase1B-v1.0.0/`. It contains the Phase 1B reports and all 100 batch folders, active data and mappings, Stage C source/schemas/scripts/tests, and a copy of the checksummed Stage B input release with the current Stage B snapshot.

Inspect `README.md` in that directory for test/validation commands. `CHECKSUMS.json` records SHA-256 values for **1,064 packaged artifacts**, and `CHECKSUMS.sha256` records the checksum-manifest digest. `RELEASE.json` identifies the package, data counts, test evidence, and source Stage B manifest hash. The package verifier reports the current manifest digest when run.

## H. Protected-data and historical-baseline audit

The Stage A tree (19 tracked files) and Stage B archive tree (8,096 tracked files) are clean against the current Git HEAD and have fresh tree hashes in `PROTECTED_TREE_AUDIT_2026-11-02.json`. The current Stage B connector verifies the StageB_Final manifest. The StageB_Final tracked working tree already contains changes to its generated SHA-256 manifest and generated validation report, plus an untracked reconciliation record from the earlier manifest repair; this report does not claim those historical generated-file changes were made during final Phase 1B packaging. Stage B source/evidence tables were not changed in this finalization.

The older `BASELINE_CHECKSUMS.json` does **not** match the current repository tree (19/19 Stage A, 661/709 StageB_Final, and 7,546/8,096 Stage B archive entries differ). It is retained as historical evidence and is not represented as a current successful comparison. The earlier `PROTECTED_BASELINE_RECHECK.json` is also a point-in-time report from before the release-manifest reconciliation. The fresh current-tree audit and verified current Stage B manifest are used for this release; the old checksum mismatch remains an explicit limitation.

## I. Remaining limitations and exit decision

Ten of 119 targets remain without accepted ordinary-food quantitative measurements. Contextual source values are recorded separately; irilone remains secondary-source-only; two targets have no verified exact numeric matrix result. The 313 Stage B validator warnings are inherited and remain visible. The legacy protected-baseline checksum file is stale against the current tree.

**Phase 1B exit decision: COMPLETE WITH DOCUMENTED LIMITATIONS.** All feasible Phase 1B acquisition, source screening, mapping reconciliation, quality checks, report updates, and reproducible release deliverables are complete. The limitations above are explicit; no value or completion claim is fabricated. Phase 2 is not part of this release.
