"""Record the final focused re-audit of the eight remaining complete-identity gaps."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
STAGE = ROOT / "stageC"
P = STAGE / "reports" / "phase1b"
B = P / "batches" / "batch_104_eligible_gap_reaudit"
CHECKPOINT = P / "CHECKPOINTS.json"
SEARCH = P / "SEARCH_LOG.csv"
SOURCES = STAGE / "data" / "food_composition" / "source_registry.csv"
COVERAGE = P / "COMPOUND_COVERAGE_REGISTER_2026-11-03.csv"
GAPS = P / "coverage_gap_register.csv"
FOOD = STAGE / "data" / "food_composition" / "food_composition.csv"
MAPPING = STAGE / "data" / "compound_food_mapping" / "compound_food_mapping.csv"

def read(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def write(path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

TARGETS = [
    ("MOL-V10-5281605", "Baicalein", "Scutellaria baicalensis food ingredient Huangqin tea baicalein exact quantitative HPLC aerial parts ordinary beverage source table", "Huangqin tea is a traditional beverage, but accessible quantitative studies located in this pass measured medicinal roots, tinctures, or extracts; the tea-oriented HPLC table was not accessible for exact sample values.", "Obtain the full sample-level HPLC table and verify aerial-part food preparation, edible basis, analyte identity, and calibration before promotion."),
    ("MOL-V10-64982", "Baicalin", "Baicalin quantitative concentration Huangqin tea infusion ordinary beverage primary HPLC sample table", "A 2026 widely-targeted HQT study reports comparatively higher baicalin in tender-leaf NenYe tea, but accessible abstract text gives no sample-level calibrated concentration and says study data are available on request. A 2023 review is a lead only; its underlying primary matrix and denominator were not independently verified. Medicinal-root and isolated-flavonoid values are out of scope.", "Obtain the 2026 study's full methods and target-specific data plus the underlying source behind the review; confirm standards, sample form, and denominator before any promotion."),
    ("MOL-V10-5281697", "Scutellarein", "Scutellarein Huangqin tea aerial parts quantitative food ingredient HPLC concentration exact analyte", "The tea source literature confirms flavonoid profiling, but no accessible primary sample-level quantitative value for exact scutellarein in an ordinary-food tea sample was verified. Related medicinal-root evidence is not transferable.", "Obtain the complete tea-part HPLC table and confirm the exact analyte is scutellarein rather than a glucuronide or other isomer."),
    ("MOL-V10-5281703", "Wogonin", "Wogonin Huangqin tea beverage aerial parts quantitative concentration HPLC primary source table", "Accessible numeric reports located in this pass were for medicinal roots or medicinal tinctures. The primary tea-oriented plant-part table was not accessible for exact values and food-denominator review.", "Obtain the primary tea table and establish dry ingredient versus brewed beverage basis; do not transfer tincture/root concentrations."),
    ("MOL-V10-5320315", "Oroxylin A", "Oroxylin A Huangqin tea ordinary food ingredient concentration HPLC aerial parts primary study", "The accessible exact-analyte numeric literature concerned medicinal Scutellaria roots/extracts. A tea-part study is a relevant lead, but its numeric results were not accessible for verification.", "Retrieve the source table and verify the measured tissue, food use, calibration, and dry/fresh denominator."),
    ("MOL-V10-2825024", "7-Methoxyflavanone", "7-Methoxyflavanone exact PubChem CID 2825024 natural food occurrence quantitative food concentration", "No qualifying ordinary-food occurrence or concentration was identified. Reports for hydroxylated or differently methoxylated Scutellaria flavanones are different structures and cannot be substituted for this Stage B identity.", "Require an exact-structure food occurrence and calibrated concentration source; do not infer from similarly named methoxyflavanones."),
    ("MOL-V10-3084961", "Wogonoside", "Wogonoside Huangqin tea aerial parts ordinary beverage concentration HPLC exact numeric", "A 2026 widely-targeted HQT study reports comparatively higher wogonoside in tender-leaf NenYe tea, but accessible abstract text gives no sample-level calibrated concentration and says study data are available on request. Earlier tea profiling provides a further source lead; medicinal-root, extract, and enriched-fraction measurements are not eligible substitutes.", "Obtain the 2026 study's full methods and target-specific data; verify analyte identity, tea sample form, calibration, and denominator before any promotion."),
    ("MOL-V17-CID-92794", "Prunin", "Prunin citrus food peel quantitative concentration targeted calibrated HPLC mg/kg", "A 1993 primary article explicitly studies quantitative distribution in immature citrus, but its numeric table is paywalled. Newer citrus peel papers identify prunin using untargeted/relative metabolomics and provide no calibrated absolute food concentration for this exact Stage B analyte.", "Obtain the 1993 primary table or a targeted standard-calibrated food-composition study; keep concentration blank until then."),
]

SOURCES_TO_ADD = [
    ("Simultaneous determination of 15 flavonoids from different parts of Scutellaria baicalensis and its chemometrics analysis", "Primary analytical measurement", "https://doi.org/10.1016/j.chmed.2018.09.005", "HPLC-DAD of roots, stems, leaves, and flowers; relevant Huangqin-tea raw-material lead", "Publisher abstract accessible; primary sample-level numerical tables unavailable in accessible text", "Do not use abstract ranks or secondary transcriptions as food concentrations; retrieve the table and confirm the exact tea matrix and denominator."),
    ("The chemopreventive effects of Huangqin-tea against AOM-induced preneoplastic colonic aberrant crypt foci in rats and omics analysis", "Primary food/beverage study", "https://pubmed.ncbi.nlm.nih.gov/33048099/", "Huangqin-tea is described as a beverage prepared from aerial parts of Scutellaria baicalensis", "Primary abstract accessible; no target-specific food concentration in accessible abstract", "The beverage context is relevant, but animal dose/extract context is not a food concentration."),
    ("Huangqin Tea Total Flavonoids–Gut Microbiota Interactions: Based on Metabolome and Microbiome Analysis", "Primary analytical measurement", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10742805/", "HPLC of a total-flavonoid fraction; baicalin is reported per gram of isolated fraction", "Full text accessible; measured enriched fraction, not ordinary tea or source-food composition", "Do not map a purified/enriched fraction concentration to tea or ingredient content."),
    ("Pharmacophylogenetic study of Scutellaria baicalensis and its substitute medicinal species based on the chloroplast genomics, metabolomics, and active ingredient", "Primary medicinal-botanical analysis", "https://pmc.ncbi.nlm.nih.gov/articles/PMC9433114/", "HPLC and metabolomics of medicinal Scutellaria species/parts", "Full text accessible; article frames roots as materia medica and substitutes as medicinal species", "Keep medicinal material results outside ordinary-food coverage."),
    ("Growth years and post-harvest processing methods have critical roles on the contents of medicinal active ingredients of Scutellaria baicalensis", "Primary medicinal-botanical analysis", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7604031/", "HPLC of processed medicinal roots", "Full text accessible; expressly medicinal root processing", "Do not transfer medicinal-root composition into food records."),
    ("Validation of a HPLC method for flavonoid biomarkers in skullcap (Scutellaria) and its use to illustrate wide variability in the quality of commercial tinctures", "Primary medicinal-product analysis", "https://pubmed.ncbi.nlm.nih.gov/18445366/", "Quantitative baicalin, baicalein, and wogonin in commercial medicinal tinctures", "Primary abstract accessible; tinctures explicitly used by herbal practitioners for treatment", "Tincture concentrations are medicinal-product values and are out of food scope."),
    ("The gap-free genome and multi-omics analysis of Citrus reticulata ‘Chachi’ reveal the dynamics of fruit flavonoid biosynthesis", "Primary untargeted metabolomics", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11301317/", "Prunin identified in immature fruit peel across developmental stages", "Full text accessible; untargeted peak-area/normalized metabolomics, no absolute calibrated prunin concentration", "Retain occurrence evidence only; do not normalize or convert relative signals into mass concentration."),
    ("Analysis of Flavonoid Metabolites in Citrus Peels (Citrus reticulata ‘Dahongpao’) Using UPLC-ESI-MS/MS", "Primary untargeted metabolomics", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6696472/", "Prunin identified in citrus peel metabolite profile", "Full text accessible; profiling/identification result, no qualifying absolute prunin concentration", "Qualitative occurrence does not meet the quantitative concentration gate."),
    ("Hesperetin 7-O-glucoside and prunin in Citrus species (C. aurantium and C. paradisi): quantitative distribution in immature fruits", "Primary analytical measurement", "https://doi.org/10.1021/jf00035a021", "Primary article title and abstract describe quantitative distribution of prunin in immature citrus", "ACS landing/first-page metadata accessible; numeric results require article purchase or author-provided full text", "Do not transcribe a number until the original table, sample unit, and denominator can be inspected."),
    ("7-Methoxyflavanone, CID 2825024", "Chemical identity reference", "https://pubchem.ncbi.nlm.nih.gov/compound/2825024", "Exact identity reference used to distinguish target from hydroxylated methoxyflavanones", "Identifier page accessible; not a food-composition source", "Use only to prevent structural-name conflation; it does not establish food occurrence."),
    ("Widely targeted metabolomics analysis reveals effects of raw material parts, harvest season, and processing technology of Huangqin (Scutellaria baicalensis Georgi) tea", "Primary comparative metabolomics study", "https://doi.org/10.1016/j.lwt.2026.119022", "Six HQT types; abstract reports comparatively higher baicalin and wogonoside in tender-leaf NenYe tea", "Publisher abstract accessible; no sample-level calibrated values in accessible text; data available from corresponding author on reasonable request", "Keep as in-scope comparative occurrence/lead only. Obtain full methods and target data; do not convert relative/comparative metabolomics into absolute food concentrations."),
    ("A comprehensive review of Huangqin (Scutellaria baicalensis Georgi) tea: chemical composition, functional properties and safety aspects", "Secondary review / source lead", "https://doi.org/10.48130/BPR-2023-0031", "Review of Huangqin-tea composition; secondary lead for baicalin references", "Review accessible as a bibliographic lead; primary data matrix and denominator have not been independently reconciled", "Use only to locate primary tea measurements; do not accept a secondary-transcribed number as a food-composition record."),
]

FOLLOWUP_SEARCHES = [
    ("MOL-V10-64982", "Baicalin", "2026 Huangqin tea widely targeted metabolomics baicalin sample-level standard calibration concentration NenYe", "2026 primary study abstract reports comparative higher baicalin in NenYe tea; no accessible numeric sample-level calibrated concentration; underlying data are available on request."),
    ("MOL-V10-3084961", "Wogonoside", "2026 Huangqin tea widely targeted metabolomics wogonoside sample-level standard calibration concentration NenYe", "2026 primary study abstract reports comparative higher wogonoside in NenYe tea; no accessible numeric sample-level calibrated concentration; underlying data are available on request."),
]
PREEXISTING_REVIEW_URLS = {"https://doi.org/10.48130/BPR-2023-0031"}

def main():
    cp = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    if cp.get("checkpoint_id") != "Phase1B-2026-11-03-batch-103-all-143-screened":
        raise RuntimeError("Unexpected checkpoint; re-audit aborted.")
    foods, maps = read(FOOD), read(MAPPING)
    if (len(foods), len(maps), cp.get("identity_complete_quantitative_compounds")) != (541, 541, 99):
        raise RuntimeError("Active dataset changed; re-audit aborted without data edits.")
    B.mkdir(parents=True, exist_ok=True)

    audit = {r["Compound_ID"]: r for r in read(STAGE / "data/stage_b_snapshot_20261103/identity_structure_audit.csv")}
    gap_ids = {r["Compound_ID"] for r in read(COVERAGE) if r["Identity_Audit_Status"] == "Complete" and r["Identity_Complete_Quantitative_Eligible"] != "true"}
    if gap_ids != {r[0] for r in TARGETS}:
        raise RuntimeError(f"Expected current eight eligible gaps; found {sorted(gap_ids)}")

    search = read(SEARCH)
    fields = list(search[0])
    existing = {(r["Compound_ID"], r["search_query"]) for r in search}
    new_events = []
    for cid, name, query, limitation, action in TARGETS:
        if (cid, query) not in existing:
            new_events.append({
                "Compound_ID": cid,
                "canonical_name": name,
                "search_query": query,
                "database_or_search_source": "Primary-source and exact-food-context re-audit; see Batch 104 evidence assessment",
                "search_date": "2026-11-03",
                "results_identified": limitation,
                "candidate_publications": "See batches/batch_104_eligible_gap_reaudit/source_assessment.csv",
                "screening_decision": "NO_NEW_QUALIFYING_MEASUREMENT",
                "reason": limitation + " " + action,
            })
    for cid, name, query, result in FOLLOWUP_SEARCHES:
        if (cid, query) not in existing:
            new_events.append({
                "Compound_ID": cid,
                "canonical_name": name,
                "search_query": query,
                "database_or_search_source": "Primary-source follow-up; publisher abstract and DOI metadata, see Batch 104 source assessment",
                "search_date": "2026-11-03",
                "results_identified": result,
                "candidate_publications": "See batches/batch_104_eligible_gap_reaudit/source_assessment.csv",
                "screening_decision": "NO_NEW_QUALIFYING_MEASUREMENT",
                "reason": "Comparative metabolomics does not establish a traceable absolute concentration without accessible target-specific values, calibration, and denominator; preserve as a follow-up lead.",
            })
    with SEARCH.open("a", encoding="utf-8", newline="") as f:
        csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\r\n").writerows(new_events)

    sources = read(SOURCES)
    source_fields = list(sources[0])
    known_urls = {r["source_url"] for r in sources}
    new_sources = []
    for name, classification, url, source_type, availability, requirement in SOURCES_TO_ADD:
        if url not in known_urls:
            new_sources.append({"source_name": name, "source_classification": classification, "source_url": url, "source_type": source_type, "availability_status": availability, "ingestion_requirement": requirement})
            known_urls.add(url)
    write(SOURCES, source_fields, sources + new_sources)

    matrix = []
    assessments = []
    for cid, name, query, limitation, action in TARGETS:
        matrix.append({"Compound_ID": cid, "Canonical_Name": name, "Identity_Status": audit[cid]["Status"], "New_Search_Query": query, "Screening_Result": limitation, "New_Quantitative_Candidates": 0, "Accepted_Record_Change": "none", "Decision": "NO_NEW_QUALIFYING_MEASUREMENT", "Limitation": limitation, "Next_Action": action})
    for index, (name, classification, url, source_type, availability, requirement) in enumerate(SOURCES_TO_ADD):
        targets = [
            "Scutellaria target gaps; possible analytes in part-specific HPLC table, but exact table rows remain unverified",
            "Scutellaria target gaps; establishes Huangqin-tea beverage context only",
            "Baicalin; enriched total-flavonoid fraction only",
            "Scutellaria medicinal-composition context; no food transfer permitted; analyte rows require source-specific verification",
            "Scutellaria medicinal-composition context; no food transfer permitted; analyte rows require source-specific verification",
            "Baicalein; Baicalin; Wogonin; medicinal tinctures only",
            "Prunin; untargeted/relative citrus-peel profiling",
            "Prunin; untargeted/relative citrus-peel profiling",
            "Prunin; primary quantitative paper, numeric table inaccessible",
            "7-Methoxyflavanone identity only; no food-occurrence evidence",
            "Baicalin; Wogonoside; in-scope tea comparison, no absolute calibrated values accessible",
            "Baicalin source lead only; primary matrix/denominator not independently verified",
        ][index]
        assessments.append({"Source_Title": name, "Source_Classification": classification, "Source_URL": url, "Relevant_Targets": targets, "Access_and_Matrix_Assessment": availability, "Scientific_Decision": requirement})
    write(B / "screening_matrix.csv", list(matrix[0]), matrix)
    write(B / "source_assessment.csv", list(assessments[0]), assessments)

    coverage = read(COVERAGE)
    refs_by_target = {
        "MOL-V10-5281605": [SOURCES_TO_ADD[i][2] for i in (0, 1, 2, 3, 4, 5)],
        "MOL-V10-64982": [SOURCES_TO_ADD[i][2] for i in (0, 1, 2, 3, 4, 5, 10, 11)],
        "MOL-V10-5281697": [SOURCES_TO_ADD[i][2] for i in (0, 1, 3, 4)],
        "MOL-V10-5281703": [SOURCES_TO_ADD[i][2] for i in (0, 1, 3, 4, 5)],
        "MOL-V10-5320315": [SOURCES_TO_ADD[i][2] for i in (0, 1, 3, 4)],
        "MOL-V10-2825024": [SOURCES_TO_ADD[9][2]],
        "MOL-V10-3084961": [SOURCES_TO_ADD[i][2] for i in (0, 1, 3, 4, 10, 11)],
        "MOL-V17-CID-92794": [SOURCES_TO_ADD[i][2] for i in (6, 7, 8)],
    }
    lookup = {r[0]: r for r in TARGETS}
    for row in coverage:
        if row["Compound_ID"] not in gap_ids:
            continue
        cid, name, query, limitation, action = lookup[row["Compound_ID"]]
        row["Relevant_Source_References"] = "; ".join(dict.fromkeys(filter(None, [row["Relevant_Source_References"], *refs_by_target[row["Compound_ID"]]])))
        row["Pending_Issues"] = limitation
        row["Next_Justified_Action"] = action
        row["Food_Composition_Evidence_Status"] = "Relevant literature lead reviewed; no qualifying absolute food concentration verified"
        row["Accepted_Quantitative_Coverage_Status"] = "Not covered"
    write(COVERAGE, list(coverage[0]), coverage)

    gap_register = read(GAPS)
    gap_fields = list(gap_register[0])
    for row in gap_register:
        if row["Compound_ID"] not in gap_ids:
            continue
        _, _, _, limitation, action = lookup[row["Compound_ID"]]
        if row["Last_Screen_Batch"] != "batch_104_eligible_gap_reaudit":
            row["Prior_Screen_Count"] = str(int(row["Prior_Screen_Count"]) + 1)
        row["Last_Screen_Batch"] = "batch_104_eligible_gap_reaudit"
        row["Last_Decision"] = "NO_NEW_QUALIFYING_MEASUREMENT; FOLLOW_UP_LEADS_RECORDED"
        row["Next_Action"] = limitation + " " + action
        if row["Compound_ID"] == "MOL-V10-2825024":
            row["Food_Context"] = "Exact 7-Methoxyflavanone food occurrence not established; similarly named flavanones are not equivalent"
        elif row["Compound_ID"] == "MOL-V17-CID-92794":
            row["Food_Context"] = "Immature citrus fruit peel is a qualitative/untargeted lead; no calibrated absolute prunin concentration verified"
        else:
            row["Food_Context"] = "Huangqin tea made from Scutellaria aerial parts is a relevant beverage lead; accessible sample-level target values remain unverified; root/tincture data are medicinal"
    write(GAPS, gap_fields, gap_register)

    current_search = read(SEARCH)
    batch_queries = {(cid, query) for cid, _, query, _, _ in TARGETS} | {(cid, query) for cid, _, query, _ in FOLLOWUP_SEARCHES}
    batch_search_events = sum((r["Compound_ID"], r["search_query"]) in batch_queries for r in current_search)
    current_coverage = read(COVERAGE)
    checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    checkpoint["search_log_events"] = len(current_search)
    batch_source_urls = {r[2] for r in SOURCES_TO_ADD}
    source_urls_present = {r["source_url"] for r in read(SOURCES)}
    batch_source_rows_added = len((batch_source_urls - PREEXISTING_REVIEW_URLS) & source_urls_present)
    checkpoint["batch_104"] = {"eligible_complete_gaps_reviewed": 8, "new_search_events": batch_search_events, "new_source_registry_entries": batch_source_rows_added, "source_assessments": len(batch_source_urls), "accepted_records": 0, "accepted_mappings": 0, "new_quantitative_candidates": 0, "identity_complete_quantitative_compounds": 99, "identity_complete_gaps_remaining": 8, "status": "NO_NEW_QUALIFYING_MEASUREMENT"}
    checkpoint["final_acquisition_state"] = "all 143 Stage B IDs screened; the remaining eight identity-complete gaps received a source-specific re-audit with no qualifying new quantitative ordinary-food measurement; evidence leads and access limitations are recorded; target remains unmet; no release created."
    CHECKPOINT.write_text(json.dumps(checkpoint, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = """# Batch 104 — focused re-audit of the eight eligible gaps

