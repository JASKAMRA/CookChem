#!/usr/bin/env python3
"""Independently check the 117 Phase 2 source-pair transcriptions."""
from __future__ import annotations

import csv
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "stageC/phase2/data/observed_cooking_pairs.csv"
OUTPUT = ROOT / "stageC/reports/phase2/source_pair_audit_2026-11-03.csv"

# Values transcribed from original published Tables 1–3.  Each tuple is
# raw mean followed by boiling, microwave, steaming, and stir-frying means.
PUMPKIN_TABLES = {
    "Aspartic acid": (17.92, 15.86, 16.92, 17.41, 16.44, "Table 2", "mg/g dry weight"),
    "Threonine": (7.18, 6.22, 6.84, 7.02, 6.51, "Table 2", "mg/g dry weight"),
    "Serine": (7.62, 6.55, 7.18, 7.47, 6.83, "Table 2", "mg/g dry weight"),
    "Glutamic acid": (22.52, 20.64, 21.72, 22.14, 21.16, "Table 2", "mg/g dry weight"),
    "Glycine": (9.64, 8.41, 9.12, 9.42, 8.78, "Table 2", "mg/g dry weight"),
    "Alanine": (14.40, 12.62, 13.71, 14.03, 13.12, "Table 2", "mg/g dry weight"),
    "Cysteine": (1.95, 1.31, 1.62, 1.81, 1.49, "Table 2", "mg/g dry weight"),
    "Valine": (11.75, 10.21, 11.11, 11.53, 10.74, "Table 2", "mg/g dry weight"),
    "Methionine": (4.54, 3.66, 4.11, 4.38, 3.89, "Table 2", "mg/g dry weight"),
    "Isoleucine": (7.56, 6.64, 7.16, 7.41, 6.91, "Table 2", "mg/g dry weight"),
    "Leucine": (15.34, 13.74, 14.76, 15.18, 14.28, "Table 2", "mg/g dry weight"),
    "Tyrosine": (9.64, 8.61, 9.22, 9.52, 8.95, "Table 2", "mg/g dry weight"),
    "Phenylalanine": (11.59, 10.23, 11.02, 11.41, 10.67, "Table 2", "mg/g dry weight"),
    "Histidine": (6.42, 5.51, 6.01, 6.26, 5.76, "Table 2", "mg/g dry weight"),
    "Lysine": (13.91, 12.42, 13.28, 13.76, 12.84, "Table 2", "mg/g dry weight"),
    "Arginine": (10.23, 9.11, 9.82, 10.11, 9.53, "Table 2", "mg/g dry weight"),
    "Proline": (7.35, 6.58, 7.01, 7.24, 6.82, "Table 2", "mg/g dry weight"),
    "Sinapic acid": (29.57, 14.22, 28.58, 29.17, 15.34, "Table 3", "mg/100 g dry weight"),
    "Rutin": (28.15, 21.04, 27.78, 26.23, 20.45, "Table 3", "mg/100 g dry weight"),
    "Isoquercitrin": (7.76, 3.98, 7.11, 5.62, 5.11, "Table 3", "mg/100 g dry weight"),
    "Astragalin": (9.22, 5.46, 8.89, 7.85, 7.14, "Table 3", "mg/100 g dry weight"),
}
PUMPKIN_SDS = {
    "Aspartic acid": (.22,.18,.15,.12,.14), "Threonine": (.14,.08,.04,.04,.08),
    "Serine": (.08,.05,.06,.08,.08), "Glutamic acid": (.43,.32,.42,.28,.52),
    "Glycine": (.14,.18,.14,.18,.17), "Alanine": (.08,.14,.13,.12,.13),
    "Cysteine": (.04,.04,.02,.02,.02), "Valine": (.12,.14,.17,.15,.15),
    "Methionine": (.14,.12,.14,.14,.12), "Isoleucine": (.09,.08,.08,.06,.04),
    "Leucine": (.11,.18,.12,.12,.13), "Tyrosine": (.12,.12,.11,.11,.12),
    "Phenylalanine": (.12,.13,.12,.11,.13), "Histidine": (.04,.10,.08,.06,.04),
    "Lysine": (.12,.14,.16,.15,.12), "Arginine": (.11,.12,.08,.18,.12),
    "Proline": (.04,.04,.08,.08,.12), "Sinapic acid": (.82,.14,.28,.20,.16),
    "Rutin": (.42,.24,.22,.26,.44), "Isoquercitrin": (.22,.012,.31,.12,.11),
    "Astragalin": (.44,.62,.32,.42,.42),
}
PUMPKIN_TREATMENT_INDEX = {"Boiling": 1, "Microwaving": 2, "Steaming": 3, "Stir-frying": 4}
PUMPKIN_METHODS = {
    "Boiling": ("boiling", "150 mL distilled water/100 g leaves", "95 °C", "10 min"),
    "Microwaving": ("microwaving", "12 mL distilled water/100 g leaves", "not reported", "3 min; 700 W"),
    "Steaming": ("steaming", "steam; no direct water immersion", "98 °C", "10 min"),
    "Stir-frying": ("stir-frying", "10 mL extra-virgin olive oil/100 g leaves", "approximately 150 °C", "2 min"),
}

