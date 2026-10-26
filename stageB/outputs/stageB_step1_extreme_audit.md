# Stage B Step 1 - Extreme Retention Provenance Audit

## Scope
This is an audit only. It does not change the target, remove observations, train a model, or claim that an extreme value is erroneous.

## Findings
* Threshold: top 1% of `Retention_Final` = 525.281679.
* Extreme observations: 12 of 1124.
* All extreme observations are retained in the primary modelling dataset.
* Their provenance is traceable through Record_ID, Paper_ID, DOI and Source_Paper_Key.
* Missing cooking conditions are common among these records; this reduces model information but is not evidence that the retention value is invalid.

## Decision
Every extreme record is labelled **RETAIN: source-level verification required before any correction**. A later source-paper check may correct only demonstrable extraction, transcription, unit or target-calculation errors. Absent that evidence, Stage B will improve modelling without deleting or capping extremes.

## Next modelling implication
The next step is to add leakage-safe process-missingness indicators and physically motivated thermal-exposure features, then evaluate them with the unchanged molecular GroupKFold protocol.
