# Phase 2 Reproducibility

## Standard-library audit

The source-pair and Phase 2 release audit scripts use Python's standard library. From the repository root:

```sh
python3 stageC/scripts/audit_phase2_source_pairs.py
python3 stageC/scripts/build_phase2_release.py
python3 -m unittest stageC.tests.test_phase2_source_audit -v
python3 -m unittest discover -s stageC/tests -p 'test_phase2*.py' -v
python3 -m unittest discover -s stageC/tests -v
```

The source-pair audit input is `stageC/phase2/data/observed_cooking_pairs.csv`; it writes `stageC/reports/phase2/source_pair_audit_2026-11-03.csv`. The immutable v0.1.0 builder refuses to overwrite a release and checks regenerated outputs against its manifest.

## Clean-copy check actually run

The existing clean copy at `/private/tmp/cookrisk-phase2-clean` contains the required Phase 2 input files, Phase1B-v1.3.0 food/mapping tables, Stage A input, Stage B evidence/model/manifest, and v0.1.0 release. The following commands were run there:

```sh
python3 stageC/scripts/build_phase2_release.py
python3 stageC/scripts/audit_phase2_source_pairs.py
```

The v0.1.0 builder reported `Verified reproducible outputs against existing immutable release Phase2-v0.1.0`. The new source audit generated the same SHA-256 `3ba84c25a40ebf255d4425943d3e81ce32498525c86994caaddb4a4da0931082` in the clean copy and the repository. This is an isolated artifact/input copy, not a full Git clone: it does not include all Stage C tests, all documentation, or historical releases. Therefore it demonstrates deterministic Phase 2 build outputs and source-audit reproducibility, not a full clean checkout test of every repository command.

The Phase2-v0.2.0 successor packages its report bundle, source-pair input, audit code, schemas, and v0.1.0 base reference. Its `--verify` command assembles a temporary expected release from the frozen v0.1.0 files and the v0.2.0 package's own reports/scripts/schemas, then compares the complete file inventory and hashes. This verification does not read mutable `stageC/phase2` or `stageC/reports/phase2` files. Run it from a repository copy containing only the two release directories and the builder at `stageC/scripts/build_phase2_v0_2_release.py` to test the packaged release inputs independently.

## Model environment (inference remains blocked)

The Stage B selected-model manifest records Python 3.12.14 and pandas 3.0.6. Stage A's reproducibility record pins NumPy 2.5.3, pandas 3.0.6, scikit-learn 1.9.1, and XGBoost 3.4.1; the artifact's embedded scikit-learn metadata is also 1.9.1. Stage B's separate 3.14.7 runtime report records NumPy 2.5.4, pandas 3.1.0, scikit-learn 1.9.1, and joblib 1.6.0, but these do not establish the original training-time joblib or transitive dependency lock. The current runtime has Python 3.14.7 and lacks joblib, NumPy, pandas, and scikit-learn.

Do not create an environment lock with an unsupported joblib version. Once the exact training snapshot is recovered, reproduce with Python 3.12.14 and the pinned Stage A versions above, plus the original joblib/transitive lock if it can be recovered. Verify the training data hash and model artifact hash before loading; apply the manifest's 22 base and 11 derived features in the original preprocessing order; log feature, model, data, environment, code, and output hashes. No model load/inference was performed.

## Hashes and immutable artifacts

Phase2-v0.1.0 still verifies all 19 manifest file hashes. Phase1B-v1.3.0 verifies all 1,321 artifact SHA-256 entries and listed byte counts. No Stage A, Stage B, Phase1B, or v0.1.0 file was changed by this audit.
