# Organization scope

This maintenance pass reorganizes Stage B files and adds safe entry points. Scientific datasets and the authoritative `StageB_Final` payload are preserved by byte copy, with integrity checked against its release checksum manifest. Historical source material is retained under `stageB/archive/`. The root `reports/run_dataset_forensic_audit.py` is project-wide and was retained because it audits shared CookChem data. Root README, shared requirements, and `.gitignore` are likewise shared.
