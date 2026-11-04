# C1B-01 — Stage C-Only Release-Linked Coverage Reconciliation

**Task:** C1B-01 — Reconfirm quantitative Phase 1B coverage  
**Status:** **COMPLETE — Phase1B-v1.3.2 counts reconciled; superseded intermediate artifacts remain identified**  
**Reconciliation date:** 2026-11-05

## Scope

This reconciliation used only Stage C Phase 1B release tables, Stage C validation outputs, Stage C code, and the Stage C release checksum manifest. It did not open or query Stage B source files or embedded Stage B snapshot payloads. It did not run the release verifier or regenerate data. No scientific data, release artifact, or manifest was modified.

## Release and artifact identity

The authoritative package is **Phase1B-v1.3.2**. Its `RELEASE.json` describes the corrected reconciliation; `VALIDATION_RESULTS.json` carries the final Phase 1 validation aggregate; and `PHASE1B_RECONCILIATION_REPORT.md` explains the distinction between identity-complete mappings and scientifically eligible quantitative coverage. Targeted entries in `CHECKSUMS.json` match the files below. The active food and mapping table hashes also match the file hashes recorded in the Stage C `CHECKPOINTS.json`.

| Stage C artifact in Phase1B-v1.3.2 | SHA-256 |
|---|---|
| `RELEASE.json` | `bbcff3b030bb65611363e7c70e3a16bb7f6651b6dbe6c131eaf69253a9f50c3f` |
| `VALIDATION_RESULTS.json` | `690dbac67d11758ab76e1510ffdd0e851643e81661bf88a9a2f23158337c1ded` |
| `PHASE1B_RECONCILIATION_REPORT.md` | `0227c92d9fa739780af00fa4b49301f66e35419d92e177e1e44f3961481a421d` |
| `stageC/data/food_composition/food_composition.csv` | `40f2e41494ce1f8cbd58ff52bd9e8678236145ad740dd8a0a25c0b6054d02ece` |
| `stageC/data/compound_food_mapping/compound_food_mapping.csv` | `e792e6a5675fdbd71e50f6afa8ea5dd48138ad45010bbede1c567a65b25e35d2` |
| `stageC/reports/phase1b/CHECKPOINTS.json` | `ebd875e6b2f46742309e9fc84c278b31d14315c0b5f0848d2ba4be87f55039d9` |
| `stageC/reports/validation/phase1_validation.json` | `db442f586d843da533e627db4f2001978e7560c468cf9731106ab4c63417a8cb` |
| `stageC/reports/validation/mapping_coverage_v20.json` | `44e11a2c4b9c156e15c7ea1d15b5aa8423e5d083961a63de73ba177dd230174e` |
| `stageC/reports/validation/mapping_rebuild_v20.csv` | `ddb0afd2019b028615624a03949e74833d617347970e00d14a548613ab733562` |

The root release manifest records these as Phase1B-v1.3.2 artifacts. The intermediate `mapping_coverage_v20.json` itself has no run identifier or source hash; its own `mapping_file` field points to `mapping_rebuild_v20.csv`.

## Reconciled definitions and counts

| Count | Definition and Stage C evidence | Disposition |
|---:|---|---|
| **584 rows** | Active v1.3.2 `food_composition.csv` rows and `compound_food_mapping.csv` rows; `CHECKPOINTS.json` records the same row counts and matching table hashes. | Current release row count. |
| **115 IDs** | Distinct non-empty `food_composition.compound_id` values among rows with finite normalized concentrations. | Incomplete raw-field count: it omits the explicit manual mapping override field. Forty-one quantitative rows have an empty source `compound_id`. |
| **116 data IDs** | Distinct `mapping_review_compound_id` when present, otherwise `compound_id`, across rows with finite normalized concentrations. All 584 normalized values are finite. | Reproducible data-level ID count; it is not, by itself, identity qualification. It corroborates the final release's 116 figure. |
| **130 raw mapped IDs** | Distinct `compound_food_mapping.compound_id` values across its 584 quantitative-available rows. | Raw mapped universe before identity/acceptance/eligibility filters. |
| **125 identity-complete mapped IDs** | `RELEASE.json` and `PHASE1B_RECONCILIATION_REPORT.md` identify this as identity-complete mapped compounds, not quantitative coverage. Five mapped IDs are identity-pending. | Correct meaning of the reported 125. The 125 value in `phase1_validation.json` is mislabeled/stale where it calls this `compounds_with_verified_quantitative_food_data`. |
| **121 accepted mapped IDs** | Final release aggregate after mapping acceptance. | Accepted mapping count; still not the quantitative eligibility count. |
| **116 scientifically eligible quantitative IDs** | Final `VALIDATION_RESULTS.json` and `RELEASE.json`. The Stage C `mapping_coverage` implementation counts IDs only when the mapping is in `VERIFIED_STATUSES`, `quantitative_data_available == "true"`, and its compound ID is in the identity-complete registry. The quantitative flag itself requires reported concentration, preparation state, measurement basis, an allowed food-use class, verified source status, and an allowed source class. | Authoritative v1.3.2 all-class quantitative eligibility count. Its identity filter is accepted here from the release-linked Stage C validation output; no protected identity roster was independently queried. |
| **80 ordinary-food eligible IDs** | Final v1.3.2 release aggregate under the same quantitative eligibility definition. | Authoritative ordinary-food count. |
| **36 eligible IDs outside ordinary food** | `116 all-class eligible − 80 ordinary-food eligible`. | Contextual/non-ordinary residual. The final aggregate does not split these 36 between food ingredients and prepared beverages. |

