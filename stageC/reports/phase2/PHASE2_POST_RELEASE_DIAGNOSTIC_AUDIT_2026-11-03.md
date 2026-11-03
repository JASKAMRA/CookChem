# Phase 2 Post-release Diagnostic Audit — 2026-11-03

**Frozen release:** `Phase2-v0.1.0` was not rebuilt or modified. Its 19 file hashes still verify. This is an audit outside the release. No cooked concentrations were created.

## 1. Full Stage C failures

Rerun: `python3 -m unittest discover -s stageC/tests -v` → **113 tests, 110 passed, 3 failed**. Exact log: `full_stagec_test_rerun_2026-11-03.log`. The Phase 2 tests pass 14/14. These failures are in Phase 1B checkpoint/coverage tests and are not caused by Phase 2 code.

| Failing assertion | Trace | Finding |
|---|---|---|
| `test_current_coverage_register_reconciles_all_143_stage_b_ids` expects 100; reads 101 | `test_phase1b_batch101.py:125` reads `stageC/reports/phase1b/COMPOUND_COVERAGE_REGISTER_2026-11-03.csv` | The committed `HEAD` register had 100; working-tree register has 101. The extra row is Batch 115 NHDC (`MOL-V15-CID-30231`). However its record `B115-ITALIAN-HARD-CANDY-NHDC` and mapping are **absent** from active `food_composition.csv` and `compound_food_mapping.csv`, each still 546 rows. So changing the test to 101 would hide an active-data/report discrepancy. The historic `CHECKPOINTS.json` also says 100. Do not edit the test/checkpoint without reconciling the NHDC ingestion. |
| `test_all_stage_b_ids_screened_and_coverage_is_identity_gated` expects 100; reads the same register | `test_phase1b_continuation_102_103.py:70` | Same NHDC report-vs-active-data discrepancy; not a Phase 2 regression. |
| `test_checkpoint_preserves_active_data_and_records_batch_totals` expects 62 source rows; active file has 63 | `test_phase1b_batch104_gap_reaudit.py:113` compares active registry with old `CHECKPOINTS.json` | Checkpoint has 62 rows / 61 unique URLs; current source registry has 63 / 62. Its extra row is the Batch 115 Italian-market sweetener/NHDC source DOI. This is a stale Phase 1B checkpoint after source research, not a Phase 2 mutation. No checkpoint was rewritten. |

**Assessment:** The assertions are stale relative to the working-tree coverage/source files, but the coverage mismatch also reflects a real Phase 1B integration inconsistency: Batch 115 is counted by the register but is not in the active measurement/mapping tables. No Phase 1B edits were made because the active request says preserve Phase 1B. The corrective owner must reconcile Batch 115 and then refresh the appropriate successor checkpoint; simply changing expected integers is not evidence-supported.

## 2. Why cooked-concentration outputs are zero

Exact compound-ID crosswalk against the four Stage B retention records yields **22 combinations**: 10 turmeric powder records × two contexts (turmeric alone and turmeric+tamarind) = 20; one black-pepper/piperine record = 1; one brewed green-tea/EGCG record = 1. The old v0.1.0 applicability screen counted 15 food rows using name-substring matching; that count is not the number of identity-joined food/retention combinations. Record-level decisions are in `retention_compatibility_matrix_2026-11-03.csv`.

- **Eligible now:** 0.
- **Unresolved pending basis/state adjudication:** 21 (20 curcumin contexts, 1 piperine).
- **Rejected for numeric output:** 1 EGCG combination, because the Stage B evidence is qualitative and has no EGCG retention fraction.
- **Unit-incompatible:** 0 for the 21 quantitative spice combinations (mg/kg ↔ mg/g is a valid ×/÷1000 conversion).
- **Compound-identity failures:** 0. Curcumin is linked by stable ID/name/SMILES with the CID warning preserved; piperine and EGCG are strict matches.
- **Food-matrix identity mismatch:** 0 direct mismatches; EGCG is a partial matrix match because the measurement is a standardized decaffeinated infusion while the source describes green-tea brewing.
- **v0.1.0 condition-level evidence gap:** 21 spice combinations were stored only as pooled retention envelopes. This audit resolves that part by transcribing source-specific boil/pressure-cook conditions into 63 scenario rows; those scenarios must remain separate and must not be averaged together.
- **Remaining measurement-basis blocker:** 21 spice combinations, because Phase1B powder/retail values do not report moisture correction and the primary cooking samples were lyophilized before reporting mg/g spice.
- **Food-state ambiguity:** 1 piperine retail aggregate (as-received homogenized sample versus source powder); the 10 turmeric records are dried powder and broadly align with source powdered spice.

