# CookRisk next-execution disposition report — 2026-11-04

**Overall status: NOT COMPLETE.** This report records the current continuation decision and does not authorize release publication, model inference, or scientific acceptance.

## 1. Repository baseline and protection

- Branch: `main`; HEAD: `067c6d117bdcf4f9274606499150a859b7c791c6`.
- Python executable: `/opt/homebrew/opt/python@3.14/bin/python3.14`; Python `3.14.7`; pip `26.2.1`.
- Pre-change state recorded in [`next_cycle_baseline_snapshot_2026-11-04_disposition.json`](next_cycle_baseline_snapshot_2026-11-04_disposition.json): 22 changed/untracked files preserved, seven release hash-file sets recorded, no Stage A/B source data changed. The existing Stage B audit report is a report-only addition.
- Existing uncommitted work was preserved. No reset, clean, stage, commit, push, branch change, protected-source change, or frozen-release edit occurred.

## 2. Phase 4 formal disposition

**Disposition: UNRECOVERABLE from repository and documented/accessibly reachable sources searched.** Phase4-v0.1.2 remains immutable and integrity-blocked. Its 18 listed artifacts consist of 9 current-source reproductions, 8 unresolved manifest matches, and 1 untraced `release_info.json`; the detached manifest sidecar is also invalid. No trusted historical release metadata was recovered.

The new search examined local refs/checkpoint trees, the configured remote, CI configuration and tool availability, repository release archives, likely user download/backup folders, and documented external-storage references. The local Codex checkpoint tree contains the same observed package and same invalid manifest/sidecar state; it is not an independent source. GitHub's remote could not be resolved (`Could not resolve host: github.com`), `gh` is unavailable, and no local CI workflow or artifact pointer exists. Repository documents identify local Stage D review-action snapshots only, not a Phase 4 backup. No Phase 4 archive candidate appeared in the previously searched repository archives or newly searched Downloads/Documents/Desktop paths.

This disposition is bounded to the sources accessible or documented in this workspace. An undocumented owner-held external archive cannot be ruled out. If one is supplied later, reopen and independently verify it before use.

The exact files and checks are in [`PHASE4_V0_1_2_INTEGRITY_INCIDENT_REPORT.md`](phase4/integrity_incident/PHASE4_V0_1_2_INTEGRITY_INCIDENT_REPORT.md) and [`phase4_v0_1_2_file_classification.json`](phase4/integrity_incident/phase4_v0_1_2_file_classification.json). The app's actual-release path stays fail-closed. A temporary synthetic manifest-valid empty package passed the adapter success path; this is a software fixture, not recovery or data validation.

### Successor plan — prepared, not built or published

If the owner approves, create `Phase4-v0.1.3` as a new package explicitly identifying v0.1.2 as unrecoverable/unverified. Record the actual source commit/tree and hashes, version-specific `release_info.json`, upstream Phase1B-v1.3.2 and Phase2-v0.3.1 references, and limitations. Independently review each primary-source extraction, identity and applicability; preserve pending/zero-accepted states until qualified human decisions exist. Build into a new directory, run formal schema and registry tests, verify every hash and sidecar independently, clean-copy validate, then update the app pin and test both verified-load and blocked paths. Publication remains an owner decision. No new release was created.

## 3. Dependency environment and schema-validation status