# raw, boiling (1/2/5/10), frying (1/2/5/10), microwaving (1/2/5)
# mean concentrations, as published in Table 1.
TURMERIC = {
    "Curcumin": (113.92, [125.33,102.93,164.67,204.00], [246.00,203.00,174.67,224.00], [200.67,73.50,35.97]),
    "Demethoxycurcumin": (40.27, [31.63,35.93,47.67,56.87], [35.33,45.30,28.50,55.13], [41.37,29.87,11.96]),
    "Bisdemethoxycurcumin": (42.90, [50.07,44.70,57.37,82.03], [38.50,51.93,34.90,67.77], [49.13,32.93,16.47]),
}
TURMERIC_SD = {
    "Curcumin": {"Boiling": (12.24,[9.61,8.30,17.50,21.38]), "Frying": (12.25,[12.77,23.43,22.37,26.96]), "Microwaving": (12.25,[18.88,9.56,2.07])},
    "Demethoxycurcumin": {"Boiling": (3.40,[3.52,4.61,4.44,5.97]), "Frying": (3.10,[3.95,4.28,2.17,4.70]), "Microwaving": (3.40,[4.48,3.80,1.90])},
    "Bisdemethoxycurcumin": {"Boiling": (3.87,[4.20,3.05,5.50,7.00]), "Frying": (3.87,[4.88,4.01,3.31,5.03]), "Microwaving": (3.87,[5.30,2.87,1.96])},
}


def close(a: str, b: float, tol: float = 0.011) -> bool:
    try:
        return abs(float(a) - b) <= tol
    except (TypeError, ValueError):
        return False