The primary cooking study contains condition-level raw/cooked means omitted by the current Phase 2 retention ledger. Table 1 gives turmeric alone 25.7 mg/g raw and 18.8/17.3/12.1 mg/g after boiling 10 min/20 min/pressure cooking 10 min; Table 3 gives black pepper 55.8 mg/g raw and 40.8/40.3/36.9 mg/g under those same conditions. Table 1 separately gives turmeric+tamarind 21.7 mg/g raw and 18.5/17.0/14.3 mg/g after those conditions. These are five-independent-determination group means ± SEM, and their calculated ratios are recorded as **apparent concentration ratios**, not total mass retention. The new `source_condition_level_retention_candidates_2026-11-03.csv` records 63 linked scenario candidates without deriving Phase1B cooked concentrations. Primary source/methods: [Suresh doctoral thesis PDF, Methods and Tables 1–3](https://ir.cftri.res.in/1533/1/SureshD.pdf); journal article [DOI 10.1016/j.jfca.2006.10.002](https://doi.org/10.1016/j.jfca.2006.10.002).

**Smallest concrete gap:** For the 11 spice Phase1B measurements, establish that the source study's `mg/g spice` denominator after lyophilization is compatible with the Phase1B as-analyzed/as-received concentration denominator—or obtain moisture/dry-matter values to convert the Phase1B observations. Exact method/duration/additive scenarios are now transcribed in the companion CSV. That makes **63 scenario-level calculations** reviewable (60 turmeric ingredient-context scenarios, separate from ordinary-food calculations, plus 3 black-pepper scenarios); none are accepted until the basis check passes. For EGCG, quantitative matched brewing retention data are missing; qualitative extraction/epimerization cannot yield a number.

## 3. Model-inference blockers

- Stage B manifest training-input SHA-256: `cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27`.
- Current Stage A input SHA-256: `750124efc8b89dff1f67764064b1049b5db51fb1b2f222d4f91cd94c56945f89` (size 570,209 bytes); exact mismatch. The expected snapshot is not present under the repository file inventory; only the current Stage A input CSV is available.
- Frozen artifact SHA-256: `0f03701099a66792c8ebf9b81d650114968a415996e17ae5dd34048f5e15cb62`; matches the manifest.
- Runtime: Python 3.14.7 versus manifest Python 3.12.14; selected-model essentials joblib/NumPy/pandas/scikit-learn are absent. XGBoost and CatBoost are also absent but are not required by this selected ExtraTrees model; they appear in the broader Stage B requirements.
- Manifest has 22 base plus 11 added features, with augmentation in `stageB/scripts/evaluate_missingness_features.py`, but does not pin NumPy/scikit-learn/joblib versions. A compatible feature list alone cannot authorize loading against the wrong training snapshot.

To make inference reproducible: recover the exact input snapshot with hash `cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27`; reproduce the manifest's training/feature-preprocessing code; obtain the original package lock or environment inventory (at least Python, NumPy, pandas, scikit-learn, joblib); load only after artifact and input hashes pass; validate a scenario-specific 33-feature row; and save inference outputs separately with model/input/environment/output hashes. If the exact snapshot cannot be recovered, the frozen model remains unusable; any retraining must be a separately versioned candidate using an explicit validation protocol. No inference or OOF reuse occurred.

## 4. Next milestone

First resolve the Phase 1B Batch 115 coverage-register/active-table mismatch in a Phase1B successor. Independently, adjudicate the as-analyzed vs lyophilized-spice denominator and encode Suresh's condition-specific means/ratios in a new Phase 2 evidence ledger. Then the smallest valid Phase 2 demonstration is the ordinary-food black-pepper/piperine row under three explicit source cooking scenarios; keep the 10 turmeric-powder outputs in a separate food-ingredient/context table. Do not report a numerical EGCG cooked concentration until quantitative retention evidence exists.

**Phase 2 status: NOT COMPLETE.** Intake, ratio validation, identity review, and compatibility audit are complete; no retention-adjusted cooked concentration has passed the basis gate and frozen-model inference remains blocked.
