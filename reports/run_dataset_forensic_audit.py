from __future__ import annotations

import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors

    RDKIT_AVAILABLE = True
except Exception:
    Chem = None
    Descriptors = None
    RDKIT_AVAILABLE = False


ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "data" / "raw" / "CookChem_Dataset_Molecular_Data_Ordered (2).xlsx"
REPORT_DIR = ROOT / "reports"
SUMMARY_JSON = REPORT_DIR / "dataset_audit_summary.json"
ISSUES_CSV = REPORT_DIR / "dataset_audit_issues.csv"
ISSUES_MD = REPORT_DIR / "dataset_audit_log.md"

REQUIRED_COLUMNS = [
    "Record_ID",
    "Paper_ID",
    "DOI",
    "Food_Name",
    "Compound_Name",
    "Compound_Class",
    "Cooking_Method",
    "Initial_Concentration",
    "Initial_Unit",
    "Final_Concentration",
    "Final_Unit",
    "Retention_Percent",
    "Degradation_Percent",
    "Assay_Method",
]
DESC_COLS = [
    "Molecular_Weight",
    "LogP",
    "TPSA",
    "HBond_Donors",
    "HBond_Acceptors",
    "Rotatable_Bonds",
    "Aromatic_Rings",
    "Hydroxyl_Groups",
    "Heavy_Atom_Count",
]
MINERAL_NAMES = {
    "Iron",
    "Calcium",
    "Sodium",
    "Potassium",
    "Magnesium",
    "Manganese",
    "Zinc",
    "Phosphorus",
    "Strontium",
}
AGGREGATE_PATTERNS = [
    r"^total\b",
    r"\btotal\b",
    r"compounds?$",
    r"phenolics?$",
    r"polyphenols?$",
    r"glucosinolates?$",
    r"anthocyanins?$",
    r"flavonoids?$",
    r"flavonols?$",
    r"acids, total$",
    r"derivatives",
    r"glycosides",
]
METHOD_ALIASES = {
    "steam": "Steaming",
    "steaming": "Steaming",
    "boiling": "Boiling",
    "microwaving": "Microwaving",
    "frying": "Frying",
    "deep frying": "Deep-frying",
    "deep-frying": "Deep-frying",
    "stir frying": "Stir-frying",
    "stir-frying": "Stir-frying",
    "air frying": "Air frying",
    "roasting": "Roasting",
    "baking": "Baking",
    "grilling": "Grilling",
    "pressure cooking": "Pressure cooking",
    "sous vide": "Sous-vide",
    "sous-vide": "Sous-vide",
    "pasteurization": "Pasteurization",
    "blanching": "Blanching",
    "sauteing": "Sauteing",
    "sauting": "Sauteing",
}
UNIT_MAP = {
    "% of raw content": "% of raw content",
    "% of raw content (peak area)": "% of raw content (peak area)",
    "mg/100g": "mg/100g",
    "mg/100g dw": "mg/100g DW",
    "mg/100g d.w.": "mg/100g DW",
    "mg/100 g dw": "mg/100g DW",
    "mg/g": "mg/g",
    "mg/g fresh rhizome": "mg/g fresh rhizome",
    "ug/100g": "ug/100g",
    "microg/100g": "ug/100g",
    "ug/g": "ug/g",
    "microg/g": "ug/g",
    "mg/kg": "mg/kg",
    "mg/100ml": "mg/100mL",
    "mg gae/100g": "mg GAE/100g",
    "mg gae/100g dw": "mg GAE/100g DW",
    "mg gae/g": "mg GAE/g",
    "mg gae/150g": "mg GAE/150g",
    "mg qe/100g": "mg QE/100g",
    "mg cae/g": "mg CAE/g",
}


def clean_text(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    return re.sub(r"\s+", " ", str(value).strip())


def norm_key(value: object) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).strip().lower())


