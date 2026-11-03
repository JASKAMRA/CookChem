# CookRisk Phase 3 recipe and meal core — v0.1.0

Status: **COMPLETE_WITH_DOCUMENTED_LIMITATIONS**. This versioned package contains the source-traceable recipe/meal core, schemas, realistic pinned-release examples, and focused synthetic tests. The tests run from this directory without network access or external release data.

Run the package's isolated core tests from the repository root:

```powershell
python -m unittest discover -s stageC/releases/Phase3-v0.1.1/stageC/tests -v
```

The calculation CLI in the working source uses the pinned Phase1B, Phase2, and Phase4 packages in the repository. The core package's independent tests use synthetic fixtures; live CLI calculations are verified in the project working tree against Phase1B-v1.3.2, Phase2-v0.3.1, and Phase4-v0.1.2. No Phase 1B, Phase 2, Stage B, or Phase 4 data is copied into this Phase 3 package.

Measured mass/volume remain distinct. Missing inputs stay missing. The release contains no cooking-retention factors; Phase2-v0.3.1 has zero quantitative cooked-concentration estimates. Clinical interpretation is outside scope.
