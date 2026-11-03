# GitHub partner local setup — verification report

**Scope:** Make the existing CookRisk prototype runnable from a partner's Windows clone. No features, calculations, datasets, schemas, Stage A, Stage B source records, or releases were changed.

## Files changed

- `README.md` — points partners to the Stage C local-app guide and clarifies that the existing prototype is non-production.
- `stageC/app/README.md` — Windows clone, Python, dependency, startup, browser, data-file, and local-runtime instructions.
- `stageC/reports/GITHUB_PARTNER_LOCAL_SETUP_REPORT.md` — this report.

The app already derives its project paths from `server.py`'s location, serves frontend assets from `stageC/app/static/`, and imports Stage C/Stage D code from repository-relative folders. The runtime imports only Python standard-library modules. No personal username or machine-specific absolute path was found in the app or setup README. No configuration file is required.

## Exact Windows commands

Replace the example URL with the repository URL the owner provides:

```powershell
git clone "https://github.com/<OWNER>/<REPOSITORY>.git" CookChem
cd CookChem
py -3 --version
py -3 stageC/app/server.py --host 127.0.0.1 --port 8765
```

The Python version must be 3.10 or newer. No `pip install` is needed to run CookRisk. Keep the server window open, then open this URL in a browser:

```text
http://127.0.0.1:8765/
```

To stop the server, press `Ctrl+C` in its PowerShell window. If port 8765 is occupied, start with `--port 8766` and open `http://127.0.0.1:8766/`.

For an existing checkout, run `cd CookChem` followed by `git pull` before starting. The pinned `stageC/releases/Phase1B-v1.3.2/` package must be present in full because startup verifies its complete manifest. Other required local inputs are listed in [`stageC/app/README.md`](../app/README.md). The repository `.gitignore` does not exclude the required app or release/data paths. Ensure these files are included in the manual GitHub push; Git tracking and remote contents were not inspected because Git operations were explicitly excluded.

## Verification results

- Current interpreter: Python **3.14.7**; `server.py --help` passed.
- The exact loopback launch command started a persistent server process; it was stopped with `Ctrl+C` after the smoke check.
- `CookRiskService().load().health()` successfully loaded and verified the pinned local inputs: 584 food records, 143 compounds, 317 Stage B evidence rows, 25 mechanism candidates, and 0 accepted cooked estimates.
- In-process app API suite: **8 passed, 0 failed, 0 skipped**.
- `node --check stageC/app/static/app.js`: passed.
- Required server, frontend, source modules, package manifests, Stage B CSV and Stage D mechanism registry were all present in this workspace.
- The Phase1B package contains 1,324 manifest-listed files; all are present. Its largest individual artifact is below GitHub's 100 MB single-file limit.
- No machine-specific path was found in the application or setup README.

## Verification limits and remaining blockers

This managed environment forbids local socket access. The HTTP request to `http://127.0.0.1:8765/api/health` was therefore blocked by the environment's socket permission, so I could not verify the page in a real browser here. The server process stayed running, and its real data-loading/health path completed successfully in-process. The app API tests exercise handlers without opening sockets.

No second physical laptop or partner GitHub clone was available. Python 3.10–3.13 were not installed here; compatibility was checked against the code's Python 3.10 syntax floor but only executed on Python 3.14.7. A partner should confirm the GitHub clone contains the listed pinned packages and Stage B/Stage D inputs, then follow the commands above. Initial page data loading verifies all 1,324 Phase1B artifacts and took about a minute in this environment; disk speed may change that time.

No remaining code or dependency blocker was identified. The remaining verification is the first partner's physical Windows clone and browser open after the owner manually pushes all required files.
