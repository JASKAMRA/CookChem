# Phase 1B final continuation — baseline audit (2026-11-03)

**Status:** `PHASE1B_BASELINE_AUDIT_COMPLETE`  
**Scope:** Stage C Phase 1B research/data only. Stage B release and Phase 1-v1.3.0 foundation are read-only dependencies.

## Verified active baseline

| Measure | Verified count |
|---|---:|
| Stage B registry universe | 143 compounds |
| Stage B identity structure audit complete | 107 |
| Stage B identity review pending | 36 |
| Active food-composition records | 511 |
| Active compound-food mappings | 511 |
| Unique compounds with any mapping | 109 |
| Unique compounds with a quantitative mapping | 109 |
| Unique identity-complete compounds with quantitative mappings eligible for exposure use | 93 |
| Pending-identity compounds with legacy mappings | 16 compounds / 46 rows |
| Orphan mappings | 0 |
| Identity-complete but not quantitatively mapped | 14 |

The distinct 109 mapped and 93 identity-complete eligible counts are preserved as separate metrics. The mapping includes 501 exact identity matches, 1 verified synonym match and 9 structure-supported matches. All 511 rows indicate quantitative data available. Data files were not changed during this audit.

Food composition SHA-256: `aa15fd49be4afd30d1f61fe06de9039d0a925c22a6c56e970ddc75033b04f127`  
Mapping SHA-256: `9dcaadf0821aee15f1666ca26c88c592bb1e98a781eb533e246ddd94dab9ca97`

The Stage B authoritative manifest was independently verified before this audit (836/836 listed files; manifest SHA-256 `b85f8293297cb5e447d2293e31cfcdafbef50497260d870d54f14da441c7359e`). The Phase 1 foundation dependency remains `stageC/releases/Phase1-v1.3.0`. Historical `Phase1B-v1.0.0` checksum/package verification failure remains recorded and that historical release is unchanged.

## Eligible unmapped compounds

The following fourteen are the complete set of audit-status `Complete` Stage B compounds without a current quantitative mapping:

| Compound_ID | Compound | Prior search disposition |
|---|---|---|
| MOL-V10-5281605 | Baicalein | Targeted Batch 099 screening; medicinal-root values excluded |
| MOL-V10-64982 | Baicalin | Targeted Batch 099 screening; medicinal-root/tincture values excluded |
| MOL-V10-5281697 | Scutellarein | Targeted Batch 099 screening; medicinal-root values excluded |
| MOL-V10-5281703 | Wogonin | Targeted Batch 099 screening; medicinal-root values excluded |
| MOL-V10-5320315 | Oroxylin A | Targeted Batch 099 screening; medicinal-root values excluded |
| MOL-V10-2825024 | 7-Methoxyflavanone | Targeted Batch 099 exact-identity search; no eligible exact-matrix value found |
| MOL-V10-3084961 | Wogonoside | Targeted Batch 099 screening; medicinal-root values excluded |
| MOL-V17-CID-5280704 | Apigetrin | No Phase 1B search-log entry; include in final bounded batch |
| MOL-V17-CID-5281673 | Myricitrin | No Phase 1B search-log entry; include in final bounded batch |
| MOL-V17-CID-6072 | Phloridzin | No Phase 1B search-log entry; include in final bounded batch |
| MOL-V17-CID-92794 | Prunin | No Phase 1B search-log entry; include in final bounded batch |
| MOL-V17-CID-5280459 | Quercitrin | No Phase 1B search-log entry; include in final bounded batch |
| MOL-V17-CID-91469 | S-equol | No Phase 1B search-log entry; include in final bounded batch |
| MOL-V17-CID-17730 | Sunset Yellow FCF | No Phase 1B search-log entry; include in final bounded batch |

The previous search dispositions are documented in the active continuation's search log and Batch 099/100 source notes. The new batch is limited to the seven previously unsearched eligible IDs; re-searching the seven already screened would duplicate work.

## Coverage ceiling and report limitations

Because only 107 of 143 compounds have a complete Stage B identity audit, even adding valid measurements for all fourteen remaining eligible compounds would produce at most **107 identity-complete quantitative compounds**. Reaching the requested threshold (>109) would require at least three pending identities to be adjudicated and then supported by qualifying food-composition evidence. Phase 1B does not resolve Stage B identities; no pending identity is inferred or unblocked here.

The active `CANDIDATES.csv` has 23 held candidate rows; historical batch candidate files contain 618 rows across 51 files and 66 distinct compound IDs. These are candidate-verification counts, not accepted-coverage counts. The active priority register and batch screening notes do not encode mutually exclusive, exhaustive qualitative-only and semiquantitative-only compound totals; those categories will be reported only for the fourteen audited gaps where the source disposition can be evidenced. No unsupported aggregate is inferred from search-query text.