def std_method(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    text = clean_text(value)
    key = norm_key(text).replace("_", " ").replace("�", "")
    return METHOD_ALIASES.get(key, text)


def std_unit(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    text = clean_text(value)
    key = norm_key(text).replace("µ", "u").replace("�", "u")
    return UNIT_MAP.get(key, text)


def pct(sorted_arr: list[float], p: float) -> float | None:
    if not sorted_arr:
        return None
    rank = max(1, math.ceil(p * len(sorted_arr)))
    return sorted_arr[rank - 1]


def as_rows(indexes: list[int]) -> str:
    return ",".join(str(i + 2) for i in indexes[:25]) + ("..." if len(indexes) > 25 else "")


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    wb = load_workbook(WORKBOOK, read_only=False, data_only=False)
    sheet_meta = []
    for ws in wb.worksheets:
        hidden_rows = sum(1 for _, dim in ws.row_dimensions.items() if dim.hidden)
        hidden_cols = sum(1 for _, dim in ws.column_dimensions.items() if dim.hidden)
        sheet_meta.append(
            {
                "sheet_name": ws.title,
                "max_row": ws.max_row,
                "max_column": ws.max_column,
                "hidden_rows": hidden_rows,
                "hidden_columns": hidden_cols,
                "merged_ranges": len(ws.merged_cells.ranges),
                "sheet_state": ws.sheet_state,
            }
        )

    sheet_name = wb.sheetnames[0]
    raw_df = pd.read_excel(WORKBOOK, sheet_name=sheet_name)
    df = raw_df.copy()

    text_cols = [
        "Record_ID",
        "Paper_ID",
        "DOI",
        "Authors",
        "Journal",
        "Country",
        "Food_Name",
        "Scientific_Name",
        "Plant_Part",
        "Compound_Name",
        "Compound_Class",
        "SMILES",
        "Cooking_Method",
        "Cooking_Medium",
        "Oil_Type",
        "Initial_Unit",
        "Final_Unit",
        "Assay_Method",
        "Notes",
        "Clean_Compound",
    ]
    numeric_cols = [
        "Year",
        "PubChem_CID",
        "Temperature_C",
        "Cooking_Time_min",
        "Pressure_kPa",
        "Microwave_Power_W",
        "Sample_Weight_g",
        "Initial_Concentration",
        "Final_Concentration",
        "Retention_Percent",
        "Degradation_Percent",
        "Replicates_n",
        "Molecular_Weight",
        "LogP",
        "TPSA",
        "HBond_Donors",
        "HBond_Acceptors",
        "Rotatable_Bonds",
        "Aromatic_Rings",
        "Hydroxyl_Groups",
        "Heavy_Atom_Count",
    ]

    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].map(clean_text)
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Clean_Compound_Standardized"] = df["Clean_Compound"].map(clean_text)
    df["Compound_Name_Standardized"] = df["Compound_Name"].map(clean_text)
    df["Food_Name_Standardized"] = df["Food_Name"].map(clean_text)
    df["Cooking_Method_Standardized_Audit"] = df["Cooking_Method"].map(std_method)
    df["Initial_Unit_Standardized_Audit"] = df["Initial_Unit"].map(std_unit)
    df["Final_Unit_Standardized_Audit"] = df["Final_Unit"].map(std_unit)

    column_profile = []
    for col in raw_df.columns:
        s = raw_df[col]
        column_profile.append(
            {
                "column": col,
                "pandas_dtype": str(s.dtype),
                "missing_count": int(s.isna().sum()),
                "missing_percent": round(float(s.isna().mean() * 100), 2),
                "all_empty": bool(s.isna().all()),
            }
        )

    normalized_headers = [re.sub(r"\s+", " ", str(c).strip().lower()) for c in raw_df.columns]
    duplicate_columns = [k for k, v in Counter(normalized_headers).items() if v > 1]
    suspicious_column_names = [
        c for c in raw_df.columns if "unnamed" in str(c).lower() or str(c).strip() == "" or str(c) != str(c).strip()
    ]
    empty_columns = [x["column"] for x in column_profile if x["all_empty"]]
    required_missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    encoding_suspect_rows = df.index[
        df.astype("string").apply(lambda col: col.str.contains("�", na=False)).any(axis=1)
    ].tolist()
    comma_decimal_candidates = []
    for col in raw_df.columns:
        s = raw_df[col].dropna().astype(str)
        if s.str.contains(r"^\d+,\d+$", regex=True).any():
            comma_decimal_candidates.append(col)

    exact_dup_rows = raw_df.index[raw_df.duplicated(keep=False)].tolist()
    near_key = [
        "Paper_ID",
        "Food_Name_Standardized",
        "Clean_Compound_Standardized",
        "Cooking_Method_Standardized_Audit",
        "Temperature_C",
        "Cooking_Time_min",
        "Initial_Concentration",
        "Final_Concentration",
    ]
    near_dup_rows = df.index[df.duplicated(subset=near_key, keep=False)].tolist()

    comparable = (
        df["Initial_Unit_Standardized_Audit"].notna()
        & df["Final_Unit_Standardized_Audit"].notna()
        & (df["Initial_Unit_Standardized_Audit"] == df["Final_Unit_Standardized_Audit"])
        & df["Initial_Concentration"].notna()
        & df["Final_Concentration"].notna()
        & (df["Initial_Concentration"] != 0)
    )
    df["Calculated_Retention_Audit"] = pd.NA
    df.loc[comparable, "Calculated_Retention_Audit"] = (
        df.loc[comparable, "Final_Concentration"] / df.loc[comparable, "Initial_Concentration"] * 100
    )
    df["Retention_Delta_Audit"] = pd.NA
    df.loc[comparable, "Retention_Delta_Audit"] = (
        pd.to_numeric(df.loc[comparable, "Calculated_Retention_Audit"]) - df.loc[comparable, "Retention_Percent"]
    )

    retention_mismatch = df.index[comparable & (df["Retention_Delta_Audit"].abs() > 2)].tolist()
    retention_not_checkable = df.index[~comparable & df["Retention_Percent"].notna()].tolist()
    ret_gt100 = df.index[df["Retention_Percent"] > 100].tolist()
    ret_gt200 = df.index[df["Retention_Percent"] > 200].tolist()
    ret_gt500 = df.index[df["Retention_Percent"] > 500].tolist()
    neg_ret = df.index[df["Retention_Percent"] < 0].tolist()
    neg_init = df.index[df["Initial_Concentration"] < 0].tolist()
    neg_final = df.index[df["Final_Concentration"] < 0].tolist()
    zero_init_ret_present = df.index[(df["Initial_Concentration"] == 0) & df["Retention_Percent"].notna()].tolist()
    final_present_ret_missing = df.index[df["Final_Concentration"].notna() & df["Retention_Percent"].isna()].tolist()
    deg_sum_mismatch = df.index[
        df["Retention_Percent"].notna()
        & df["Degradation_Percent"].notna()
        & ((df["Retention_Percent"] + df["Degradation_Percent"] - 100).abs() > 2)
    ].tolist()
    unit_mismatch_rows = df.index[
        df["Initial_Unit_Standardized_Audit"].notna()
        & df["Final_Unit_Standardized_Audit"].notna()
        & (df["Initial_Unit_Standardized_Audit"] != df["Final_Unit_Standardized_Audit"])
    ].tolist()

    missing_method = df.index[df["Cooking_Method"].isna()].tolist()
    missing_temp = df.index[df["Temperature_C"].isna()].tolist()
    missing_time = df.index[df["Cooking_Time_min"].isna()].tolist()
    frying_missing_oil = df.index[
        df["Cooking_Method_Standardized_Audit"].isin(
            ["Frying", "Deep-frying", "Stir-frying", "Air frying", "Sauteing"]
        )
        & df["Oil_Type"].isna()
    ].tolist()
    microwave_missing_power = df.index[
        df["Cooking_Method_Standardized_Audit"].eq("Microwaving") & df["Microwave_Power_W"].isna()
    ].tolist()
    pressure_missing_pressure = df.index[
        df["Cooking_Method_Standardized_Audit"].eq("Pressure cooking") & df["Pressure_kPa"].isna()
    ].tolist()
    suspicious_temp = df.index[
        df["Temperature_C"].notna() & ((df["Temperature_C"] < 0) | (df["Temperature_C"] > 300))
    ].tolist()
    suspicious_time = df.index[
        df["Cooking_Time_min"].notna() & ((df["Cooking_Time_min"] <= 0) | (df["Cooking_Time_min"] > 1440))
    ].tolist()

    method_alias_groups = defaultdict(set)
    for raw, std in zip(df["Cooking_Method"].dropna(), df["Cooking_Method_Standardized_Audit"].dropna()):
        method_alias_groups[std].add(raw)
    method_alias_issues = {k: sorted(v) for k, v in method_alias_groups.items() if len(v) > 1}

    food_variant_groups = defaultdict(set)
    food_norm = df["Food_Name"].dropna().map(lambda x: re.sub(r"[^a-z0-9]+", " ", x.lower()).strip())
    for raw, norm in zip(df["Food_Name"].dropna(), food_norm):
        food_variant_groups[norm].add(raw)
    food_variants = {k: sorted(v) for k, v in food_variant_groups.items() if len(v) > 1}

    class_variant_groups = defaultdict(set)
    for raw in df["Compound_Class"].dropna():
        class_variant_groups[raw.lower()].add(raw)
    class_variants = {k: sorted(v) for k, v in class_variant_groups.items() if len(v) > 1}

    compound_variant_groups = defaultdict(set)
    for clean_name, raw_name in zip(df["Clean_Compound_Standardized"], df["Compound_Name_Standardized"]):
        compound_variant_groups[clean_name].add(raw_name)
    compound_multi_variant = {k: sorted(v) for k, v in compound_variant_groups.items() if len(v) > 1}

    compound_classification = []
    for name, g in df.groupby("Clean_Compound_Standardized", dropna=True):
        lname = name.lower()
        classification = "UNKNOWN"
        if name in MINERAL_NAMES:
            classification = "NUTRIENT/MINERAL"
        elif any(re.search(pat, lname) for pat in AGGREGATE_PATTERNS):
            classification = "AGGREGATE_MEASUREMENT"
        elif lname == "resistant starch":
            classification = "MIXTURE/COMPLEX"
        elif lname == "proanthocyanidins":
            classification = "AGGREGATE_MEASUREMENT"
        elif lname in {"total phenolics", "total phenolic compounds", "total phenolic"}:
            classification = "AGGREGATE_MEASUREMENT"
        compound_classification.append(
            {
                "compound": name,
                "classification": classification,
                "rows": int(len(g)),
                "raw_name_variants": sorted(compound_variant_groups[name]),
            }
        )
    aggregate_compounds = [
        x
        for x in compound_classification
        if x["classification"] in {"AGGREGATE_MEASUREMENT", "MIXTURE/COMPLEX", "NUTRIENT/MINERAL"}
    ]

    smiles_rows = []
    same_name_diff_structures = []
    diff_names_same_structure = defaultdict(set)
    for idx, row in df.iterrows():
        smi = row.get("SMILES")
        canonical = None
        valid = False
        mw_calc = None
        if pd.notna(smi) and str(smi).strip() and RDKIT_AVAILABLE:
            mol = Chem.MolFromSmiles(str(smi).strip())
            if mol is not None:
                valid = True
                canonical = Chem.MolToSmiles(mol, canonical=True)
                mw_calc = Descriptors.MolWt(mol)
                diff_names_same_structure[canonical].add(row["Clean_Compound_Standardized"])
        smiles_rows.append(
            {
                "row": int(idx) + 2,
                "clean_compound": row["Clean_Compound_Standardized"],
                "smiles": "" if pd.isna(smi) else str(smi),
                "valid": valid,
                "canonical_smiles": canonical,
                "mw_calc": mw_calc,
            }
        )
    smiles_df = pd.DataFrame(smiles_rows)
    invalid_smiles_rows = smiles_df.loc[
        smiles_df["smiles"].astype(str).str.strip().ne("") & ~smiles_df["valid"], "row"
    ].tolist()
    empty_smiles_rows = smiles_df.loc[smiles_df["smiles"].astype(str).str.strip().eq(""), "row"].tolist()
    for name, g in smiles_df.groupby("clean_compound", dropna=True):
        uniq = sorted(set(x for x in g["canonical_smiles"].dropna().tolist() if x))
        if len(uniq) > 1:
            same_name_diff_structures.append(
                {
                    "compound": name,
                    "distinct_canonical_smiles": len(uniq),
                    "canonical_smiles": uniq,
                }
            )
    shared_structure_groups = [
        {"canonical_smiles": k, "clean_compounds": sorted(v)}
        for k, v in diff_names_same_structure.items()
        if len(v) > 1
    ]

    descriptor_conflicts = []
    incomplete_descriptor_compounds = []
    for name, g in df.groupby("Clean_Compound_Standardized", dropna=True):
        distinct_vectors = g[DESC_COLS].astype(str).drop_duplicates()
        distinct_smiles = g["SMILES"].dropna().nunique()
        distinct_mw = g["Molecular_Weight"].dropna().round(6).nunique()
        distinct_logp = g["LogP"].dropna().round(6).nunique()
        distinct_tpsa = g["TPSA"].dropna().round(6).nunique()
        missing_cols = [c for c in DESC_COLS if g[c].isna().any()]
        if missing_cols:
            incomplete_descriptor_compounds.append(
                {"compound": name, "rows": int(len(g)), "missing_descriptor_columns": missing_cols}
            )
        if len(distinct_vectors) > 1 or distinct_smiles > 1:
            if distinct_smiles <= 1 and distinct_mw <= 1 and distinct_logp <= 1 and distinct_tpsa <= 1:
                conflict_class = "A. Harmless formatting/rounding"
            elif distinct_smiles <= 1:
                conflict_class = "B. Different valid representations of the same molecule"
            elif any(x in name.lower() for x in ["total", "compounds", "starch"]):
                conflict_class = "D. Ambiguous compound"
            else:
                conflict_class = "C. Different molecular identities incorrectly sharing one name"
            descriptor_conflicts.append(
                {
                    "compound": name,
                    "rows": int(len(g)),
                    "distinct_smiles": int(distinct_smiles),
                    "distinct_molecular_weight": int(distinct_mw),
                    "distinct_logp": int(distinct_logp),
                    "distinct_tpsa": int(distinct_tpsa),
                    "distinct_descriptor_vectors": int(len(distinct_vectors)),
                    "classification": conflict_class,
                }
            )

    obs_per_compound = df.groupby("Clean_Compound_Standardized", dropna=True).size().sort_values(ascending=False)
    obs_per_food = df.groupby("Food_Name_Standardized", dropna=True).size().sort_values(ascending=False)
    obs_per_method = (
        df.groupby("Cooking_Method_Standardized_Audit", dropna=True).size().sort_values(ascending=False)
    )
    obs_per_class = df.groupby("Compound_Class", dropna=True).size().sort_values(ascending=False)

    issues = []
    issue_counter = 1

    def add_issue(
        severity: str,
        category: str,
        affected_rows: str,
        affected_compounds: str,
        column: str,
        issue_type: str,
        description: str,
        evidence: str,
        recommended_action: str,
        source_verification_required: str = "No",
    ) -> None:
        nonlocal issue_counter
        issue_id = f"AUDIT-{issue_counter:03d}"
        issue_counter += 1
        issues.append(
            {
                "Issue_ID": issue_id,
                "Severity": severity,
                "Category": category,
                "Status": "OPEN",
                "Affected_Rows": affected_rows,
                "Affected_Compounds": affected_compounds,
                "Column": column,
                "Issue_Type": issue_type,
                "Description": description,
                "Evidence": evidence,
                "Recommended_Action": recommended_action,
                "Resolution": "",
                "Source_Verification_Required": source_verification_required,
            }
        )

    if required_missing:
        add_issue(
            "Critical",
            "Structure",
            "ALL",
            "ALL",
            "Columns",
            "Missing required columns",
            "Required preprocessing columns are missing.",
            f"Missing columns: {required_missing}",
            "Restore the required schema before preprocessing.",
        )
    if encoding_suspect_rows:
        add_issue(
            "High",
            "Encoding",
            str(len(encoding_suspect_rows)),
            "MULTIPLE",
            "Text fields",
            "Replacement-character corruption",
            "Rows contain replacement characters that may corrupt parsing or standardization.",
            f"Example worksheet rows: {as_rows(encoding_suspect_rows)}",
            "Review source encoding and clean these text values before preprocessing.",
            "Yes",
        )
    if exact_dup_rows:
        add_issue(
            "High",
            "Duplicates",
            str(len(exact_dup_rows)),
            "MULTIPLE",
            "ALL",
            "Exact duplicate rows",
            "Some workbook rows are exact duplicates.",
            f"Example worksheet rows: {as_rows(exact_dup_rows)}",
            "Review duplicate groups and classify them before any deletion.",
        )
    if near_dup_rows:
        add_issue(
            "High",
            "Duplicates",
            str(len(near_dup_rows)),
            "MULTIPLE",
            "Observation key",
            "Near-duplicate candidates",
            "Rows share the same near-duplicate audit key and may represent duplicate observations or minor transcription drift.",
            f"Example worksheet rows: {as_rows(near_dup_rows)}",
            "Inspect these groups manually before preprocessing.",
            "Yes",
        )
    if ret_gt100:
        add_issue(
            "Medium",
            "Retention",
            str(len(ret_gt100)),
            "MULTIPLE",
            "Retention_Percent",
            "Retention above 100%",
            "Retention values above 100% are present and need classification rather than deletion.",
            f">100: {len(ret_gt100)}, >200: {len(ret_gt200)}, >500: {len(ret_gt500)}",
            "Classify each case as explainable, unit-related, calculation-related, or source-verification-required.",
            "Yes",
        )
    if retention_mismatch:
        add_issue(
            "High",
            "Retention",
            str(len(retention_mismatch)),
            "MULTIPLE",
            "Retention_Percent",
            "Reported vs calculated retention mismatch",
            "Comparable rows disagree with calculated retention by more than 2 percentage points.",
            f"Example worksheet rows: {as_rows(retention_mismatch)}",
            "Review source formulas and unit handling for these rows.",
            "Yes",
        )
    if retention_not_checkable:
        add_issue(
            "Medium",
            "Retention",
            str(len(retention_not_checkable)),
            "MULTIPLE",
            "Retention fields",
            "Retention not checkable",
            "Reported retention cannot be recalculated for some rows due to missing values, unit issues, or zero denominators.",
            f"Example worksheet rows: {as_rows(retention_not_checkable)}",
            "Split these rows by root cause before preprocessing.",
            "Yes",
        )
    if unit_mismatch_rows:
        add_issue(
            "High",
            "Units",
            str(len(unit_mismatch_rows)),
            "MULTIPLE",
            "Initial_Unit,Final_Unit",
            "Initial/final unit mismatch",
            "Initial and final concentration units disagree after audit standardization.",
            f"Example worksheet rows: {as_rows(unit_mismatch_rows)}",
            "Review convertibility and source extraction before recalculating retention.",
            "Yes",
        )
    if zero_init_ret_present:
        add_issue(
            "Critical",
            "Retention",
            str(len(zero_init_ret_present)),
            "MULTIPLE",
            "Initial_Concentration,Retention_Percent",
            "Zero denominator with retention present",
            "Initial concentration is zero while retention is reported.",
            f"Example worksheet rows: {as_rows(zero_init_ret_present)}",
            "Verify source transcription and whether the initial value is truly zero.",
            "Yes",
        )
    if final_present_ret_missing:
        add_issue(
            "Medium",
            "Retention",
            str(len(final_present_ret_missing)),
            "MULTIPLE",
            "Final_Concentration,Retention_Percent",
            "Final concentration present but retention missing",
            "Rows contain final concentration without reported retention.",
            f"Example worksheet rows: {as_rows(final_present_ret_missing)}",
            "Review whether retention should be calculated later or remains intentionally absent.",
            "Yes",
        )
    if missing_method:
        add_issue(
            "High",
            "Cooking variables",
            str(len(missing_method)),
            "MULTIPLE",
            "Cooking_Method",
            "Missing cooking method",
            "Cooking method is absent in some rows.",
            f"Example worksheet rows: {as_rows(missing_method)}",
            "Trace the source-paper extraction for these observations.",
            "Yes",
        )
    if frying_missing_oil:
        add_issue(
            "Medium",
            "Cross-column logic",
            str(len(frying_missing_oil)),
            "MULTIPLE",
            "Cooking_Method,Oil_Type",
            "Frying rows missing oil type",
            "Oil-based cooking rows are missing oil type.",
            f"Example worksheet rows: {as_rows(frying_missing_oil)}",
            "Review whether oil type was omitted, not applicable, or unavailable in source papers.",
            "Yes",
        )
    if microwave_missing_power:
        add_issue(
            "Medium",
            "Cross-column logic",
            str(len(microwave_missing_power)),
            "MULTIPLE",
            "Cooking_Method,Microwave_Power_W",
            "Microwave rows missing power",
            "Microwaving rows lack microwave power.",
            f"Example worksheet rows: {as_rows(microwave_missing_power)}",
            "Review source reporting and extraction completeness.",
            "Yes",
        )
    if pressure_missing_pressure:
        add_issue(
            "Medium",
            "Cross-column logic",
            str(len(pressure_missing_pressure)),
            "MULTIPLE",
            "Cooking_Method,Pressure_kPa",
            "Pressure-cooking rows missing pressure",
            "Pressure-cooking rows lack pressure values.",
            f"Example worksheet rows: {as_rows(pressure_missing_pressure)}",
            "Review whether pressure is omitted or not reported in source papers.",
            "Yes",
        )
    if method_alias_issues:
        add_issue(
            "Medium",
            "Categorical consistency",
            str(sum(len(v) for v in method_alias_issues.values())),
            "MULTIPLE",
            "Cooking_Method",
            "Method alias inconsistencies",
            "Raw cooking-method labels collapse into the same standardized category but remain inconsistent in source form.",
            f"Alias groups: {json.dumps(method_alias_issues, ensure_ascii=True)}",
            "Review and finalize canonical method mapping before preprocessing.",
        )
    if food_variants:
        add_issue(
            "Medium",
            "Food identity",
            str(len(food_variants)),
            "MULTIPLE",
            "Food_Name",
            "Food-name variants",
            "Equivalent food names appear in multiple raw spellings or formats.",
            f"Example variant groups: {json.dumps(dict(list(food_variants.items())[:10]), ensure_ascii=True)}",
            "Prepare a food-name review list before modelling.",
        )
    if class_variants:
        add_issue(
            "Medium",
            "Classification",
            str(len(class_variants)),
            "MULTIPLE",
            "Compound_Class",
            "Compound-class variants",
            "Compound classes differ only by capitalization or spelling.",
            f"Variant groups: {json.dumps(class_variants, ensure_ascii=True)}",
            "Prepare a class review list before preprocessing.",
        )
    if compound_multi_variant:
        add_issue(
            "Medium",
            "Compound identity",
            str(len(compound_multi_variant)),
            "MULTIPLE",
            "Compound_Name,Clean_Compound",
            "Multiple raw names per cleaned compound",
            "Some cleaned compounds merge multiple raw compound names.",
            f"Example groups: {json.dumps(dict(list(compound_multi_variant.items())[:10]), ensure_ascii=True)}",
            "Review whether each cleaned grouping is scientifically defensible.",
            "Yes",
        )
    if aggregate_compounds:
        add_issue(
            "High",
            "Compound identity",
            str(sum(x["rows"] for x in aggregate_compounds)),
            str(len(aggregate_compounds)),
            "Clean_Compound",
            "Aggregate or non-single-molecule entities present",
            "The cleaned compound list includes aggregate measurements, mixtures, or minerals.",
            f"Examples: {json.dumps(aggregate_compounds[:15], ensure_ascii=True)}",
            "Isolate non-single-molecule entities before molecular-feature preprocessing.",
            "Yes",
        )
    if invalid_smiles_rows:
        add_issue(
            "High",
            "SMILES",
            str(len(invalid_smiles_rows)),
            "MULTIPLE",
            "SMILES",
            "Invalid SMILES strings",
            "Non-empty SMILES strings fail RDKit parsing.",
            f"Example worksheet rows: {','.join(str(r) for r in invalid_smiles_rows[:25])}",
            "Review invalid SMILES and the corresponding molecular identities.",
            "Yes",
        )
    if empty_smiles_rows:
        add_issue(
            "Informational",
            "SMILES",
            str(len(empty_smiles_rows)),
            "MULTIPLE",
            "SMILES",
            "Missing SMILES",
            "Some observations have no SMILES string.",
            f"Example worksheet rows: {','.join(str(r) for r in empty_smiles_rows[:25])}",
            "Separate non-resolvable compounds from resolvable single-molecule entities.",
            "Yes",
        )
    if same_name_diff_structures:
        add_issue(
            "Critical",
            "Molecular identity",
            str(sum(int((df["Clean_Compound_Standardized"] == x["compound"]).sum()) for x in same_name_diff_structures)),
            str(len(same_name_diff_structures)),
            "Clean_Compound,SMILES",
            "Same cleaned compound maps to multiple structures",
            "A single cleaned compound name maps to multiple canonical SMILES.",
            f"Conflicts: {json.dumps(same_name_diff_structures[:20], ensure_ascii=True)}",
            "Resolve each conflicting compound before descriptor-based preprocessing.",
            "Yes",
        )
    if shared_structure_groups:
        add_issue(
            "Medium",
            "Molecular identity",
            str(len(shared_structure_groups)),
            "MULTIPLE",
            "Clean_Compound,SMILES",
            "Different names share the same structure",
            "Multiple cleaned names collapse to the same canonical SMILES.",
            f"Examples: {json.dumps(shared_structure_groups[:20], ensure_ascii=True)}",
            "Review synonym groups and decide whether canonical naming is needed.",
            "Yes",
        )
    if descriptor_conflicts:
        add_issue(
            "Critical",
            "Descriptors",
            str(sum(x["rows"] for x in descriptor_conflicts)),
            str(len(descriptor_conflicts)),
            "Descriptor columns",
            "Descriptor conflicts within cleaned compounds",
            "The same cleaned compound has multiple descriptor vectors or molecular identities.",
            f"Conflicts: {json.dumps(descriptor_conflicts[:20], ensure_ascii=True)}",
            "Resolve descriptor conflicts or isolate affected compounds before preprocessing.",
            "Yes",
        )
    if incomplete_descriptor_compounds:
        add_issue(
            "High",
            "Descriptors",
            str(sum(x["rows"] for x in incomplete_descriptor_compounds)),
            str(len(incomplete_descriptor_compounds)),
            "Descriptor columns",
            "Incomplete descriptor coverage",
            "Some cleaned compounds have missing descriptor fields across rows.",
            f"Incomplete compounds: {json.dumps(incomplete_descriptor_compounds, ensure_ascii=True)}",
            "Review whether each case is unresolved, aggregate, or partially entered.",
            "Yes",
        )

    severity_counts = Counter(x["Severity"] for x in issues)
    category_counts = Counter(x["Category"] for x in issues)
    critical_high = [x for x in issues if x["Severity"] in {"Critical", "High"}]
    affected_observation_rows = sorted(
        set(
            exact_dup_rows
            + near_dup_rows
            + neg_ret
            + neg_init
            + neg_final
            + ret_gt100
            + retention_mismatch
            + retention_not_checkable
            + deg_sum_mismatch
            + unit_mismatch_rows
            + zero_init_ret_present
            + final_present_ret_missing
            + missing_method
            + missing_temp
            + missing_time
            + frying_missing_oil
            + microwave_missing_power
            + pressure_missing_pressure
            + suspicious_temp
            + suspicious_time
        )
    )

    summary = {
        "repo_audit": {
            "intended_raw_input_default": "data/raw/CookChem_Dataset_Molecular_Data_Filled.xlsx",
            "new_raw_workbook": str(WORKBOOK.relative_to(ROOT)),
            "preprocessing_scripts": ["preprocessing/scripts/run_preprocessing.py"],
            "molecular_identity_scripts": [
                "molecular_features/scripts/retrieve_pubchem.py",
                "molecular_features/scripts/validate_smiles.py",
                "molecular_features/scripts/fill_molecular_data.py",
                "molecular_features/scripts/run_molecular_features.py",
            ],
            "rdkit_descriptor_scripts": [
                "molecular_features/scripts/generate_rdkit_descriptors.py",
                "molecular_features/scripts/run_molecular_features.py",
            ],
            "report_manifest_scripts": [
                "preprocessing/scripts/run_preprocessing.py",
                "molecular_features/scripts/run_molecular_features.py",
            ],
            "old_823_outputs": [
                "data/preprocessing/final/cookchem_preprocessed_dataset.csv",
                "data/preprocessing/final/cookchem_preprocessed_dataset.xlsx",
                "data/preprocessing/final/preprocessing_manifest.json",
                "data/preprocessing/intermediate/cookchem_preprocessing_validation_flags.csv",
                "data/preprocessing/intermediate/duplicate_review.csv",
                "data/preprocessing/intermediate/missingness_report.csv",
                "data/preprocessing/intermediate/validation_flag_summary.csv",
                "preprocessing/reports/preprocessing_report.md",
                "molecular_features/outputs/molecular_features.csv",
                "molecular_features/outputs/molecular_features.xlsx",
                "molecular_features/outputs/molecular_feature_manifest.json",
                "molecular_features/reports/molecular_feature_report.md",
                "data/molecular_features/cookchem_with_molecular_features.csv",
            ],
            "new_901_outputs_detected": [],
            "stale_reference_detected": True,
        },
        "workbook": {
            "sheet_meta": sheet_meta,
            "observation_sheet": sheet_name,
            "rows": int(len(df)),
            "columns": list(raw_df.columns),
            "column_profile": column_profile,
            "required_missing": required_missing,
            "duplicate_columns": duplicate_columns,
            "suspicious_column_names": suspicious_column_names,
            "empty_columns": empty_columns,
        },
        "summary_stats": {
            "total_observations": int(len(df)),
            "total_raw_compound_variants": int(df["Compound_Name_Standardized"].nunique(dropna=True)),
            "total_cleaned_compounds": int(df["Clean_Compound_Standardized"].nunique(dropna=True)),
            "obs_per_compound_top10": [{"compound": k, "count": int(v)} for k, v in obs_per_compound.head(10).items()],
            "obs_per_food_top10": [{"food": k, "count": int(v)} for k, v in obs_per_food.head(10).items()],
            "obs_per_method_top10": [{"method": k, "count": int(v)} for k, v in obs_per_method.head(10).items()],
            "obs_per_class_top10": [{"class": k, "count": int(v)} for k, v in obs_per_class.head(10).items()],
            "compounds_with_1_obs": int((obs_per_compound == 1).sum()),
            "compounds_with_le_2_obs": int((obs_per_compound <= 2).sum()),
            "compounds_with_le_5_obs": int((obs_per_compound <= 5).sum()),
            "compounds_with_ge_10_obs": int((obs_per_compound >= 10).sum()),
        },
        "findings": {
            "retention_gt100_count": len(ret_gt100),
            "retention_gt200_count": len(ret_gt200),
            "retention_gt500_count": len(ret_gt500),
            "retention_mismatch_count": len(retention_mismatch),
            "retention_not_checkable_count": len(retention_not_checkable),
            "exact_duplicate_count": len(exact_dup_rows),
            "near_duplicate_count": len(near_dup_rows),
            "molecular_identity_conflict_count": len(same_name_diff_structures),
            "descriptor_conflict_count": len(descriptor_conflicts),
            "incomplete_descriptor_compound_count": len(incomplete_descriptor_compounds),
            "aggregate_non_molecular_count": len(aggregate_compounds),
            "source_verification_required_issue_count": sum(
                1 for x in issues if x["Source_Verification_Required"] == "Yes"
            ),
            "affected_observation_count": len(affected_observation_rows),
        },
        "compound_classification": compound_classification,
        "descriptor_conflicts": descriptor_conflicts,
        "same_name_diff_structures": same_name_diff_structures,
        "different_names_same_structure": shared_structure_groups,
        "issues": issues,
    }

    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    pd.DataFrame(issues).to_csv(ISSUES_CSV, index=False)

    md_lines = [
        "# CookRisk Dataset Audit Log",
        "",
        "## Audit Metadata",
        f"- Dataset: {WORKBOOK}",
        "- Audit date: 2026-08-23",
        "- Auditor: Codex",
        "- Dataset version: CookChem_Dataset_Molecular_Data_Ordered (2).xlsx",
        f"- Total observations: {len(df)}",
        f"- Total raw compound variants: {df['Compound_Name_Standardized'].nunique(dropna=True)}",
        f"- Total cleaned compounds: {df['Clean_Compound_Standardized'].nunique(dropna=True)}",
        "",
        "## Summary",
        f"- Critical: {severity_counts.get('Critical', 0)}",
        f"- High: {severity_counts.get('High', 0)}",
        f"- Medium: {severity_counts.get('Medium', 0)}",
        f"- Low: {severity_counts.get('Low', 0)}",
        f"- Informational: {severity_counts.get('Informational', 0)}",
        "",
        "## Issues",
        "",
    ]
    for issue in issues:
        md_lines.extend(
            [
                f"### {issue['Issue_ID']}",
                f"- Severity: {issue['Severity']}",
                f"- Category: {issue['Category']}",
                f"- Status: {issue['Status']}",
                f"- Affected rows: {issue['Affected_Rows']}",
                f"- Affected compounds: {issue['Affected_Compounds']}",
                f"- Description: {issue['Description']}",
                f"- Evidence: {issue['Evidence']}",
                f"- Why it matters: {issue['Issue_Type']}",
                f"- Recommended investigation: {issue['Recommended_Action']}",
                "- Resolution: ",
                "- Resolution date: ",
                "",
            ]
        )
    ISSUES_MD.write_text("\n".join(md_lines), encoding="utf-8")

    print(json.dumps({
        "issue_count": len(issues),
        "severity_counts": dict(severity_counts),
        "category_counts": dict(category_counts),
        "critical_high_count": len(critical_high),
    }))


if __name__ == "__main__":
    main()
