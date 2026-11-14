# Descriptor coverage

All **439/439** eligible observations have finite values for each of the eight existing RDKit fields: molecular weight, LogP, TPSA, H-bond donors, H-bond acceptors, rotatable bonds, aromatic rings, and hydroxyl groups. Repeated canonical molecular IDs were checked for descriptor consistency; the source table carries canonical IDs and descriptor values, but does **not** carry canonical SMILES. No molecular identity, SMILES, or descriptor was invented or resolved externally in this implementation.

The descriptor vector is included in every molecular feature experiment. `descriptor_identity_consistency.csv` records the consistency check.
