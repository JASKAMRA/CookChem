# Phase 2 Follow-up Evidence Audit — 2026-11-03

**Scope:** continuation of the frozen `Phase2-v0.1.0` diagnostic. This report is additive; it does not edit the release, Stage A, Stage B, or Phase 1B releases. No cooked-concentration output was generated.

## Disposition

| Evidence set | Decision | Count |
|---|---|---:|
| Turmeric/curcumin Phase 1B combinations | Unresolved: Phase 1B commercial powder basis cannot be bridged to the cooking study denominator | 20 |
| Black pepper/piperine | Unresolved: retail sample physical state and denominator are not shown to match cooking-study spice powder | 1 combination; 3 separate scenarios |
| Green tea/EGCG | Rejected for numeric calculation: linked Stage B evidence is qualitative and has no quantitative retention factor | 1 |
| Scientifically accepted cooked concentrations | None | 0 |

The 20 turmeric rows remain classified as **food ingredient**. They are contextual ingredient records, not ordinary-food cooked concentrations. Their two source contexts (turmeric alone and turmeric with tamarind) stay distinct.

## Turmeric measurement-basis bridge

Phase 1B records `PAUDEL2025-002-Co-T-1-CURCUMIN` through `PAUDEL2025-002-Co-T-10-CURCUMIN` are commercial turmeric powder observations. The source says commercial samples were transported to the laboratory for preparation and analysis; the commercial-sample table reports curcumin in mg/g with triplicate analysis. It does not report a sample moisture percentage, dry-matter fraction, lyophilization, or a conversion factor. The Phase 1B field therefore correctly remains **as-analyzed commercial powder; moisture correction not stated**. The paper separately describes drying/freeze-drying for prepared fresh-rhizome experimental material, which cannot be transferred to the commercial samples.

The Suresh source methods say spices were purchased locally, powdered, and cooked as 1 g spice in 100 mL water; the turmeric-only and turmeric+tamarind cooking products were lyophilized before extraction. Tables 1 and 3 report mg/g spice and condition-specific raw/cooked group means. Neither the thesis methods/tables nor the journal record supplies a moisture value or a stated equation that converts the reported values between the initial spice mass and lyophilized cooked material. Thus “mg/g” alone does not establish denominator equivalence with the Phase 1B commercial powder measurements. No generic dry-weight or moisture conversion is scientifically supported here.

Accordingly, the 20 candidate links remain unresolved. Their source contexts and conditions are preserved in `source_condition_level_retention_candidates_2026-11-03.csv`; the recorded quotients are **apparent concentration ratios** (cooked group-mean concentration divided by raw group-mean concentration), not total analyte mass retention and not Phase 1B cooked concentrations.

Primary sources: [Paudel et al., commercial turmeric measurements](https://onlinelibrary.wiley.com/doi/10.1155/jfq/8925770); [Suresh thesis, methods and Tables 1–3](https://ir.cftri.res.in/1533/1/SureshD.pdf); [Suresh et al., journal record](https://doi.org/10.1016/j.jfca.2006.10.002).

## Black pepper/piperine: scenario-by-scenario review

Phase 1B record `KOREA-PEPPER-2021-PIPERINE` is an ordinary-food retail aggregate. The primary 2021 paper reports 71 black-pepper retail samples, homogenized before analysis, and piperine as 4418 ± 946 mg/100 g sample (equivalent to 44,180 mg/kg on the reported sample-mass basis). It gives no moisture correction or dry-weight basis. “Homogenized” describes the analytical preparation; it does not say whether the pepper was bought whole or already ground.

Suresh's cooking study explicitly uses locally purchased spice that was powdered, then reports piperine group means in mg/g spice after cooking/lyophilization. The identities and units are compatible (piperine; mg/kg can be divided by 1000 to express mg/g), but the physical starting state and concentration denominator are not established as equivalent. The three scenarios were reviewed independently:

| Scenario | Source conditions | Piperine means, mg/g spice (raw → cooked) | Apparent concentration ratio | Decision |
|---|---|---:|---:|---|
| Boiling 10 min | 1 g spice/100 mL water; boil 10 min | 55.8 ± 3.40 → 40.8 ± 2.76 | 73.11828% | Unresolved; sample-state/basis bridge absent |
| Boiling 20 min | 1 g spice/100 mL water; boil 20 min | 55.8 ± 3.40 → 40.3 ± 3.26 | 72.22222% | Unresolved; sample-state/basis bridge absent |
| Pressure cooking 10 min | 1 g spice/100 mL water; 15 psi | 55.8 ± 3.40 → 36.9 ± 2.74 | 66.12903% | Unresolved; sample-state/basis bridge absent |

Each study value is mean ± SEM from five independent determinations. Formula for the displayed ratios: `cooked group mean concentration / raw group mean concentration`. No ratio was applied to the Phase 1B retail value. A valid application requires evidence that the retail sample's pre-analysis state and denominator correspond to the powdered spice and reporting basis in the cooking study (or the source's measured moisture/dry-matter factors and a defensible conversion). That is the smallest missing pepper-specific evidence.

