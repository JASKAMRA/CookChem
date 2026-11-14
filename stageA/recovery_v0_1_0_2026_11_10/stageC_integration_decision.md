# Stage C integration decision — no code change justified

The existing `stageC/src/stage_c/cooking_integration.py` already separates apparent concentration ratios, concentration retention, total-mass retention, measured retention, and model-predicted retention. Its fail-closed behavior blocks unregistered model predictions and prevents apparent ratios being used as total-mass multipliers.

No Stage C code was changed in this recovery version. A change would be premature because this package does not approve a model or a target contract. The next integration change, only after scientific approval, is to register a separately versioned model-prediction package through the existing `model_predicted_retention` path with an explicit semantic type, hashes, applicability result, and uncertainty declaration.
