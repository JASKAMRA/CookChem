# Molecular Feature Report

Generated: 2026-08-23T09:51:04.662586+00:00

## Input Dataset

- Input file: `data\preprocessing\final\cookchem_preprocessed_dataset.csv`
- Observation rows: 823
- Observation columns: 65

Raw data and preprocessing outputs were not modified.

## Run Summary

- Unique compounds: 104
- PubChem retrieval attempts this run: 7
- PubChem cache hits this run: 0
- PubChem retrieved: 5
- Already present molecular identities: 97
- Unresolved compounds: 1
- Ambiguous compounds: 1
- Valid SMILES: 74
- Invalid or missing SMILES: 30
- Complete RDKit descriptors: 74
- Incomplete/not generated descriptors: 30
- RDKit version: 2026.03.5
- Python version: 3.12.13


## Outputs

- molecular feature CSV: `molecular_features\outputs\molecular_features.csv`
- molecular feature Excel: `molecular_features\outputs\molecular_features.xlsx`
- PubChem cache: `molecular_features\outputs\pubchem_cache.csv`
- manifest: `molecular_features\outputs\molecular_feature_manifest.json`
- report: `molecular_features\reports\molecular_feature_report.md`
- merged observation dataset: `data\molecular_features\cookchem_with_molecular_features.csv`

## Descriptor Definitions

| descriptor | rdkit_function |
| --- | --- |
| Molecular_Weight | rdkit.Chem.Descriptors.MolWt(mol) |
| LogP | rdkit.Chem.Crippen.MolLogP(mol) |
| TPSA | rdkit.Chem.rdMolDescriptors.CalcTPSA(mol) |
| H_Bond_Donors | rdkit.Chem.Lipinski.NumHDonors(mol) |
| H_Bond_Acceptors | rdkit.Chem.Lipinski.NumHAcceptors(mol) |
| Rotatable_Bonds | rdkit.Chem.Lipinski.NumRotatableBonds(mol) |
| Heavy_Atom_Count | mol.GetNumHeavyAtoms() |
| Ring_Count | rdkit.Chem.rdMolDescriptors.CalcNumRings(mol) |
| Aromatic_Ring_Count | rdkit.Chem.rdMolDescriptors.CalcNumAromaticRings(mol) |

Molecular descriptors are calculated from validated molecular structures and are not manually entered into the dataset.

## PubChem Retrieval Method

Uses PubChem PUG REST via Python standard-library urllib. Results are cached in `molecular_features/outputs/pubchem_cache.csv`. Ambiguous matches are flagged, not silently resolved.

## Retrieval Errors and Review Items

| compound_name_input | retrieval_status | error_message |
| --- | --- | --- |
| Cyanidin-3-glucoside | ambiguous | Multiple PubChem CIDs returned: [197081, 441667] |
| Resistant Starch | not_found | HTTPError 404: PUGREST.NotFound |

## Limitations

- Failed or ambiguous lookups are explicitly flagged.
- Missing descriptors are not converted to zero.
- No EDA, modelling, risk scoring, application work, or raw-data modification was performed.
