# CookChem Stage B

Stage B contains the cooking-retention modeling work and the CookRisk literature evidence package.

## Authoritative evidence release

The sole authoritative Stage B evidence deliverable is [`release/StageB_FINALIZED/`](release/StageB_FINALIZED/). It contains 143 compounds, 317 interaction-evidence records, 133 drug/probe rows, 163 bibliography rows, 161 study rows, and 88 traceable warnings. Its status is `FINALIZED_WITH_DOCUMENTED_SCIENTIFIC_LIMITATIONS`.

The release consolidates the best validated state from V19 batches 001–012 on the immutable V18 baseline. Earlier folders, including `StageB_Final` (119 compounds), V18, and V19, are retained as non-authoritative historical records for provenance and reproducibility. Do not use them as the current evidence package or resume their research queues.

## Validate the evidence release

From the repository root, run:

```powershell
python stageB/release/StageB_FINALIZED/scripts/validate_final.py stageB/release/StageB_FINALIZED
python stageB/release/StageB_FINALIZED/scripts/validate_stageb_finalized.py stageB/release/StageB_FINALIZED
python stageB/release/StageB_FINALIZED/scripts/mutation_test_final.py stageB/release/StageB_FINALIZED
```

The release README records the complete test and manifest commands. Technical validation checks structure, references, provenance and integrity; it does not certify that every historical scientific claim has been independently re-reviewed.

## Repository layout

- `release/StageB_FINALIZED/` — sole authoritative literature-evidence package.
- Other `release/StageB_*` folders — historical, non-authoritative snapshots.
- `scripts/`, `outputs/`, `final_model/` — existing retention-model work and outputs.
- `validation/`, `provenance/`, `archive/` — repository-level validation, organization history and preserved older materials.

Stage B finalization is complete. Further Stage B evidence research or expansion is stopped; any next-stage work requires a separate user instruction.