Primary source: [Korea et al., black-pepper retail piperine measurements](https://pmc.ncbi.nlm.nih.gov/articles/PMC7914320/); cooking values and methods: [Suresh thesis](https://ir.cftri.res.in/1533/1/SureshD.pdf).

## Phase 1B regression/checkpoint investigation

The legacy root active tables and `CHECKPOINTS.json` are not the latest Phase 1B successor. Direct release inspection shows:

| Release | Food rows | Batch 115 NHDC record |
|---|---:|---|
| Phase1B-v1.1.0 | 570 | Absent |
| Phase1B-v1.2.9 | 584 | Present in food and mapping tables |
| Phase1B-v1.3.0 | 584 | Present in food and mapping tables |

The NHDC record in v1.2.9/v1.3.0 is `B115-ITALIAN-HARD-CANDY-NHDC` / `MOL-V15-CID-30231`. Its published category summary is 11 ± 10 mg/kg among three detections, with only one above LOQ and the mean/SD incorporating LOQ/2 substitutions. It is retained with that limitation and counted as one compound, not as three exact sample measurements.

The root Phase 1B working tree still has 546 food and mapping rows while its current coverage register contains 101; the legacy checkpoint/test expects 100. Its active source registry has 63 rows while the legacy checkpoint expects 62. These are legacy working-tree/checkpoint inconsistencies, not Phase 2 regressions. The right action is **not** to change the historic expected counts or transplant Batch 115 into the legacy root. The justified successor integration already exists in Phase1B-v1.2.9/v1.3.0; the three old root-suite assertions remain tied to the older branch. No checkpoint or test expectation was changed.

## Model inference reproducibility

The frozen model manifest expects training input SHA-256 `cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27`. Both repository copies found at `data/preprocessing/final/cookchem_molecular_retention_preprocessed.csv` and `stageA/input/cookchem_molecular_retention_preprocessed.csv` are 570,209 bytes and have SHA-256 `750124efc8b89dff1f67764064b1049b5db51fb1b2f222d4f91cd94c56945f89`. A content-hash scan of 36,373 repository files found no copy of the expected snapshot, including release archives. The `.joblib` artifact itself matches its expected SHA-256 `0f03701099a66792c8ebf9b81d650114968a415996e17ae5dd34048f5e15cb62`.

The manifest records Python 3.12.14 and pandas 3.0.6. The selected ExtraTrees artifact needs joblib, NumPy, pandas, and scikit-learn; the current Python 3.14.7 environment lacks those modules. The manifest does not pin NumPy, scikit-learn, or joblib versions, so an exact package environment cannot yet be reproduced from repository evidence. XGBoost/CatBoost are listed in broad Stage B requirements but are not runtime dependencies for this selected ExtraTrees model. The input snapshot hash is the primary blocker; do not install packages or load the model against a different training snapshot.

Reproducible setup procedure once the original snapshot and package lock are recovered:

1. Create an isolated environment with Python 3.12.14 (e.g. `python3.12 -m venv .venv-stageb-inference`).
2. Install the recovered, exact lock file for joblib, NumPy, pandas 3.0.6, scikit-learn, and transitive dependencies; do not resolve unpinned “latest” versions.
3. Verify the training CSV hash above and the model artifact hash before deserialization.
4. Apply the manifest's 22 base features and `stageB/scripts/evaluate_missingness_features.py::augmented_features` 11 derived features in the original preprocessing order; validate all 33 feature names/types and scenario inputs.
5. Record input, model, environment-lock, code, and output hashes with inference output. Never substitute Stage A OOF predictions for new-record inference.

Until items 1–4 have reproducible inputs, inference remains blocked; no inference was attempted.

## Validation and release integrity

- Focused Phase 2 tests: **14/14 passed** (`python3 -m unittest discover -s stageC/tests -p 'test_phase2*.py' -v`).
- Full Stage C suite: **113 total, 110 passed, 3 failed**. All three are the legacy Phase 1B count assertions described above; no Phase 2 test failed. Full-run log: `full_stagec_test_rerun_2026-11-03.log`.
- `Phase2-v0.1.0`: all 19 manifest file hashes matched; no release file was modified.
- `Phase1B-v1.3.0`: all 1,321 artifact hashes and byte lengths in `CHECKSUMS.json` matched.
- The frozen Phase 2 validation record reports the prior clean-copy regeneration of 11 generated files with matching SHA-256 outputs. No new code/data release was warranted by this evidence-only audit; no successor release was created.

## Final status

**NOT COMPLETE.** The requested basis/state bridges are not established; therefore zero scientifically valid cooked-concentration outputs were generated. The exact model training snapshot is unavailable, and the full Stage C suite retains three legacy Phase 1B checkpoint failures.
