from __future__ import annotations
from typing import Any
import pandas as pd
try:
    import rdkit
    from rdkit import Chem
    RDKIT_AVAILABLE = True
    RDKIT_VERSION = rdkit.__version__
    RDKIT_IMPORT_ERROR = ""
except Exception as exc:
    Chem = None
    RDKIT_AVAILABLE = False
    RDKIT_VERSION = "unavailable"
    RDKIT_IMPORT_ERROR = str(exc)

def validate_smiles_value(smiles: Any, identity_status: str) -> dict[str, Any]:
    if pd.isna(smiles) or not str(smiles).strip():
        return {"SMILES_Valid": False, "SMILES_Status": "unresolved_identity" if identity_status != "already_present" else "missing", "RDKit_Mol": None}
    if not RDKIT_AVAILABLE:
        return {"SMILES_Valid": False, "SMILES_Status": "rdkit_unavailable", "RDKit_Mol": None}
    try:
        mol = Chem.MolFromSmiles(str(smiles))
        if mol is None:
            return {"SMILES_Valid": False, "SMILES_Status": "invalid", "RDKit_Mol": None}
        return {"SMILES_Valid": True, "SMILES_Status": "valid", "RDKit_Mol": mol}
    except Exception:
        return {"SMILES_Valid": False, "SMILES_Status": "parse_error", "RDKit_Mol": None}

def validate_smiles_dataframe(df: pd.DataFrame):
    rows, mols = [], []
    for _, row in df.iterrows():
        v = validate_smiles_value(row.get("SMILES"), row.get("Molecular_Identity_Status", ""))
        d = row.to_dict()
        d["SMILES_Valid"] = v["SMILES_Valid"]
        d["SMILES_Status"] = v["SMILES_Status"]
        rows.append(d)
        mols.append(v["RDKit_Mol"])
    return pd.DataFrame(rows), mols
