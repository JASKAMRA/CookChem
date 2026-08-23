from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from generate_rdkit_descriptors import DESCRIPTOR_COLUMNS, DESCRIPTOR_DEFINITIONS, RDKIT_AVAILABLE as DESC_RDKIT, RDKIT_IMPORT_ERROR as DESC_ERR, RDKIT_VERSION, add_rdkit_descriptors
from retrieve_pubchem import collect_unique_compounds, normalize_lookup_name, resolve_pubchem_identities
from validate_smiles import RDKIT_AVAILABLE as VAL_RDKIT, RDKIT_IMPORT_ERROR as VAL_ERR, validate_smiles_dataframe

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PREPROCESSING_FINAL_DIR = PROJECT_ROOT / "data" / "preprocessing" / "final"
OUTPUT_DIR = PROJECT_ROOT / "molecular_features" / "outputs"
REPORT_DIR = PROJECT_ROOT / "molecular_features" / "reports"
DATA_MOLECULAR_DIR = PROJECT_ROOT / "data" / "molecular_features"
FEATURE_OUTPUT_COLUMNS = ["Compound_Key", "Compound_Name", "normalized_lookup_name", "Original_Compound_Names", "PubChem_CID", "SMILES", "Molecular_Formula", *DESCRIPTOR_COLUMNS, "SMILES_Valid", "SMILES_Status", "Molecular_Identity_Status", "PubChem_Retrieval_Status", "Descriptor_Status", "Observation_Count", "PubChem_Error_Message"]

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=None)
    p.add_argument("--disable-pubchem", action="store_true")
    p.add_argument("--pubchem-timeout", type=int, default=12)
    p.add_argument("--pubchem-delay", type=float, default=0.25)
    return p.parse_args()

def resolve_input(path: Path | None) -> Path:
    if path is not None:
        p = path if path.is_absolute() else PROJECT_ROOT / path
        if not p.exists():
            raise FileNotFoundError(p)
        return p
    preferred = PREPROCESSING_FINAL_DIR / "cookchem_preprocessed_dataset.csv"
    if preferred.exists():
        return preferred
    candidates = sorted(PREPROCESSING_FINAL_DIR.glob("*.csv"))
    if not candidates:
        raise FileNotFoundError("Run preprocessing first; no preprocessed CSV exists.")
    return candidates[0]

def count_status(df: pd.DataFrame, column: str, status: str) -> int:
    return int((df[column].fillna("") == status).sum())

def safe_markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    d = df.fillna("").astype(str)
    cols = list(d.columns)
    return "\n".join(["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |", *["| " + " | ".join(row[c] for c in cols) + " |" for _, row in d.iterrows()]])

def build_merged_dataset(observations: pd.DataFrame, features: pd.DataFrame):
    name_col = "Compound_Name_Standardized" if "Compound_Name_Standardized" in observations.columns else "Compound_Name"
    obs = observations.copy(deep=True)
    obs["_MolecularFeature_Merge_Key"] = obs[name_col].map(normalize_lookup_name)
    mf = features[["normalized_lookup_name", "Compound_Name", "PubChem_CID", "SMILES", "Molecular_Formula", *DESCRIPTOR_COLUMNS, "SMILES_Valid", "Molecular_Identity_Status", "Descriptor_Status"]].copy()
    dup = mf[mf.duplicated("normalized_lookup_name", keep=False)]
    if not dup.empty:
        return observations.copy(deep=True), dup
    merged = obs.merge(mf, left_on="_MolecularFeature_Merge_Key", right_on="normalized_lookup_name", how="left", suffixes=("", "_MolecularFeature"), validate="many_to_one").drop(columns=["_MolecularFeature_Merge_Key"])
    return merged, dup