def audit_row(row: dict[str, str]) -> dict[str, str]:
    doi = row["source_doi"]
    method = row["cooking_method"]
    compound = row["compound_name"]
    errors: list[str] = []
    basis_warning = False
    if doi == "10.3390/molecules31162740":
        expected = PUMPKIN_TABLES.get(compound)
        if expected is None or method not in PUMPKIN_METHODS:
            errors.append("unknown_compound_or_treatment")
            expected_mean = expected_sd = None
            table, unit = "Table 2/3", "not established"
        else:
            values = {"Boiling": expected[1], "Microwaving": expected[2], "Steaming": expected[3], "Stir-frying": expected[4]}
            expected_mean = values[method]
            expected_sd = None  # SD is retained in source table; pair file has it.
            table, unit = expected[5], expected[6]
            _, expected_medium, expected_temperature, expected_condition = PUMPKIN_METHODS[method]
            if row["food_matrix"] != "Cucurbita maxima leaves": errors.append("food_identity_differs_from_primary_source")
            if "raw" not in row["raw_state"].lower(): errors.append("raw_control_state_not_documented")
            if method.lower() not in row["cooking_method"].lower(): errors.append("cooking_method_differs_from_primary_source")
            if row["time_min"] != expected_condition.split()[0]: errors.append("cooking_duration_differs_from_primary_source")
            if expected_temperature == "not reported":
                if row["temperature_c"].strip(): errors.append("temperature_reported_where_source_does_not_report_it")
            else:
                expected_temp_number = re.search(r"[0-9]+(?:\.[0-9]+)?", expected_temperature)
                if not expected_temp_number or not close(row["temperature_c"], float(expected_temp_number.group())):
                    errors.append("temperature_differs_from_primary_source")
            medium = row["cooking_medium"].lower()
            if method == "Boiling" and "water" not in medium: errors.append("cooking_medium_differs_from_primary_source")
            if method == "Microwaving" and ("12 ml" not in medium or "distilled water" not in medium): errors.append("cooking_medium_differs_from_primary_source")
            if method == "Steaming" and "steam" not in medium: errors.append("cooking_medium_differs_from_primary_source")
            if method == "Stir-frying" and "olive oil" not in medium: errors.append("cooking_medium_differs_from_primary_source")
            if method == "Microwaving" and row["microwave_power_w"] != "700": errors.append("microwave_power_differs_from_primary_source")
            if method != "Microwaving" and row["microwave_power_w"].strip(): errors.append("unexpected_microwave_power")
            if not close(row["raw_mean_value"], expected[0]): errors.append("raw_mean_differs_from_primary_table")
            if not close(row["cooked_mean_value"], expected_mean): errors.append("cooked_mean_differs_from_primary_table")
            sds = PUMPKIN_SDS[compound]
            sd_idx = PUMPKIN_TREATMENT_INDEX[method]
            if not close(row["raw_sd_value"], sds[0]): errors.append("raw_sd_differs_from_primary_table")
            if not close(row["cooked_sd_value"], sds[sd_idx]): errors.append("cooked_sd_differs_from_primary_table")
            if row["measurement_unit"].strip().lower() != unit.lower(): errors.append("unit_differs_from_primary_table")
            if row["replicates_n"] != "3": errors.append("replicate_count_differs_from_primary_table")
        food_state = "fresh leaves; raw control or cooked leaves; post-cook samples frozen, lyophilized, ground"
        basis = "dry weight; reported mg/g DW for amino acids and mg/100 g DW for phenolics"
        prep = "100 g leaves; boiled 150 mL water/95 °C/10 min; steamed 98 °C/10 min; microwave 12 mL water/700 W/3 min; stir-fry 10 mL EVOO/approximately 150 °C/2 min"
        analytical = "n=3 biological replicates, each pooled from 5 plants; analytical triplicates; mean ± SD. Amino acids: acid hydrolysis/amino-acid analyzer; phenolics: HPLC-DAD. Cooking water/condensate/oil discarded."
        meaning = "Apparent concentration ratio on dry-weight basis; not total mass retention because cooked edible yield and discarded-medium analyte were not measured."
        source_url = "https://pmc.ncbi.nlm.nih.gov/articles/PMC13515228/"
        locator = f"{table}; Methods §§3.1–3.5; statistical methods §3.12"
        if row["ratio_semantics"] != "apparent_concentration_ratio_not_total_mass_retention": errors.append("ratio_semantics_not_explicit_apparent_ratio")
    elif doi == "10.3390/foods12163086":
        expected = TURMERIC.get(compound)
        if expected is None:
            errors.append("unknown_curcuminoid")
            expected_mean = None
        else:
            if row["food_matrix"] != "Curcuma longa rhizome": errors.append("food_identity_differs_from_primary_source")
            if "fresh" not in row["raw_state"].lower(): errors.append("raw_state_differs_from_primary_source")
            if method not in {"Boiling", "Frying", "Microwaving"}: errors.append("cooking_method_differs_from_primary_source")
            t = int(row["time_min"])
            if method == "Boiling": idx = t - 1 if t in (1,2) else (2 if t == 5 else 3)
            elif method == "Frying": idx = t - 1 if t in (1,2) else (2 if t == 5 else 3)
            elif method == "Microwaving": idx = t - 1 if t in (1,2) else 2
            else: idx = -1
            series = expected[1] if method == "Boiling" else expected[2] if method == "Frying" else expected[3] if method == "Microwaving" else []
            expected_mean = series[idx] if 0 <= idx < len(series) else None
            if expected_mean is None:
                errors.append("treatment_missing_from_primary_table")
            else:
                if not close(row["raw_mean_value"], expected[0]): errors.append("raw_mean_differs_from_primary_table")
                if not close(row["cooked_mean_value"], expected_mean): errors.append("cooked_mean_differs_from_primary_table")
                sd_data = TURMERIC_SD[compound][method]
                sd_idx = idx
                if not close(row["raw_sd_value"], sd_data[0]): errors.append("raw_sd_differs_from_primary_table")
                if not close(row["cooked_sd_value"], sd_data[1][sd_idx]): errors.append("cooked_sd_differs_from_primary_table")
                if row["replicates_n"] != "3": errors.append("replicate_count_differs_from_primary_table")
            # The source table labels the result as mg/g plant material. Fresh
            # rhizome is the starting material, but the cooked-sample denominator
            # is not explicit enough to relabel this as mg/g fresh rhizome.
            if row["measurement_unit"].strip().lower() != "mg/g plant material": errors.append("unit_differs_from_primary_table")
            else: basis_warning = True
            if method == "Boiling":
                if not close(row["temperature_c"], 100): errors.append("temperature_differs_from_primary_source")
                if "water" not in row["cooking_medium"].lower(): errors.append("cooking_medium_differs_from_primary_source")
                if row["microwave_power_w"].strip(): errors.append("unexpected_microwave_power")
            elif method == "Frying":
                if row["temperature_c"].strip(): errors.append("temperature_reported_where_source_does_not_report_it")
                if "ceramic" not in row["cooking_medium"].lower() or "no oil" not in row["cooking_medium"].lower(): errors.append("frying_medium_differs_from_primary_source")
                if row["microwave_power_w"].strip(): errors.append("unexpected_microwave_power")
            elif method == "Microwaving":
                if row["temperature_c"].strip(): errors.append("temperature_reported_where_source_does_not_report_it")
                if row["microwave_power_w"] != "800": errors.append("microwave_power_differs_from_primary_source")
                if "dry" not in row["cooking_medium"].lower(): errors.append("microwave_medium_differs_from_primary_source")
        table, unit = "Table 1", "mg/g plant material (source wording); cooked-sample denominator requires caution"
        food_state = "2 g fresh rhizome slices; cooked sample state as processed in the study"
        basis = "Table 1 reports mg/g plant material; Methods identify fresh rhizome as the starting material, but the post-cooking denominator is not explicitly defined; no dry-weight conversion or cooked yield reported"
        prep = "boil in deionized water at 100 °C; dry ceramic pan frying without oil; microwave at 800 W; 1/2/5/10 min; 10-min microwave charred and excluded"
        analytical = "n=3; reported mean ± SD. Methanol extraction (10 mL/sample), ultrasound 10 min, centrifuged twice, filtered; HPLC with LC-MS qualitative identification."
        meaning = "Apparent concentration ratio from condition-level means; not total mass retention because cooked mass yield is not reported."
        source_url = "https://pmc.ncbi.nlm.nih.gov/articles/PMC10453412/"
        locator = "Table 1; Methods §§2.1–2.4; Results §3"
        if row["ratio_semantics"] != "concentration_ratio_not_mass_retention": errors.append("ratio_semantics_not_explicit_apparent_ratio")
    else:
        errors.append("unrecognized_primary_source")
        expected_mean = None
        table, unit, food_state, basis, prep, analytical, meaning, source_url, locator = ("", "", "", "", "", "", "", "", "")

    try:
        ratio = float(row["cooked_mean_value"]) / float(row["raw_mean_value"])
        pct = ratio * 100
        if abs(float(row["concentration_ratio_percent"]) - pct) > 0.011:
            errors.append("stored_ratio_differs_from_independent_recalculation")
    except (ValueError, ZeroDivisionError):
        ratio = pct = float("nan")
        errors.append("ratio_not_calculable")

    if row["temperature_c"].strip() == "" and method == "Frying" and doi == "10.3390/foods12163086":
        temp_assessment = "not reported by source"
    elif row["temperature_c"].strip() == "" and method == "Microwaving" and doi == "10.3390/foods12163086":
        temp_assessment = "not reported by source; microwave power recorded"
    elif row["temperature_c"].strip() == "" and method == "Microwaving" and doi == "10.3390/molecules31162740":
        temp_assessment = "not reported; power 700 W and time 3 min reported"
    else:
        temp_assessment = row["temperature_c"] + (" °C" if row["temperature_c"].strip() else "not reported")
    verdict = ("VERIFIED_WITH_BASIS_LIMITATION" if basis_warning else "VERIFIED_AGAINST_PRIMARY_TABLE") if not errors else "REVIEW_REQUIRED"
    unit_assessment = ("Existing field says fresh-rhizome basis; source says mg/g plant material but does not explicitly state the post-cooking denominator. Retain source wording and treat basis compatibility as unresolved." if basis_warning else "Existing unit label agrees with the primary table basis.")
    return {
        **row,
        "source_verification_status": verdict,
        "source_table_or_locator": locator,
        "source_food_state": food_state,
        "source_measurement_basis": basis,
        "source_reported_unit": unit,
        "existing_measurement_unit_field_assessment": unit_assessment,
        "source_cooking_conditions": prep,
        "source_temperature_assessment": temp_assessment,
        "source_replicate_and_statistic_definition": analytical,
        "source_extraction_and_analytical_method": analytical,
        "source_mass_retention_interpretation": meaning,
        "independently_recalculated_ratio": f"{ratio:.10f}",
        "independently_recalculated_ratio_percent": f"{pct:.6f}",
        "primary_source_url": source_url,
        "audit_error_codes": ";".join(errors),
    }


def main(input_path: Path = INPUT, output_path: Path = OUTPUT) -> None:
    with input_path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    audited = [audit_row(r) for r in rows]
    if len(audited) != 117:
        raise SystemExit(f"Expected 117 source pairs, found {len(audited)}")
    accepted_statuses = {"VERIFIED_AGAINST_PRIMARY_TABLE", "VERIFIED_WITH_BASIS_LIMITATION"}
    if any(r["source_verification_status"] not in accepted_statuses for r in audited):
        failures = [f"{r['pair_id']}:{r['audit_error_codes']}" for r in audited if r["audit_error_codes"]]
        raise SystemExit("Source pair audit failed: " + ", ".join(failures))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(audited[0])
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(audited)
    print(f"Verified {len(audited)} source pairs against original Tables 1–3; ratios independently recalculated.")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT, help="source-pair CSV")
    parser.add_argument("--output", type=Path, default=OUTPUT, help="record-level audit CSV")
    args = parser.parse_args()
    main(args.input, args.output)
