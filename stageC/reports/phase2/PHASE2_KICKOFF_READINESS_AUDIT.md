# Stage C Phase 2 kickoff and readiness audit

Date: 2026-11-03. Phase 1B closure at 125/130 was accepted by the user; Phase 2 is now authorized. The previous Phase 1B minimum remains unmet by five compounds, and that shortfall is explicitly preserved in [the Phase 1B closeout](../phase1b/PHASE1B_CLOSEOUT_2026-11-03.md).

## What was inspected

- Read-only Phase 1B successor `Phase1B-v1.3.0`: 143 compounds, 130 identity-complete, 13 identity-pending; 584 food records/mappings; 125 accepted identity-complete quantitative food-covered compounds.
- Stage A input: 1,124 rows and 197 `Canonical_Molecular_ID` groups. Its OOF file has 5,620 rows: 1,124 per model across ExtraTrees reference, Random Forest, RBF-SVR, XGBoost, and tuned XGBoost.
- Stage A report selects Extra Trees as the benchmark to retain. Stage A itself has no fitted model artifact. A frozen Stage B Extra Trees candidate exists at `stageB/final_model/cookrisk_retention_stageB_selected.joblib`, and its artifact checksum matches its manifest. However, that manifest records input SHA-256 `cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27`, while the current Stage A input is `750124efc8b89dff1f67764064b1049b5db51fb1b2f222d4f91cd94c56945f89`. The current Python environment also lacks joblib, NumPy, pandas, scikit-learn, and XGBoost. The candidate is therefore held; no new-record inference is performed from it or from OOF rows.
- Stage B V20 has three cooking/brewing evidence records. The first two describe measured cooking losses; the green-tea record describes extraction and catechin epimerization without a single EGCG retention percentage.

## Identity crosswalk result

The crosswalk uses a strict equality check on Stage A CID, canonical compound name, and canonical SMILES string against Stage B. This is conservative and reproducible; CID by itself can point to a different entity. Results across 197 Stage A groups:

| Status | Groups |
|---|---:|
| Exact CID + name + SMILES string match | 19 |
| Stable molecular ID + name + SMILES match, CID discrepancy | 1 |
| CID candidate, name or structure needs review | 36 |
| Conflicting CIDs within a Stage A group | 9 |
| No Stage A CID | 5 |
| No matching Stage B CID | 127 |

Of the 19 strict matches, 18 already have accepted Phase 1B quantitative food coverage. Curcumin is now separately matched through identical stable molecular ID, canonical name, and canonical SMILES despite a Stage A CID discrepancy (Stage A resolved-CID field is blank). It is not counted as a strict CID match. The full auditable table is `stageC/phase2/data/stagea_stageb_identity_crosswalk.csv`.

Every non-strict candidate has since been reviewed and documented in `stageC/phase2/data/identity_candidate_review.csv`: 27 same-name CID candidates are pending structure equivalence review, 9 CID candidates also conflict with the Stage A canonical label and remain pending name/structure review, and all 9 within-group CID conflicts remain pending reconciliation. Stage B's PubChem identity audit can support its own registry structure, but this runtime has no cheminformatics toolkit to normalize and compare the Stage A SMILES against the returned PubChem structure. No identity ceiling or coverage count is increased from these unresolved candidates.

## Source-backed observed retention ledger

Suresh et al. (2007) tested turmeric, red pepper, and black pepper under boiling for 10 or 20 minutes and pressure cooking for 10 minutes, quantifying active principles in extracts of freeze-dried cooked spice samples by HPLC. The paper reports 16–34% piperine loss in black pepper and 27–53% curcumin loss in turmeric. In tamarind's presence it reports 12–30% curcumin loss. Complementing these source-reported loss ranges gives retention intervals of 66–84%, 47–73%, and 70–88%, respectively. These are study-condition ranges, not confidence intervals or universal factors. [Primary paper](https://doi.org/10.1016/j.jfca.2006.10.002)

For green tea, Jin et al. (2019) measured eight catechins in infusions at 60 °C and 95 °C over 5–300 minutes; their results show extraction changes and epimerization, so the Stage B summary does not support a single EGCG retention coefficient. This stays qualitative until an exact analyte-by-condition table is ingested with the correct interpretation. [Primary full text](https://www.mdpi.com/1420-3049/24/9/1735)

The intervals are recorded in `stageC/phase2/data/observed_retention_evidence.csv`. One primary study supplies 33 directly observed raw/cooked concentration pairs for three turmeric curcuminoids across boiling, dry-pan frying, and 800 W microwaving. A second supplies 84 pairs covering four pumpkin-leaf phytochemicals and 17 amino acids across boiling, microwaving, steaming, and stir-frying. They are recorded in `stageC/phase2/data/observed_cooking_pairs.csv`, with means, SDs, n=3, conditions, source locators, units, and matching Stage A record IDs. The turmeric values are from [Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC10453412/); pumpkin leaf values are from [Tables 2 and 3](https://pmc.ncbi.nlm.nih.gov/articles/PMC13515228/).

The turmeric values are mg/g fresh rhizome, pumpkin phytochemicals are mg/100 g dry weight, and amino acids are mg/g dry weight. Their ratios are retained as apparent concentration ratios, not total analyte mass retention. The source values are condition-level means, not matched replicate-level pairs; ratio uncertainty is not derived because replicate-level covariance is unavailable. Pumpkin analyte rows are not joined to Stage B IDs where identity crosswalk is pending. These observed measurements do not apply an external retention coefficient to Phase 1B composition data. **No Phase 1B concentration has been adjusted yet.** EGCG still has no matching accepted Phase 1B food concentration in this release.

## Implemented arithmetic and validation

`stageC/src/stage_c/phase2_retention.py` converts a loss interval `[Lmin, Lmax]` to `[100 − Lmax, 100 − Lmin]` and can apply that interval to a concentration only when the caller explicitly confirms exact compound identity, food matrix, cooking conditions, and compatible measurement basis. Its unit tests cover the complement calculation, interval application, invalid bounds, and blocked incompatible evidence.

Rebuild the Phase 2 intake outputs with `python3 stageC/scripts/audit_phase2_readiness.py` from the repository root. The summary is `stageC/phase2/data/phase2_intake_summary.json`. Stage A input SHA-256 and Stage B V20 manifest SHA-256 are recorded there.

The Phase 2 test module now includes paired-data, CID-discrepancy, complete-review-ledger, and model-readiness gate checks; it passes **9/9**. The 117 source-pair ratios also match their Stage A `Retention_Final` values to 0.01 percentage point (0 discordances). The earlier repository-wide `unittest` run executed 104 tests: **101 passed and 3 failed**, with no setup errors. The three failures are old data-count assertions: two expect 100 covered compounds while the repository-root Phase 1B working-tree register reports 101, and one compares the live source-registry row count (63) to a historical checkpoint count (62). These legacy assertions were not changed.

## Next Phase 2 work

1. Obtain a reproducible structure-normalization tool/runtime, then adjudicate the 36 CID candidates and 9 within-group conflicts against PubChem structures; current ledger preserves each as pending.
2. Expand the source-compatible observed-pair ledger across additional compounds and matrices, keeping concentration ratios distinct from mass retention.
3. Reconcile the Stage B model's recorded input checksum with the current Stage A source and restore a compatible runtime; only then validate the full preprocessing/inference path. Do not serve OOF rows as predictions.
4. Add end-to-end tests for one source-compatible example before expanding to recipes or meals.
