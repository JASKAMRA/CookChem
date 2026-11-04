# C1B-02 — Partner Windows/Browser Verification Procedure

**Purpose:** Verify only the owner-designated candidate archive and the separately provisioned runtime inputs. This is a procedure and return template; no partner execution is claimed.

## Inputs required from the authorized owner

Before starting, obtain:

1. `CookRisk-reviewed.zip` and its owner-recorded exact-byte SHA-256.
2. `C1B_02_CANDIDATE_HANDOFF_MANIFEST.json` and its expected SHA-256 (`c2e809c8bbda167c0fd20c7b99d86fb9c22331427d7ccb5c16771c33937b805b`).
3. The owner-approved instructions and exact-byte digests for separately provisioned runtime dependencies: the complete Phase1B-v1.3.2 package, Phase2-v0.3.1, Phase4-v0.1.2, the protected Stage B interaction-evidence runtime input, `stageD/src/`, and `stageD/data/mechanism_evidence_registry.json`. These are not in the candidate archive. Protected inputs must come directly from their authorized owner; do not obtain them from this candidate. The app guide requires these repository-relative inputs at runtime. The original Phase1B verifier expects all 1,324 manifest-listed artifacts; do not call it passing on a partial package.
4. A writable test directory and Windows 10/11 with PowerShell.

If an input or its owner-supplied digest is missing, stop and report BLOCKED. The earlier handoff reference `067c6d117bdcf4f9274606499150a859b7c791c6` excludes local continuation changes and is not a substitute for the current owner-designated revision/archive. Do not substitute another revision or dependency.

## 1. Verify archive and manifest bytes before extraction

In PowerShell, from the directory containing the files:

```powershell
Get-FileHash .\CookRisk-reviewed.zip -Algorithm SHA256
Get-FileHash .\C1B_02_CANDIDATE_HANDOFF_MANIFEST.json -Algorithm SHA256
```

Compare each full digest to the owner-provided value. For the manifest, the expected digest is `c2e809c8bbda167c0fd20c7b99d86fb9c22331427d7ccb5c16771c33937b805b`. Any mismatch stops the run. Do not normalize line endings, edit the files, or re-zip before hashing.

## 2. Extract and verify candidate file inventory

After both hashes match, extract the ZIP into an empty directory while preserving its relative paths. Place the owner-supplied manifest at the repository root (or use the owner-designated manifest path). From that root:

```powershell
$manifest = Get-Content -Raw .\C1B_02_CANDIDATE_HANDOFF_MANIFEST.json | ConvertFrom-Json
$problems = @()
foreach ($entry in $manifest.files) {
    $path = $entry.path
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        $problems += "MISSING $path"
        continue
    }
    $file = Get-Item -LiteralPath $path
    $actual = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($file.Length -ne [long]$entry.size_bytes) { $problems += "SIZE_MISMATCH $path" }
    if ($actual -ne $entry.sha256_exact_bytes) { $problems += "SHA256_MISMATCH $path" }
}
if ($problems.Count -gt 0) { $problems; throw 'Candidate manifest verification failed' }
'Candidate manifest verification: PASS'
```

Record the printed result and any errors. Separately provisioned dependency digests must be checked against the owner's exact-byte records using `Get-FileHash -Algorithm SHA256`. Do not state the Phase1B full-package verifier passed unless the complete owner-provisioned package is present and its verifier returns PASS with the documented artifact count.

## 3. Record runtime version and start app

```powershell
py -3 --version
py -3 stageC/app/server.py --host 127.0.0.1 --port 8765
```

The documented runtime floor is Python 3.10+. Record the exact version. Runtime dependencies are standard-library Python plus the separately provisioned repository-relative inputs listed above; do not install unapproved packages. Leave the server running for API and browser checks. Save the complete console output. If startup fails because any dependency is missing or fails integrity checks, record the error and stop; do not repair or regenerate a frozen release.

## 4. Check health API

In a second PowerShell window:

```powershell
$response = Invoke-WebRequest -Uri 'http://127.0.0.1:8765/api/health'
$response.StatusCode
$response.Content
```

Record the exact status and body. The documented expected health is HTTP 200 with a degraded Phase 4 context status (`DEGRADED_PHASE4_CONTEXT_UNAVAILABLE`). Confirm Phase 4 contextual records are withheld. A different status/body is a result to report, not something to edit around.

## 5. Check browser behavior

Open `http://127.0.0.1:8765/` in the partner's browser. Record browser name/version and whether:

- The local CookRisk interface loads and remains on loopback.
- The visible Phase 4 integrity/degraded notice appears.
- Phase 4 contextual records are withheld.
- Review submission is clearly disabled because trusted reviewer authentication is unavailable.
- The browser console shows errors (copy exact messages; do not redact by paraphrasing).

Stop the server with `Ctrl+C`. Do not submit review actions or write review data.

## 6. Partner return template

```text
C1B-02 partner result

Owner approver / approval record:
Owner-designated revision or archive filename:
Owner-designated archive SHA-256:
Candidate manifest SHA-256:
Archive Get-FileHash output:
Manifest Get-FileHash output:
Candidate manifest file check: PASS / FAIL
Runtime dependency identifiers and owner-provided digests:
Windows edition and build:
PowerShell version:
Python version (`py -3 --version` exact output):
Browser name and version:
Phase1B full-package verifier command/output/artifact count (or NOT RUN and why):
App startup command and full console output:
Health API command:
Health API HTTP status:
Health API response body:
Browser page loaded: YES / NO
Phase 4 degraded notice visible: YES / NO
Phase 4 contextual records withheld: YES / NO
Review submission visibly disabled: YES / NO
Browser console errors (exact):
Other failures/tracebacks (exact):
Partner name/date:
```

## Status rule

Return the complete result to the owner for review. This procedure does not itself pass C1B-02. Exact-byte integrity evidence, an owner-designated current handoff, and genuine partner Windows/browser results are required. Windows portability is not verified until the partner's evidence is received and reviewed.
