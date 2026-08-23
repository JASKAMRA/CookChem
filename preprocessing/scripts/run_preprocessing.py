from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
INTERMEDIATE_DIR = PROJECT_ROOT / "data" / "preprocessing" / "intermediate"
FINAL_DIR = PROJECT_ROOT / "data" / "preprocessing" / "final"
REPORT_DIR = PROJECT_ROOT / "preprocessing" / "reports"

REQUIRED_COLUMNS = ["Record_ID", "Paper_ID", "DOI", "Food_Name", "Compound_Name", "Compound_Class", "Cooking_Method", "Initial_Concentration", "Initial_Unit", "Final_Concentration", "Final_Unit", "Retention_Percent", "Degradation_Percent", "Assay_Method"]
NUMERIC_COLUMNS = ["Year", "PubChem_CID", "Temperature_C", "Cooking_Time_min", "Pressure_kPa", "Microwave_Power_W", "Sample_Weight_g", "Initial_Concentration", "Final_Concentration", "Retention_Percent", "Degradation_Percent", "Replicates_n", "Molecular_Weight", "LogP", "TPSA", "HBond_Donors", "HBond_Acceptors", "Rotatable_Bonds", "Aromatic_Rings", "Hydroxyl_Groups", "Heavy_Atom_Count"]
TEXT_COLUMNS = ["Record_ID", "Paper_ID", "DOI", "Authors", "Journal", "Country", "Food_Name", "Scientific_Name", "Plant_Part", "Compound_Name", "Compound_Class", "SMILES", "Cooking_Method", "Cooking_Medium", "Oil_Type", "Initial_Unit", "Final_Unit", "Assay_Method", "Notes"]
COOKING_METHOD_MAP = {"steam": "Steaming", "steaming": "Steaming", "boiling": "Boiling", "microwaving": "Microwaving", "frying": "Frying", "deep-frying": "Deep-frying", "deep frying": "Deep-frying", "air frying": "Air frying", "stir-frying": "Stir-frying", "stir frying": "Stir-frying", "sauting": "Sauteing", "saut eing": "Sauteing", "sauteing": "Sauteing", "sous-vide": "Sous-vide", "sous vide": "Sous-vide", "pressure cooking": "Pressure cooking", "baking": "Baking", "roasting": "Roasting", "grilling": "Grilling", "blanching": "Blanching", "pasteurization": "Pasteurization"}
UNIT_MAP = {"% of raw content": "% of raw content", "% of raw content (peak area)": "% of raw content (peak area)", "mg/100g": "mg/100g", "mg/100g dw": "mg/100g DW", "mg/100g d.w.": "mg/100g DW", "mg/100 g dw": "mg/100g DW", "mg/g": "mg/g", "mg/g fresh rhizome": "mg/g fresh rhizome", "ug/100g": "ug/100g", "microg/100g": "ug/100g", "ug/g": "ug/g", "microg/g": "ug/g", "mg/kg": "mg/kg", "mg/100ml": "mg/100mL", "mg gae/100g": "mg GAE/100g", "mg gae/100g dw": "mg GAE/100g DW", "mg gae/g": "mg GAE/g", "mg gae/150g": "mg GAE/150g", "mg qe/100g": "mg QE/100g", "mg cae/g": "mg CAE/g"}

def clean_text(value: Any) -> Any:
    if pd.isna(value):
        return value
    return re.sub(r"\s+", " ", str(value).strip())

def normalized_key(value: Any) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).strip().lower())

def standardize_cooking_method(value: Any) -> Any:
    if pd.isna(value):
        return value
    text = clean_text(value)
    key = normalized_key(text).replace("_", " ").replace("�", "")
    return COOKING_METHOD_MAP.get(key, text)

def standardize_unit(value: Any) -> Any:
    if pd.isna(value):
        return value
    text = clean_text(value)
    key = normalized_key(text).replace("µ", "u").replace("�", "u")
    return UNIT_MAP.get(key, text)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--sheet", default=None)
    parser.add_argument("--retention-tolerance", type=float, default=2.0)
    return parser.parse_args()

def read_dataset(path: Path, sheet: str | int | None) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        xl = pd.ExcelFile(path)
        selected = sheet if sheet is not None else xl.sheet_names[0]
        if isinstance(selected, str) and selected.isdigit():
            selected = int(selected)
        return pd.read_excel(path, sheet_name=selected)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported input type: {path.suffix}")

def resolve_input(input_path: Path | None) -> Path:
    if input_path is not None:
        p = input_path if input_path.is_absolute() else PROJECT_ROOT / input_path
        if not p.exists():
            raise FileNotFoundError(p)
        return p
    preferred = RAW_DIR / "CookChem_Dataset_Molecular_Data_Filled.xlsx"
    if preferred.exists():
        return preferred
    candidates = sorted([*RAW_DIR.glob("*.xlsx"), *RAW_DIR.glob("*.xls"), *RAW_DIR.glob("*.csv")], key=lambda p: p.stat().st_size, reverse=True)
    if not candidates:
        raise FileNotFoundError(f"No raw Excel/CSV files found in {RAW_DIR}")
    return candidates[0]

