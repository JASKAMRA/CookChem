# Stage A cooking-retention integration readiness

Status: **IN_PROGRESS — adapter contract and conservative calculations implemented; executable Stage A integration blocked by missing deployment artifacts and an undefined target contract.** This is a read-only inspection. Stage A was not run, imported, changed, or used to generate predictions.

## Verified current artifacts

| Item | Observed repository state |
|---|---|
| Preprocessed input | `stageA/input/cookchem_molecular_retention_preprocessed.csv`, 1,124 rows and 197 molecular groups per `stageA/outputs/stageA_qa.json` |
| Input SHA-256 | `cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27` |
| Current runner SHA-256 | `a2de32f24600d18df6a503aba001ce4484295f0802b2ba7d09bbaa6bfc704d0c` |
| Model selection | QA reports `XGBoost_tuned`; selected parameters are in `stageA/outputs/stageA_qa.json` |
| Prediction output | Existing `stageA/outputs/stageA_oof_predictions.csv`; held-out rows contain `Model`, `Record_ID`, `Canonical_Molecular_ID`, `actual`, `predicted`, `fold`, and `tuning` |
| Serialized model | **Not present** in the Stage A package. No model-artifact hash, serving estimator, or serialization format can be verified. |
| Stage A output manifest | **Not present** in the Stage A package. The existing `stageA_qa.json` reports run details but does not hash inputs, code, model, or predictions. |

The existing output is grouped cross-validation output for observed rows, not a fitted model interface for arbitrary recipe inputs. It cannot be used as an inference package. No Stage A inference or prediction regeneration was performed.

## Read-only training and preprocessing contract

- Features: 22 source predictors and five deterministic engineered features (`Temperature × Time`, `log1p(Cooking_Time_min)`, `log1p(Initial_Concentration)`, `LogP × Temperature`, and `TPSA × Cooking_Time_min`). Heavy Atom Count is omitted.
- Numeric preprocessing: median imputation and standard scaling, fit inside each training fold.
- Categorical preprocessing: missing-value fill with `Missing`, one-hot encoding with unknown categories ignored, fit inside each training fold.
- Target transform: `log1p(Retention_Final)`; predictions are inverse transformed with clipped `expm1` before original-scale metrics.
- Validation: five-fold `GroupKFold` using `Canonical_Molecular_ID`, seed 42; selected XGBoost tuning is nested within outer training partitions.
- Documented runtime: Python 3.12.14, NumPy 2.5.3, pandas 3.0.6, scikit-learn 1.9.1, XGBoost 3.4.1. Python itself is not pinned in `stageA/stageA_requirements.txt`.
- Serialization: none documented or found; the runner constructs fold-local pipelines and writes CSV/JSON evaluation outputs only.

## Scientific and technical blockers

1. The source does not document the operational definition, unit, denominator, or measurement basis of `Retention_Final`. The observed feature `Initial_Unit_Standardized` is not enough to establish the target's output semantics.
2. No serialized selected model exists to hash or apply. The Stage A runner would retrain/evaluate and is explicitly out of bounds for this task.
3. No machine-readable prediction-output manifest or serving contract exists. Input/output provenance therefore cannot be verified from historical OOF files alone.
4. Food/compound identity and matrix applicability are not proven by the molecular model's descriptor features. Those checks must be supplied independently.
5. Model predictions remain unapproved scientific predictions. A checksum or software test cannot establish measured retention or scientific acceptance.

## Implemented handoff

`stageC/src/stage_c/cooking_integration.py` accepts a supplied record only with explicit food and compound IDs, matrix/state, cooking conditions, semantic type, basis and denominator, provenance, and review state. Supplied predictions require hashes for input, code, model artifact, and output, plus runtime/package/model metadata. The compatibility adapter requires eight explicit true/false/unknown gates and reports unresolved reasons. A mock is always ineligible for estimation.

`calculate_cooked_concentration` keeps apparent concentration ratio separate from concentration retention and total-mass retention. It requires scientific approval and all compatibility gates. Total-mass retention additionally requires measured raw and cooked mass in the same basis. Model-predicted and generic measured retention require an explicit underlying retention basis before calculation. These APIs have synthetic tests only; no Stage A prediction is loaded or calculated.

## Next action

For executable Stage A integration, obtain an approved, immutable inference package that includes a serialized model and hash, exact environment lock, hashed feature/preprocessing contract, target-unit/denominator definition, versioned prediction schema, source input and output hashes, and scientific approval criteria. Until then, Stage C Phase 2 remains **IN_PROGRESS** and the existing Phase2-v0.3.1 cooked-estimate set remains empty.