- No Python 3.12 installation, `uv`, `pyenv`, Conda/Mamba, repository virtual environment, approved pip mirror, lockfile, container recipe, or CI workflow was found. Docker CLI exists but its daemon/socket is unavailable. GitHub Actions artifacts could not be queried because the remote is unreachable and GitHub CLI is absent.
- `PIP_INDEX_URL`, `PIP_EXTRA_INDEX_URL`, `UV_INDEX_URL`, and standard pip mirror configuration are absent. The local pip cache yielded 27 wheel archives; none is the pinned schema-validation set. PyPI installation of the declared pins failed on DNS. No package was installed.
- `stageC/requirements-dev.txt` specifies `attrs==26.1.0`, `jsonschema==4.26.0`, `jsonschema-specifications==2025.9.1`, `referencing==0.37.0`, and `rpds-py==2026.9.1`. Phase 3 carries this pin set; Phase 4's current dev file has a broader `jsonschema>=4.18,<5` range. Root and Stage B ML requirements are not complete locks; Stage A's training-time `joblib` version is missing.
- Official package metadata confirms the pinned core versions satisfy their base version constraints on Python 3.12.14. However, `referencing==0.37.0` needs unpinned `typing-extensions>=4.4.0` on Python `<3.13`; schemas also use `date-time` and `uri`, whose format checks require optional validator packages. The current requirements file is therefore not a complete reproducible lock. An owner-approved, license-reviewed and hash-locked dependency set is still required.
- A hash lock must not be fabricated. Recommended future setup is an owner-approved Python 3.12.14 environment plus an approved wheelhouse/index and a complete lock (runtime + dev/test, transitive pins and artifact hashes). Until supplied, exact installation is blocked.
- **Formal Draft 2020-12 validation: BLOCKED.** All 50 schema files parse as valid JSON, but no formal schema validation or `$ref`/format/positive-negative fixture suite is claimed.

See [`DEPENDENCY_AND_TEST_STABILIZATION_2026-11-04.md`](DEPENDENCY_AND_TEST_STABILIZATION_2026-11-04.md) for package and command details.

## 4. Fresh automated test baseline

Executed on Python 3.14.7 in this workspace; these are not results from the unavailable supported clean environment.

| Command / suite | Result | Classification |
|---|---|---|
| `python3 -m unittest discover -s stageC/tests -v` | 248 run; 5 skipped; 2 errors | One legitimate fail-closed Phase 4 manifest error in recipe integration; one missing-`jsonschema` import error. |
| `python3 -m unittest discover -s stageC/releases/Phase3-v0.1.2/stageC/tests -v` | 57 run; 2 errors | Both imports require missing `jsonschema`. |
| `python3 -m unittest discover -s stageC/phase4/tests -v` | 13 run; 1 failure | Integrity assertion finds `Phase4-v0.1.0/release_info.json` observed hash `12303bf9…` versus expected `5b749b70…`. The assertion was not changed. |
| `python3 -m unittest discover -s stageD/tests -v` | 63 run; 0 failures; 6 skipped | Schema checks skipped because `jsonschema` is absent. |
| `python3 -m unittest discover -s stageC/tests -p test_app_api.py -v` | 9 run; 0 failures | Includes fail-closed integrity, no cooked number without evidence, and human-review workflow checks. |

Stage C's integration traceback is `SourceIntegrityError: Phase 4 manifest digest does not match its pinned release hash`. The test results and logs are summarized in the dependency report; temporary full logs are in `/private/tmp/cookrisk_final_cycle_test_1.log` through `_5.log`.

The real local service health smoke returned `DEGRADED_PHASE4_CONTEXT_UNAVAILABLE`: 584 Phase1B foods loaded, Phase 2 accepted cooking evidence 0, Phase 4 `BLOCKED_INTEGRITY` with 0 context records, and 317 Stage B rows loaded. This confirms the current real-data app keeps Phase 4 withheld.

### Release hash checks

The currently frozen valid packages verify: Phase1B-v1.3.2 **1,324/1,324** (detached manifest SHA-256 `df3a95ae0957b68a89e38098c0824877196aa74ef7dd92573e6ab1f37e39b9b5`), StageB V20 **839/839**, Phase2-v0.3.1 **50/50**, Phase3-v0.1.2 **47/47**. Phase4-v0.1.2 is **not verified**. No release hashes were repaired or rewritten.

## 5. Stage A owner-decision readiness

- Decision packet: [`STAGE_A_RF01_RF15_DECISION_REGISTER.md`](phase2/STAGE_A_RF01_RF15_DECISION_REGISTER.md). RF-01–RF-15 are prepared with alternatives, conservative interim handling and required evidence; approvals remain **0/15**.
- Accountability: repository tracker requires an owner response, scientific reviewer, artifact, locator, date and rationale, but does not name an accountable owner. The user-provided context names Professor Ganesh Bagler as professor; repository evidence does not assign him the RF-01–RF-15 approver role, so that role remains to be confirmed.
- Model manifest expects input hash `cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27`; current Stage A input is `750124efc8b89dff1f67764064b1049b5db51fb1b2f222d4f91cd94c56945f89` (570,209 bytes). Model artifact hash matches its recorded pin, but exact training snapshot, target basis/denominator, preprocessing contract and joblib training version are not all supplied. New-record inference remains blocked; no OOF substitutions.