**Decision:** no new qualifying quantitative food-composition measurements were added. The active dataset remains unchanged at 541 food records and 541 mappings, with 99/107 identity-complete compounds covered and eight eligible gaps.

## Scope and findings

This re-audit targeted Baicalein, Baicalin, Scutellarein, Wogonin, Oroxylin A, 7-Methoxyflavanone, Wogonoside, and Prunin. It follows the earlier Batch 099 review and accounts for the new evidence leads surfaced by the final continuation.

- Huangqin tea is a traditional non-Camellia beverage made from aerial Scutellaria parts, so tea-specific evidence is potentially in scope. A 2026 primary widely-targeted metabolomics study of six HQT types reports comparatively higher baicalin and wogonoside in tender-leaf NenYe tea. The accessible abstract gives no sample-level calibrated concentrations; the study says supporting data are available from the corresponding author on request. This is an in-scope comparative occurrence lead, not an accepted quantitative food value. A primary HPLC-DAD study of Scutellaria parts and a primary Huangqin-tea study were also logged. A 2023 review was retained as a route to primary sources, not as quantitative evidence. The 2023 HQT study of an enriched total-flavonoid fraction is not a beverage or source-ingredient measurement.
- Other Scutellaria numeric sources located in this pass concern medicinal roots, tinctures, processed roots, or extracts. They do not establish ordinary-food composition and were not transferred. Exact 7-Methoxyflavanone was kept distinct from hydroxylated or otherwise methoxylated flavanones.
- Prunin is reported as present in immature citrus peel in primary metabolomics studies. The accessible studies use untargeted/relative peak profiling rather than a target-calibrated absolute food concentration. The 1993 primary paper describes quantitative distribution, but its numeric tables were not accessible for verification. No value, unit, basis, or uncertainty was inferred.

