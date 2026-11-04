# CookRisk partner Windows verification package — 2026-11-04

**Purpose:** reproducible handoff checklist for a partner's Windows clone. No Windows partner run has been performed; status is **PENDING**.

## Revision and supported-runtime boundary

- Repository branch at local audit: `main`; committed HEAD `067c6d117bdcf4f9274606499150a859b7c791c6`.
- Local continuation changes are uncommitted and are not present at that commit or confirmed on GitHub. The owner must push or provide a reviewed archive before the partner verifies those changes.
- Prototype app code has a declared Python **3.10+** syntax/runtime floor and uses the standard library at runtime. Only Python 3.14.7 on macOS was exercised in this workspace. Windows compatibility is not verified.
- Python **3.12.14** is the recommended candidate for the future complete test environment because the Stage A/B reproducibility record names that version. A complete environment lock is still missing; this is a recommendation, not a qualified support claim.

## Clone and verify files

Run in PowerShell, substituting the URL and reviewed revision supplied by the owner:

```powershell
git clone "<OWNER-PROVIDED-URL>" CookChem
Set-Location CookChem
git rev-parse HEAD
git status --short
py -3 --version
```

Do not continue if the checked-out revision differs from the revision the owner asked you to verify. Keep the full repository tree; do not copy only `stageC/app`.

Verify the Phase1B package:

```powershell
py -3 stageC/releases/Phase1B-v1.3.2/verify_release.py
```

Expected: `status: PASS`, release `Phase1B-v1.3.2`, 1,324 artifacts. Phase2 and Phase3 package tests below independently exercise their package manifests. Phase4-v0.1.2 is expected to fail integrity checks and must remain blocked; do not alter its manifest or sidecar.

## Runtime-only app smoke check

No third-party install is required just to start the local app:

```powershell
py -3 stageC/app/server.py --host 127.0.0.1 --port 8765
```

Keep the process open and visit `http://127.0.0.1:8765/` in a browser on the same PC. Expected: local research prototype loads with a visible Phase 4 integrity warning; Phase4-v0.1.2 contextual records are withheld. A working page does not mean Phase 4 is verified or the app is production-ready. Stop with `Ctrl+C`.

## Development/test dependencies

Formal schema checks need an approved Python environment and a complete lock. The current pins satisfy the core `jsonschema` constraints, but Python 3.12 needs an unpinned conditional `typing-extensions` dependency; URI/date-time format checking also needs optional validator packages. No complete hash lock or approved mirror is currently available. Do not treat a plain requirements install as reproducible. When the project maintainer supplies an approved lock and package source, install only that lock in a virtual environment, for example:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --disable-pip-version-check --require-hashes -r <OWNER-APPROVED-LOCKFILE>
.\.venv\Scripts\python.exe -m pip freeze
```

Do not install alternate versions if resolution fails. Save the environment output and error for the project maintainer. The standalone Phase4 release requirement uses a wider range; the shared Stage C pins specify `jsonschema==4.26.0` and several transitive pins. The project still needs a complete owner-approved lock with runtime, format-checking dependencies, transitive pins and artifact hashes before claiming reproducible installation.

## Verification commands

From the repository root:

```powershell
py -3 -m unittest discover -s stageC/tests -v
py -3 -m unittest discover -s stageC/tests -p test_app_api.py -v
py -3 -m unittest discover -s stageC/releases/Phase3-v0.1.2/stageC/tests -v
py -3 -m unittest discover -s stageC/phase4/tests -v
py -3 -m unittest discover -s stageD/tests -v
```

For the Stage C PowerShell fixture checks, use PowerShell 7 (`pwsh`) because `Test-Json` is required:

```powershell
pwsh -NoProfile -File stageC/scripts/validate_json_schemas.ps1
```

Expected current caveats: the app API focused suite should pass; Stage C recipe-release integration should refuse the invalid Phase 4 digest; Phase 3 and schema-aware tests require the approved `jsonschema` environment; the Phase4 package integrity test should continue to expose release mismatches. These are current local findings, not a guarantee for a different revision or Windows runtime. Report exact command output, Python/pip versions, installed package versions and checked-out commit.

## Required partner result

Return the commit ID, Windows edition/build, Python version, browser/version, package install log, exact test counts and tracebacks, release verification output, and whether the local page showed the expected degraded Phase 4 notice. Do not mark partner verification complete until these results are reviewed. This prototype has no authentication, multi-user controls, production deployment safeguards, or clinical interpretation workflow.
