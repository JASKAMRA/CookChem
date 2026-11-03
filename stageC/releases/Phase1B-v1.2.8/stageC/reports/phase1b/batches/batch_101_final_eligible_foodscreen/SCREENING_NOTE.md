# Batch 101 — final eligible food screen

**Decision:** bounded Phase 1B continuation complete; the requested >109 identity-complete compound target was not achieved and is not reachable under the current Stage B identity audit.

## Baseline and result

The independently checked baseline was 143 Stage B compounds, 107 identity-complete and 36 identity-pending; 511 food records and 511 mappings covered 93 identity-complete compounds. Batch 101 appended 28 records and 28 mappings while preserving the baseline files as the original prefix. Four new identity-complete compounds are now covered: phloridzin, quercitrin, S-equol and Sunset Yellow FCF. The active dataset has 539 records/mappings, 113 compounds with any quantitative mapping, and 97/107 identity-complete compounds covered. There are zero orphan mappings.

The identity-pending set still has 36 compounds; 16 have 46 legacy mapping rows. Those rows remain ineligible for identity-complete coverage despite their mapping labels. Ten identity-complete compounds remain uncovered. Reaching 110 requires 13 additional compounds; at most ten currently uncovered compounds can be gained without Stage B identity adjudication. No pending identity was changed.

## Accepted measurements

| Compound | Records | Source / locator | Original basis and qualification |
|---|---:|---|---|
| Phloridzin | 22 | Zielińska et al. 2020, DOI 10.3390/antiox9111054, Tables 1 and 3 | 11 apple cultivars, peel and flesh; µg/g FW; mean ± SD, n=4; HPLC-DAD with MS/MS identity confirmation. [Source](https://www.mdpi.com/2076-3921/9/11/1054) |
| Quercitrin | 1 | Butkeviciute et al. 2022, DOI 10.3390/antiox11020266, Figure 4 and text | Galaval apple flesh on G.11 rootstock, 148 ± 18 µg/g DW; HPLC-PDA and authentic standard. The reported SD is from three consecutive tests; it is not treated as independent biological replication. [Source](https://www.mdpi.com/2076-3921/11/2/266) |
| S-equol | 1 | Jou et al. 2013, DOI 10.1016/j.jff.2013.01.006, Table 1 | Commercial ready-to-serve stinky tofu aggregate, 1.2 ± 1.0 mg/100 g wet weight, n=138; 126/138 detectable and all measured equol was S-enantiomer. Mixed preparation methods and nondetect handling of the mean remain limitations. [Source](https://doi.org/10.1016/j.jff.2013.01.006) |
| Sunset Yellow FCF (E110) | 4 | Floriano et al. 2018, DOI 10.21577/0103-5053.20170173, Table 3 | Retail sports drinks S1/S4/S6/S7; 11.49 ± 1.14, 9.06 ± 0.77, 11.84 ± 0.91, and 3.79 ± 0.33 mg/L. HPLC-UV-Vis, LOQ 0.5 mg/L; replicate count and meaning of ± are unspecified. No density conversion. [Source](https://www.scielo.br/j/jbchs/a/VzpDPnjj3XtvSDYKyGqNpLJ/?lang=en) |

Original units and bases remain in the active records; only unit-equivalent normalizations are present. No value was converted across moisture or density bases.

## Held and rejected findings

- **Apigetrin:** chrysanthemum result 16.04 mg/g powder held because moisture basis is unspecified; separate graph-level values were not reconstructed and identity was tentative.
- **Myricitrin:** HPLC-DAD food table held because basis is absent and the paper's apple text conflicts (228 vs 240 mg/kg).
- **Prunin:** primary abstract confirms occurrence but the numeric table is inaccessible; no value, unit or basis inferred.
- **Quercitrin in green coffee:** 22 Table 8 lot values remain outside the accepted food table because prolonged acidic extraction (pH 2, 70% ethanol, 60 °C, 1.5 h) may alter glycosides and does not establish native intact-food quercitrin.

The four candidate/source decisions and 22 individual coffee-lot exclusions are in `rejected_candidates.csv`; four unresolved source leads are also preserved in the central candidate register. The evidence and reasons are recorded in `source_registry.csv`, `SEARCH_LOG.csv`, `coverage_gap_register.csv`, and the Stage C candidate ledger. These held findings remain open for evidence-based follow-up.

The complete 143-compound state, including identity status, quantitative mapping counts, logged search events and gap dispositions, is in `COMPOUND_COVERAGE_REGISTER_2026-11-03.csv`. The older 119-row priority register is retained as historical; no priority was assigned to new targets without a separate scoring review.

## Search and traceability

Batch 101 added seven previously unlogged search events. The cumulative search log has 418 events across 126 of 143 IDs and includes all 107 identity-complete IDs. The other 17 unlogged compounds are identity-pending and excluded from Phase 1B acquisition. The source registry has 31 entries. The central candidate register has 27 rows. The gap register has 13 rows, of which ten are identity-complete uncovered targets and three are retained identity-pending legacy entries.

## Validation and integrity

- Focused scientific/data validation: PASS; 539 records, 539 mappings, zero food/mapping errors, zero orphans, zero Stage B snapshot changes.
- Identity-pending mapping rows recomputed by joining the live mapping file to the Stage B audit: 46 rows across 16 compounds.
- Food SHA-256: `616a62c3cce8426b058e8aee3c6e746438ee2eea49680f2da492e10101172115`
- Mapping SHA-256: `9774a96396107409a53f6bef5960daffacf5e40ae25d26e7ecaabbbc8c1d6bc1`
- Baseline food and mapping hashes in `coverage_delta.json` match the pre-append audit. Stage B and Phase 1-v1.3.0 were not modified.
- The first 511 data rows plus headers retain their exact baseline byte hashes. A regenerated mapping file matches all active mapping rows and row order; its whole-file hash differs only because it serializes the appended rows with CRLF line endings while the active append intentionally preserves the original CRLF prefix and uses LF for the 28 new rows.
- Historical Phase1B-v1.0.0 integrity limitations remain historical; no new Phase 1B release was created.

The >109 target remains **not achieved**. Phase 1B does not resolve Stage B identities; further progress past 107 identity-complete compounds depends on Stage B review and subsequent qualifying measurements.
