#!/usr/bin/env python3
"""Build a read-only Stage A/Stage B crosswalk and Stage C Phase 2 intake audit."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHASE1B = ROOT / "stageC/releases/Phase1B-v1.3.0"
STAGEB = ROOT / "stageB/release/StageB_V20_20261103"
OUT = ROOT / "stageC/phase2/data"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_cid(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    try:
        number = Decimal(value)
        if number == number.to_integral_value():
            return str(int(number))
    except Exception:
        pass
    return value


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    stage_a_input = ROOT / "stageA/input/cookchem_molecular_retention_preprocessed.csv"
    stage_a_oof = ROOT / "stageA/outputs/stageA_oof_predictions.csv"
    stage_a_qa = json.loads((ROOT / "stageA/outputs/stageA_qa.json").read_text())
    stageb_model_path = ROOT / "stageB/final_model/cookrisk_retention_stageB_selected.joblib"
    stageb_model_manifest_path = ROOT / "stageB/final_model/stageB_selected_model_manifest.json"
    stageb_model_manifest = json.loads(stageb_model_manifest_path.read_text()) if stageb_model_manifest_path.exists() else {}
    stage_b_registry_path = STAGEB / "data/compound_registry.csv"
    stage_b_retention_path = STAGEB / "data/cooking_retention_evidence.csv"
    food_mapping_path = PHASE1B / "stageC/data/compound_food_mapping/compound_food_mapping.csv"
    phase1_validation = json.loads((PHASE1B / "stageC/reports/validation/phase1_validation.json").read_text())

    stage_a_rows = read_csv(stage_a_input)
    stage_b_rows = read_csv(stage_b_registry_path)
    source_retention = read_csv(stage_b_retention_path)
    food_mappings = read_csv(food_mapping_path)
    oof_rows = read_csv(stage_a_oof)

    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in stage_a_rows:
        groups[row["Canonical_Molecular_ID"]].append(row)
    registry_by_cid = {
        normalize_cid(row.get("PubChem_CID", "")): row
        for row in stage_b_rows
        if normalize_cid(row.get("PubChem_CID", ""))
    }
    covered_stage_b_ids = {
        row["compound_id"]
        for row in food_mappings
        if row.get("quantitative_data_available", "").strip().lower() == "true"
        and row.get("mapping_status", "") == "Exact identity match"
    }

    crosswalk: list[dict[str, str]] = []
    statuses: Counter[str] = Counter()
    for group_id, rows in sorted(groups.items()):
        cid_set = {normalize_cid(row.get("PubChem_CID", "")) for row in rows if row.get("PubChem_CID", "").strip()}
        name_set = {row.get("Canonical_Compound_Name", "").strip().casefold() for row in rows if row.get("Canonical_Compound_Name", "").strip()}
        smiles_set = {row.get("Canonical_SMILES", "").strip() for row in rows if row.get("Canonical_SMILES", "").strip()}
        first = rows[0]
        cid = next(iter(cid_set)) if len(cid_set) == 1 else ""
        candidate = registry_by_cid.get(cid) if cid else None
        stable_structure_candidates = [
            item for item in stage_b_rows
            if item.get("Compound_ID", "") == group_id
            and len(name_set) == 1 and len(smiles_set) == 1
            and next(iter(name_set)) == item.get("Canonical_Name", "").strip().casefold()
            and next(iter(smiles_set)) == item.get("SMILES", "").strip()
        ]
        status = "STRICT_MATCH"
        if len(cid_set) > 1:
            status = "INTRA_GROUP_CID_CONFLICT"
        elif not cid:
            status = "NO_CID"
        elif candidate is None:
            if len(stable_structure_candidates) == 1:
                candidate = stable_structure_candidates[0]
                status = "STABLE_ID_STRUCTURE_MATCH_CID_DISCREPANCY"
            else:
                status = "NO_STAGEB_CID_MATCH"
        elif len(name_set) != 1 or len(smiles_set) != 1:
            status = "INTRA_GROUP_NAME_OR_STRUCTURE_CONFLICT"
        elif (
            next(iter(name_set)) != candidate.get("Canonical_Name", "").strip().casefold()
            or next(iter(smiles_set)) != candidate.get("SMILES", "").strip()
        ):
            status = "CID_MATCH_REQUIRES_STRUCTURE_REVIEW"
        stage_b_id = candidate.get("Compound_ID", "") if candidate else ""
        identity_status = candidate.get("Identity_Status", "") if candidate else ""
        if status == "STRICT_MATCH" and identity_status.lower().startswith("identity pending"):
            status = "STRICT_STRUCTURE_MATCH_STAGEB_IDENTITY_PENDING"
        statuses[status] += 1
        crosswalk.append({
            "stagea_group_id": group_id,
            "stagea_record_count": str(len(rows)),
            "stagea_compound_name": first.get("Canonical_Compound_Name", first.get("Compound_Name", "")),
            "stagea_pubchem_cid": cid or "|".join(sorted(cid_set)),
            "stagea_pubchem_cid_resolved": "|".join(sorted({normalize_cid(row.get("PubChem_CID_Resolved", "")) for row in rows if normalize_cid(row.get("PubChem_CID_Resolved", ""))})),
            "stagea_canonical_smiles": next(iter(smiles_set)) if len(smiles_set) == 1 else "",
            "stageb_compound_id_candidate": stage_b_id,
            "stageb_canonical_name": candidate.get("Canonical_Name", "") if candidate else "",
            "stageb_identity_status": identity_status,
            "phase1b_accepted_quantitative_coverage": str(stage_b_id in covered_stage_b_ids).lower() if stage_b_id else "false",
            "crosswalk_status": status,
            "crosswalk_note": "Stage A CID differs or is unresolved; stable molecular ID, name, and canonical SMILES match Stage B." if status == "STABLE_ID_STRUCTURE_MATCH_CID_DISCREPANCY" else "",
        })
    crosswalk_fields = list(crosswalk[0])
    write_csv(OUT / "stagea_stageb_identity_crosswalk.csv", crosswalk_fields, crosswalk)

    # Individually disposition every non-strict CID candidate and intra-group CID conflict.
    review_rows: list[dict[str, str]] = []
    stageb_by_cid = {normalize_cid(row.get("PubChem_CID", "")): row for row in stage_b_rows if normalize_cid(row.get("PubChem_CID", ""))}
    audit_rows = read_csv(STAGEB / "identity/identity_structure_audit.csv")
    audit_by_cid = {normalize_cid(row.get("PubChem_CID", "")): row for row in audit_rows}
    def norm_name(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", (value or "").casefold().replace("β", "beta").replace("α", "alpha"))
    for entry in crosswalk:
        status = entry["crosswalk_status"]
        if status == "CID_MATCH_REQUIRES_STRUCTURE_REVIEW":
            cid = normalize_cid(entry["stagea_pubchem_cid"])
            sb = stageb_by_cid.get(cid, {})
            audit = audit_by_cid.get(cid, {})
            same_name = norm_name(entry["stagea_compound_name"]) == norm_name(sb.get("Canonical_Name", ""))
            review_rows.append({
                "stagea_group_id": entry["stagea_group_id"],
                "stagea_name": entry["stagea_compound_name"],
                "stagea_cid": cid,
                "stagea_smiles": entry["stagea_canonical_smiles"],
                "stageb_compound_id_candidate": sb.get("Compound_ID", ""),
                "stageb_name": sb.get("Canonical_Name", ""),
                "stageb_cid": cid,
                "stageb_smiles": sb.get("SMILES", ""),
                "stageb_identity_audit_status": audit.get("Status", ""),
                "stageb_pubchem_name_alias_match": audit.get("PubChem_Name_or_Alias_Match", ""),
                "review_decision": "PENDING_STRUCTURE_EQUIVALENCE_REVIEW" if same_name else "PENDING_NAME_AND_STRUCTURE_REVIEW",
                "decision_basis": "CID points to a Stage B PubChem-audited structure, but Stage A and Stage B canonical SMILES differ; exact structure equivalence not established in this environment." if same_name else "CID candidate conflicts with the Stage A canonical label and structure; possible broad class, related isomer, or wrong CID. Do not auto-join.",
            })
        elif status == "INTRA_GROUP_CID_CONFLICT":
            source_rows = groups[entry["stagea_group_id"]]
            cids = sorted({normalize_cid(row.get("PubChem_CID", "")) for row in source_rows if normalize_cid(row.get("PubChem_CID", ""))})
            review_rows.append({
                "stagea_group_id": entry["stagea_group_id"],
                "stagea_name": entry["stagea_compound_name"],
                "stagea_cid": "|".join(cids),
                "stagea_smiles": entry["stagea_canonical_smiles"],
                "stageb_compound_id_candidate": "",
                "stageb_name": "",
                "stageb_cid": "",
                "stageb_smiles": "",
                "stageb_identity_audit_status": "",
                "stageb_pubchem_name_alias_match": "",
                "review_decision": "PENDING_INTRA_GROUP_CID_CONFLICT",
                "decision_basis": "Multiple non-empty CIDs occur within one Stage A molecular group; source-row structure and identifier reconciliation required before any Stage B join.",
            })
    write_csv(OUT / "identity_candidate_review.csv", list(review_rows[0]), review_rows)

    # Source-level conversions are transparent complements of primary-reported losses.
    evidence_by_id = {row["processing_id"]: row for row in source_retention}
    evidence_rows: list[dict[str, str]] = []
    specifications = [
        ("P2-RET-001", "PROC-001", "Black pepper", "Black pepper alone; boiling 10/20 min or pressure cooking 10 min; reported envelope across tested conditions", "16", "34", "PRIMARY_REPORTED_LOSS_INTERVAL", "Interval is across experimental conditions, not a universal coefficient; red gram modifies loss."),
        ("P2-RET-002", "PROC-002", "Turmeric", "Turmeric; boiling 10/20 min or pressure cooking 10 min; general reported envelope", "27", "53", "PRIMARY_REPORTED_LOSS_INTERVAL", "Interval is across experimental conditions, not a universal coefficient; maximum loss was reported for pressure cooking 10 min."),
        ("P2-RET-003", "PROC-002", "Turmeric with tamarind", "Same cooking study; turmeric cooked in presence of tamarind", "12", "30", "PRIMARY_REPORTED_LOSS_INTERVAL", "Separate matrix context; do not pool with turmeric-alone interval."),
        ("P2-RET-004", "PROC-003", "Green tea infusion", "Brewing at 60 or 95 °C for 5–300 min", "", "", "QUALITATIVE_TRANSFORMATION_EVIDENCE", "The cited record describes extraction and catechin epimerization; it provides no single EGCG retention factor."),
    ]
    for record_id, source_id, matrix, conditions, loss_low, loss_high, kind, limitation in specifications:
        source = evidence_by_id[source_id]
        retained_low = retained_high = ""
        if loss_low:
            low, high = Decimal(100) - Decimal(loss_high), Decimal(100) - Decimal(loss_low)
            retained_low, retained_high = str(low), str(high)
        evidence_rows.append({
            "phase2_retention_record_id": record_id,
            "stageb_processing_id": source_id,
            "compound_id": source.get("Canonical_Molecular_ID", ""),
            "compound_name": source.get("compound_name", ""),
            "food_matrix": matrix,
            "cooking_conditions": conditions,
            "source_reported_result": source.get("quantitative_result", ""),
            "loss_low_percent": loss_low,
            "loss_high_percent": loss_high,
            "derived_retention_low_percent": retained_low,
            "derived_retention_high_percent": retained_high,
            "evidence_kind": kind,
            "application_status": "SOURCE_LEDGER_ONLY_NO_CONCENTRATION_ADJUSTMENT",
            "source_doi": source.get("doi", ""),
            "source_url": source.get("source_url", ""),
            "limitation": limitation + " This source-ledger record is not joined to Phase 1B concentrations.",
        })
    write_csv(OUT / "observed_retention_evidence.csv", list(evidence_rows[0]), evidence_rows)

    # Directly transcribed raw/cooked Curcuma longa measurements from one primary study.
    # Ratios are concentration ratios only; cooked yield is not reported for mass balance.
    pair_specs = [
        ("R227", "Curcumin", "Boiling", "water", "100", "", "1", "113.92", "12.24", "125.33", "9.61"),
        ("R228", "Curcumin", "Boiling", "water", "100", "", "2", "113.92", "12.24", "102.93", "8.30"),
        ("R229", "Curcumin", "Boiling", "water", "100", "", "5", "113.92", "12.24", "164.67", "17.50"),
        ("R230", "Curcumin", "Boiling", "water", "100", "", "10", "113.92", "12.24", "204.00", "21.38"),
        ("R231", "Curcumin", "Frying", "dry ceramic pan; no oil", "", "", "1", "113.92", "12.25", "246.00", "12.77"),
        ("R232", "Curcumin", "Frying", "dry ceramic pan; no oil", "", "", "2", "113.92", "12.25", "203.00", "23.43"),
        ("R233", "Curcumin", "Frying", "dry ceramic pan; no oil", "", "", "5", "113.92", "12.25", "174.67", "22.37"),
        ("R234", "Curcumin", "Frying", "dry ceramic pan; no oil", "", "", "10", "113.92", "12.25", "224.00", "26.96"),
        ("R235", "Curcumin", "Microwaving", "dry", "", "800", "1", "113.92", "12.25", "200.67", "18.88"),
        ("R236", "Curcumin", "Microwaving", "dry", "", "800", "2", "113.92", "12.25", "73.50", "9.56"),
        ("R237", "Curcumin", "Microwaving", "dry", "", "800", "5", "113.92", "12.25", "35.97", "2.07"),
        ("R243", "Demethoxycurcumin", "Boiling", "water", "100", "", "1", "40.27", "3.40", "31.63", "3.52"),
        ("R244", "Demethoxycurcumin", "Boiling", "water", "100", "", "2", "40.27", "3.40", "35.93", "4.61"),
        ("R245", "Demethoxycurcumin", "Boiling", "water", "100", "", "5", "40.27", "3.40", "47.67", "4.44"),
        ("R246", "Demethoxycurcumin", "Boiling", "water", "100", "", "10", "40.27", "3.40", "56.87", "5.97"),
        ("R247", "Demethoxycurcumin", "Frying", "dry ceramic pan; no oil", "", "", "1", "40.27", "3.10", "35.33", "3.95"),
        ("R248", "Demethoxycurcumin", "Frying", "dry ceramic pan; no oil", "", "", "2", "40.27", "3.10", "45.30", "4.28"),
        ("R249", "Demethoxycurcumin", "Frying", "dry ceramic pan; no oil", "", "", "5", "40.27", "3.10", "28.50", "2.17"),
        ("R250", "Demethoxycurcumin", "Frying", "dry ceramic pan; no oil", "", "", "10", "40.27", "3.10", "55.13", "4.70"),
        ("R251", "Demethoxycurcumin", "Microwaving", "dry", "", "800", "1", "40.27", "3.40", "41.37", "4.48"),
        ("R252", "Demethoxycurcumin", "Microwaving", "dry", "", "800", "2", "40.27", "3.40", "29.87", "3.80"),
        ("R253", "Demethoxycurcumin", "Microwaving", "dry", "", "800", "5", "40.27", "3.40", "11.96", "1.90"),
        ("R216", "Bisdemethoxycurcumin", "Boiling", "water", "100", "", "1", "42.90", "3.87", "50.07", "4.20"),
        ("R217", "Bisdemethoxycurcumin", "Boiling", "water", "100", "", "2", "42.90", "3.87", "44.70", "3.05"),
        ("R218", "Bisdemethoxycurcumin", "Boiling", "water", "100", "", "5", "42.90", "3.87", "57.37", "5.50"),
        ("R219", "Bisdemethoxycurcumin", "Boiling", "water", "100", "", "10", "42.90", "3.87", "82.03", "7.00"),
        ("R220", "Bisdemethoxycurcumin", "Frying", "dry ceramic pan; no oil", "", "", "1", "42.90", "3.87", "38.50", "4.88"),
        ("R221", "Bisdemethoxycurcumin", "Frying", "dry ceramic pan; no oil", "", "", "2", "42.90", "3.87", "51.93", "4.01"),
        ("R222", "Bisdemethoxycurcumin", "Frying", "dry ceramic pan; no oil", "", "", "5", "42.90", "3.87", "34.90", "3.31"),
        ("R223", "Bisdemethoxycurcumin", "Frying", "dry ceramic pan; no oil", "", "", "10", "42.90", "3.87", "67.77", "5.03"),
        ("R224", "Bisdemethoxycurcumin", "Microwaving", "dry", "", "800", "1", "42.90", "3.87", "49.13", "5.30"),
        ("R225", "Bisdemethoxycurcumin", "Microwaving", "dry", "", "800", "2", "42.90", "3.87", "32.93", "2.87"),
        ("R226", "Bisdemethoxycurcumin", "Microwaving", "dry", "", "800", "5", "42.90", "3.87", "16.47", "1.96"),
    ]
    source_rows_by_id = {row["Record_ID"]: row for row in stage_a_rows}
    pair_rows = []
    accepted_crosswalk_ids = {
        row["stagea_group_id"]: row["stageb_compound_id_candidate"]
        for row in crosswalk
        if row["crosswalk_status"] in {"STRICT_MATCH", "STABLE_ID_STRUCTURE_MATCH_CID_DISCREPANCY"}
    }
    for record_id, compound_name, method, medium, temp, power, minutes, raw, raw_sd, cooked, cooked_sd in pair_specs:
        source_row = source_rows_by_id[record_id]
        pair_rows.append({
            "pair_id": f"P2-CUR-{record_id}", "source_stagea_record_id": record_id,
            "stagea_compound_group_id": source_row["Canonical_Molecular_ID"],
            "stageb_compound_id": accepted_crosswalk_ids.get(source_row["Canonical_Molecular_ID"], ""), "compound_name": compound_name,
            "food_matrix": "Curcuma longa rhizome", "raw_state": "fresh uncooked rhizome",
            "cooking_method": method, "cooking_medium": medium,
            "temperature_c": temp, "time_min": minutes, "microwave_power_w": power,
            "raw_mean_mg_per_g": raw, "raw_sd_mg_per_g": raw_sd,
            "cooked_mean_mg_per_g": cooked, "cooked_sd_mg_per_g": cooked_sd,
            "measurement_unit": "mg/g fresh rhizome",
            "raw_mean_value": raw, "raw_sd_value": raw_sd,
            "cooked_mean_value": cooked, "cooked_sd_value": cooked_sd,
            "replicates_n": "3", "concentration_ratio_percent": str((Decimal(cooked) / Decimal(raw) * 100).quantize(Decimal("0.01"))),
            "ratio_semantics": "concentration_ratio_not_mass_retention",
            "ratio_uncertainty": "not derived; replicate-level covariance unavailable",
            "evidence_class": "primary_observed_pair", "not_model_prediction": "true",
            "source_doi": "10.3390/foods12163086", "source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10453412/",
            "source_locator": "Table 1; fresh rhizome baseline and cooked treatment row",
            "limitations": "2 g rhizome slices; cooked concentration is mg/g; cooked mass yield not supplied, so ratio is not total analyte mass retention. These are condition-level group means, not matched replicate-level pairs. Stage A row is a provenance pointer only; values transcribed from primary table. SD marked not reported where source table omits it.",
        })
    # Four phytochemicals measured before/after household cooking in a second primary study.
    pumpkin_specs = [
        ("Sinapic acid", "1", "29.57", "0.82", [("Boiling", "14.22", "0.14"), ("Microwaving", "28.58", "0.28"), ("Steaming", "29.17", "0.20"), ("Stir-frying", "15.34", "0.16")]),
        ("Rutin", "5", "28.15", "0.42", [("Boiling", "21.04", "0.24"), ("Microwaving", "27.78", "0.22"), ("Steaming", "26.23", "0.26"), ("Stir-frying", "20.45", "0.44")]),
        ("Isoquercitrin", "13", "7.76", "0.22", [("Boiling", "3.98", "0.012"), ("Microwaving", "7.11", "0.31"), ("Steaming", "5.62", "0.12"), ("Stir-frying", "5.11", "0.11")]),
        ("Astragalin", "17", "9.22", "0.44", [("Boiling", "5.46", "0.62"), ("Microwaving", "8.89", "0.32"), ("Steaming", "7.85", "0.42"), ("Stir-frying", "7.14", "0.42")]),
    ]
    pumpkin_conditions = {
        "Boiling": ("water; 150 mL per 100 g leaves", "95", "10", ""),
        "Microwaving": ("12 mL distilled water; 100 g leaves", "", "3", "700"),
        "Steaming": ("steam; 98 °C", "98", "10", ""),
        "Stir-frying": ("10 mL extra-virgin olive oil; 100 g leaves", "150", "2", ""),
    }
    for compound_name, first_record_id, raw, raw_sd, cooked_values in pumpkin_specs:
        stagea_records = {
            (row["Cooking_Method_Standardized"]): row
            for row in stage_a_rows
            if row.get("DOI") == "10.3390/molecules31162740"
            and row.get("Canonical_Compound_Name") == compound_name
        }
        for method, cooked, cooked_sd in cooked_values:
            record = stagea_records[method]
            medium, temp, minutes, power = pumpkin_conditions[method]
            pair_rows.append({
                "pair_id": f"P2-PUM-{record['Record_ID']}",
                "source_stagea_record_id": record["Record_ID"],
                "stagea_compound_group_id": record["Canonical_Molecular_ID"],
                "stageb_compound_id": "",
                "compound_name": compound_name,
                "food_matrix": "Cucurbita maxima leaves",
                "raw_state": "raw leaves; control",
                "cooking_method": method,
                "cooking_medium": medium,
                "temperature_c": temp,
                "time_min": minutes,
                "microwave_power_w": power,
                "raw_mean_mg_per_g": "", "raw_sd_mg_per_g": "",
                "cooked_mean_mg_per_g": "", "cooked_sd_mg_per_g": "",
                "measurement_unit": "mg/100 g dry weight",
                "raw_mean_value": raw, "raw_sd_value": raw_sd,
                "cooked_mean_value": cooked, "cooked_sd_value": cooked_sd,
                "replicates_n": "3",
                "concentration_ratio_percent": str((Decimal(cooked) / Decimal(raw) * 100).quantize(Decimal("0.01"))),
                "ratio_semantics": "apparent_concentration_ratio_not_total_mass_retention",
                "ratio_uncertainty": "not derived; replicate-level covariance unavailable",
                "evidence_class": "primary_observed_group_means",
                "not_model_prediction": "true",
                "source_doi": "10.3390/molecules31162740",
                "source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC13515228/",
                "source_locator": "Table 3; raw control and named cooking-treatment column",
                "limitations": "Three independent biological replicates; values reported on dry-weight basis. Apparent concentration ratio is not mass retention. Stage A row is provenance pointer only; values transcribed from primary table.",
            })
    amino_acid_specs = [
        ("Aspartic acid", "21", "17.92", ".22", [("Boiling","15.86",".18"),("Microwaving","16.92",".15"),("Steaming","17.41",".12"),("Stir-frying","16.44",".14")]),
        ("Threonine", "25", "7.18", ".14", [("Boiling","6.22",".08"),("Microwaving","6.84",".04"),("Steaming","7.02",".04"),("Stir-frying","6.51",".08")]),
        ("Serine", "29", "7.62", ".08", [("Boiling","6.55",".05"),("Microwaving","7.18",".06"),("Steaming","7.47",".08"),("Stir-frying","6.83",".08")]),
        ("Glutamic acid", "33", "22.52", ".43", [("Boiling","20.64",".32"),("Microwaving","21.72",".42"),("Steaming","22.14",".28"),("Stir-frying","21.16",".52")]),
        ("Glycine", "37", "9.64", ".14", [("Boiling","8.41",".18"),("Microwaving","9.12",".14"),("Steaming","9.42",".18"),("Stir-frying","8.78",".17")]),
        ("Alanine", "41", "14.40", ".08", [("Boiling","12.62",".14"),("Microwaving","13.71",".13"),("Steaming","14.03",".12"),("Stir-frying","13.12",".13")]),
        ("Cysteine", "45", "1.95", ".04", [("Boiling","1.31",".04"),("Microwaving","1.62",".02"),("Steaming","1.81",".02"),("Stir-frying","1.49",".02")]),
        ("Valine", "49", "11.75", ".12", [("Boiling","10.21",".14"),("Microwaving","11.11",".17"),("Steaming","11.53",".15"),("Stir-frying","10.74",".15")]),
        ("Methionine", "53", "4.54", ".14", [("Boiling","3.66",".12"),("Microwaving","4.11",".14"),("Steaming","4.38",".14"),("Stir-frying","3.89",".12")]),
        ("Isoleucine", "57", "7.56", ".09", [("Boiling","6.64",".08"),("Microwaving","7.16",".08"),("Steaming","7.41",".06"),("Stir-frying","6.91",".04")]),
        ("Leucine", "61", "15.34", ".11", [("Boiling","13.74",".18"),("Microwaving","14.76",".12"),("Steaming","15.18",".12"),("Stir-frying","14.28",".13")]),
        ("Tyrosine", "65", "9.64", ".12", [("Boiling","8.61",".12"),("Microwaving","9.22",".11"),("Steaming","9.52",".11"),("Stir-frying","8.95",".12")]),
        ("Phenylalanine", "69", "11.59", ".12", [("Boiling","10.23",".13"),("Microwaving","11.02",".12"),("Steaming","11.41",".11"),("Stir-frying","10.67",".13")]),
        ("Histidine", "73", "6.42", ".04", [("Boiling","5.51",".10"),("Microwaving","6.01",".08"),("Steaming","6.26",".06"),("Stir-frying","5.76",".04")]),
        ("Lysine", "77", "13.91", ".12", [("Boiling","12.42",".14"),("Microwaving","13.28",".16"),("Steaming","13.76",".15"),("Stir-frying","12.84",".12")]),
        ("Arginine", "81", "10.23", ".11", [("Boiling","9.11",".12"),("Microwaving","9.82",".08"),("Steaming","10.11",".18"),("Stir-frying","9.53",".12")]),
        ("Proline", "85", "7.35", ".04", [("Boiling","6.58",".04"),("Microwaving","7.01",".08"),("Steaming","7.24",".08"),("Stir-frying","6.82",".12")]),
    ]
    for compound_name, first_record_id, raw, raw_sd, cooked_values in amino_acid_specs:
        stagea_records = {
            row["Cooking_Method_Standardized"]: row
            for row in stage_a_rows
            if row.get("DOI") == "10.3390/molecules31162740"
            and row.get("Canonical_Compound_Name") == compound_name
        }
        for method, cooked, cooked_sd in cooked_values:
            record = stagea_records[method]
            medium, temp, minutes, power = pumpkin_conditions[method]
            pair_rows.append({
                "pair_id": f"P2-PUM-{record['Record_ID']}",
                "source_stagea_record_id": record["Record_ID"],
                "stagea_compound_group_id": record["Canonical_Molecular_ID"],
                "stageb_compound_id": "",
                "compound_name": compound_name,
                "food_matrix": "Cucurbita maxima leaves",
                "raw_state": "raw leaves; control",
                "cooking_method": method,
                "cooking_medium": medium,
                "temperature_c": temp,
                "time_min": minutes,
                "microwave_power_w": power,
                "raw_mean_mg_per_g": "", "raw_sd_mg_per_g": "",
                "cooked_mean_mg_per_g": "", "cooked_sd_mg_per_g": "",
                "measurement_unit": "mg/g dry weight",
                "raw_mean_value": raw, "raw_sd_value": raw_sd,
                "cooked_mean_value": cooked, "cooked_sd_value": cooked_sd,
                "replicates_n": "3",
                "concentration_ratio_percent": str((Decimal(cooked) / Decimal(raw) * 100).quantize(Decimal("0.01"))),
                "ratio_semantics": "apparent_concentration_ratio_not_total_mass_retention",
                "ratio_uncertainty": "not derived; replicate-level covariance unavailable",
                "evidence_class": "primary_observed_group_means",
                "not_model_prediction": "true",
                "source_doi": "10.3390/molecules31162740",
                "source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC13515228/",
                "source_locator": "Table 2; raw control and named cooking-treatment column",
                "limitations": "Three independent biological replicates; values reported on dry-weight basis. Apparent concentration ratio is not mass retention. Stage A row is provenance pointer only; values transcribed from primary table.",
            })
    write_csv(OUT / "observed_cooking_pairs.csv", list(pair_rows[0]), pair_rows)
    stage_a_by_record_id = {row["Record_ID"]: row for row in stage_a_rows}
    retention_crosscheck_discordances = [
        row["pair_id"] for row in pair_rows
        if (Decimal(row["concentration_ratio_percent"]) - Decimal(stage_a_by_record_id[row["source_stagea_record_id"]]["Retention_Final"])).copy_abs() > Decimal("0.01")
    ]

    fitted_artifacts = [
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "stageA").rglob("*")
        if path.is_file() and path.suffix.lower() in {".pkl", ".pickle", ".joblib", ".onnx", ".cbm"}
    ]
    model_runtime_packages = {name: importlib.util.find_spec(name) is not None for name in ("joblib", "numpy", "pandas", "sklearn", "xgboost")}
    stageb_model_hash = sha256(stageb_model_path) if stageb_model_path.exists() else ""
    stageb_model_hash_matches_manifest = bool(stageb_model_hash) and stageb_model_hash == stageb_model_manifest.get("artifact", {}).get("sha256", "")
    stageb_model_input_hash_matches_current = stageb_model_manifest.get("input", {}).get("sha256", "") == sha256(stage_a_input)
    oof_models = Counter(row["Model"] for row in oof_rows)
    strict_matches = [row for row in crosswalk if row["crosswalk_status"] == "STRICT_MATCH"]
    strict_covered = sum(row["phase1b_accepted_quantitative_coverage"] == "true" for row in strict_matches)
    summary = {
        "phase": "Stage C Phase 2 kickoff",
        "phase1b_release": "Phase1B-v1.3.0",
        "phase1b_closeout": "user accepted closure below 130 minimum",
        "stage_b_release": "StageB_V20_20261103",
        "stage_a_input_sha256": sha256(stage_a_input),
        "stage_b_manifest_sha256": sha256(STAGEB / "manifests/SHA256SUMS.json"),
        "stage_a_rows": len(stage_a_rows),
        "stage_a_molecular_groups": len(groups),
        "stage_a_oof_rows": len(oof_rows),
        "stage_a_oof_rows_by_model": dict(oof_models),
        "stage_a_qa_groups": stage_a_qa.get("unique_molecular_groups"),
        "stage_a_deployable_model_artifacts_found": len(fitted_artifacts),
        "stage_a_deployable_model_artifacts": fitted_artifacts,
        "stageb_selected_model_candidate_found": stageb_model_path.exists(),
        "stageb_selected_model_sha256_matches_manifest": stageb_model_hash_matches_manifest,
        "stageb_selected_model_input_sha256_matches_current_stagea": stageb_model_input_hash_matches_current,
        "stageb_selected_model_manifest_input_sha256": stageb_model_manifest.get("input", {}).get("sha256", ""),
        "current_stagea_input_sha256": sha256(stage_a_input),
        "inference_runtime_packages_available": model_runtime_packages,
        "stageb_model_inference_readiness": "READY" if stageb_model_hash_matches_manifest and stageb_model_input_hash_matches_current and all(model_runtime_packages.values()) else "BLOCKED_CHECKSUM_OR_RUNTIME_GATE",
        "stage_a_stage_b_crosswalk_status_counts": dict(sorted(statuses.items())),
        "identity_candidate_review_rows": len(review_rows),
        "identity_candidate_review_decisions": dict(sorted(Counter(row["review_decision"] for row in review_rows).items())),
        "strict_structure_crosswalk_groups": len(strict_matches),
        "stable_id_structure_crosswalk_groups_with_cid_discrepancy": statuses["STABLE_ID_STRUCTURE_MATCH_CID_DISCREPANCY"],
        "strict_structure_crosswalk_with_phase1b_coverage": strict_covered,
        "phase1b_food_records": phase1_validation["mapping_coverage"]["food_composition_records"],
        "phase1b_verified_compound_coverage": phase1_validation["mapping_coverage"]["compounds_with_verified_quantitative_food_data"],
        "stage_b_retention_source_records": len(source_retention),
        "phase2_retention_ledger_rows": len(evidence_rows),
        "phase2_primary_observed_cooking_pairs": len(pair_rows),
        "phase2_primary_observed_cooking_analytes": len({row["compound_name"] for row in pair_rows}),
        "phase2_stagea_retention_crosscheck_discordances": len(retention_crosscheck_discordances),
        "phase2_quantitative_retention_intervals": sum(bool(row["loss_low_percent"]) for row in evidence_rows),
        "phase2_cooked_concentrations_generated": 0,
        "phase2_status": "PRIMARY_OBSERVED_PAIRS_AND_IDENTITY_REVIEW_DOCUMENTED; STAGEB_MODEL_CANDIDATE_BLOCKED_BY_INPUT_HASH_AND_RUNTIME_GATES; NO_PHASE1B_CONCENTRATION_ADJUSTMENT",
    }
    (OUT / "phase2_intake_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