Target-level dispositions and actions are in `screening_matrix.csv`; source access, matrix, and quantitative-status assessments are in `source_assessment.csv`. The eight rows remain uncovered in the cumulative register. No candidate measurement was converted to zero or promoted from a secondary citation.

## Updated state

- Screened universe: 143/143 Stage B IDs; ten Batch 104 targeted search events (including two follow-ups on the 2026 tea study); 448 cumulative search-log events; 12 source assessments and 11 new source-registry entries recorded. One already-registered source was deduplicated.
- Accepted identity-complete quantitative coverage: 99/107; identity-pending compounds: 36; legacy identity-blocked mappings: 46; orphans: 0.
- Accepted data changes in Batch 104: 0 food records, 0 mappings.
- Pending identity candidate ledger remains 42 rows (39 numeric, one qualitative-only, two method-only); Batch 104 adds no such rows.
- Minimum target of 130 remains unmet by 31. At most eight additional compounds can come from the current complete-identity gaps; at least 23 pending identities would still need formal Stage B review and qualifying evidence even if all eight gaps were filled.

This is a bounded source audit, not proof that measurements do not exist. The remaining practical blockers are obtaining the 2026 tea study's target-specific data and methods, access to primary tea tables and the 1993 citrus table, or new targeted calibrated food-composition studies. No Phase 1B release was created.

