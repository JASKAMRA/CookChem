# Run CookRisk locally on Windows

CookRisk is a local, non-production research prototype. The server uses the Python standard library and the existing Stage C and Stage D modules; it does not need third-party packages, external services, or configuration files to run.

## Requirements

- Windows 10 or 11 with PowerShell.
- Git for Windows.
- Python 3.10 or newer. The code uses only Python's standard library at runtime.
- A writable clone directory. Reviewer actions, when explicitly submitted, are saved under `stageD/data/` in that clone.

## Clone the repository

Replace the example GitHub URL with the repository URL provided by its owner:

```powershell
git clone "https://github.com/<OWNER>/<REPOSITORY>.git" CookChem
cd CookChem
```

To update an existing clone after the owner has pushed changes:

```powershell
cd CookChem
git pull
```

## Check Python and dependencies

```powershell
py -3 --version
```

Use Python 3.10 or newer. If the Windows Python launcher is unavailable, use `python` instead of `py -3` in the commands below.

The application itself requires no `pip install` step. Its runtime imports are all from Python's standard library, and the repository-relative modules and data are loaded from the cloned project. The pinned packages in `stageC/requirements-dev.txt` are only for schema/development tests, not for running the app.

No application configuration is required. Paths are derived from the server file's location, so the clone can be placed in any writable directory. Keep these repository files and folders in the clone because the server verifies and reads them at runtime:

- `stageC/app/` — server and browser assets (`static/index.html`, `static/app.js`, `static/style.css`).
- `stageC/src/` and `stageD/src/` — application modules.
- `stageC/releases/Phase1B-v1.3.2/` — complete pinned package; the app verifies its complete manifest.
- `stageC/releases/Phase2-v0.3.1/` and `stageC/phase4/releases/Phase4-v0.1.2/` — pinned cooking and evidence-context packages.
- `stageB/release/StageB_V20_20261103/data/interaction_evidence.csv` — read-only Stage B evidence input.
- `stageD/data/mechanism_evidence_registry.json` — source-linked mechanism candidates.

The repository `.gitignore` does not exclude these data or release paths. Do not copy the app directory by itself; use the complete repository checkout so the pinned sources and schemas remain available.

## Start CookRisk

Run this from the `CookChem` repository root in PowerShell:

```powershell
py -3 stageC/app/server.py --host 127.0.0.1 --port 8765
```

Keep this PowerShell window open while using the app. The server prints its local address and a non-production notice. On first page load, the app verifies the 1,324 files in the pinned Phase1B package and loads its local records. That initial check took about a minute in the current Windows environment; time depends on disk speed. Later requests use the already loaded data.

If port 8765 is already in use, choose another local port, for example:

```powershell
py -3 stageC/app/server.py --host 127.0.0.1 --port 8766
```

Then use the matching URL below with `8766` instead.

## Open it in a browser

Open:

```text
http://127.0.0.1:8765/
```

To stop CookRisk, return to the server's PowerShell window and press `Ctrl+C`.

## Optional application API test

The focused in-process API test uses Python's standard library and does not require the development packages:

```powershell
py -3 -m unittest stageC.tests.test_app_api -v
```

## Local data and limits

The app reads the pinned local releases and Stage B evidence source. It does not run Stage A, write to Stage B source records, create a release, or provide clinical interpretation. Reviewer actions are saved separately in the Stage D JSONL audit log with local backup snapshots. The prototype binds only to the local machine and does not send data to an external service. It has no authentication, multi-user controls, or production deployment safeguards.
