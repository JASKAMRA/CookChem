"""Reproducibly update the first-pass caffeine PK extraction from publisher full text.

The five condition-level Cmax summaries below are transcribed from Table 1 of
White et al. (2016). The output remains pending and is not selected downstream.
"""
from __future__ import annotations

import copy
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTRACTED_ON = "2026-11-03"
TABLE = [
    ("A", "hot coffee", "20 min", 3.74, 1.09, 1.96, 5.95),
    ("B", "cold coffee", "2 min", 3.64, 1.36, 1.81, 8.17),
    ("C", "cold coffee", "20 min", 3.56, 1.06, 1.69, 5.77),
    ("D", "sugar-free energy drink", "2 min", 3.36, 1.20, 1.40, 5.78),
    ("E", "sugar-free energy drink", "20 min", 3.14, 0.95, 1.87, 5.25),
]
METHODS_N_NOTE = (
    "The abstract reports 24 completers; Methods says 24 recruited and two excluded for poor venous access. "
    "Table 1 does not give condition-specific analyzed n; denominator discrepancy is unresolved."
)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    sources = read_json(ROOT / "data" / "source_registry.json")
    source = sources[0]
    source["full_text_url"] = "https://www.tandfonline.com/doi/pdf/10.3109/15563650.2016.1146740"
    source["access_status"] = "full_text_reviewed"
    source["provenance"].update({
        "registration_method": "PubMed bibliographic verification plus first-pass review of publisher full text and Table 1",
        "full_text_accessed_on": EXTRACTED_ON,
        "full_text_review_note": "Publisher article and Table 1 reviewed; independent reviewer still pending.",
    })
    write_json(ROOT / "data" / "source_registry.json", sources)

    previous = read_json(ROOT / "data" / "evidence_registry.json")[0]
    previous["compound_reference"]["match_rationale"] = (
        "The publisher full text identifies caffeine as the analyte and reports caffeine measurements, but does not state a "
        "PubChem CID or structure. Phase1B-v1.3.1 candidate MOL-693364CB16A9EA2D is Caffeine (PubChem CID 2519); "
        "retain NAME_ONLY_MATCH until a second reviewer adjudicates this source-to-registry identity link."
    )
    previous["study"]["population_or_model"] = (
        "Healthy non-caffeine-naive adults aged 18–30. Abstract reports 24 completers; Methods reports 24 recruited and "
        "two excluded for poor venous access; final analyzable denominator is unclear."
    )
    previous["conditions"].update({
        "dose_basis": "160 mg caffeine per condition; open-label, group-randomized, crossover study; five conditions",
        "preparation": "Four hundred fifty mL beverage per condition; instant coffee used 4.1 g powder, energy drink was sugar-free",
        "experimental_conditions": [
            "A: hot coffee prepared with 85 °C water, consumed over 20 min",
            "B: cold coffee refrigerated at 4 °C, consumed over 2 min",
            "C: cold coffee refrigerated at 4 °C, consumed over 20 min",
            "D: sugar-free energy drink refrigerated at 4 °C, consumed over 2 min",
            "E: sugar-free energy drink refrigerated at 4 °C, consumed over 20 min",
            "Plasma samples collected at 0, 5, 10, 20, 40, 60, 90, 120, 240, and 480 min from start of beverage consumption",
        ],
        "denominator_note": METHODS_N_NOTE,
    })
    previous["identity_assessment"].update({
        "basis": "Publisher full text names caffeine and measures caffeine. The candidate Phase1B record is Caffeine, PubChem CID 2519, but that identifier is not cited in the study; keep name-only status pending independent adjudication.",
        "review_status": "pending",
    })
    previous["applicability_assessment"].update({
        "preparation": "Specific 160 mg caffeine doses in 450 mL instant coffee or sugar-free energy drink, temperature and consumption-rate protocols in Methods; does not establish a general food-matrix correction.",
        "rationale": "Human PK under these tested beverage conditions is contextual evidence only. It cannot be converted into food concentration, recipe dose, cooking retention, or exposure multipliers; applicability to other matrices, populations, and doses is unresolved.",
    })
    common_limitations = [
        METHODS_N_NOTE,
        "Small single-center study; no dose-response assessment.",
        "One investigator disclosed consultancy with the American Beverage Association, Red Bull GmbH, and Monster Energy; study funding was from the American Beverage Association.",
        "Identity remains name-only pending adjudication despite an unambiguous common-name candidate in Phase1B.",
        "Context-limited: the results are not food-composition values, cooking-retention factors, safety thresholds, or clinical recommendations.",
        "One-pass extraction; independent second review remains pending.",
    ]
    entries = []

    qualitative = copy.deepcopy(previous)
    qualitative["evidence_id"] = "EVD-PK-0001"
    qualitative["outcome"] = {
        "measure": "Between-condition plasma caffeine pharmacokinetic comparison",
        "result_type": "qualitative_observation",
        "reported_result": "One-way repeated-measures ANOVA found a difference in mean Cmax (p=0.043), but no pairwise comparison reached statistical significance. The paper reported no significant between-condition differences for AUC0–infinity, Tmax, MRT, MAT, half-life, or clearance divided by assumed bioavailability.",
        "numeric_value": None,
        "unit": None,
        "denominator": METHODS_N_NOTE,
        "uncertainty": "The reported omnibus Cmax test is significant, but no pairwise comparison was significant; do not infer a specific pairwise effect or equivalence.",
    }
    qualitative["limitations"] = common_limitations
    qualitative["extraction"] = {
        "status": "full_text_extracted",
        "method": "First-pass manual transcription and paraphrase from publisher full text; results and methods checked against the PubMed abstract; no automated or LLM-generated acceptance.",
        "source_location": "Taylor & Francis full text, Results paragraphs 1–2; Methods, Pharmacokinetic analysis; PubMed Abstract Results",
        "extracted_on": EXTRACTED_ON,
    }
    qualitative["review"].update({
        "status": "pending_second_reviewer",
        "quality_class": "not_rated",
        "reviewer_notes": "Full text inspected in a first-pass extraction. Independent verification, identity adjudication, and applicability review remain pending.",
        "decision_rationale": "Source-level observation is retained but not accepted downstream because the identity/applicability gates and second review are unresolved.",
    })
    entries.append(qualitative)

    for code, matrix, duration, mean, sd, low, high in TABLE:
        row = copy.deepcopy(previous)
        row["evidence_id"] = f"EVD-PK-0001-{code}"
        row["conditions"]["condition_code"] = code
        row["conditions"]["condition_description"] = f"{matrix}, consumed over {duration}"
        row["outcome"] = {
            "measure": "Maximum observed plasma caffeine concentration (Cmax), condition-level mean",
            "result_type": "measured_numeric",
            "reported_result": f"{mean:.2f} ± {sd:.2f} µg/mL (range {low:.2f}–{high:.2f})",
            "numeric_value": mean,
            "unit": "µg/mL",
            "denominator": f"Condition {code} group mean; {METHODS_N_NOTE}",
            "uncertainty": f"Reported as mean ± SD with range; SD={sd:.2f} µg/mL, range={low:.2f}–{high:.2f} µg/mL.",
            "dispersion_type": "standard deviation",
            "standard_deviation": sd,
            "range_min": low,
            "range_max": high,
            "condition_code": code,
        }
        row["limitations"] = common_limitations
        row["extraction"] = {
            "status": "full_text_extracted",
            "method": "First-pass manual transcription of the published table row; values and units preserved without normalization or derivation.",
            "source_location": f"Taylor & Francis full text, Table 1, Cmax column, condition {code}; Methods and Results paragraphs 1–2",
            "extracted_on": EXTRACTED_ON,
        }
        row["review"].update({
            "status": "pending_second_reviewer",
            "quality_class": "not_rated",
            "reviewer_notes": "Numeric mean, SD, and observed range transcribed as printed in Table 1. Final analyzable n is not stated consistently across abstract and methods; independent review is pending.",
            "decision_rationale": "A source-reported table value is preserved, but it is not accepted for downstream use until independent review and identity/applicability adjudication.",
        })
        entries.append(row)
    write_json(ROOT / "data" / "evidence_registry.json", entries)

    with (ROOT / "reports" / "source_bibliography.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["source_id", "title", "authors", "year", "journal", "volume_issue_pages", "doi", "pmid", "url", "full_text_url", "access_status", "source_type"])
        writer.writerow([source["source_id"], source["title"], "; ".join(source["authors"]), source["publication_year"], source["journal"], source["volume_issue_pages"], source["doi"], source["pmid"], source["url"], source["full_text_url"], source["access_status"], source["source_type"]])

    with (ROOT / "reports" / "pending_evidence_register.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["evidence_id", "source_id", "category", "result_type", "identity_status", "applicability_status", "review_status", "pending_reason", "required_next_action", "downstream_eligible"])
        for row in entries:
            writer.writerow([row["evidence_id"], row["source_id"], row["category"], row["outcome"]["result_type"], row["identity_assessment"]["match_status"], row["applicability_assessment"]["status"], row["review"]["status"], "Name-only identity; context-limited; independent reviewer pending; methods/abstract participant-count discrepancy" if row["outcome"]["result_type"] == "measured_numeric" else "Full-text qualitative finding; name-only identity; context-limited; independent reviewer pending", "Independently verify source location and participant denominator; adjudicate identity and matrix applicability; keep PK evidence separate from recipe dose calculations", "false"])

    table = "\n".join(f"| {code} | {matrix}, {duration} | {mean:.2f} | {sd:.2f} | {low:.2f}–{high:.2f} |" for code, matrix, duration, mean, sd, low, high in TABLE)
    (ROOT / "reports" / "extraction_report.md").write_text(f"""# Phase 4 source and extraction report — working registry v0.1.1

Status: **IN_PROGRESS**. Phase 4 scope is proposed; no source record is accepted for downstream use.

| Measure | Count | Meaning |
|---|---:|---|
| Registered primary sources | 1 | White et al. 2016 |
| Sources with bibliographic identifiers verified | 1 | PubMed record confirms title, authors, journal, year, DOI, PMID |
| Publisher full texts reviewed | 1 | Full text and Table 1 inspected |
| Evidence records | 6 | Five condition-level measured Cmax rows and one qualitative between-condition result |
| Measured numeric records | 5 | Means, SDs, ranges, units, condition labels, and source table locations retained |
| Qualitative records | 1 | Omnibus and pairwise statistical findings kept separate from arm-level estimates |
| Accepted records | 0 | Identity/applicability gates and independent review remain pending |

Source: White JR et al., *Clinical Toxicology* 2016;54(4):308–312. DOI 10.3109/15563650.2016.1146740; PMID 27100333. Bibliography: https://pubmed.ncbi.nlm.nih.gov/27100333/. Primary full text/Table 1: https://www.tandfonline.com/doi/pdf/10.3109/15563650.2016.1146740.

Table 1 reports mean ± SD (range) Cmax in µg/mL:

| Arm | Condition | Mean | SD | Range |
|---|---|---:|---:|---:|
{table}

Each row is stored as a separate evidence record so conditions and denominators cannot be collapsed. Values are source-reported, not calculated by CookRisk. Conditions are 160 mg caffeine in 450 mL beverage. The source's abstract says 24 subjects completed, whereas Methods says 24 were recruited and two were excluded for poor venous access; Table 1 does not state condition-specific analyzed n. The discrepancy is recorded and not resolved by assumption.

The study reports an omnibus difference in mean Cmax (one-way repeated-measures ANOVA p=0.043) with no pairwise comparison statistically significant. This finding is separately recorded; it does not establish equivalence or a specific arm-to-arm difference. The article reports American Beverage Association funding and investigator consultancy disclosures, retained as limitations.

Identity remains `NAME_ONLY_MATCH` because the source does not cite a structure identifier, despite a Phase1B caffeine candidate (PubChem CID 2519). Applicability remains `CONTEXT_LIMITED`; none of these plasma concentrations are food concentrations, recipe-dose multipliers, cooking factors, safety thresholds, or clinical recommendations. All six records remain pending an independent second review.
""", encoding="utf-8")

    (ROOT / "reports" / "identity_applicability_review.md").write_text("""# Phase 4 identity and applicability review — working registry v0.1.1

## Current counts

| Dimension | Status | Count |
|---|---|---:|
| Registered sources | full-text reviewed | 1 |
| Evidence records | full-text extracted | 6 |
| Outcomes | measured numeric | 5 |
| Outcomes | qualitative | 1 |
| Identity | NAME_ONLY_MATCH | 6 |
| Applicability | CONTEXT_LIMITED | 6 |
| Independent review | pending second reviewer | 6 |
| Accepted downstream records | none | 0 |

## Decision

The paper names caffeine; the Phase1B-v1.3.1 candidate is Caffeine (PubChem CID 2519). The paper does not report CID, InChI, or structure, so the cross-reference stays `NAME_ONLY_MATCH` pending independent adjudication. Five source-reported plasma Cmax means and one statistical comparison record are scientifically extracted but not identity-adjudicated.

The trial concerns 160 mg caffeine in fixed-volume instant coffee or a sugar-free energy drink, consumed under five temperature/rate protocols in healthy adults. Applicability is context-limited to the exact human study conditions. Plasma PK outcomes cannot be used as food-composition values, direct consumed-dose multipliers, cooking retention, safety thresholds, or clinical guidance.

The study's denominator is internally unresolved in the publication: the abstract says 24 subjects completed; Methods says 24 recruited and two excluded; Table 1 supplies no condition-specific n. The package records this conflict without choosing a denominator. Funding and author consultancy disclosures are also retained for independent quality assessment.

All evidence is excluded by the Phase 3 read-only context selector until a second reviewer adjudicates identity, conditions, applicability, and quality. The current adapter only selects accepted contextual evidence; it does not expose quantitative PK values to calculations.
""", encoding="utf-8")

    (ROOT / "reports" / "validation_report.md").write_text("""# Phase 4 validation report — working registry v0.1.1

- Application-level validation covers unique IDs, evidence-to-source references, identity status consistency, numeric/qualitative separation, and acceptance gates.
- Phase 3 context selector excludes all six evidence records: identity is name-only, applicability is context-limited, and review remains pending.
- Five measured numeric evidence rows preserve source units, means, SDs, ranges, condition codes, denominator caveat, and Table 1 locations; one qualitative statistical result is a distinct row.
- No record is accepted and no Phase 4 value is integrated into Phase 3 exposure calculations.
- Phase 4 release remains `IN_PROGRESS`; see the v0.1.1 release metadata for package checksums and validation status.
- Formal JSON Schema Draft 2020-12 validation is **NOT RUN** unless the declared `jsonschema>=4.18,<5` development dependency is available. Application-level tests do not substitute for metaschema validation.
""", encoding="utf-8")

    (ROOT / "README.md").write_text("""# CookRisk Phase 4 evidence layer

Current status: **IN_PROGRESS**. There was no approved Phase 4/Stage D specification in the current top-level Stage C documentation, so `PROPOSED_SCOPE.md` remains explicitly proposed.

The working registry contains one publisher-full-text-reviewed primary human caffeine PK source and six separate extracted evidence records: five condition-level measured Cmax outcomes from Table 1 and one qualitative statistical comparison. All records remain `NAME_ONLY_MATCH`, `CONTEXT_LIMITED`, and `pending_second_reviewer`; the Phase 3 selector returns none. These plasma PK results cannot be used as food concentrations, recipe-dose multipliers, cooking-retention values, safety thresholds, or clinical advice.

The package records the article's abstract-versus-methods participant-count discrepancy and author funding/consultancy disclosures. Exact table rows are preserved without pooling or unit conversion. See `reports/extraction_report.md`, `reports/identity_applicability_review.md`, and `reports/pending_evidence_register.csv`.

`data/` holds bibliographic and evidence registries; `schemas/` declares Draft 2020-12; `src/phase4_registry.py` performs application-level validation and exposes a read-only context-only selector. No Stage B or Phase 2 records are copied into this layer. Phase 1B-v1.3.1 and Phase2-v0.3.0 are version-scoped dependencies only.

Run working-tree tests from the repository root:

```powershell
python -m unittest discover -s stageC/phase4/tests -v
```

Install `stageC/phase4/requirements-dev.txt` to run the optional formal JSON Schema validator. Phase4-v0.1.0 remains an immutable abstract-only historical snapshot; the full-text continuation is packaged separately as Phase4-v0.1.1.
""", encoding="utf-8")

    (ROOT / "PROPOSED_SCOPE.md").write_text("""# Phase 4 evidence layer — proposed scope

**Status: PROPOSED, not previously approved.** No formal Phase 4/Stage D specification was present in the current project documentation. This proposal continues the documented boundaries: Phase 1B provides source-verified food/compound records, Phase 2 provides cooking evidence, and Phase 3 calculates exposure without clinical interpretation.

## Purpose and boundaries

Maintain a versioned, source-traceable research evidence registry that can later contextualize exposure. The initial category is human pharmacokinetics and food-matrix context. Candidate future categories include food/compound occurrence, bioavailability, metabolism, cooking/preparation, dose-response, toxicology, and clinical outcomes. A category does not imply calculation or clinical applicability.

- Phase1B-v1.3.1 remains the read-only compound/food identity dependency. Identity-complete does not imply quantitative eligibility.
- Phase2-v0.3.0 remains the read-only cooking evidence dependency. Phase 4 does not duplicate or reinterpret it.
- Stage B interaction evidence remains exclusively in its own registry.
- Human plasma PK values are not food concentration, cooking retention, or direct recipe-dose multipliers.
- Evidence validity, identity match, applicability, and review acceptance remain separate states.

## Workflow and evidence states

Source registration, extraction, unit/denominator verification, identity assessment, applicability assessment, quality review, and acceptance are separately recorded. Automated extraction cannot accept evidence. Only independently human-reviewed records with adjudicated identity and applicability can enter a context-only downstream view. Quantitative PK access requires a separate future contract; the current Phase 3 adapter intentionally exposes no quantitative PK values.

## Current proposed scope demonstration

The working v0.1.1 registry contains one primary human study with publisher full text and Table 1 reviewed: five condition-level Cmax rows plus a separate qualitative statistical comparison. All six remain pending review, name-only in identity, context-limited, and excluded downstream. The source's participant denominator discrepancy is preserved. Phase4-v0.1.0 remains the immutable abstract-only predecessor.

This is an initial workflow demonstration, not a complete literature review, accepted scientific evidence base, or clinical interpretation stage.
""", encoding="utf-8")
    print(json.dumps({"sources": len(sources), "evidence_records": len(entries),
                      "measured_numeric": sum(e["outcome"]["result_type"] == "measured_numeric" for e in entries),
                      "qualitative": sum(e["outcome"]["result_type"] == "qualitative_observation" for e in entries),
                      "accepted": sum(e["review"]["status"].startswith("accepted") for e in entries)}, indent=2))


if __name__ == "__main__":
    main()