## Verification

- Phase 1 validation: PASS; 541 food records and 541 mappings; zero food or mapping errors/orphans; Stage B snapshot unchanged.
- Focused tests: PASS, 32/32 across food composition, compound mapping, Batch 101 regression, continuation batches 102–103, and the Batch 104 audit.
- Independent mapping reconstruction: PASS; active mappings match the saved independent 541-row reconstruction.
"""
    (B / "BATCH_104_GAP_REAUDIT_REPORT.md").write_text(report, encoding="utf-8")
    (B / "coverage_delta.json").write_text(json.dumps({"batch":"104","date":"2026-11-03","eligible_gaps_reviewed":8,"new_search_events":batch_search_events,"new_sources_added":batch_source_rows_added,"source_assessments":len(batch_source_urls),"accepted_records_added":0,"accepted_mappings_added":0,"eligible_quantitative_coverage":99,"eligible_gaps_remaining":8,"research_screened":"143/143","search_log_events":len(current_search),"food_records":len(foods),"mapping_rows":len(maps),"target_minimum":130,"target_achieved":False,"decision":"NO_NEW_QUALIFYING_MEASUREMENT"}, indent=2)+"\n", encoding="utf-8")

    progress_heading = "## Batch 104 — eligible-gap source re-audit — 2026-11-03"
    progress_path = P / "PROGRESS.md"
    progress_text = progress_path.read_text(encoding="utf-8")
    if progress_heading not in progress_text:
        with progress_path.open("a", encoding="utf-8") as f:
            f.write("\n\n" + progress_heading + "\n\nThe eight remaining identity-complete gaps received a targeted food-context and primary-source follow-up. Huangqin tea was treated as a potential beverage matrix; no accessible primary sample-level values and denominators were verified for the exact targets. Prunin evidence remained qualitative/untargeted or behind the primary table paywall. No accepted data changed; 99/107 coverage remains. See `batches/batch_104_eligible_gap_reaudit/BATCH_104_GAP_REAUDIT_REPORT.md`.\n")
    (P / "NEXT_STEPS.md").write_text("""# Next steps — post Batch 104

