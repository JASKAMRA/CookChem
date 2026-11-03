# CookRisk Stage B V8 quality release

Final dataset: `outputs/stageB_food_drug_interactions_v8.csv` (60 anchors, 189 rows, 121 unique PMID publications). This is a qualified evidence library, not a clinical or exposure model.

Read `reports/CookRisk_StageB_V8_Handoff.pdf`, `outputs/claim_level_audit.csv`, and `outputs/warning_resolution_ledger.csv` together with the dataset. Four resveratrol outcomes (SB-0051 through SB-0054) preserve legacy GMR/CI values for traceability but are explicitly HELD from numerical integration pending original full-table review. SB-0066 is provisional apigenin/rutin attribution. No automatic master-retention merge is authorized by standalone identity verification.

V7 is immutable at `../release_v7_20261015_clean`. V8 changes only five records/13 fields, documented in `outputs/evidence_change_log.csv`. The compound registry and original evidence IDs/schema are preserved. New-source snapshots are under `sources`; inherited primary caches are under `inherited_sources`, using the original paths relative to Stage B. `inputs/v7_*` retains original source, selection, processing and screening ledgers with their original meaning. Fresh all-record review scope is in `outputs/all_record_review_audit.csv`; inherited full-text review is not claimed as newly repeated review.

## Reproduce

Python 3 with reportlab and pypdf is required for the PDF. The data build/validation otherwise uses the standard library. Run from this directory:

```
python build.py
python validate.py
python report.py
python package.py
```

The original V7 directory and original project tree must remain in their relative locations for baseline validation and offline rebuild. Network is not required to rebuild using captured sources. `baseline.py` documents the initial immutable baseline audit and isolated V7 suite execution; `collect.py`, `access_followup.py` and `history_search.py` document the research collection and historical search. These research scripts should not be rerun merely to reproduce a frozen release; network responses may change and access may be rate-limited. Do not replace frozen snapshots silently.

V7 checks: 42/42 and 10/10 mutation detections, isolated rebuild identical. V8 checks: 26/26 and 12/12 mutation detections. Preservation manifest covers all 8,087 prior files. Automated checks do not settle unresolved study reporting or prove every legacy scientific extraction independently correct. Source-number token screening is diagnostic, not a numerical proof.

## Scope and remaining uncertainty

21 records have selected-full-text review, 164 abstract review, 4 qualitative abstract support with numerical table review pending. There are 22 open warning entries across 21 codes (20 inherited open plus two newly explicit), one previously resolved and two not applicable. No newly discovered historical selection dates are invented; original search dates are distinguished from selection dates. Fourteen deferred candidates received triage only; none was added. Stage A, exposure estimation and risk scoring were untouched. No independent second reviewer or exhaustive literature-review claim is made.

Package excludes isolated rebuild workspace and page preview PNGs. `SHA256SUMS.json` checks the delivered release files; package integrity is recorded in the sibling ZIP SHA256 file. The ZIP is portable for inspection; full preservation/rebuild tests require the immutable original workspace baseline described above.
