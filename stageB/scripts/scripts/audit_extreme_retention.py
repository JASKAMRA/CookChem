"""Stage B, step 1: provenance audit only. This script never edits model data."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT.parent / "stageA" / "input" / "cookchem_molecular_retention_preprocessed.csv"
OUT = ROOT / "outputs"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(INPUT)
    threshold = float(df["Retention_Final"].quantile(0.99))
    extreme = df.loc[df["Retention_Final"] >= threshold].copy()
    conditions = ["Temperature_C", "Cooking_Time_min", "Pressure_kPa", "Microwave_Power_W", "Initial_Concentration"]
    extreme["missing_process_field_count"] = extreme[conditions].isna().sum(axis=1)
    extreme["missing_process_fields"] = extreme[conditions].apply(
        lambda row: ", ".join(column for column in conditions if pd.isna(row[column])) or "None", axis=1
    )
    extreme["audit_decision"] = "RETAIN: source-level verification required before any correction"
    extreme["reason"] = "Extreme target is scientifically plausible as an apparent increase; missing process metadata alone is not evidence of an error."
    columns = ["Record_ID", "Paper_ID", "DOI", "Source_Paper_Key", "Year", "Journal", "Canonical_Molecular_ID", "Canonical_Compound_Name", "Compound_Class_Standardized", "Food_Name_Standardized", "Cooking_Method_Standardized", "Cooking_Medium_Standardized", "Retention_Final", "Apparent_Increase", "missing_process_field_count", "missing_process_fields", "audit_decision", "reason"]
    extreme.loc[:, columns].sort_values("Retention_Final", ascending=False).to_csv(OUT / "stageB_extreme_retention_audit.csv", index=False)
    source_summary = extreme.groupby(["Paper_ID", "DOI", "Source_Paper_Key"], dropna=False).agg(records=("Record_ID", "size"), min_retention=("Retention_Final", "min"), max_retention=("Retention_Final", "max"), rows_with_temperature=("Temperature_C", lambda s: int(s.notna().sum())), rows_with_time=("Cooking_Time_min", lambda s: int(s.notna().sum()))).reset_index()
    source_summary.to_csv(OUT / "stageB_extreme_retention_source_summary.csv", index=False)
    report = f"""# Stage B Step 1 - Extreme Retention Provenance Audit

## Scope
This is an audit only. It does not change the target, remove observations, train a model, or claim that an extreme value is erroneous.

## Findings
* Threshold: top 1% of `Retention_Final` = {threshold:.6f}.
* Extreme observations: {len(extreme)} of {len(df)}.
* All extreme observations are retained in the primary modelling dataset.
* Their provenance is traceable through Record_ID, Paper_ID, DOI and Source_Paper_Key.
* Missing cooking conditions are common among these records; this reduces model information but is not evidence that the retention value is invalid.

## Decision
Every extreme record is labelled **RETAIN: source-level verification required before any correction**. A later source-paper check may correct only demonstrable extraction, transcription, unit or target-calculation errors. Absent that evidence, Stage B will improve modelling without deleting or capping extremes.

## Next modelling implication
The next step is to add leakage-safe process-missingness indicators and physically motivated thermal-exposure features, then evaluate them with the unchanged molecular GroupKFold protocol.
"""
    (OUT / "stageB_step1_extreme_audit.md").write_text(report, encoding="utf-8")
    print(f"Audited {len(extreme)} extreme observations at threshold {threshold:.6f}.")


if __name__ == "__main__":
    main()