Current state: 143/143 Stage B IDs screened; 99/107 identity-complete compounds have accepted quantitative food data; 8 complete-identity gaps remain; 36 Stage B identity reviews remain pending. The 130 minimum is not achieved.

Batch 104 performed a focused re-audit of all eight complete-identity gaps and found no additional qualifying sample-level food measurements in accessible primary sources. A 2026 widely-targeted HQT study reports comparative baicalin and wogonoside findings in tender-leaf tea, but accessible abstract text has no calibrated sample values and the underlying data are available on request. The remaining specific opportunities are to obtain the full 2026 methods/data and older HQT HPLC table, verify tea sample basis and food context, and obtain the 1993 primary prunin table or a targeted standard-calibrated citrus assay. Do not use secondary review numbers, comparative metabolomics signals, medicinal-root/tincture values, or enriched-extract concentrations as ordinary-food measurements.

Any coverage increase beyond 107 requires formal Stage B identity review plus qualifying food evidence. Final validation and the independent 541-row mapping reconstruction passed; repeat them after any data/code change. No Phase 1B release has been created.
""", encoding="utf-8")
    (P / "RESUME_INSTRUCTIONS.md").write_text("""# Resume instructions

Active checkpoint: `Phase1B-2026-11-03-batch-103-all-143-screened`, updated with Batch 104. All 143 Stage B IDs have been screened and the eight complete-identity gaps have received a focused follow-up. Read `batches/batch_104_eligible_gap_reaudit/BATCH_104_GAP_REAUDIT_REPORT.md`, its screening matrix, and source assessment before resuming.

