"""
Fills the empty molecular-descriptor columns (Molecular_Weight ... Heavy_Atom_Count)
for rows 531-560 of CookChem_Dataset_Final_Clean.xlsx.

Run this on your own machine / Google Colab where internet + pip both work:

    pip install pubchempy rdkit openpyxl
    python fill_molecular_data.py

It fetches CanonicalSMILES from PubChem by CID, then computes descriptors
with RDKit locally (so results match RDKit conventions, same as the rest
of your dataset).

BEFORE RUNNING: fix these two known-bad CIDs in the sheet (see chat) -
    Row 533 (PhIP)            -> should be CID 1936, not 10214
    Row 553 (Lycopene)        -> should be CID 446925, not 5280489
Rows with NO CID (Total_Phenolics, Proanthocyanidins, Resistant_Starch) are
skipped automatically since they're compound classes, not single molecules.
"""

import time
import openpyxl
import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

INPUT_FILE = "CookChem_Dataset_Final_Clean.xlsx"
SHEET_NAME = "CookChem Dataset"

COL = {
    "compound": 11, "cid": 13, "smiles": 14,
    "mw": 33, "logp": 34, "tpsa": 35, "hbd": 36, "hba": 37,
    "rotb": 38, "arom": 39, "oh": 40, "heavy": 41,
}

def descriptors_from_smiles(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return {
        "mw": round(Descriptors.MolWt(mol), 2),
        "logp": round(Descriptors.MolLogP(mol), 2),
        "tpsa": round(Descriptors.TPSA(mol), 2),
        "hbd": rdMolDescriptors.CalcNumHBD(mol),
        "hba": rdMolDescriptors.CalcNumHBA(mol),
        "rotb": rdMolDescriptors.CalcNumRotatableBonds(mol),
        "arom": rdMolDescriptors.CalcNumAromaticRings(mol),
        "oh": sum(1 for atom in mol.GetAtoms()
                  if atom.GetSymbol() == "O" and atom.GetTotalNumHs() == 1),
        "heavy": mol.GetNumHeavyAtoms(),
    }

def main():
    wb = openpyxl.load_workbook(INPUT_FILE)
    ws = wb[SHEET_NAME]

    for row in range(2, ws.max_row + 1):
        cid = ws.cell(row, COL["cid"]).value
        existing_mw = ws.cell(row, COL["mw"]).value
        compound = ws.cell(row, COL["compound"]).value

        if existing_mw not in (None, ""):
            continue  # already filled
        if not cid:
            print(f"Row {row} ({compound}): no CID, skipping (mixture/class, needs manual handling)")
            continue

        try:
            c = pcp.Compound.from_cid(int(cid))
            smiles = c.canonical_smiles
        except Exception as e:
            print(f"Row {row} ({compound}, CID {cid}): PubChem lookup failed - {e}")
            continue

        d = descriptors_from_smiles(smiles)
        if d is None:
            print(f"Row {row} ({compound}): RDKit could not parse SMILES '{smiles}'")
            continue

        ws.cell(row, COL["smiles"]).value = smiles
        ws.cell(row, COL["mw"]).value = d["mw"]
        ws.cell(row, COL["logp"]).value = d["logp"]
        ws.cell(row, COL["tpsa"]).value = d["tpsa"]
        ws.cell(row, COL["hbd"]).value = d["hbd"]
        ws.cell(row, COL["hba"]).value = d["hba"]
        ws.cell(row, COL["rotb"]).value = d["rotb"]
        ws.cell(row, COL["arom"]).value = d["arom"]
        ws.cell(row, COL["oh"]).value = d["oh"]
        ws.cell(row, COL["heavy"]).value = d["heavy"]

        print(f"Row {row} ({compound}, CID {cid}): filled OK")
        time.sleep(0.3)  # be nice to PubChem's rate limit

    out_file = "CookChem_Dataset_Final_Clean_FILLED.xlsx"
    wb.save(out_file)
    print(f"\nSaved: {out_file}")

if __name__ == "__main__":
    main()
