# Stage A closure and transition record — 2026-11-04 continuation

## Decision

**Stage A engineering closure: NOT SATISFIED. Stage B transition: NOT AUTHORIZED.** Stage A now has a pinned Python environment, a hash guard, a disposable benchmark reproduction, independent metric checks, an RF-01–RF-15 evidence matrix, and twelve automated tests. The runner now writes a path-independent `stageA_run_manifest.json` containing the lock/code/input/output hashes, schema/feature order, exact fold membership hashes, preprocessing contract, estimator settings, package versions and platform. The fresh run is repeatable from the new lock, but its predictions and some metrics differ from the repository's historical outputs. The historical run's full dependency environment and provenance are absent, so that discrepancy remains unresolved. Linux/Windows execution and inference readiness are also unverified. Docker CLI exists but its daemon socket is absent; no Podman, WSL, Wine, or Windows runtime is available here.

Engineering completion, scientific review, and human approval remain separate. This record does not approve any target definition or authorize inference.

## Repository and environment snapshot

- Branch: `main`; HEAD: `067c6d117bdcf4f9274606499150a859b7c791c6`.
- The pre-existing modified/untracked Stage B–D work was preserved; no Stage B source data or frozen release was changed. All new benchmark outputs were written under `/tmp`; tracked `stageA/outputs/` were not overwritten.
- Current shell default: Python 3.14.7. A cached Python 3.12.14 interpreter was found at the Codex runtime path and used to create isolated environments.
- Validated runtime: macOS 26.6 arm64; Python 3.12.14; pip 25.0.1; NumPy 2.5.3; pandas 3.0.6; scikit-learn 1.9.1; XGBoost 3.4.1; SciPy 1.18.1; joblib 1.6.0; cloudpickle 3.1.2; narwhals 2.28.0; python-dateutil 4.0.0; threadpoolctl 3.7.0; tzdata 2026.6; Homebrew `libomp` 23.1.5.
- The direct Stage A requirements were already pinned. A full Python package lock was added at `stageA/stageA-requirements-py312.lock`. It installed successfully into a second clean Python 3.12.14 venv; `pip check` reported no broken requirements. macOS XGBoost required the separate OpenMP runtime.
- Root `requirements.txt` is for the wider repository and has unpinned NumPy/pandas; `stageB/requirements-stageB.txt` is a separate Stage B environment. Neither was used for the Stage A run.

Final `git status --short` snapshot (other than Stage A paths, these changes were present before this cycle and were preserved):

```text
 M stageA/scripts/run_stage_a.py
 M stageA/scripts/write_stage_a_docs.py
 M stageA/stageA_reproducibility.md
 M stageC/app/README.md
 M stageC/app/server.py
 M stageC/app/static/app.js
 M stageC/app/static/style.css
 M stageC/src/stage_c/release_adapters.py
 M stageC/tests/test_app_api.py
 M stageD/data/evidence_review_queue.json
 M stageD/data/mechanism_evidence_registry.json
 M stageD/data/phase5/evidence_review_assignment_unassigned.json
 M stageD/data/phase5/evidence_review_coverage_dashboard.json
 M stageD/reports/mechanism_reviewer_packets.md
 M stageD/reports/phase45_mechanism_registry_report.md
 M stageD/reports/phase5/evidence_review_queue_report.md
 M stageD/src/stage_d/evidence_queue.py
?? stageA/STAGE_A_CLOSURE_AND_TRANSITION_2026-11-04.md
?? stageA/STAGE_A_REPRODUCTION_AUDIT_2026-11-04.md
?? stageA/STAGE_A_RF01_RF15_EVIDENCE_MATRIX_2026-11-04.md
?? stageA/STAGE_A_RF01_RF15_HUMAN_DECISION_HANDOFF_2026-11-04.md
?? stageA/reports/
?? stageA/stageA-requirements-py312.lock
?? stageA/tests/
?? stageB/reports/V20_PENDING_IDENTITY_REVIEW_AUDIT.md
?? stageC/reports/DEPENDENCY_AND_TEST_STABILIZATION_2026-11-04.md
?? stageC/reports/NEXT_CYCLE_EXECUTION_STATUS_2026-11-04.md
?? stageC/reports/NEXT_DEVELOPER_CONTINUATION_REPORT.md
?? stageC/reports/NEXT_EXECUTION_DISPOSITION_REPORT_2026-11-04.md
?? stageC/reports/PARTNER_WINDOWS_VERIFICATION_PACKAGE_2026-11-04.md
?? stageC/reports/next_cycle_baseline_snapshot.json
?? stageC/reports/next_cycle_baseline_snapshot_2026-11-04.json
?? stageC/reports/next_cycle_baseline_snapshot_2026-11-04_disposition.json
?? stageC/reports/phase2/STAGE_A_RF01_RF15_DECISION_REGISTER.md
?? stageC/reports/phase4/integrity_incident/
?? stageD/reports/STAGEB_V20_SOURCE_PIN_RECONCILIATION_2026-11-04.md
?? stageD/reports/source_integrity_incident/
```