The release registry totals are **143 compounds: 130 identity-complete and 13 identity-pending**. Within the Phase 1B mapped set, the separate figures are **130 raw mapped, 125 identity-complete, 5 identity-pending, 121 accepted, and 116 scientifically eligible quantitative**. These stages of qualification are not interchangeable.

### Food-use categories and overlap

At the row level the active table contains **335 ordinary-food**, **221 food-ingredient**, and **28 prepared-beverage** records (584 total). Using the explicit review-ID override where present, data-level unique quantitative IDs are **80 ordinary food**, **38 food ingredient**, and **9 prepared beverage**. The class counts overlap: ingredient/beverage union is 47, 11 of those IDs also occur in ordinary-food rows, and the all-class union is 116. These category-specific data counts are not substituted for the release's identity-filtered eligibility counts. The release only reports the filtered ingredient/beverage categories together as the 36 IDs outside ordinary food.

## Explanation of the three disputed figures

### 125 / 584

The Stage C release explicitly defines **125** as identity-complete mapped IDs. It is not the quantitative eligibility count. The packaged `phase1_validation.json` uses the field name `compounds_with_verified_quantitative_food_data` for 125, but that conflicts with the more specific v1.3.2 `RELEASE.json`, `VALIDATION_RESULTS.json`, and reconciliation report. The v1.3.2 reconciliation report states that 125 is identity completion and corrects quantitative eligibility to 116 overall / 80 ordinary food. Thus the 125 field in `phase1_validation.json` is a stale/mislabeled aggregate, not a second quantitative result.

### 111 / 546

`mapping_coverage_v20.json` reports 111 verified quantitative IDs and 546 food/mapping rows; it points to `mapping_rebuild_v20.csv`, which independently contains 546 rows and 116 candidate IDs. This is an intermediate mapping snapshot bundled inside the later v1.3.2 package, not the active 584-row table. The final package contains 584 rows and the corrected 116 eligibility result. The 38-row input difference and changed candidate/eligibility totals show that the 111 value was computed on a different, earlier mapping input. The intermediate report does not identify its originating run or table hash, so its exact pre-package generation revision is not documented; it is superseded for current coverage.

### 115 IDs

The 115 count came from distinct non-empty `food_composition.compound_id` values alone. That field is empty on 41 quantitative rows; the table separately carries `mapping_review_compound_id`, and the Stage C mapping builder treats an accepted review ID as the mapping decision. Counting with that explicit override first yields 116 data-level IDs. The official 116 eligibility figure additionally applies the release's verified-mapping and identity-complete filters; it is taken from the release-linked Stage C validation aggregate, not inferred solely from the 116 data-level cardinality.

## Reproducible Stage C-only count

Run from the repository root. This snippet reads only the two Stage C Phase 1B CSV tables and does not open or query an identity registry or any Stage B source/snapshot:

```sh
python3 - <<'PY'
import csv
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

root = Path("stageC/releases/Phase1B-v1.3.2/stageC/data")
with (root / "food_composition/food_composition.csv").open(encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

def finite(value):
    try:
        return Decimal(value.strip()).is_finite()
    except (InvalidOperation, TypeError, AttributeError):
        return False

by_class = defaultdict(set)
raw_ids, effective_ids = set(), set()
finite_rows = 0
for row in rows:
    if not finite(row.get("normalized_concentration", "")):
        continue
    finite_rows += 1
    raw = row.get("compound_id", "").strip()
    if raw:
        raw_ids.add(raw)
    effective = row.get("mapping_review_compound_id", "").strip() or raw
    if effective:
        effective_ids.add(effective)
        by_class[row["food_use_classification"]].add(effective)

print("food rows", len(rows), "finite normalized rows", finite_rows)
print("direct source IDs", len(raw_ids), "review-override/fallback IDs", len(effective_ids))
print("unique IDs by food-use class", {k: len(v) for k, v in sorted(by_class.items())})
print("ordinary + ingredient union", len(by_class["ordinary food"] | by_class["food ingredient"]))
PY
```

Recorded output: **584** rows; **584** finite normalized rows; **115** direct source IDs; **116** review-override/fallback IDs; class counts **ordinary 80, ingredient 38, prepared beverage 9**; ordinary-plus-ingredient union **107**. The identity-qualified 116 and 80 values are separately evidenced by `VALIDATION_RESULTS.json` and the v1.3.2 reconciliation report, using the documented filter above.

## Validation and disposition

- Active table SHA-256 values match the Stage C checkpoint and the corresponding targeted entries in the Phase1B-v1.3.2 checksum manifest.
- Targeted checksum-manifest entries were checked for the Stage C artifacts listed above. The release verifier was not run because it traverses the protected embedded dependency.
- No tests were run; this task is a read-only count reconciliation.
- The unexplained run provenance of the 546-row intermediate remains a documentation limitation, but it does not change the v1.3.2 active dataset or its reconciled final metrics.

**C1B-01 is COMPLETE for Phase1B-v1.3.2 coverage reconciliation.** The current quantitative eligibility figures are **116 across all classes and 80 ordinary-food eligible**. The former 125 is an identity-complete mapping count; 111 is a superseded intermediate result; 115 is a direct-field-only count that omitted review-ID overrides. No later task was started.

## Preservation confirmation

Only this C1B-01 report was modified. No Stage B source file or embedded Stage B snapshot was opened, queried, tested, or changed. No Stage A or Stage D file was changed. The 117 accepted Phase 2 observations, scientific datasets, frozen releases, manifests, historical outputs, and user changes were preserved. No Git operation or remote access occurred.
