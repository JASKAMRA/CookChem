# C1-01 — Schema Validation Environment Report

**Official phase:** Stage C → Phase 1: Software Foundation  
**Task:** C1-01 — Approved, reproducible schema-validation environment  
**Status:** **COMPLETE for the approved Python 3.14.7 macOS arm64 target**  
**Date:** 2026-11-04

## Approval and scope

The project owner explicitly approved **PyPI** as the package source and approved the dependency licenses in the conversation on 2026-11-04. Packages were obtained only from `https://pypi.org/simple`; no other package source was used. The approved scope is the C1-01 schema-validation environment and its synthetic software tests.

## Reproducible environment

- Runtime: **CPython 3.14.7**.
- Platform: **macOS 26.6, arm64** (`macosx_26_0_arm64`).
- Environment used: isolated virtual environment at `/private/tmp/cookrisk-c1-01-py314-env`.
- Complete direct and transitive dependency lock: [`requirements-c1-01-py314-macos-arm64.lock`](/Users/ayushkamboj3/CookChem/stageC/requirements-c1-01-py314-macos-arm64.lock).
- Lock SHA-256: `a86722c40bbc5ee79014d54ccb8e2c34273a816e1f6736f66815f73a3378a7ee`.
- The lock uses exact versions and SHA-256 artifact hashes, selects `jsonschema[format]`, and records the resolved platform-specific dependency closure. The `referencing` package's `typing-extensions` conditional is for Python `<3.13`, so it does not apply to Python 3.14.7.
- All 17 locked distributions were installed from the approved PyPI source into the isolated environment using hash enforcement. The installation completed successfully; `pip check` reported **No broken requirements found**.

| Distribution | Version |
|---|---:|
| arrow | 1.4.0 |
| attrs | 26.1.0 |
| fqdn | 1.6.0 |
| idna | 3.20 |
| isoduration | 20.11.0 |
| jsonpointer | 3.8 |
| jsonschema | 4.26.0 |
| jsonschema-specifications | 2025.9.1 |
| python-dateutil | 4.0.0 |
| referencing | 0.37.0 |
| rfc3339-validator | 0.1.4 |
| rfc3987 | 1.3.8 |
| rpds-py | 2026.9.1 |
| six | 1.17.0 |
| tzdata | 2026.6 |
| uri-template | 1.3.0 |
| webcolors | 25.10.0 |

The owner approved the dependency licenses as a set. Package artifact hashes are in the lock. Some upstream wheel metadata does not declare a standard SPDX license field (including `arrow` and `isoduration`); their source distributions/wheels include license files. `rfc3987` declares GPL-3.0-or-later. This report records upstream metadata and the owner's approval without asserting a separate legal opinion.

## Reproduction commands

The checked-in lock targets macOS arm64 with CPython 3.14.7. To reproduce from approved PyPI and enforce the lock hashes:

```sh
python3.14 -m venv .venv-c1-01
.venv-c1-01/bin/python -m pip download \
  --index-url https://pypi.org/simple \
  --only-binary=:all: --require-hashes \
  --dest /tmp/c1-01-wheelhouse \
  -r stageC/requirements-c1-01-py314-macos-arm64.lock
.venv-c1-01/bin/python -m pip install \
  --no-index --find-links /tmp/c1-01-wheelhouse --require-hashes \
  -r stageC/requirements-c1-01-py314-macos-arm64.lock
.venv-c1-01/bin/python -m pip check
PYTHONDONTWRITEBYTECODE=1 .venv-c1-01/bin/python -m unittest discover \
  -s stageC/tests -p 'test_c1_01_schema_validation.py' -v
```

The executed environment was first populated from the approved index into `/private/tmp/cookrisk-c1-01-py314-wheelhouse`, then installed offline with `--no-index`, `--find-links`, and `--require-hashes`. The lock includes a platform-specific `rpds-py` wheel hash; another OS or architecture needs its own reviewed lock and is not covered by this result. This report does not claim cross-platform validation or a Python 3.12 run.

## Validation coverage and results

The focused tests in [`test_c1_01_schema_validation.py`](/Users/ayushkamboj3/CookChem/stageC/tests/test_c1_01_schema_validation.py) use synthetic fixtures under `stageC/tests/fixtures/c1_01_schema_validation/`. They verify:

1. Positive Draft 2020-12 validation with internal fragment and registered cross-file `$ref` resolution.
2. Rejection of invalid data through the referenced schema and local constraints.
3. Rejection of an invalid schema by `Draft202012Validator.check_schema`.
4. Fail-closed behavior for an external `$ref` missing from the local registry; no network resolver is configured.
5. Availability and enforcement of `uri` and `date-time` format checking, including invalid-value rejection.

Exact focused test command executed:

```sh
PYTHONDONTWRITEBYTECODE=1 /private/tmp/cookrisk-c1-01-py314-env/bin/python \
  -m unittest discover -s stageC/tests -p 'test_c1_01_schema_validation.py' -v
```

Result: **6 tests run, 6 passed, 0 failed, 0 skipped**. `pip check` passed. An independent runtime check confirmed Python 3.14.7, the installed `jsonschema`/`referencing` versions, and acceptance of valid URI and date-time samples by the format checker. Invalid values were also rejected by the focused tests.

These are synthetic software validation fixtures, not food measurements or scientific evidence.

## Acceptance criteria

| Criterion | Status | Evidence |
|---|---|---|
| Reproducible dependency environment | **VERIFIED for macOS arm64 / CPython 3.14.7** | Exact-version hash lock; isolated installation succeeded. |
| Approved source and license decision | **VERIFIED** | Owner explicitly approved PyPI and licenses; source was `https://pypi.org/simple`. |
| Exact package versions and artifact hashes | **VERIFIED for locked platform** | Lock contains 17 exact distributions with SHA-256 hashes; hash-enforced installation succeeded. |
| Positive and negative Draft 2020-12 fixtures | **PASS** | Focused tests. |
| Internal and cross-file `$ref` resolution | **PASS** | Positive test with local registry. |
| Unregistered external reference fails closed | **PASS** | Focused test; no network retriever. |
| URI/date-time format checking | **PASS** | Format dependencies present; valid and invalid cases tested. |
| Required focused command, zero skips | **PASS** | 6 passed, 0 failed, 0 skipped. |

## Files changed for C1-01

- `stageC/requirements-c1-01-py314-macos-arm64.lock` — exact platform lock with artifact hashes.
- `stageC/reports/C1_01_SCHEMA_VALIDATION_ENVIRONMENT_REPORT.md` — this report, updated from the earlier blocked state with approved provenance and test evidence.
- The existing C1-01 focused test and its seven synthetic fixtures were retained unchanged.

## Boundaries and limitations

C1-01 is complete for the explicitly locked macOS arm64 / CPython 3.14.7 target. Other platforms and Python versions are not validated by this lock. This task establishes the formal schema-validation dependency environment and tests; it does not claim that every application runtime path has been integrated with a shared validator.

No Stage A model, data, or artifact was run or modified. Stage B was not inspected, tested, audited, regenerated, or modified. No Stage C Phase 1B–7 deliverable, scientific data, accepted 117-observation boundary, release, manifest, or historical output was modified or tested. Stage D was unchanged. No Git operation or remote access was performed. Work stopped after C1-01.
