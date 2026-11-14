# Stage A + Stage C recovery repository audit

Generated: 2026-11-09T20:50:37.929695+00:00

## Authoritative historical inputs inspected

| Path | SHA-256 | Role |
|---|---|---|
| `data/reviewed/cookchem_molecular_retention_master.csv` | `a32a3b404ac2b050ddd536fc0cca2f5fa7c8fdbb9677e66ff01f217bcfb11e2c` | Reviewed historical source table; not altered |
| `stageA/input/cookchem_molecular_retention_preprocessed.csv` | `cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27` | 1,124-row historical supervised input; not altered |
| `stageC/phase2/data/observed_cooking_pairs.csv` | `5c9e372969f9dd29890b494567cc9c5216d2c4d2ead36f369bccd023dc04860e` | Primary-source cooking-pair audit evidence |
| `stageB/final_model/cookrisk_retention_stageB_selected.joblib` | `0f03701099a66792c8ebf9b81d650114968a415996e17ae5dd34048f5e15cb62` | Historical candidate artifact; not loaded |

## Finding

This recovery package contains no trained model and no replacement dataset. The ledger retains all 1,124 historical model rows and records why none is admitted to a rebuilt model. The current scientific gate is blocked, not an engineering failure to be bypassed.
