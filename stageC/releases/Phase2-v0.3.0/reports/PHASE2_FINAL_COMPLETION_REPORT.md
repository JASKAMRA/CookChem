# CookRisk Stage C Phase 2 — Finalization Report (Audit Snapshot)

**Status: NOT COMPLETE.** This is an evidence-backed finalization snapshot, not a claim that the scientific cooked-concentration objective has been achieved. The frozen Phase2-v0.1.0 release remains unchanged.

## Architecture and inputs

Phase 2 integrates 584 Phase1B-v1.3.0 food concentration rows; preserves 335 ordinary-food rows separately from 249 food-ingredient/prepared-beverage rows; carries Stage A/B identity status; holds four Stage B retention evidence records; and transcribes 117 raw/cooked group-mean observations across 24 analytes from two primary sources. Source, table, method, conditions, units, group means/SDs, replicate count, and limitations are retained in the input and audit CSVs.

## Source observations

The turmeric paper reports 33 curcuminoid group-mean pairs for fresh starting rhizome across boiling, dry-pan frying, and microwave conditions. Table 1 uses mg/g plant material; it does not explicitly define the post-cooking denominator or report cooked mass yield. The older input label “mg/g fresh rhizome” is flagged as more specific than the source warrants.

The pumpkin-leaf paper reports 84 observations: 17 amino acids and four phenolics across boiling, microwave, steaming, and stir-frying. Amino acids are mg/g dry weight; phenolics are mg/100 g dry weight. It uses three biological replicates, reports mean ± SD, lyophilizes cooked samples, discards cooking media, and labels the resulting ratios apparent retention. The source audit checks all 117 numeric table transcriptions and reports 117/117 verified, with the 33 turmeric basis warnings kept explicit.

Every ratio is `cooked group mean / raw group mean`. No ratio is mislabeled total mass retention; no ratio is applied to Phase1B concentrations.

## Identity and composition integration

Nineteen cross-phase links are strict matches. Curcumin is manually linked by stable ID, name, and structure with its CID discrepancy visible. Of 45 other candidates, 27 remain possible matches, 9 conflicts, and 9 unresolved. No candidate was forced into a match; Stage A resolved CIDs are missing for the candidate groups.

Phase 1B Batch115 NHDC appears in Phase1B-v1.2.9 and v1.3.0. The older root active tables/checkpoints are a separate historical interface. Their two coverage expectations (100 vs 101) and source registry expectation (62 vs 63) remain unchanged; the full root suite reports these three legacy failures.

## Compatibility and output

There are 22 potential Phase1B food × retention combinations: 20 turmeric ingredient-context rows, one black pepper/piperine row (reviewed under three separately preserved scenarios), and one green-tea/EGCG beverage row. Outcome: 0 accepted cooked concentrations, 21 unresolved spice combinations, and 1 rejected numeric EGCG combination because the evidence is qualitative. No other measured pumpkin analytes have a matched Phase1B pumpkin-leaf composition concentration and linked Stage B numeric retention factor.

The turmeric source basis cannot be converted from as-analyzed commercial powder to the cooking study denominator without source-specific moisture/denominator/yield data. The pepper retail source does not establish whole versus ground purchase state or moisture basis. EGCG lacks quantitative compatible retention. Cooked output remains a valid empty table.

## Model readiness

Required training snapshot SHA-256: `cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27`; no match was found in 36,373 repository files, the one Git revision for each of the two CSV paths, or the user-home filename search. Both current CSV copies hash to `750124efc8b89dff1f67764064b1049b5db51fb1b2f222d4f91cd94c56945f89`. The model artifact hash matches. Manifest records Python 3.12.14 and pandas 3.0.6; Stage A reproducibility pins NumPy 2.5.3, pandas 3.0.6, scikit-learn 1.9.1, XGBoost 3.4.1; the joblib pin for training-time serialization is not established. Model inference was not attempted; OOF predictions were not substituted.

## Validation and release

The focused Phase 2 suite passes 15/15; the full Stage C suite reports 114 tests, 111 passed, and 3 failed, all unchanged legacy Phase 1B count/checkpoint assertions. The Phase2-v0.2.0 clean-copy rebuild matched all 45 packaged file hashes; its release audit test passes 1/1. v0.1.0 hashes verified 19/19; Phase1B-v1.3.0 checksums verified 1,321/1,321.

The additive source audit, identity audit, and methodology/data/limitations/reproducibility/validation/handoff reports are packaged in the versioned **Phase2-v0.2.0** audit successor. It preserves v0.1.0 and remains **NOT COMPLETE**; no cooked output or model inference is represented as successfully executed.
