# Dependency and test stabilization — 2026-11-04

## Environment observed

- Host Python: **3.14.7**; pip: **26.2.1**.
- The Stage A/B model manifest records Python **3.12.14**, NumPy **2.5.3**, pandas **3.0.6**, scikit-learn **1.9.1**, and XGBoost **3.4.1**.
- `jsonschema`, `attrs`, `jsonschema-specifications`, `referencing`, and `rpds-py` are not installed in the active host interpreter.
- The repository's `stageC/requirements-dev.txt` pins those five schema-validation dependencies. The frozen Phase 3 package carries the same pin set. Phase 4's current development requirement instead specifies `jsonschema>=4.18,<5`; Stage D has no dedicated requirements file. Root `requirements.txt` and `stageB/requirements-stageB.txt` contain unpinned scientific packages except XGBoost in Stage B.
- No complete environment lock or hash-locked install artifact is present. The frozen model's training-time joblib version is also not recorded.
- `python3.12`, `uv`, `pyenv`, and a repository virtual environment were not found on the available PATH/checked project locations.
- The existing pip HTTP cache contains 162 cache files (including metadata), with 27 cached wheel archives identified. None is `jsonschema`, `attrs`, `jsonschema-specifications`, `referencing`, or `rpds-py`; the cache directory is treated as disabled by pip because it is not writable to this process. No cache artifact was installed.
- Independently parsed all repository `*.schema.json` files under Stage B/C/D: **50/50 are valid JSON syntax**. This does not substitute for Draft 2020-12 semantic schema validation, which remains blocked by missing `jsonschema`.

## Pinned dependency constraints checked against package metadata

The public PyPI release metadata and the upstream `jsonschema` validation documentation were inspected read-only. This confirms the declared core pins are version-compatible with the recorded Python 3.12.14 runtime, but does **not** create a locked install:

- `jsonschema==4.26.0` requires Python `>=3.10`; core dependencies are `attrs>=22.2.0`, `jsonschema-specifications>=2023.03.6`, `referencing>=0.28.4`, and `rpds-py>=0.25.0`. The project pins satisfy those minimums.
- `jsonschema-specifications==2025.9.1` requires `referencing>=0.31.0`; the project pins `0.37.0`.
- `referencing==0.37.0` requires `attrs>=22.2.0`, `rpds-py>=0.7.0`, and conditionally `typing-extensions>=4.4.0` for Python `<3.13`. Therefore, Python 3.12 installs an extra conditional dependency not explicitly pinned by `stageC/requirements-dev.txt`; that file is not a complete lock.
- `rpds-py==2026.9.1` requires Python `>=3.11`, so its declared Python floor includes 3.12.14.
- PyPI lists a CPython 3.12 Windows x86-64 wheel for `rpds-py==2026.9.1` (SHA-256 `5ce8943f79c2210f7abcc28e86367b03b28d95027fd01c46d2472373ae70c86f`). This suggests no Rust build is needed on that platform if the approved source provides that exact wheel; it was not downloaded or installed.
- The project schemas use `date`, `date-time`, and `uri` formats. `jsonschema` documents that format checks requiring optional libraries may silently accept values if the package extra/dependency is absent. `stageC/requirements-dev.txt` does not select `jsonschema[format]` or `jsonschema[format-nongpl]`; an owner-approved, license-reviewed format dependency set and exact pins are required before claiming complete URI/date-time format validation.

Primary metadata/docs: [jsonschema 4.26.0 PyPI JSON](https://pypi.org/pypi/jsonschema/4.26.0/json), [jsonschema-specifications 2025.9.1 PyPI JSON](https://pypi.org/pypi/jsonschema-specifications/2025.9.1/json), [referencing 0.37.0 PyPI JSON](https://pypi.org/pypi/referencing/0.37.0/json), [rpds-py 2026.9.1 PyPI release](https://pypi.org/project/rpds-py/2026.9.1/), and [upstream format-validation documentation](https://python-jsonschema.readthedocs.io/en/stable/validate/).

## Install attempt and result

Attempted an isolated install to `/private/tmp/cookrisk-nextcycle-deps` using the repository's declared exact Stage C pins. Installation could not reach `pypi.org` because DNS/network access is unavailable (`NameResolutionError`); it ended with “No matching distribution found” for `attrs==26.1.0`. No dependency files or installed global packages were changed.

This is an environment-access blocker, not evidence that the declared core pins are incompatible. PyPI metadata indicates the core versions include Python 3.12, but a real install remains unverified and the missing conditional/format pins prevent a complete reproducible lock. Do not loosen pins or select versions to make this host pass.

## Current suite results

| Suite | Result | Interpretation |
|---|---:|---|
| Stage C | 248 tests; 5 skipped; 2 errors | One integration setup fails closed on the Phase 4 manifest digest mismatch; one schema test cannot import missing `jsonschema`. |
| Stage D | 63 tests; 0 failures; 6 skipped | Schema checks are skipped because `jsonschema` is unavailable. |
| Phase 3-v0.1.2 package | 57 tests; 2 import errors | Two tests import missing `jsonschema`. |
| Phase 4 registry | 13 tests; 1 failure | Integrity assertion correctly detects a Phase 4 release artifact/manifest mismatch. |

The focused Stage C app API suite passed after the Phase 4 fail-closed behavior and Stage B source-pin reconciliation. Suite counts overlap and must not be added. These are software tests only, not scientific validation.

Fresh rerun in this execution cycle added an actual pinned-input HTTP-handler regression test for `/api/health` and `/api/catalog`. The focused API command `python3 -m unittest discover -s stageC/tests -p 'test_app_api.py' -v` ran **10 tests, all passed**. The real Phase 4 integrity failure returns health HTTP 200 with `DEGRADED_PHASE4_CONTEXT_UNAVAILABLE`, reports zero loaded Phase 4 records, and leaves the verified catalog route available with 584 foods. This test exercises the repository's current pinned inputs; it does not relax the release integrity gate.

Latest full rerun: `python3 -m unittest discover -s stageC/tests -v` — **249 tests, 2 errors, 5 skipped**. The errors remain the expected Phase 4 frozen-manifest digest rejection in recipe-release integration and missing `jsonschema` import in `test_recipe_schema`. Latest Stage D rerun: `python3 -m unittest discover -s stageD/tests -v` — **63 tests, 0 failures, 6 skipped**; skips still require `jsonschema`. The complete Stage C log is `/private/tmp/cookrisk_continuation_stagec.log`; the Stage D log is `/private/tmp/cookrisk_continuation_staged.log`. These are temporary diagnostics, not release artifacts.

An isolated synthetic trusted-package smoke check built a temporary empty Phase 4 fixture with a matching manifest and sidecar, then called the unchanged release adapter: it was accepted as `IN_PROGRESS`, `manifest_verified=true`, with zero selected records. This verifies the adapter's success path on synthetic structure only; it does not validate or recover actual Phase 4 evidence.

## Stabilization decision

Do not edit assertions to hide integrity failures. Keep Phase 4 inputs withheld. Once an approved PyPI mirror or trusted wheelhouse is available, the maintainer must resolve and pin the Python-3.12 conditional dependency and any required format-validation extras, review licenses and wheel hashes, and produce the complete owner-approved lock (runtime + dev/test). Then provision Python **3.12.14**, run all suites and schema/integration checks, and record the lock hash and command outputs. Until then the supported environment is not reproducibly installed in this workspace.