## Stage A task register

| Task | Status | Evidence / remaining work |
|---|---|---|
| Preserve repository and historical outputs | COMPLETE | Only Stage A runner/docs/tests/lock and this report set changed in this cycle. No frozen release, Stage B source table, or committed Stage A output changed. |
| Verify Stage A dataset snapshot | COMPLETE for current benchmark input | SHA-256 `750124efc8b89dff1f67764064b1049b5db51fb1b2f222d4f91cd94c56945f89`; current hash guard fails closed on any other bytes. The historical OOF rows' IDs, molecular groups and actual targets align with this table. Historical output metadata itself did not record the SHA. |
| Reproduce current Stage A pipeline | COMPLETE in validated macOS arm64 environment | Full five-model/five-fold run completed in a disposable copy. A second clean venv installed from the new lock and produced byte-identical OOF predictions, fold audit, tuning and robustness outputs. Details are in `STAGE_A_REPRODUCTION_AUDIT_2026-11-04.md` and the detailed fold comparison report in `stageA/reports/`. |
| Reconcile reproduction with historical results | OPEN / BLOCKING | Fold assignments and audit match, but historical and regenerated predictions differ; historical transitive package versions and run provenance are missing. Do not replace old outputs until explained and explicitly versioned. |
| Input, feature and failure checks | COMPLETE for tested cases | Twelve Stage A tests pass, including snapshot hash, invalid/missing inputs, feature formulas, transform, model configuration, fold separation, OOF schema/actuals, metric calculation, output hashes and two full repeated runs with identical serialized manifests/outputs. |
| Python/macOS environment | COMPLETE for this platform | Exact Python 3.12.14 and all locked Python packages verified. XGBoost required Homebrew `libomp` 23.1.5. Linux `libgomp` and Windows Visual C++ Redistributable prerequisites and commands are documented but not run; no runnable environment is available on this host. |
| RF-01–RF-15 evidence preparation | COMPLETE; all decisions PENDING | `STAGE_A_RF01_RF15_EVIDENCE_MATRIX_2026-11-04.md` links each question to inspected code/data and records unresolved assumptions and consequences; `STAGE_A_RF01_RF15_HUMAN_DECISION_HANDOFF_2026-11-04.md` provides 15 fillable pending decision forms. The tracker remains OPEN, 0/15 approved. No individual owner/reviewer is named in the tracker. |
| Stage A inference package | BLOCKED | Stage A run produces benchmark/OOF reports, not a fitted deployment estimator package. The frozen Stage B model artifact hash matches its manifest, but the Stage B manifest's expected input hash (`cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27`) differs from the current Stage A snapshot. Do not load it for inference. |

## Validation evidence

- Clean lock install: `/tmp/cookrisk-stagea-locktest/bin/python -m pip install -r stageA/stageA-requirements-py312.lock` — PASS.
- Dependency consistency: `/tmp/cookrisk-stagea-locktest/bin/python -m pip check` — PASS, no broken requirements.
- Stage A test command: `/tmp/cookrisk-stagea-locktest/bin/python -m unittest discover -s stageA/tests -v` — **12 tests, 12 passed**.
- Full benchmark: `/tmp/cookrisk-stagea-locktest/bin/python stageA/scripts/run_stage_a.py` executed from a disposable Stage A tree — PASS; stored project outputs unchanged.
- Documentation generation: `write_stage_a_docs.py` executed against a disposable output tree — PASS; regenerated reproducibility instructions contain the lock, platform setup and frozen Stage B transform distinction.
- Recalculation: MAE, RMSE and R² independently recomputed from both historical and regenerated OOF rows; each summary agrees to floating-point precision.
- Fold check: 25/25 fold audit intersections are zero; reconstructed `GroupKFold` validation membership exactly matches saved folds. Audit SHA-256 remains `1584f6025f807f1422080ae6a2d1d5c5865d7cb0a032dd36e84ddc750235bc8a`.

## Closure checklist

- [x] Python 3.12.14 macOS environment established and locked; Linux/Windows prerequisites and commands recorded, execution still pending.
- [x] Current exact training input hash verified and guarded before training.
- [x] Five-fold benchmark rerun without overwriting stored outputs.
- [x] Metrics independently recalculated; fold separation and model/OOF structure tested.
- [x] RF-01–RF-15 evidence matrix prepared; all approvals remain pending.
- [x] Reproduction and test commands documented.
- [ ] Explain and resolve historical-versus-regenerated prediction/metric discrepancy; preserve existing output history until then.
- [ ] Validate locked setup and tests on Linux and Windows.
- [ ] Resolve the separate Stage B snapshot mismatch before any inference integration.
- [ ] Human scientific owner and independent reviewer must be designated; keep RF decisions pending until source-backed responses arrive.

**Transition confirmation:** Stage A engineering closure criteria are not yet satisfied. No Stage B or later-stage work was started in this cycle.
