# Dataset and Evidence Development

## Evidence construction principle

The project’s dataset work proceeds from primary source tables, not arithmetic-only matching. A record is meaningful only with analyte identity, source locator, food matrix, preparation context, and compatible raw/cooked measurement basis. Reported values and experimental means are retained at the source’s unit/basis; technical replicates are not expanded into artificial independent rows. Exclusions and unresolved candidates remain documented.

## Versioned evidence history (separate contexts)

| Package/context | Reported rows and coverage | Role / status |
|---|---|---|
| Historical benchmark | 1,124 rows; 197 molecular groups; 183 source families reported in controlled comparison | `Retention_Final` ML benchmark. Not an ACR dataset. |
| Recovery v0.2.0 | 117 verified source-pair observations; 24 molecular groups; 2 DOI families; 2 food matrices | Initial narrow ACR set; source/food generalization is not supportable. |
| Recovery v0.3.0 | 338 rows; 45 compounds; 6 DOI families; 9 food matrices; 12 methods | 221 arithmetic-matching historical rows were source-reverified; report says no new literature rows. |
| Recovery v0.4.0 | 374 rows; 46 compound groups; 7 DOI families; 14 matrices | 36 newly admitted rows from an independent study. |
| Recovery v0.5.0 | 379 rows; 49 compound groups; 8 DOI families; 15 matrices and methods | Added five related potato/vitamin-C treatment records; source diversity improved narrowly. |
| Recovery v0.6.0 | Same 379-row v0.5 parent; no new observations | Controlled source-confounding and feature-ablation analysis. |
| Recovery v0.7.0 | 407 observations; 9 DOI families | Added 28 vitamin-C fresh-weight pairs; six categorical overlaps, each only two sources; not enough for source-transfer claims. |
| Recovery v0.8–v1.0 / 439 family | 439 observations; 10 DOI families; 49 compound labels; 46 IDs; 22 matrices; 16 methods in v0.9 report | v0.8 adds 32 source-linked sweet potato phenolic pairs. v0.9/v1.0 find zero strict protocol-identical cross-source replications; v1.0 adds no data and trains no model. |
| Final prototype | 439 eligible rows, 10 sources | Existing model results are retained as historical reports, but current bytes were reported to mismatch the manifest’s expected parent SHA; therefore the outputs are BLOCKED/UNVERIFIED against present bytes. |
| Batch021 ACR master | 1,016 rows; 32 DOI families; 51 compound labels/48 canonical IDs; 66 matrices; 41 methods | Current CSV SHA-256 `d866d0ffab8c335e0469f2815c3cdf518b3d019be1bdf2e37ba2ced2e7d5d3c1`; Batch021 adds 78 pairs to 938 parent rows; manifest lacks a dataset hash. The separate validation audit records historical input SHA-256 `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`; exact bytes are unavailable, so audit attribution to the current CSV is BLOCKED/UNVERIFIED. |
| Verified ACR reconstruction | 1,016 rows; 32 DOI families; 48 identities; 66 matrices; 41 methods | A separate reconstruction with its own source/identity and evaluation artifacts. Not interchangeable with Batch021. |
| Strict/extended/exploratory tiers | 338 / 948 / 989 arithmetic-matching rows (source-heldout exploratory analysis uses 971) | Evidence tiers differ. The 338 strict tier is source-and-arithmetic verified; extended/exploratory tiers are not equivalent evidence classes. |

The detailed source admission sequence and batch table-level references are in [the master inventory](../EXISTING_RESULTS_MASTER_INVENTORY.md#r-16--controlled-literature-acquisition--dataset-expansion-batches). No dataset is designated canonical here.

## Reported source acquisition outcomes

- Batch reports describe direct individual-analyte raw/cooked pairs with basis, method, and locator retained when available.
- Reported exclusions include non-detect pairs; aggregate endpoints; ambiguous analyte/isomer identity; missing canonical descriptor identity; unspecified or incompatible measurement basis; and values available only as percentages or narrative summaries without auditable raw/cooked table values.
- One v0.5 candidate was excluded because basis was not specified; another remained pending because primary table/method access was unavailable.
- Candidate B in v0.8 admitted 32 compatible chlorogenic and trans-ferulic pairs, while neochlorogenic values remained outside model-ready data due to unresolved exact identity/descriptor mapping.
- v1.0 candidate literature review reported zero additional observations and zero strict source matches; wet-basis wording was not silently converted to fresh-weight, dry-weight data were not converted, and analyte isomers were not merged.

## Dataset integrity and provenance caveats

- The 1,124-row benchmark input is recorded with SHA-256 `750124efc8b89dff1f67764064b1049b5db51fb1b2f222d4f91cd94c56945f89` in its closure record.
- The final-prototype manifest expected parent SHA `d3960dc6ec808ca1783cbb2c57d35fb4676da04feeff675280c1f07eb072005a`; a later authorized inventory reported current source bytes as `475c60a737be166fca208f2573a9916eef7983e00b5ddbff39f336408c40134a`. Treat that metric/data linkage as unresolved.
- Batch021 and the verified reconstruction both report 1,016 rows and 32 DOIs but have different identity counts and artifact hashes. Never infer equality from counts.
- This assembly did not modify or rehash source datasets; all dataset properties in this section are reported from existing artifacts.
