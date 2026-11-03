# Stage C Phase 2 — cooking-retention integration

**Status: NOT COMPLETE.** Source-pair transcription and compatibility audits are available; no cooked concentrations passed the scientific compatibility gates. Phase 1B is a read-only input at the versioned Phase1B-v1.3.0 release.

## Phase 2 v0.1.0 integration release

`stageC/releases/Phase2-v0.1.0/` contains the versioned interim release. It integrates all 584 Phase 1B rows, separates 335 ordinary-food records from 249 food-ingredient/prepared-beverage records, accepts 19 strict Stage A–B identity links plus a manual structure match for Curcumin with its CID discrepancy retained, and exports the 117 experimental ratios as apparent concentration ratios.

No retention-adjusted cooked concentration was produced: the 3 quantitative Stage B intervals do not have adequately matched Phase 1B matrix, process, and measurement basis. The frozen model was not loaded because its training-data hash differs from current Stage A. Exit status is **NOT COMPLETE**.

## Intake and scientific rules

- `data/stagea_stageb_identity_crosswalk.csv` records strict Stage A-to-Stage B matches and unresolved candidates. A separate status is used when stable molecular ID, name, and canonical SMILES agree but the Stage A CID conflicts; CID alone is not used to join.
- `data/identity_candidate_review.csv` records a decision for all 36 CID/name/structure candidates and all 9 within-group CID conflicts. Every unresolved row is kept pending rather than force-mapped.
- `data/observed_retention_evidence.csv` preserves source-reported cooking/brewing effects. Numeric loss ranges are complemented to retention ranges with source and matrix limitations retained. These remain separate from Phase 1B composition rows.
- `data/observed_cooking_pairs.csv` contains 117 raw/cooked concentration pairs: 33 curcuminoid pairs from initially fresh turmeric rhizome and 84 pairs covering 4 pumpkin-leaf phenolics plus 17 amino acids. The source-pair audit independently checks all table means, SDs, replicate counts, units, and ratios. For the turmeric source, the paper says mg/g plant material but does not explicitly define the post-cooking denominator; the older `mg/g fresh rhizome` label is therefore flagged as over-specific. Pumpkin values are reported on a dry-weight basis. Ratios remain apparent concentration ratios, not total analyte mass retention.
- `src/stage_c/phase2_retention.py` provides interval arithmetic and blocks concentration adjustment unless compound, matrix, cooking conditions, and basis compatibility are all attested by the caller.
- `scripts/audit_phase2_readiness.py` rebuilds the intake crosswalk and evidence ledger from read-only Stage A and Stage B inputs.

## Current gates

Stage A has 1,124 input rows across 197 molecular groups and 5,620 out-of-fold predictions across five models. A frozen Stage B Extra Trees candidate exists, and its artifact hash matches its manifest, but the manifest's training-input hash differs from the current Stage A input hash. This mismatch alone prevents inference; no environment install can establish compatibility with the current data revision. The current runtime also lacks joblib, NumPy, pandas, scikit-learn, and XGBoost. OOF predictions are for validation and cannot be applied to new food records.

Nineteen Stage A groups have strict CID, canonical name, and canonical SMILES agreement with Stage B. Curcumin has one additional manually accepted stable-ID/name/SMILES match; its Stage A PubChem CID is unresolved and its discrepancy remains visible. Among the 45 candidate rows, 27 remain possible matches, 9 identity conflicts, and 9 unresolved; none is promoted by CID equality alone. No model-to-food predictions or Phase 1B-adjusted cooked concentrations are generated.

These observed pairs are source-compatible within each study: same analyte and matrix, with raw controls and specified cooking conditions. They are empirical source transcriptions, not predictions. Pumpkin-leaf analytes remain linked to their Stage A molecular group only; unresolved Stage A-to-Stage B identity joins are left blank. [Turmeric study, Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC10453412/), [pumpkin-leaf study, Tables 2 and 3](https://pmc.ncbi.nlm.nih.gov/articles/PMC13515228/).

## Reproduce

From the CookChem repository root:

```sh
python3 stageC/scripts/audit_phase2_readiness.py
python3 stageC/scripts/audit_phase2_source_pairs.py
python3 stageC/scripts/build_phase2_release.py
python3 -m unittest stageC.tests.test_phase2_source_audit -v
python3 -m unittest discover -s stageC/tests -p 'test_phase2*.py' -v
python3 -m unittest discover -s stageC/tests -v
```

Source table comparisons for all 117 rows are in `stageC/reports/phase2/source_pair_audit_2026-11-03.csv`; compatibility decisions are in `retention_compatibility_matrix_2026-11-03.csv`; candidate source cooking conditions are in `source_condition_level_retention_candidates_2026-11-03.csv`. Full architecture, identity, methods, limitations, and handoff reports are in the `stageC/reports/phase2/` directory.

Current validation: Phase 2 tests pass 14/14. The complete Stage C suite runs 113 tests: 110 pass and 3 pre-existing Phase 1B assertions fail on stale expected counts (eligible coverage 100 vs current 101; source registry checkpoint 62 vs current 63; the second coverage check also expects 100). The Phase 2 release report records these failures without changing or weakening the Phase 1B tests.