def write_report(input_path: Path, observations: pd.DataFrame, features: pd.DataFrame, cache: pd.DataFrame, manifest: dict[str, Any], retrieval_stats: dict[str, int], output_paths: dict[str, Path]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    defs = pd.DataFrame([{"descriptor": k, "rdkit_function": v} for k, v in DESCRIPTOR_DEFINITIONS.items()])
    errors = cache[cache["retrieval_status"].fillna("").isin(["api_error", "ambiguous", "not_found"])][["compound_name_input", "retrieval_status", "error_message"]].head(25)
    rdkit_note = "" if manifest["rdkit_available"] else f"\n\nRDKit is unavailable. Import error: `{manifest['rdkit_import_error']}`"
    out_lines = "\n".join([f"- {k}: `{v.relative_to(PROJECT_ROOT)}`" for k, v in output_paths.items()])
    report = f"""# Molecular Feature Report\n\nGenerated: {manifest['timestamp_utc']}\n\n## Input Dataset\n\n- Input file: `{input_path.relative_to(PROJECT_ROOT)}`\n- Observation rows: {len(observations)}\n- Observation columns: {len(observations.columns)}\n\nRaw data and preprocessing outputs were not modified.\n\n## Run Summary\n\n- Unique compounds: {manifest['unique_compound_count']}\n- PubChem retrieval attempts this run: {retrieval_stats['pubchem_retrieval_attempts']}\n- PubChem cache hits this run: {retrieval_stats['pubchem_cache_hits']}\n- PubChem retrieved: {manifest['pubchem_retrieved_count']}\n- Already present molecular identities: {manifest['already_present_count']}\n- Unresolved compounds: {manifest['unresolved_count']}\n- Ambiguous compounds: {manifest['ambiguous_count']}\n- Valid SMILES: {manifest['valid_smiles_count']}\n- Invalid or missing SMILES: {manifest['invalid_or_missing_smiles_count']}\n- Complete RDKit descriptors: {manifest['descriptor_complete_count']}\n- Incomplete/not generated descriptors: {manifest['descriptor_incomplete_count']}\n- RDKit version: {manifest['rdkit_version']}\n- Python version: {manifest['python_version']}\n{rdkit_note}\n\n## Outputs\n\n{out_lines}\n\n## Descriptor Definitions\n\n{safe_markdown_table(defs)}\n\nMolecular descriptors are calculated from validated molecular structures and are not manually entered into the dataset.\n\n## PubChem Retrieval Method\n\nUses PubChem PUG REST via Python standard-library urllib. Results are cached in `molecular_features/outputs/pubchem_cache.csv`. Ambiguous matches are flagged, not silently resolved.\n\n## Retrieval Errors and Review Items\n\n{safe_markdown_table(errors)}\n\n## Limitations\n\n- Failed or ambiguous lookups are explicitly flagged.\n- Missing descriptors are not converted to zero.\n- No EDA, modelling, risk scoring, application work, or raw-data modification was performed.\n"""
    (REPORT_DIR / "molecular_feature_report.md").write_text(report, encoding="utf-8")

def main() -> None:
    args = parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_MOLECULAR_DIR.mkdir(parents=True, exist_ok=True)
    input_path = resolve_input(args.input)
    observations = pd.read_csv(input_path)
    compounds = collect_unique_compounds(observations)
    cache_path = OUTPUT_DIR / "pubchem_cache.csv"
    resolved, cache, retrieval_stats = resolve_pubchem_identities(compounds, cache_path, enable_pubchem=not args.disable_pubchem, timeout=args.pubchem_timeout, delay_seconds=args.pubchem_delay)
    validated, mols = validate_smiles_dataframe(resolved)
    features = add_rdkit_descriptors(validated, mols)[FEATURE_OUTPUT_COLUMNS].sort_values("Compound_Name").reset_index(drop=True)
    if features.duplicated("Compound_Key").any():
        raise ValueError("Duplicate Compound_Key found in molecular feature output.")
    feature_csv = OUTPUT_DIR / "molecular_features.csv"
    feature_xlsx = OUTPUT_DIR / "molecular_features.xlsx"
    merged_csv = DATA_MOLECULAR_DIR / "cookchem_with_molecular_features.csv"
    manifest_path = OUTPUT_DIR / "molecular_feature_manifest.json"
    report_path = REPORT_DIR / "molecular_feature_report.md"
    features.to_csv(feature_csv, index=False)
    features.to_excel(feature_xlsx, index=False)
    merged, dup_join = build_merged_dataset(observations, features)
    if dup_join.empty:
        merged.to_csv(merged_csv, index=False)
    retrieved = count_status(features, "Molecular_Identity_Status", "retrieved")
    unresolved = int(features["Molecular_Identity_Status"].fillna("").isin(["not_found", "api_error", "manual_review_required"]).sum())
    ambiguous = count_status(features, "Molecular_Identity_Status", "ambiguous")
    valid_smiles = int((features["SMILES_Valid"].fillna(False) == True).sum())
    complete = count_status(features, "Descriptor_Status", "complete")
    output_files = {"molecular_features_csv": str(feature_csv.relative_to(PROJECT_ROOT)), "molecular_features_xlsx": str(feature_xlsx.relative_to(PROJECT_ROOT)), "pubchem_cache": str(cache_path.relative_to(PROJECT_ROOT)), "manifest": str(manifest_path.relative_to(PROJECT_ROOT)), "report": str(report_path.relative_to(PROJECT_ROOT)), "merged_observation_dataset": str(merged_csv.relative_to(PROJECT_ROOT))}
    manifest = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "input_file": str(input_path.relative_to(PROJECT_ROOT)), "input_row_count": int(len(observations)), "unique_compound_count": int(len(features)), "output_files": output_files, "pubchem_retrieval_count": retrieval_stats["pubchem_retrieval_attempts"], "pubchem_cache_hits": retrieval_stats["pubchem_cache_hits"], "pubchem_retrieved_count": retrieved, "already_present_count": count_status(features, "Molecular_Identity_Status", "already_present"), "unresolved_count": unresolved, "ambiguous_count": ambiguous, "valid_smiles_count": valid_smiles, "invalid_smiles_count": int((features["SMILES_Status"] == "invalid").sum()), "invalid_or_missing_smiles_count": int(len(features) - valid_smiles), "descriptor_complete_count": complete, "descriptor_incomplete_count": int(len(features) - complete), "rdkit_available": bool(DESC_RDKIT and VAL_RDKIT), "rdkit_version": RDKIT_VERSION, "rdkit_import_error": DESC_ERR or VAL_ERR, "python_version": platform.python_version(), "script_version": "cookchem_molecular_features_v1", "raw_data_modified": False, "preprocessing_outputs_modified": False, "observation_rows_deleted": 0, "duplicate_compound_keys": int(features.duplicated("Compound_Key").sum()), "duplicate_join_keys": int(len(dup_join)), "unmatched_compounds_after_merge": [] if dup_join.empty else ["merge skipped due duplicate join keys"]}
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    output_paths = {"molecular feature CSV": feature_csv, "molecular feature Excel": feature_xlsx, "PubChem cache": cache_path, "manifest": manifest_path, "report": report_path, "merged observation dataset": merged_csv}
    write_report(input_path, observations, features, cache, manifest, retrieval_stats, output_paths)
    print("CookChem molecular feature pipeline finished.")
    print(f"Input observations: {len(observations)}")
    print(f"Unique compounds: {len(features)}")
    print(f"PubChem retrieval attempts: {retrieval_stats['pubchem_retrieval_attempts']}")
    print(f"PubChem retrieved: {retrieved}")
    print(f"Unresolved: {unresolved}")
    print(f"Ambiguous: {ambiguous}")
    print(f"Valid SMILES: {valid_smiles}")
    print(f"Invalid/missing SMILES: {len(features) - valid_smiles}")
    print(f"Descriptor complete: {complete}")
    print(f"Descriptor incomplete/not generated: {len(features) - complete}")
    print(f"RDKit available: {manifest['rdkit_available']}")
    print(f"Molecular features: {feature_csv.relative_to(PROJECT_ROOT)}")
    print(f"Report: {report_path.relative_to(PROJECT_ROOT)}")
    print(f"Merged observation dataset: {merged_csv.relative_to(PROJECT_ROOT)}")

if __name__ == "__main__":
    main()
