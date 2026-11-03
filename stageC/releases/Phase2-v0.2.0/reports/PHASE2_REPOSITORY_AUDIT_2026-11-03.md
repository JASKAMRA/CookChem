# Phase 2 Repository and Architecture Audit — 2026-11-03

## Scope and preservation

Audited Stage C source, scripts, schemas, tests, documentation, Phase 2 inputs/generated outputs, releases, selected Stage B model metadata, Phase 1B interfaces, and recent Git history. No Stage A/B, Phase1B, or Phase2-v0.1.0 artifact was edited. No historical checkpoint or expected count was changed.

## Architecture

| Layer | Location | Role / finding |
|---|---|---|
| Phase 1 foundation | `stageC/src/stage_c/` | Python package for food composition, mapping, validation, units, provenance, exposure, Stage B snapshot connector, and retention interval helpers. |
| CLI | `stageC/src/stage_c/cli.py` | Read-only Stage B inspect/import, food ingest/map/validate, and raw exposure commands. It does not expose a Phase 2 cooked-concentration command. |
| Phase 2 intake | `stageC/phase2/data/` | Crosswalk, candidate decisions, four Stage B retention records, and 117 source-published raw/cooked pairs. |
| Phase 2 build | `stageC/scripts/audit_phase2_readiness.py`, `build_phase2_release.py` | Rebuilds Stage A/B identity/evidence intake and deterministic Phase 1B integration, apparent ratios, compatibility review, and empty cooked-output schema. |
| Phase 2 logic | `stageC/src/stage_c/phase2_retention.py` | Decimal interval arithmetic; caller must attest compound, matrix, process, and basis gates. It does not itself adjudicate source evidence. |
| Phase 2 tests | `stageC/tests/test_phase2*.py` | Tests interval arithmetic, guarded output, integration, identity states, and model gates. Added `test_phase2_source_audit.py` exercises the independent 117-row source-table check. |
| Schemas | `stageC/schemas/` | Phase 1 food/mapping/provenance/exposure schemas; there is no dedicated Phase 2 source-pair or cooked-output JSON schema. Phase 2 data are CSV plus release validation metadata. |
| Versioned inputs/outputs | `stageC/releases/Phase1B-v1.3.0/`, `stageC/releases/Phase2-v0.1.0/` | Phase 1B source and mapping tables are pinned as inputs; v0.1.0 is immutable. |

## Data and evidence flow

Phase1B-v1.3.0 contributes 584 food measurements/mappings. The Phase 2 builder preserves ordinary-food rows separately from ingredient/prepared-beverage rows, links Stage A/B identities conservatively, and records the source observations and retention ledger in different tables. The 117 raw/cooked observations are not joined to Phase 1B concentrations. The compatibility audit identifies 22 potential concentration/retention combinations: 20 turmeric ingredient-context rows, one pepper/piperine row, and one EGCG prepared-beverage row. None passes all scientific gates.

The new `audit_phase2_source_pairs.py` independently compares each row to manually transcribed original table means/SDs and independently recomputes `cooked mean / raw mean`. The output matrix adds source locator, basis, cooking protocol, sample preparation, assay/statistic, uncertainty interpretation, and status for each pair.

## Gaps and inconsistencies

- The frozen Phase 2 release has no Phase 2 schemas, no standalone source-level audit matrix, and only a compact completion report. The present audit adds source-level reporting and documentation; it does not change output eligibility.
- Phase 2's root builder uses `Path(__file__).resolve()` to find the project root and reads explicit release/input paths. It has no external service dependency. The separate model artifact references a historical Windows path in its manifest; that path is metadata, not an active CLI dependency.
- The 33 turmeric pair rows label units as `mg/g fresh rhizome`. The primary table reports `mg/g` and text says `mg per 1 g of plant material`; methods establish fresh rhizome as the starting material but do not explicitly define the denominator after cooking. The new audit flags this over-specific legacy unit label and leaves the basis unresolved.
- The 45 candidate identity records remain conservative: 27 possible, 9 conflicts, and 9 unresolved. Stage A `PubChem_CID_Resolved` is blank for these candidate groups; an equal reported CID is not by itself accepted identity evidence. No molecular graph toolkit is installed in this runtime, so no new structure-isomorphism decision is claimed.
- Root Phase 1B working-tree counts are from a legacy interface and disagree with the latest versioned Phase1B release. Three tests read the old root working tree/checkpoint. They were preserved and not altered.
- The project worktree is dirty and contains numerous pre-existing untracked Phase 1B/Stage B/Phase 2 artifacts. There are no Git tags for the current Phase 2 release; release lineage is expressed through its manifests and directory names. The additive audit files are also uncommitted workspace files.
- Existing scripts are mostly repository-relative, but default paths are resolved from script location and expect repository layout. No absolute user-home path was found in the Phase 2 builder/source audit scripts; the model manifest retains its original Windows provenance path.

## Release decision

The 117-row source audit and its deterministic validator add traceable evidence, while unresolved basis and identity issues still prevent cooked output. Phase2-v0.1.0 remains unchanged. A successor release is appropriate only as an additive audit/documentation release; it must continue to say NOT COMPLETE and keep its cooked-output table empty.
