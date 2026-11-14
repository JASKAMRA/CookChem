# Model scope and limitations

## Decision: C — no defensible predictive model is currently supported

The package implements working, fold-safe research experiments, but no serialized prediction model is released. The best descriptive source-held-out candidate was `random_forest` (pooled R² -0.0475, MAE 51.58, RMSE 175.39). Source-held-out performance is a stress test dominated by source-specific compound, food, basis and protocol domains; it does not demonstrate new-source generalisation.

All results predict only the observed **apparent concentration ratio** `100 × cooked concentration / raw concentration`. They must not be interpreted as total-mass retention, clinical advice, cooking guidance, or deployment evidence. Measurement basis is represented but never converted. The lack of strict cross-source protocol-identical replications remains the decisive scientific blocker.

The only potentially legitimate future use is restricted descriptive, within-source interpolation after a separate, pre-specified assessment of that source's experimental design. This package makes no end-user prediction claim and does not modify Stage C.
