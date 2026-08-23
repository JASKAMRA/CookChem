from __future__ import annotations
from typing import Any
import pandas as pd
try:
    import rdkit
    from rdkit.Chem import Crippen, Descriptors, Lipinski, rdMolDescriptors
    RDKIT_AVAILABLE = True
    RDKIT_VERSION = rdkit.__version__
    RDKIT_IMPORT_ERROR = ""
except Exception as exc:
    Crippen = Descriptors = Lipinski = rdMolDescriptors = None
    RDKIT_AVAILABLE = False
    RDKIT_VERSION = "unavailable"
    RDKIT_IMPORT_ERROR = str(exc)
DESCRIPTOR_COLUMNS = ["Molecular_Weight", "LogP", "TPSA", "H_Bond_Donors", "H_Bond_Acceptors", "Rotatable_Bonds", "Heavy_Atom_Count", "Ring_Count", "Aromatic_Ring_Count"]
DESCRIPTOR_DEFINITIONS = {"Molecular_Weight": "rdkit.Chem.Descriptors.MolWt(mol)", "LogP": "rdkit.Chem.Crippen.MolLogP(mol)", "TPSA": "rdkit.Chem.rdMolDescriptors.CalcTPSA(mol)", "H_Bond_Donors": "rdkit.Chem.Lipinski.NumHDonors(mol)", "H_Bond_Acceptors": "rdkit.Chem.Lipinski.NumHAcceptors(mol)", "Rotatable_Bonds": "rdkit.Chem.Lipinski.NumRotatableBonds(mol)", "Heavy_Atom_Count": "mol.GetNumHeavyAtoms()", "Ring_Count": "rdkit.Chem.rdMolDescriptors.CalcNumRings(mol)", "Aromatic_Ring_Count": "rdkit.Chem.rdMolDescriptors.CalcNumAromaticRings(mol)"}

def descriptor_values(mol: Any) -> dict[str, Any]:
    return {"Molecular_Weight": Descriptors.MolWt(mol), "LogP": Crippen.MolLogP(mol), "TPSA": rdMolDescriptors.CalcTPSA(mol), "H_Bond_Donors": Lipinski.NumHDonors(mol), "H_Bond_Acceptors": Lipinski.NumHAcceptors(mol), "Rotatable_Bonds": Lipinski.NumRotatableBonds(mol), "Heavy_Atom_Count": mol.GetNumHeavyAtoms(), "Ring_Count": rdMolDescriptors.CalcNumRings(mol), "Aromatic_Ring_Count": rdMolDescriptors.CalcNumAromaticRings(mol)}

def add_rdkit_descriptors(df: pd.DataFrame, molecules: list[Any]) -> pd.DataFrame:
    out = df.copy(deep=True)
    for c in DESCRIPTOR_COLUMNS:
        out[c] = pd.NA
    statuses = []
    for idx, mol in enumerate(molecules):
        if not RDKIT_AVAILABLE:
            statuses.append("not_generated")
        elif not bool(out.iloc[idx]["SMILES_Valid"]):
            identity_status = str(out.iloc[idx].get("Molecular_Identity_Status", ""))
            statuses.append("unresolved_identity" if identity_status in {"not_found", "ambiguous", "api_error", "manual_review_required"} else "invalid_structure")
        else:
            try:
                for c, v in descriptor_values(mol).items():
                    out.iat[idx, out.columns.get_loc(c)] = v
                statuses.append("complete")
            except Exception:
                statuses.append("incomplete")
    out["Descriptor_Status"] = statuses
    return out
