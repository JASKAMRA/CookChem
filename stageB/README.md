# CookChem Stage B

Stage B contains two related but distinct resources: the cooking-retention model experiments and the CookRisk literature evidence package. This cleanup changes organization and execution paths only; it does not alter scientific records or model outputs.

## Authoritative release

The sole authoritative evidence release is [`release/StageB_Final/`](release/StageB_Final/). It is the existing consolidated release, copied into this repository without regeneration. Its canonical tables live in `release/StageB_Final/data/`; its own README and handoff explain evidence scope, record counts, validation limits, and scientific cautions. The release remains a literature evidence resource, not clinical decision support.

## Layout

- `scripts/` — active, version-independent entry points plus model research scripts.
- `outputs/`, `final_model/` — existing retention experiments, their outputs, and selected model; paths are preserved.
- `release/StageB_Final/` — authoritative evidence release.
- `validation/` — cleanup inventories and non-invasive release check results.
- `provenance/` — provenance notes for this organization pass.
- `documentation/` — project workflow and change records.
- `archive/scripts/` — original version-specific builders, finalizers, auditors, validators, mutation tests, and consolidation tools. Exact duplicate nested experiment scripts are preserved under `archive/scripts/duplicates/`.
- `archive/releases/` — preserved V2–V12 releases, expansions, V6 workspaces, and legacy workspace snapshots.
- `archive/reports/` — legacy project handoffs and release archive files.

The root `README.md`, `.gitignore`, and `requirements.txt` remain shared project files. Stage A remains untouched.

## Active evidence workflow

Run from the repository root (Python 3):

```powershell
python stageB/scripts/validate.py
python stageB/scripts/mutation_tests.py
python stageB/scripts/audit.py
```

Validation and mutation checks run on disposable copies so the authoritative release and its checksums stay unchanged. Results are written to `stageB/validation/`. A clean mutation result means each injected integrity defect was detected; it does not establish scientific validity.

To build a new staging tree, provide an explicit V11 directory and a destination that does not exist:

```powershell
python stageB/scripts/build.py <path-to-release_v11> <new-staging-directory>
```

The build copies the source before applying V12 build logic. Finalize that staging copy with `python stageB/scripts/finalize.py <staging-directory>`. Consolidate a finalized V12 tree using `python stageB/scripts/consolidate.py <path-to-release_v12> <new-destination>`. These commands reject the authoritative release path; do not point them at it. Historical versions are available under `archive/releases/`.

## Retention model workflow

Existing experiments remain under `scripts/` and write to `outputs/`. They read Stage A's preprocessed input at `stageA/input/cookchem_molecular_retention_preprocessed.csv`; the input is shared and was not moved. `freeze_stageb_candidate.py` writes the retained model under `final_model/`. Install the model dependencies listed in `stageB/requirements-stageB.txt` in addition to shared project requirements. Model execution was not available in the current Python environment because NumPy is absent; the active scripts passed syntax compilation, while model runtime imports require installing those dependencies. The archived literature evidence package is separate from these model experiments.

## Stage C interface

Stage C should read the stable, unversioned CSV tables in `release/StageB_Final/data/`, join by the recorded compound/publication/evidence identifiers, and retain warning and provenance fields. Review `release/StageB_Final/documentation/FINAL_HANDOFF.md` and `manual_review_status.csv` before interpreting the records. Do not treat in-vitro or animal observations as clinical effects, infer ordinary food exposure from supplement doses, or convert the evidence package into patient-specific advice.

## Known limitations

The final release records unresolved source-audit, quantitative-outcome, and manual scientific review flags. The checks validate structure, references, and file integrity, not the truth of each claim. Model experiment dependencies are broader than the shared repository requirements. Archived historical scripts may retain their original command-line interfaces and versioned output names.
