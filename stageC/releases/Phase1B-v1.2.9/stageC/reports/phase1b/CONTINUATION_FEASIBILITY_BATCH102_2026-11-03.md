# Phase 1B continuation feasibility — pre-Batch 102

**Checkpoint verified:** `Phase1B-2026-11-03-batch-101-final-continuation`. The active files contain 539 food records and 539 mappings over the 143-compound Stage B universe. They cover 113 distinct compounds with quantitative mapping when identity-pending rows are included, but only 97/107 identity-complete compounds are currently eligible. There are 36 identity-pending compounds, 16 represented by 46 blocked mapping rows, 10 identity-complete gaps, and zero orphans. The current food and mapping SHA-256 values are `616a62c3cce8426b058e8aee3c6e746438ee2eea49680f2da492e10101172115` and `9774a96396107409a53f6bef5960daffacf5e40ae25d26e7ecaabbbc8c1d6bc1`; the original 511-row data prefixes still match their audited hashes.

## Feasibility

The current identity-complete ceiling is **107**, below the 130 minimum. Raising accepted coverage from 97 to 130 requires 33 additional qualifying compounds. Even accepting measurements for all ten current identity-complete gaps would reach only 107; at least 23 currently identity-pending compounds would also need formal Stage B identity adjudication and qualifying ordinary-food evidence. Phase 1B will not change Stage B or count pending identities as accepted coverage.

This ceiling does not restrict the research universe. The current search log has 418 events across 126 of 143 compounds, including all 107 identity-complete IDs and 19 identity-pending IDs. The remaining 17 identity-pending IDs need a first bounded quantitative-food screen. Research can continue across all 143 while identity decisions remain separate.

## Next bounded batch

Batch 102 will screen the three still-open identity-complete evidence leads from Batch 101 (Apigetrin, Myricitrin, Prunin) and 12 previously unlogged identity-pending compounds. Existing Batch 101 evidence and the seven already-screened complete-identity gaps will not be repeated without a new source lead. Candidate values for pending identities will remain isolated from the accepted food table and eligible-coverage count.

The actual Batch 101 baseline and continuation rules are in `CHECKPOINTS.json`, `COMPOUND_COVERAGE_REGISTER_2026-11-03.csv`, and `batches/batch_101_final_eligible_foodscreen/SCREENING_NOTE.md`. Stage B, Stage C Phase 1-v1.3.0, Stage A, and all historical releases remain protected.
