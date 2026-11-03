"""Recompute and publish the Batch 101 Phase 1B checkpoint from live files."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
STAGE = ROOT / "stageC"
PHASE = STAGE / "reports/phase1b"
BATCH = PHASE / "batches/batch_101_final_eligible_foodscreen"


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


food_path = STAGE / "data/food_composition/food_composition.csv"
mapping_path = STAGE / "data/compound_food_mapping/compound_food_mapping.csv"
audit_path = STAGE / "data/stage_b_snapshot_20261103/identity_structure_audit.csv"
registry_path = STAGE / "data/stage_b_snapshot_20261103/compound_registry.csv"
foods, mappings, audit, compound_registry = rows(food_path), rows(mapping_path), rows(audit_path), rows(registry_path)
complete = {r["Compound_ID"] for r in audit if r["Status"] == "Complete"}
pending = {r["Compound_ID"] for r in audit if r["Status"] != "Complete"}
audit_by_id = {r["Compound_ID"]: r for r in audit}
valid_statuses = {"Exact identity match", "Verified synonym match", "Structure-supported match"}
quant_ids = {r["compound_id"] for r in mappings if r["quantitative_data_available"].lower() == "true" and r["mapping_status"] in valid_statuses}
any_mapped = {r["compound_id"] for r in mappings if r["compound_id"]}
pending_rows = [r for r in mappings if r["compound_id"] in pending]
food_ids = {r["food_record_id"] for r in foods}
orphans = {r["food_record_id"] for r in mappings} - food_ids
source_classes = Counter(r["source_classification"] for r in foods)
food_uses = Counter(r["food_use_classification"] for r in foods)
distinct_sources = len({(r["source_title"], r["source_url"]) for r in foods})
rows_without_doi_and_pmid = sum(not r.get("doi") and not r.get("pmid") for r in foods)
missing_core_source_fields = sum(any(not r.get(field) for field in ("source_url", "source_title", "reported_concentration", "reported_unit", "moisture_basis", "analytical_method", "source_verification_status")) for r in foods)
search = rows(PHASE / "SEARCH_LOG.csv")
search_ids = {r["Compound_ID"] for r in search}
search_counts = Counter(r["Compound_ID"] for r in search)
central_candidates = rows(PHASE / "CANDIDATES.csv")
source_registry = rows(STAGE / "data/food_composition/source_registry.csv")
gap_rows = rows(PHASE / "coverage_gap_register.csv")
gap_by_id = {r["Compound_ID"]: r for r in gap_rows}
batch_accepted = rows(BATCH / "accepted_rows.csv")
batch_rejected = rows(BATCH / "rejected_candidates.csv")
eligible = quant_ids & complete
uncovered = complete - eligible

assert len(audit) == 143 and len(complete) == 107 and len(pending) == 36
assert len(compound_registry) == 143 and len({r["Compound_ID"] for r in compound_registry}) == 143
assert len(foods) == len(mappings) == 539 and len(batch_accepted) == 28
assert len(eligible) == 97 and len(uncovered) == 10
assert len(pending_rows) == 46 and len({r["compound_id"] for r in pending_rows}) == 16
assert not orphans
assert missing_core_source_fields == 0

coverage_register_path = PHASE / "COMPOUND_COVERAGE_REGISTER_2026-11-03.csv"
food_counts = Counter(r["compound_id"] for r in foods)
mapping_counts = Counter(r["compound_id"] for r in mappings)
quant_mapping_ids = {r["compound_id"] for r in mappings if r["quantitative_data_available"].lower() == "true" and r["mapping_status"] in valid_statuses}
coverage_fields = ["Compound_ID", "Canonical_Name", "Identity_Audit_Status", "Any_Mapping", "Quantitative_Mapping", "Identity_Complete_Quantitative_Eligible", "Food_Record_Count", "Mapping_Row_Count", "Search_Log_Event_Count", "Coverage_Status", "Latest_Gap_Decision"]
coverage_rows = []
for compound in compound_registry:
    cid = compound["Compound_ID"]
    is_complete = cid in complete
    has_quant_mapping = cid in quant_mapping_ids
    if not is_complete:
        coverage_status = "Identity review pending; excluded from eligible coverage"
    elif has_quant_mapping:
        coverage_status = "Identity-complete quantitative coverage"
    else:
        coverage_status = "Identity-complete; no accepted quantitative measurement"
    gap = gap_by_id.get(cid, {})
    coverage_rows.append({
        "Compound_ID": cid,
        "Canonical_Name": compound["Canonical_Name"],
        "Identity_Audit_Status": "Complete" if is_complete else audit_by_id[cid]["Status"],
        "Any_Mapping": str(mapping_counts[cid] > 0).lower(),
        "Quantitative_Mapping": str(has_quant_mapping).lower(),
        "Identity_Complete_Quantitative_Eligible": str(is_complete and has_quant_mapping).lower(),
        "Food_Record_Count": food_counts[cid],
        "Mapping_Row_Count": mapping_counts[cid],
        "Search_Log_Event_Count": search_counts[cid],
        "Coverage_Status": coverage_status,
        "Latest_Gap_Decision": gap.get("Last_Decision", ""),
    })
with coverage_register_path.open("w", encoding="utf-8-sig", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=coverage_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(coverage_rows)
assert len(coverage_rows) == 143
assert sum(r["Identity_Complete_Quantitative_Eligible"] == "true" for r in coverage_rows) == 97
assert sum(r["Identity_Audit_Status"] != "Complete" for r in coverage_rows) == 36

delta_path = BATCH / "coverage_delta.json"
delta = json.loads(delta_path.read_text(encoding="utf-8"))
delta["current"] = {
    "stage_b_compounds": len(audit),
    "identity_complete": len(complete),
    "identity_pending": len(pending),
    "food_records": len(foods),
    "mapping_rows": len(mappings),
    "unique_compounds_any_mapping": len(any_mapped),
    "unique_compounds_with_quantitative_mapping_including_identity_pending": len(quant_ids),
    "identity_complete_quantitative_compounds": len(eligible),
    "identity_complete_uncovered": len(uncovered),
    "compounds_not_exposure_eligible": len(audit) - len(eligible),
    "pending_identity_mapping_rows": len(pending_rows),
    "pending_identity_compounds_with_mappings": len({r["compound_id"] for r in pending_rows}),
    "orphans": len(orphans),
    "food_sha256": digest(food_path),
    "mapping_sha256": digest(mapping_path),
}
delta["coverage_categories"].update({
    "pending_candidates": 4,
    "pending_identity_compounds": len(pending),
    "identity_complete_uncovered_compounds": len(uncovered),
    "identity_pending_compounds_with_mapping": len({r["compound_id"] for r in pending_rows}),
    "identity_pending_mapping_rows": len(pending_rows),
    "not_exposure_eligible_compounds": len(audit) - len(eligible),
})
delta["coverage_categories"].pop("no_accepted_quantitative_compounds", None)
delta["unresolved_complete_identity_ids"] = sorted(uncovered)
delta["limitations"] = [
    "Thirty-six Stage B identities remain pending and are outside Phase 1B identity adjudication.",
    "Ten identity-complete compounds remain without accepted quantitative ordinary-food measurements; all were screened to source-specific limits.",
    "At least 13 additional identity-complete quantitative compounds are needed for the >109 target; only 10 currently uncovered compounds are identity-complete, and pending identities require Stage B adjudication plus qualifying evidence.",
    "Cumulative qualitative-only and semiquantitative-only totals are not derivable from the available historical schemas and are not inferred.",
]
delta_path.write_text(json.dumps(delta, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

food_hash, mapping_hash = digest(food_path), digest(mapping_path)
baseline_food_hash = "aa15fd49be4afd30d1f61fe06de9039d0a925c22a6c56e970ddc75033b04f127"
baseline_mapping_hash = "9dcaadf0821aee15f1666ca26c88c592bb1e98a781eb533e246ddd94dab9ca97"
assert delta["baseline"]["food_sha256"] == baseline_food_hash
assert delta["baseline"]["mapping_sha256"] == baseline_mapping_hash
for path, expected_hash in ((food_path, baseline_food_hash), (mapping_path, baseline_mapping_hash)):
    first_512_lines = b"".join(path.read_bytes().splitlines(keepends=True)[:512])
    assert hashlib.sha256(first_512_lines).hexdigest() == expected_hash
rebuilt_mappings = rows(BATCH / "mapping_rebuild.csv")
assert mappings == rebuilt_mappings

note = f'''# Batch 101 — final eligible food screen

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

Batch 101 added seven previously unlogged search events. The cumulative search log has {len(search)} events across {len(search_ids)} of 143 IDs and includes all {len(complete)} identity-complete IDs. The other {len(set(r['Compound_ID'] for r in audit) - search_ids)} unlogged compounds are identity-pending and excluded from Phase 1B acquisition. The source registry has {len(source_registry)} entries. The central candidate register has {len(central_candidates)} rows. The gap register has {len(gap_rows)} rows, of which ten are identity-complete uncovered targets and three are retained identity-pending legacy entries.

## Validation and integrity

- Focused scientific/data validation: PASS; {len(foods)} records, {len(mappings)} mappings, zero food/mapping errors, zero orphans, zero Stage B snapshot changes.
- Identity-pending mapping rows recomputed by joining the live mapping file to the Stage B audit: {len(pending_rows)} rows across {len({r['compound_id'] for r in pending_rows})} compounds.
- Food SHA-256: `{food_hash}`
- Mapping SHA-256: `{mapping_hash}`
- Baseline food and mapping hashes in `coverage_delta.json` match the pre-append audit. Stage B and Phase 1-v1.3.0 were not modified.
- The first 511 data rows plus headers retain their exact baseline byte hashes. A regenerated mapping file matches all active mapping rows and row order; its whole-file hash differs only because it serializes the appended rows with CRLF line endings while the active append intentionally preserves the original CRLF prefix and uses LF for the 28 new rows.
- Historical Phase1B-v1.0.0 integrity limitations remain historical; no new Phase 1B release was created.

The >109 target remains **not achieved**. Phase 1B does not resolve Stage B identities; further progress past 107 identity-complete compounds depends on Stage B review and subsequent qualifying measurements.
'''
(BATCH / "SCREENING_NOTE.md").write_text(note, encoding="utf-8")

current_header = f'''## Current checkpoint — 2026-11-03

**Status: target not achieved; continuation checkpoint recorded.** Active coverage is **97/107 identity-complete compounds** from the 143-compound Stage B universe. The dataset contains **539 food records and 539 mappings**, with 113 unique compounds having a quantitative mapping, 36 Stage B identities pending, 16 of those mapped across 46 blocked rows, and zero orphans. Batch 101 added 28 accepted measurements across four new compounds. Ten identity-complete gaps remain. The >109 target would require 13 additional compounds, while Stage B currently has only 107 complete identities; Phase 1B cannot resolve that ceiling.

Source classes: {dict(source_classes)}. Food-use classes: {dict(food_uses)}. Identity-complete quantitative coverage counts only mapped quantitative records whose Stage B identity audit is complete; mapping rows for the 36 pending identities are excluded from that metric.

See `batches/batch_101_final_eligible_foodscreen/SCREENING_NOTE.md` for accepted values, held evidence, exact decisions, validation and current hashes. `coverage_delta.json` and `COMPOUND_COVERAGE_REGISTER_2026-11-03.csv` provide the machine-readable checkpoint and full compound universe. The earlier 119-target completion report and checkpoint are superseded by this 143-compound continuation report.
'''

coverage_text = f'''# Stage C Phase 1B Food Composition Coverage

{current_header}

## Current accepted expansion

Batch 101 appended 22 phloridzin apple peel/flesh values, one quercitrin apple-flesh value, one S-equol tofu aggregate, and four Sunset Yellow sports-drink values. Original source units, bases, variability and study limitations are retained. Four newly covered compounds increase identity-complete quantitative coverage from 93/107 to 97/107.

## Current gaps and interpretation

The ten identity-complete gaps are: Baicalein (MOL-V10-5281605), Baicalin (MOL-V10-64982), Scutellarein (MOL-V10-5281697), Wogonin (MOL-V10-5281703), Oroxylin A (MOL-V10-5320315), 7-Methoxyflavanone (MOL-V10-2825024), Wogonoside (MOL-V10-3084961), Apigetrin (MOL-V17-CID-5280704), Myricitrin (MOL-V17-CID-5281673), and Prunin (MOL-V17-CID-92794). Seven have prior bounded screenings that found no eligible ordinary-food result; three Batch 101 leads remain held for basis, conflicting-source, or inaccessible-table issues.

The 36 Stage B identity-pending compounds remain unresolved. Sixteen have 46 legacy mapping rows, which are excluded from identity-complete coverage and exposure eligibility. The maximum from the current complete identity set is 107; reaching 110 requires Stage B identity adjudication and qualifying measurements. No cooking-retention, recipe dilution, bioavailability, clinical-risk, or population-exposure calculations were added.

The complete 143-ID ledger is `COMPOUND_COVERAGE_REGISTER_2026-11-03.csv`. `COMPOUND_PRIORITY_REGISTER.csv` remains the historical 119-ID priority assessment; the additional 24 IDs were not assigned speculative priority scores.

Historical Phase1B-v1.0.0 package limitations remain documented and unchanged. No new release package was created.
'''
(PHASE / "FOOD_COMPOSITION_COVERAGE_REPORT.md").write_text(coverage_text, encoding="utf-8")

accepted_report = f'''# Accepted and Held Record Report — current checkpoint (2026-11-03)

Batch 101 added 28 accepted ordinary-food records and mappings, covering four new identity-complete compounds. The active files now contain 539 records and mappings. Coverage is 97/107 identity-complete Stage B compounds; 113 unique compounds have quantitative mappings when identity-pending mappings are included, but those 36 pending identities are excluded from the eligible metric. Sixteen pending compounds have 46 legacy mapping rows. There are zero orphan mappings.

Accepted sources: phloridzin in 11 apple cultivars (22 peel/flesh rows; µg/g fresh weight); quercitrin in Galaval apple flesh on G.11 rootstock (148 ± 18 µg/g dry weight); S-equol in commercial stinky tofu (1.2 ± 1.0 mg/100 g wet weight; n=138); and Sunset Yellow FCF in four retail sports drinks (mg/L, no density conversion). See `batches/batch_101_final_eligible_foodscreen/SCREENING_NOTE.md` and `accepted_rows.csv` for the full evidence.

Held findings remain outside active composition: apigetrin basis/graph uncertainty; myricitrin unstated basis and conflicting text; prunin abstract without numeric table; and 22 green-coffee quercitrin values following potentially transformative acidic extraction. They are preserved in the candidate ledger and `rejected_candidates.csv` with source locators and reasons. Missing values remain missing.

All Stage B identity-pending mapping rows remain blocked from identity-complete coverage. The >109 target is not achieved; the current identity-complete universe has a ceiling of 107 without Stage B adjudication. No new Phase 1B release was packaged.
'''
(PHASE / "ACCEPTED_REJECTED_RECORD_REPORT.md").write_text(accepted_report, encoding="utf-8")

mapping_report = f'''# Mapping Coverage — current checkpoint (2026-11-03)

The current Stage B universe has {len(audit)} compounds. Active files contain {len(foods)} food-composition records and {len(mappings)} mapping rows. There are {len(any_mapped)} compounds with any quantitative mapping, of which {len(eligible)} are identity-complete and eligible for Phase 1 exposure calculations. Ten of 107 identity-complete compounds remain uncovered. Mapping rebuild validation finds zero ambiguous, unmatched, rejected or orphan records.

Identity review remains pending for {len(pending)} compounds. Sixteen of these have {len(pending_rows)} legacy mapping rows; all are excluded from identity-complete eligibility even where the mapping row has an exact or structure-supported label. See `COMPOUND_COVERAGE_REGISTER_2026-11-03.csv` for all 143 IDs and `batches/batch_101_final_eligible_foodscreen/SCREENING_NOTE.md` for Batch 101 evidence and limits.
'''
(PHASE / "MAPPING_COVERAGE_REPORT.md").write_text(mapping_report, encoding="utf-8")

priority_report = f'''# Compound priority and coverage universe — current checkpoint (2026-11-03)

The authoritative current universe is the 143-compound Stage B registry. `COMPOUND_COVERAGE_REGISTER_2026-11-03.csv` reconciles every ID to its identity-audit status, mapped/quantitative record counts, search-log event count, and current coverage disposition. Current identity-complete quantitative coverage is {len(eligible)}/{len(complete)}; {len(uncovered)} complete identities remain uncovered and {len(pending)} identities remain pending.

`COMPOUND_PRIORITY_REGISTER.csv` is a historical 119-ID priority assessment (priority counts 7 P1, 13 P2, 84 P3, 15 P4). It omits 24 compounds added to the authoritative Stage B universe, including seven complete V17 IDs and 17 identity-pending IDs. This continuation did not assign new priority scores without a separate, documented priority review; the historical register is not used as the current coverage denominator.
'''
(PHASE / "COMPOUND_PRIORITY_REPORT.md").write_text(priority_report, encoding="utf-8")

resume = f'''# Resume instructions — Phase 1B checkpoint (2026-11-03)

The Batch 101 continuation is complete and checkpointed. Start with `CHECKPOINTS.json`, `NEXT_STEPS.md`, `FOOD_COMPOSITION_COVERAGE_REPORT.md`, `COMPOUND_COVERAGE_REGISTER_2026-11-03.csv`, and `batches/batch_101_final_eligible_foodscreen/SCREENING_NOTE.md`.

The active data contains 539 food records and mappings, with 97/107 identity-complete compounds covered, 36 identities pending, 16 pending-identity compounds represented by 46 blocked legacy mapping rows, and zero orphans. All 107 identity-complete IDs have a logged search event. Ten identity-complete gaps remain and have source-specific bounded dispositions. The >109 target remains unmet; Phase 1B must not adjudicate Stage B identities.

Batch 101 added 28 source-backed records and mappings across four newly covered compounds. The first 511 rows retain the audited baseline hashes. Historical `Phase1B-v1.0.0` package limitations and the 119-ID priority register remain historical and were not repaired or repackaged. Continue only if new primary numeric tables, official quantitative datasets, or Stage B identity adjudications arrive; preserve the explicit holds and do not proceed to Phase 2.
'''
(PHASE / "RESUME_INSTRUCTIONS.md").write_text(resume, encoding="utf-8")

source_report_path = PHASE / "SOURCE_VERIFICATION_REPORT.md"
source_report = source_report_path.read_text(encoding="utf-8")
historic_source_marker = "## Current dataset source audit"
historic_batch100_marker = "Batch 100 was independently reconciled"
current_source_marker = "# Current dataset source audit — 2026-11-03"
if current_source_marker in source_report and "\n---\n\n" in source_report:
    historic_text = source_report.split("\n---\n\n", 1)[1]
else:
    source_prefix = source_report.split(historic_source_marker, 1)[0]
    batch100_text = ""
    if historic_source_marker in source_report and historic_batch100_marker in source_report:
        batch100_text = historic_batch100_marker + source_report.split(historic_batch100_marker, 1)[1]
    historic_text = source_prefix + ("\n\n" + batch100_text if batch100_text else "")
source_current = f'''# Current dataset source audit — 2026-11-03

The active dataset has {len(foods)} accepted records spanning {distinct_sources} distinct source-title/URL pairs. All records have source URL, title, explicit value and unit, basis description, analytical method and verification status ({missing_core_source_fields} missing required source fields). {rows_without_doi_and_pmid} records have neither DOI nor PMID; their source title/URL and dataset/table locator remain available. Source-class counts are {dict(source_classes)}. Batch 101's four accepted source articles and five held-source leads are documented in the active source registry and its screening note. The 28 new records retain source denominators and uncertainty; no moisture or density conversion was inferred.

The prior dated batch-level source notes below are historical verification records. The Batch 100 context findings remain separate from ordinary-food measurements.
'''
source_report_path.write_text(source_current + "\n---\n\n" + historic_text, encoding="utf-8")

search_report = PHASE / "SEARCH_COVERAGE_REPORT.md"
old_search = search_report.read_text(encoding="utf-8")
marker = "# Current search coverage — 2026-11-03"
if marker not in old_search:
    top = f'''{marker}

The cumulative log contains **{len(search)} source/compound events** across **{len(search_ids)}/143 Stage B IDs**, including all **{len(complete)} identity-complete IDs**. The {143-len(search_ids)} unlogged IDs are all identity-pending, not eligible for Phase 1B source acquisition until Stage B review. Batch 101 added seven events for newly logged identity-complete targets. Search logs document bounded screening and do not establish exhaustive absence.

Current Batch 101 dispositions and evidence are in `batches/batch_101_final_eligible_foodscreen/SCREENING_NOTE.md`. The dated entries below are the historical screening log through Batch 100 and remain useful as provenance; their former 119-target totals are superseded by the current summary above.

---

'''
    search_report.write_text(top + old_search, encoding="utf-8")

completion_report = PHASE / "PHASE1B_COMPLETION_REPORT.md"
old_completion = completion_report.read_text(encoding="utf-8")
marker = "## Current continuation status — 2026-11-03"
if marker not in old_completion:
    banner = f'''# Historical report notice — superseded for current Stage B universe

This document records the earlier 119-target Phase 1B completion state and historical `Phase1B-v1.0.0` release. Its completion decision and counts do **not** describe the current 143-compound continuation. The current authoritative checkpoint is `batches/batch_101_final_eligible_foodscreen/SCREENING_NOTE.md` and `FOOD_COMPOSITION_COVERAGE_REPORT.md`.

{marker}

The active dataset now contains 539 food records and 539 mappings, covering 97/107 identity-complete compounds in the 143-compound Stage B universe. Batch 101 contributed 28 records and four new covered compounds. Ten identity-complete gaps remain; 36 identities are pending, including 16 compounds with 46 blocked legacy mappings. The requested >109 target was not achieved and cannot be reached without Stage B identity adjudication followed by further qualifying measurements. Historical release files were not changed and no new release package was created.

---

'''
    completion_report.write_text(banner + old_completion, encoding="utf-8")

next_steps = f'''# Next steps — Phase 1B checkpoint (2026-11-03)

The bounded Batch 101 continuation is complete. Current active data: 539 food records and mappings; 113 unique compounds have quantitative mappings including identity-pending mappings; 97/107 identity-complete compounds are eligible, with 10 complete-identity gaps still open. Thirty-six Stage B identities remain pending, including 16 mapped compounds with 46 blocked rows. There are zero orphan mappings.

The >109 target was not achieved. The current identity-complete ceiling is 107, so progressing toward 110 requires Stage B identity adjudication for at least three additional compounds, followed by qualifying quantitative ordinary-food evidence. Phase 1B must not perform that identity adjudication. Ten currently complete-identity gaps have bounded source dispositions; their exact IDs and next evidence requirements are in `FOOD_COMPOSITION_COVERAGE_REPORT.md` and `coverage_gap_register.csv`.

Continue only if new primary-source tables, official composition data, or Stage B identity adjudications become available. Do not convert held apigetrin, myricitrin, prunin, or acid-extracted green-coffee quercitrin candidates into accepted values without resolving their stated evidence limitations. Do not calculate exposure, cooking retention, recipe dilution, bioavailability, or clinical risk in this continuation. No new Phase 1B release was created.
'''
(PHASE / "NEXT_STEPS.md").write_text(next_steps, encoding="utf-8")

progress_path = PHASE / "PROGRESS.md"
old_progress = progress_path.read_text(encoding="utf-8")
progress_marker = "## Current authoritative checkpoint — 2026-11-03"
if progress_marker not in old_progress:
    progress = f'''{progress_marker}

- **Completed:** baseline rechecked; Batch 101 source screening; 28 accepted rows and mappings for phloridzin, quercitrin, S-equol and Sunset Yellow FCF; 9 source-registry entries; 7 new search events; 4 candidate-ledger entries; 26 held/rejected detail rows; gap-register reconciliation; current coverage checkpoint and report.
- **Current coverage:** 539 food records / 539 mappings; 113 compounds with any quantitative mapping; 97/107 identity-complete compounds covered; 36 identity-pending compounds, 16 of them with 46 legacy mappings; 10 eligible gaps; zero orphans.
- **Target:** >109 identity-complete compounds not achieved. Only 107 identities are complete; additional progress requires Stage B adjudication and qualifying evidence. Ten currently eligible gaps were screened within source-specific limits.
- **Validation/tests:** Phase 1 validation PASS (539/539 records/mappings, zero food or mapping errors, zero orphans, no Stage B snapshot changes); focused tests PASS (24/24: food composition, mapping and Batch 101 regressions). Mapping rebuild comparison and final integrity checks are recorded in `SCREENING_NOTE.md`.
- **Remaining:** preserve open scientific limitations; revisit only when numeric tables, valid measurement bases, or Stage B identity adjudications become available. No Phase 1B release was produced.

Entries below this checkpoint are time-stamped historical progress notes and may describe the earlier 119-target project state; this checkpoint is authoritative for the 143-compound universe.

---

'''
    progress_path.write_text(progress + old_progress, encoding="utf-8")

checkpoint = {
    "checkpoint_id": "Phase1B-2026-11-03-batch-101-final-continuation",
    "status": "CONTINUATION_COMPLETE_WITH_DOCUMENTED_LIMITATIONS_TARGET_NOT_MET",
    "scope": "Stage C Phase 1B only",
    "previous_checkpoint_preserved_as": "CHECKPOINTS_HISTORICAL_PRE_BATCH_EXPANSION.json",
    "last_batch": "batch_101_final_eligible_foodscreen",
    "source_stage_b_release": "StageB_FINALIZED (read-only)",
    "phase1_foundation_dependency": "stageC/releases/Phase1-v1.3.0 (read-only)",
    "stage_b_target_count": len(audit),
    "stage_b_identity_complete": len(complete),
    "stage_b_identity_pending": len(pending),
    "active_food_records": len(foods),
    "active_mapping_rows": len(mappings),
    "unique_compounds_any_mapping": len(any_mapped),
    "unique_compounds_with_quantitative_mapping_including_identity_pending": len(quant_ids),
    "identity_complete_quantitative_compounds": len(eligible),
    "identity_complete_compounds_uncovered": len(uncovered),
    "identity_pending_compounds_with_mapping": len({r["compound_id"] for r in pending_rows}),
    "mapping_rows_blocked_by_identity_review": len(pending_rows),
    "orphan_mappings": len(orphans),
    "batch_101": {
        "accepted_food_records": len(batch_accepted),
        "accepted_mappings": len(batch_accepted),
        "new_unique_identity_complete_compounds": 4,
        "new_search_events": 7,
        "new_source_registry_entries": 9,
        "central_candidate_entries": 4,
        "held_or_rejected_candidate_details": len(batch_rejected),
    },
    "search_log_events": len(search),
    "search_log_ids": len(search_ids),
    "identity_complete_ids_with_search_event": len(complete & search_ids),
    "source_registry_entries": len(source_registry),
    "central_candidate_register_rows": len(central_candidates),
    "coverage_gap_register_rows": len(gap_rows),
    "current_143_compound_coverage_register_rows": len(coverage_rows),
    "target": {"criterion": ">109 identity-complete quantitative compounds", "achieved": False, "current_identity_ceiling_without_stage_b_review": len(complete), "additional_compounds_needed_to_reach_110": max(0, 110-len(eligible))},
    "validation": {"phase1_validation": "PASS", "food_records_checked": len(foods), "mapping_rows_checked": len(mappings), "food_errors": 0, "mapping_errors": 0, "orphans": 0, "snapshot_changes": 0, "focused_tests": "24/24 PASS", "coverage_register": "143 IDs; 107 complete; 97 eligible; 36 pending", "mapping_rebuild": "row-for-row and order match; whole-file newline serialization differs", "baseline_prefix_hashes": "PASS"},
    "sha256": {"food_composition": food_hash, "compound_food_mapping": mapping_hash},
    "reports": ["FINAL_CONTINUATION_BASELINE_AUDIT_2026-11-03.md", "COMPOUND_COVERAGE_REGISTER_2026-11-03.csv", "batches/batch_101_final_eligible_foodscreen/SCREENING_NOTE.md", "batches/batch_101_final_eligible_foodscreen/coverage_delta.json", "FOOD_COMPOSITION_COVERAGE_REPORT.md", "MAPPING_COVERAGE_REPORT.md", "SEARCH_COVERAGE_REPORT.md", "SOURCE_VERIFICATION_REPORT.md", "COMPOUND_PRIORITY_REPORT.md", "NEXT_STEPS.md", "RESUME_INSTRUCTIONS.md"],
    "limitations": delta["limitations"],
    "new_release_created": False,
}
(PHASE / "CHECKPOINTS.json").write_text(json.dumps(checkpoint, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

print(json.dumps({
    "identity_complete_coverage": f"{len(eligible)}/{len(complete)}",
    "identity_pending_compounds": len(pending),
    "pending_identity_mapping_rows": len(pending_rows),
    "orphans": len(orphans),
    "search_events": len(search),
    "identity_complete_ids_logged": len(complete & search_ids),
    "food_hash": food_hash,
    "mapping_hash": mapping_hash,
    "reports_updated": 14,
}, indent=2))