Coverage is 99/107; no Batch 104 measurement qualified. A 2026 widely-targeted HQT study reports comparatively higher baicalin and wogonoside in tender-leaf tea; its accessible abstract gives no sample-level calibrated values and the study data are available on request. The next justified acquisition requires its target-specific methods/data, primary tea-table values with interpretable food denominators, the original prunin table, a new targeted calibrated food study, or formal Stage B review. Do not edit Stage B, Stage A, the Phase 1-v1.3.0 foundation, or historical releases.
""", encoding="utf-8")

    appendix = "\n\n## Batch 104 eligible-gap audit — 2026-11-03\n\nThe eight remaining complete-identity gaps were re-audited against primary food-context sources. No qualifying absolute food measurements were accessible; tea-specific and prunin follow-up leads and limitations are preserved in `batches/batch_104_eligible_gap_reaudit/`. Accepted coverage remains 99/107; no data or mappings were added.\n"
    for fn in ["FOOD_COMPOSITION_COVERAGE_REPORT.md", "MAPPING_COVERAGE_REPORT.md", "SEARCH_COVERAGE_REPORT.md", "SOURCE_VERIFICATION_REPORT.md", "ACCEPTED_REJECTED_RECORD_REPORT.md", "PHASE1B_COMPLETION_REPORT.md"]:
        report_path = P / fn
        existing_text = report_path.read_text(encoding="utf-8")
        if "## Batch 104 eligible-gap audit — 2026-11-03" not in existing_text:
            with report_path.open("a", encoding="utf-8") as f:
                f.write(appendix)

    print(json.dumps({"status":"BATCH104_REAUDIT_RECORDED","gaps_reviewed":8,"new_search_events":batch_search_events,"new_source_registry_entries":batch_source_rows_added,"source_assessments":len(batch_source_urls),"cumulative_search_events":len(current_search),"records_added":0,"mappings_added":0,"coverage":"99/107","remaining_gaps":8}, indent=2))

if __name__ == "__main__":
    main()
