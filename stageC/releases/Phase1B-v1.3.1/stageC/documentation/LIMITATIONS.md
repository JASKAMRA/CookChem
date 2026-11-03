# Limitations

- No quantitative raw-food concentration records are present; no real exposure can currently be computed.
- Stage B is `READY_WITH_WARNINGS`, not a blanket scientific verification. It has 19 pending chemical identity reviews, 105 incomplete food-occurrence reviews, 17 supplement/medicinal-botanical contexts, 13 high numeric/unit warning flags, and incomplete source-audit coverage.
- Stage B interaction evidence and three cooking-retention records are separate evidence types and cannot populate food composition.
- Quantitative source acquisition requires a supplied/retrieved dataset and record-level verification. No API key or external dataset is bundled.
- Density-dependent volume conversions, wet/dry conversions, cooking retention, uncertainty propagation, clinical interpretation, and risk scoring are out of Phase 1.
- Current test-runner environment does not include pytest. Tests use Python's standard-library unittest and passed there; pytest itself was not run.