## 6. Stage B and Stage D reviewer readiness

- StageB V20: 143 compounds, 130 identity-complete, 13 pending. [`V20_PENDING_IDENTITY_REVIEW_AUDIT.md`](../../stageB/reports/V20_PENDING_IDENTITY_REVIEW_AUDIT.md) preserves unresolved stereochemistry, isomer, salt/mixture and structural questions. It does not claim independent chemistry approval.
- Stage D: 317/317 evidence rows remain `NOT_REVIEWED`; 25 mechanism candidates remain pending independent review. [`evidence_review_queue_report.md`](../../stageD/reports/phase5/evidence_review_queue_report.md) and [`mechanism_reviewer_packets.md`](../../stageD/reports/mechanism_reviewer_packets.md) carry source references, locators, evidence boundaries and reviewer questions. Assignment/action workflow is auditable; no decisions were added. StageB queue/source rows remain 317/317 field-equal per [`source-pin reconciliation`](../../stageD/reports/STAGEB_V20_SOURCE_PIN_RECONCILIATION_2026-11-04.md).

## 7. Stage C scientific safeguards

- Phase1B-v1.3.2 remains 584 food records/mappings, 116 quantitative compounds overall, 80 ordinary-food eligible.
- Phase 2 has 117 audited observations and 22 food/evidence combinations; accepted cooked-concentration outputs remain **0**. Do not infer total-mass retention from apparent concentration ratios or bridge bases without measurements.
- Raw-reference recipe calculations remain distinct from cooked-data-supported outputs. Missing uncertainty bounds stay explicit. Exposure is not clinical risk.
- No new scientific measurement or validation result was generated in this cycle.

## 8. Partner Windows verification package status

Instructions are in [`PARTNER_WINDOWS_VERIFICATION_PACKAGE_2026-11-04.md`](PARTNER_WINDOWS_VERIFICATION_PACKAGE_2026-11-04.md). App runtime uses Python standard library and binds to loopback; prototype code floor is Python 3.10, but Windows was not executed here. Use Python 3.12.14 as the recommended verification candidate once provided; this is not yet a qualified support claim. The partner must run the commands from the exact reviewed/pushed revision. Current local changes are uncommitted and not available through the remote. Expected actual app status is Phase 4 degraded with contextual records withheld. Partner clone/browser verification remains **PENDING**.

## 9. Final gates and next actions

| Gate | State | Next accountable action |
|---|---|---|
| Phase 4 original recovery | UNRECOVERABLE from accessible/documented sources | Owner supplies authenticated archive/backup if one exists; otherwise review/approve successor plan. |
| Reproducible Python/test environment | BLOCKED | Maintainer supplies supported Python 3.12.14 plus approved complete lock/wheelhouse or reachable approved mirror. |
| Formal schema validation | BLOCKED | Run Draft 2020-12 validation with the approved environment, including valid/invalid fixtures and `$ref`s. |
| Stage A inference | BLOCKED | Named owner provides RF-01–RF-15 decisions, exact data snapshot and full preprocessing/model environment contract. |
| Stage B identity review | PENDING | Qualified chemistry reviewer adjudicates 13 pending identities. |
| Stage C cooked concentrations | 0 accepted | Primary evidence must satisfy identity, matrix, basis, units, cooking and retention/yield gates. |
| Stage D evidence/mechanisms | 0 human decisions | Qualified reviewers process the 317 queue and 25 candidates; preserve audit trail. |
| Partner/production readiness | PENDING / NOT PRODUCTION-READY | Partner runs Windows/browser checks; separate security, privacy, accessibility and deployment review. |

**Release decision:** keep all frozen releases untouched. Do not publish a Phase 4 successor or call the system complete until its owner, provenance, integrity, test, science and human-review gates are satisfied.
