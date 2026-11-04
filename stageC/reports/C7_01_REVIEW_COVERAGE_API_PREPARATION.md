# C7-01 Preparation — Review-Coverage API Contract

**Status:** **LIMITED PREPARATION COMPLETE; C7-01 AND STAGE C REMAIN INCOMPLETE**  
**Date:** 2026-11-05

## Diagnosis and contract evidence

The review-coverage endpoint previously returned `build_coverage_dashboard(queue, events)` unchanged. That dashboard response did not include top-level `record_count`.

The intended meaning is supported by three existing Stage C consumers/contracts:

1. `stageC/app/static/app.js` reads `data.record_count` and labels it **“Immutable source queue”**.
2. `stageC/app/server.py` already exposes the same full-source count as `source.record_count` in the review-queue response, distinct from the filtered `total_count`.
3. The existing Stage C test `test_review_queue_api_keeps_machine_triage_separate_from_human_state` expects `record_count` on `/api/review-coverage`.

The app README describes the local/read-only limitations but does not define the coverage JSON schema. The UI, queue endpoint, and existing test consistently establish that coverage needs the full unfiltered source queue count. Therefore, adding this field is a justified API contract correction, not a change to review eligibility or workflow behavior.

## Change made

`CookRiskService.review_coverage()` now adds `record_count = len(queue["records"])` to the dashboard response. All other dashboard fields and review-queue behavior are preserved.

The new isolated test supplies a synthetic in-memory queue snapshot and a controlled dashboard result. It patches `build_review_queue` to raise if called, proving the test does not invoke the real review-queue loader. It verifies the API returns the full queue count and preserves dashboard counts.

## Exact isolated test command and result

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=stageC/tests python3 -m unittest -v \
  test_app_api.AppApiTests.test_review_coverage_api_returns_full_source_count_from_isolated_snapshot \
  test_app_api.AppApiTests.test_review_action_api_rejects_without_trusted_identity_and_writes_nothing \
  test_app_api.AppApiTests.test_review_action_ui_discloses_unavailable_authentication_and_stays_disabled
```

**Result:** 3 tests run, 3 passed, 0 failed, 0 skipped. The selected tests use synthetic fixtures/test doubles and do not call the Stage B review-queue or pinned-data loaders. No full API suite or Stage B-sensitive test was run.

## Files changed

- `stageC/app/server.py` — add the full source queue count to the coverage response.
- `stageC/tests/test_app_api.py` — add the isolated synthetic coverage contract regression test.
- `stageC/reports/C7_01_REVIEW_COVERAGE_API_PREPARATION.md` — this evidence report.

## Remaining blockers

- **C1B-02:** exact-byte policy is approved and recorded, but a current owner-reviewed revision/archive and partner Windows/browser verification remain outstanding.
- **C7-01:** this is preparation only. Its remaining integration, allowed regression validation, clean-copy/Windows chain, and release acceptance are incomplete. Do not treat this change as finalization or a release.
- **Stage C overall:** incomplete. No Phase 2 work was started and no Stage C completion claim is made.

## Preservation

Only the two authorized Stage C application/test files above and this preparation report changed. No Stage B source or embedded snapshot was read or loaded by the isolated tests. Stage A and Stage D were not modified. Scientific datasets, frozen releases, manifests, historical outputs, and the 117 accepted Phase 2 observations were preserved. No Git operation or remote access occurred.