def require_columns(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

def prepare(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy(deep=True)
    for c in TEXT_COLUMNS:
        if c in out.columns:
            out[c] = out[c].map(clean_text)
    for c in NUMERIC_COLUMNS:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    out["Food_Name_Standardized"] = out["Food_Name"].map(clean_text)
    out["Compound_Name_Standardized"] = out["Compound_Name"].map(clean_text)
    out["Cooking_Method_Standardized"] = out["Cooking_Method"].map(standardize_cooking_method)
    out["Initial_Unit_Standardized"] = out["Initial_Unit"].map(standardize_unit)
    out["Final_Unit_Standardized"] = out["Final_Unit"].map(standardize_unit)
    return out

def add_flags(df: pd.DataFrame, tolerance: float) -> pd.DataFrame:
    out = df.copy(deep=True)
    out["Flag_Missing_Required_Field"] = out[REQUIRED_COLUMNS].isna().any(axis=1)
    out["Flag_Retention_GT_100"] = out["Retention_Percent"] > 100
    out["Flag_Retention_GT_200"] = out["Retention_Percent"] > 200
    out["Flag_Retention_GT_500"] = out["Retention_Percent"] > 500
    out["Flag_Retention_Negative"] = out["Retention_Percent"] < 0
    out["Flag_Degradation_Retention_Sum_Check"] = (out["Retention_Percent"] + out["Degradation_Percent"] - 100).abs() > tolerance
    out["Flag_Initial_Final_Unit_Mismatch"] = out["Initial_Unit_Standardized"].notna() & out["Final_Unit_Standardized"].notna() & (out["Initial_Unit_Standardized"] != out["Final_Unit_Standardized"])
    comparable = out["Initial_Unit_Standardized"].notna() & out["Final_Unit_Standardized"].notna() & (out["Initial_Unit_Standardized"] == out["Final_Unit_Standardized"]) & out["Initial_Concentration"].notna() & out["Final_Concentration"].notna() & (out["Initial_Concentration"] != 0)
    out["Calculated_Retention_Percent"] = pd.NA
    out.loc[comparable, "Calculated_Retention_Percent"] = out.loc[comparable, "Final_Concentration"] / out.loc[comparable, "Initial_Concentration"] * 100
    out["Retention_Calculation_Delta"] = pd.NA
    out.loc[comparable, "Retention_Calculation_Delta"] = pd.to_numeric(out.loc[comparable, "Calculated_Retention_Percent"]) - out.loc[comparable, "Retention_Percent"]
    out["Flag_Retention_Calculation_Mismatch"] = False
    out.loc[comparable, "Flag_Retention_Calculation_Mismatch"] = pd.to_numeric(out.loc[comparable, "Retention_Calculation_Delta"]).abs() > tolerance
    out["Flag_Retention_Calculation_Not_Checkable"] = ~comparable
    out["Flag_Assay_Method_Missing"] = out["Assay_Method"].isna()
    out["Flag_PubChem_CID_Missing"] = out.get("PubChem_CID", pd.Series(index=out.index)).isna()
    out["Flag_SMILES_Missing"] = out.get("SMILES", pd.Series(index=out.index)).isna()
    descriptor_cols = [c for c in ["Molecular_Weight", "LogP", "TPSA", "HBond_Donors", "HBond_Acceptors", "Rotatable_Bonds", "Aromatic_Rings", "Hydroxyl_Groups", "Heavy_Atom_Count"] if c in out.columns]
    out["Flag_Molecular_Descriptor_Incomplete"] = out[descriptor_cols].isna().any(axis=1) if descriptor_cols else True
    text_cols = [c for c in TEXT_COLUMNS if c in out.columns]
    out["Flag_Encoding_Suspect"] = out[text_cols].astype("string", errors="ignore").apply(lambda r: r.astype(str).str.contains("�", regex=False).any(), axis=1)
    keys = ["Paper_ID", "Food_Name_Standardized", "Compound_Name_Standardized", "Cooking_Method_Standardized", "Temperature_C", "Cooking_Time_min", "Initial_Concentration", "Final_Concentration", "Retention_Percent"]
    out["Flag_Potential_Duplicate_Key"] = out.duplicated(subset=keys, keep=False)
    flag_cols = [c for c in out.columns if c.startswith("Flag_")]
    out["Review_Flag_Count"] = out[flag_cols].sum(axis=1)
    out["Needs_Source_Verification"] = out["Review_Flag_Count"] > 0
    return out

def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    d = df.fillna("").astype(str)
    cols = list(d.columns)
    return "\n".join(["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |", *["| " + " | ".join(row[c] for c in cols) + " |" for _, row in d.iterrows()]])

def main() -> None:
    args = parse_args()
    INTERMEDIATE_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    input_path = resolve_input(args.input)
    raw = read_dataset(input_path, args.sheet)
    require_columns(raw)
    processed = add_flags(prepare(raw), args.retention_tolerance)
    missingness = pd.DataFrame({"column": processed.columns, "missing_count": processed.isna().sum().values, "missing_percent": (processed.isna().mean().values * 100).round(2), "dtype": [str(t) for t in processed.dtypes]})
    flag_summary = pd.DataFrame([{"flag": c, "count": int(processed[c].fillna(False).sum()), "percent": round(float(processed[c].fillna(False).mean() * 100), 2)} for c in processed.columns if c.startswith("Flag_")]).sort_values("count", ascending=False)
    duplicate_keys = ["Paper_ID", "Food_Name_Standardized", "Compound_Name_Standardized", "Cooking_Method_Standardized", "Temperature_C", "Cooking_Time_min", "Initial_Concentration", "Final_Concentration", "Retention_Percent"]
    duplicate_review = processed[processed.duplicated(subset=duplicate_keys, keep=False)].sort_values(duplicate_keys)
    outputs = {
        "validation_flags": INTERMEDIATE_DIR / "cookchem_preprocessing_validation_flags.csv",
        "missingness": INTERMEDIATE_DIR / "missingness_report.csv",
        "duplicates": INTERMEDIATE_DIR / "duplicate_review.csv",
        "flag_summary": INTERMEDIATE_DIR / "validation_flag_summary.csv",
        "final_csv": FINAL_DIR / "cookchem_preprocessed_dataset.csv",
        "final_xlsx": FINAL_DIR / "cookchem_preprocessed_dataset.xlsx",
        "manifest": FINAL_DIR / "preprocessing_manifest.json",
    }
    processed.to_csv(outputs["validation_flags"], index=False)
    missingness.to_csv(outputs["missingness"], index=False)
    duplicate_review.to_csv(outputs["duplicates"], index=False)
    flag_summary.to_csv(outputs["flag_summary"], index=False)
    processed.to_csv(outputs["final_csv"], index=False)
    processed.to_excel(outputs["final_xlsx"], index=False)
    manifest = {"generated_at_utc": datetime.now(timezone.utc).isoformat(), "input_file": str(input_path.relative_to(PROJECT_ROOT)), "input_rows": int(len(raw)), "input_columns": int(len(raw.columns)), "output_rows": int(len(processed)), "output_columns": int(len(processed.columns)), "retention_tolerance_percentage_points": args.retention_tolerance, "raw_data_modified": False, "rows_deleted": 0, "molecular_descriptors_regenerated": False, "external_lookups_performed": False}
    outputs["manifest"].write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    report = f"""# CookChem Preprocessing Report\n\nGenerated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n## Input\n\n- Source file: `{input_path.relative_to(PROJECT_ROOT)}`\n- Raw rows: {len(raw)}\n- Raw columns: {len(raw.columns)}\n\nThe raw file was read only. It was not overwritten or modified.\n\n## Retention Summary\n\n- Minimum retention: {processed['Retention_Percent'].min()}\n- Median retention: {processed['Retention_Percent'].median()}\n- Mean retention: {round(float(processed['Retention_Percent'].mean()), 4)}\n- Maximum retention: {processed['Retention_Percent'].max()}\n- Records with retention >100%: {int((processed['Retention_Percent'] > 100).sum())}\n- Records with retention >200%: {int((processed['Retention_Percent'] > 200).sum())}\n- Records with retention >500%: {int((processed['Retention_Percent'] > 500).sum())}\n\nRetention values greater than 100% were flagged for review, not removed.\n\n## Duplicate Review\n\n{len(duplicate_review)} records were flagged for duplicate review.\n\n## Top Missingness\n\n{markdown_table(missingness.sort_values('missing_count', ascending=False).head(15))}\n\n## Validation Flag Summary\n\n{markdown_table(flag_summary)}\n\n## Scientific Handling Rules Applied\n\n- Source-reported columns were preserved.\n- Standardized values were added in new columns.\n- Missing values were not invented.\n- Retention >100% was not treated as an automatic error.\n- Raw data was not overwritten.\n- Molecular descriptors were not regenerated.\n- No external paper or PubChem lookup was performed.\n"""
    (REPORT_DIR / "preprocessing_report.md").write_text(report, encoding="utf-8")
    print("CookChem preprocessing complete.")
    print(f"Input: {input_path.relative_to(PROJECT_ROOT)}")
    print(f"Rows: {len(raw)} -> {len(processed)}")
    print(f"Final CSV: {outputs['final_csv'].relative_to(PROJECT_ROOT)}")
    print(f"Report: {(REPORT_DIR / 'preprocessing_report.md').relative_to(PROJECT_ROOT)}")

if __name__ == "__main__":
    main()
