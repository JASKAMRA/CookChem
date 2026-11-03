# CookRisk Stage C Phase 2 v0.1.0

Status: **NOT COMPLETE — reproducible interim integration release.**

This release integrates all 584 Phase 1B rows, separates ordinary-food from ingredient/beverage context, preserves identity cross-phase statuses, validates 117 experimental apparent concentration ratios, and records explicit cooking-applicability decisions. It does not provide retention-adjusted cooked concentrations: no Phase 1B row currently passes all exact identity, food matrix/state, cooking-process, and measurement-basis gates. The frozen Stage B model is not used because its training-input hash differs from current Stage A and the runtime dependencies are missing.

Rebuild from repository root: `python3 stageC/scripts/build_phase2_release.py`. Validate: `python3 -m unittest discover -s stageC/tests -p 'test_phase2*.py' -v` and `python3 -m unittest discover -s stageC/tests -v`. Release data are generated with Python standard library only. Historical Phase 1B and frozen Stage A/Stage B artifacts are read-only inputs.
