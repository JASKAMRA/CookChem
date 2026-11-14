"""Build a provenance-first Stage A / Stage C recovery package.

This script deliberately does not train, load, or alter a historical model.  It
classifies the existing supervised rows using only reproducible repository and
previously checked primary-source evidence.  Any row without that evidence is
kept in the ledger as unresolved rather than promoted into a new training set.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
MASTER = ROOT / "data" / "reviewed" / "cookchem_molecular_retention_master.csv"
MODEL_INPUT = ROOT / "stageA" / "input" / "cookchem_molecular_retention_preprocessed.csv"
PHASE2 = ROOT / "stageC" / "phase2" / "data" / "observed_cooking_pairs.csv"

# These mismatches were independently checked against the publisher/PubMed pages
# listed in source_verification_report.md.  The mapping is intentionally narrow:
# all other rows remain unresolved, not implicitly accepted.
DOI_MISMATCHES = {
    "10.1016/j.lwt.2021.111500": "Publisher identifies fish oil-gelatin electrospun membranes, not the stored avocado/Persin cooking experiment.",
    "10.1016/j.foodchem.2015.04.132": "PubMed identifies melamine determination in dairy products, not the stored potato/antheraxanthin cooking experiment.",
    "10.1016/j.foodcont.2023.109800": "Publisher identifies alpha-lactalbumin ELISA in hypoallergenic formula, not the stored kimchi/capsaicin cooking experiment.",
    "10.1016/j.lwt.2022.113400": "Publisher identifies nixtamalization/acrylamide-precursor work, not the stored black-pepper/piperine cooking experiment.",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(value: str) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except ValueError:
        return None


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    master = read_csv(MASTER)
    model_ids = {row["Record_ID"] for row in read_csv(MODEL_INPUT)}
    phase2 = read_csv(PHASE2)
    phase2_by_id = {row["source_stagea_record_id"]: row for row in phase2}
    historical = [row for row in master if row["Record_ID"] in model_ids]
    if len(historical) != 1124 or len(model_ids) != 1124:
        raise RuntimeError("Expected exactly 1,124 historical supervised rows")

    ledger: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    for row in historical:
        rid = row["Record_ID"]
        target = number(row["Retention_Final"])
        initial, final = number(row["Initial_Concentration"]), number(row["Final_Concentration"])
        calculated = None if initial in (None, 0) or final is None else 100 * final / initial
        phase2_record = phase2_by_id.get(rid)
        if phase2_record:
            status = "VERIFIED"
            target_class = "VERIFIED_APPARENT_RATIO"
            evidence = (
                "Stage C Phase 2 primary-source pair; source locator: "
                f"{phase2_record['source_locator']}. Its declared semantics are "
                f"{phase2_record['ratio_semantics']}."
            )
            inclusion = "EXCLUDED_FROM_MODEL_REBUILD"
            reason = "Verified apparent concentration ratio, not total-mass retention; yield/mass basis absent."
        elif row["DOI"].strip().lower() in DOI_MISMATCHES:
            status = "DOI_MISMATCH"
            target_class = "UNRESOLVED_TARGET_SEMANTICS"
            evidence = DOI_MISMATCHES[row["DOI"].strip().lower()]
            inclusion = "EXCLUDED_FROM_MODEL_REBUILD"
            reason = "Claimed experiment is contradicted by DOI metadata."
        elif row.get("Retention_Eligibility_Promotion_Reason", "").strip():
            status = "TARGET_FORMULA_UNRESOLVED"
            target_class = "UNRESOLVED_TARGET_SEMANTICS"
            evidence = row["Retention_Eligibility_Promotion_Reason"]
            inclusion = "EXCLUDED_FROM_MODEL_REBUILD"
            reason = "A stored target-review/promotion note requires source-level formula adjudication; it is not deployment evidence."
        else:
            status = "INSUFFICIENT_EVIDENCE"
            target_class = "UNRESOLVED_TARGET_SEMANTICS"
            evidence = (
                "No audited primary-paper table/figure locator and source-to-target derivation "
                "is present in the repository recovery evidence."
            )
            inclusion = "EXCLUDED_FROM_MODEL_REBUILD"
            reason = "No source-level target contract established."
        target_matches_ratio = calculated is not None and target is not None and abs(target - calculated) <= 0.1
        ledger_row = {
            "record_id": rid,
            "paper_id": row["Paper_ID"],
            "doi": row["DOI"],
            "source_paper_key": row.get("Source_Paper_Key", ""),
            "compound": row["Compound_Name"],
            "canonical_molecular_id": row["Canonical_Molecular_ID"],
            "food_matrix": row["Food_Name"],
            "cooking_method": row["Cooking_Method"],
            "temperature_c": row["Temperature_C"],
            "time_min": row["Cooking_Time_min"],
            "initial_concentration": row["Initial_Concentration"],
            "initial_unit": row["Initial_Unit"],
            "final_concentration": row["Final_Concentration"],
            "final_unit": row["Final_Unit"],
            "reported_retention_percent": row["Reported_Retention_Percent"],
            "calculated_concentration_ratio_percent": "" if calculated is None else f"{calculated:.10g}",
            "retention_final": row["Retention_Final"],
            "retention_final_matches_stored_ratio": str(target_matches_ratio).lower(),
            "evidence_status": status,
            "target_classification": target_class,
            "source_locator_or_evidence": evidence,
            "model_rebuild_disposition": inclusion,
            "exclusion_reason": reason,
        }
        ledger.append(ledger_row)
        exclusions.append({key: ledger_row[key] for key in (
            "record_id", "paper_id", "doi", "compound", "evidence_status", "target_classification",
            "model_rebuild_disposition", "exclusion_reason"
        )})

    ledger_fields = list(ledger[0])
    write_csv(OUT / "source_to_target_ledger.csv", ledger, ledger_fields)
    write_csv(OUT / "dataset_exclusion_log.csv", exclusions, list(exclusions[0]))
    status_counts = Counter(row["evidence_status"] for row in ledger)
    target_counts = Counter(row["target_classification"] for row in ledger)
    ratio_matches = sum(row["retention_final_matches_stored_ratio"] == "true" for row in ledger)
    verified = [row for row in ledger if row["evidence_status"] == "VERIFIED"]
    mismatch_rows = [row for row in ledger if row["evidence_status"] == "DOI_MISMATCH"]

    (OUT / "repository_audit.md").write_text(f"""# Stage A + Stage C recovery repository audit

Generated: {datetime.now(timezone.utc).isoformat()}

## Authoritative historical inputs inspected

| Path | SHA-256 | Role |
|---|---|---|
| `data/reviewed/cookchem_molecular_retention_master.csv` | `{sha256(MASTER)}` | Reviewed historical source table; not altered |
| `stageA/input/cookchem_molecular_retention_preprocessed.csv` | `{sha256(MODEL_INPUT)}` | 1,124-row historical supervised input; not altered |
| `stageC/phase2/data/observed_cooking_pairs.csv` | `{sha256(PHASE2)}` | Primary-source cooking-pair audit evidence |
| `stageB/final_model/cookrisk_retention_stageB_selected.joblib` | `{sha256(ROOT / 'stageB/final_model/cookrisk_retention_stageB_selected.joblib')}` | Historical candidate artifact; not loaded |

## Finding

This recovery package contains no trained model and no replacement dataset. The ledger retains all 1,124 historical model rows and records why none is admitted to a rebuilt model. The current scientific gate is blocked, not an engineering failure to be bypassed.
""", encoding="utf-8")

    (OUT / "target_definition_contract.md").write_text("""# Target-definition contract — status BLOCKED

## No approved Stage A model target

No common target is approved for retraining or inference in this release.

### Verified limited target family

`VERIFIED_APPARENT_RATIO = 100 × C_cooked / C_raw`

This is a unit-preserving cooked/raw concentration ratio for the 117 linked Phase 2 observations. It is not total-mass retention. It cannot yield cooked analyte mass without compatible raw/cooked yield, moisture basis, and cooking-liquid disposition.

### Explicitly prohibited substitutions

- Do not call an apparent concentration ratio total-mass retention.
- Do not use `Apparent_Increase` as a predictor.
- Do not invent a yield factor or infer it from food type.
- Do not pass `Retention_Final` model outputs into a Stage C cooked-exposure calculation.

## Requirements to approve any future target

For every admitted source row: original paper locator; original values and units; numerator and denominator; raw/cooked basis; yield and liquid disposition when total-mass retention is claimed; reproducible equation; named scientific review.
""", encoding="utf-8")

    (OUT / "source_verification_report.md").write_text(f"""# Source verification report — preliminary, fail-closed

## Ledger result

- Historical supervised rows: **{len(ledger)}**
- `VERIFIED`: **{len(verified)}** — all are verified apparent concentration ratios, not total-mass retention.
- `DOI_MISMATCH`: **{len(mismatch_rows)}**
- Other unresolved rows: **{len(ledger) - len(verified) - len(mismatch_rows)}**
- Stored targets matching a raw/final concentration calculation: **{ratio_matches}**

## Primary-source evidence used

1. Zagórska et al. (2023), *Impact of Thermal Processing on the Composition of Curcuma longa Rhizome*, DOI `10.3390/foods12163086`, [primary full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10453412/), Table 1. Phase 2 confirms the 33 linked records are concentration ratios and documents missing cooked yield.
2. Stryjecka et al. (2026), *Effects of Household Cooking Methods on the Nutritional, Phytochemical and Functional Properties of Cucurbita maxima Leaves*, DOI `10.3390/molecules31162740`, [PubMed record](https://pubmed.ncbi.nlm.nih.gov/42653823/), Tables 2–3. Phase 2 confirms the 84 linked records are dry-weight concentration ratios and documents missing cooked yield.

## Independently checked DOI mismatches

- `10.1016/j.lwt.2021.111500`: [publisher record](https://www.sciencedirect.com/science/article/pii/S0023643821006538) is fish oil-gelatin electrospun membranes, not avocado/Persin cooking.
- `10.1016/j.foodchem.2015.04.132`: [PubMed record](https://pubmed.ncbi.nlm.nih.gov/26041169/) is melamine determination in dairy products, not potato/antheraxanthin cooking.
- `10.1016/j.foodcont.2023.109800`: [publisher record](https://www.sciencedirect.com/science/article/abs/pii/S0956713523002001) is alpha-lactalbumin ELISA in hypoallergenic formula, not kimchi/capsaicin cooking.
- `10.1016/j.lwt.2022.113400`: [publisher record](https://www.sciencedirect.com/science/article/pii/S0023643822003358) is maize nixtamalization/acrylamide precursors, not black-pepper/piperine cooking.

## Limit

This is a machine-readable ledger for every supervised row, not a claim that every DOI has now been independently re-extracted. Rows without a primary-source table locator and reproducible transformation remain unresolved by design.
""", encoding="utf-8")

    (OUT / "dataset_reconstruction_report.md").write_text(f"""# Dataset reconstruction decision

## Decision: no clean modelling dataset released

All **{len(ledger)}** historical supervised rows are excluded from a new model dataset in this release. This prevents a false impression that arithmetic agreement alone establishes physical retention.

| Evidence status | Rows |
|---|---:|
""" + "\n".join(f"| {key} | {value} |" for key, value in sorted(status_counts.items())) + f"""

## Why no model was trained

The only verified subset has {len(verified)} observations across {len({x['canonical_molecular_id'] for x in verified})} molecular groups and represents apparent concentration ratios. It lacks yield/mass data and cannot support total-mass cooking exposure. The remaining rows require source-by-source reconstruction before they can be included in any scientifically defined target family.
""", encoding="utf-8")

    (OUT / "stageA_model_comparison.md").write_text("""# Stage A model comparison — not run

No model was retrained, loaded, selected, or compared in this recovery version. Historical Extra Trees, Random Forest, SVR, and XGBoost results remain historical evaluation artifacts only. Comparing models before approving a common scientific target would be invalid.
""", encoding="utf-8")

    (OUT / "stageA_deployment_contract.md").write_text("""# Stage A deployment contract — BLOCKED

The Stage C adapter may accept a `model_predicted_retention` record only after a future package supplies an approved model artifact, preprocessing schema, target contract, model/data hashes, applicability checks, uncertainty declaration, and scientific approval. This recovery package deliberately supplies none of these, so it cannot authorize inference.
""", encoding="utf-8")

    (OUT / "stageC_integration_decision.md").write_text("""# Stage C integration decision — no code change justified

The existing `stageC/src/stage_c/cooking_integration.py` already separates apparent concentration ratios, concentration retention, total-mass retention, measured retention, and model-predicted retention. Its fail-closed behavior blocks unregistered model predictions and prevents apparent ratios being used as total-mass multipliers.

No Stage C code was changed in this recovery version. A change would be premature because this package does not approve a model or a target contract. The next integration change, only after scientific approval, is to register a separately versioned model-prediction package through the existing `model_predicted_retention` path with an explicit semantic type, hashes, applicability result, and uncertainty declaration.
""", encoding="utf-8")

    (OUT / "end_to_end_validation_report.md").write_text("""# End-to-end validation — BLOCKED BY SCIENTIFIC GATE

No raw-to-cooked model path was executed. The existing Stage C Phase 3 raw-reference and fail-closed cooking-integration behavior are preserved. Model-predicted cooked exposure remains unavailable; measured apparent ratios remain distinct from total-mass retention.
""", encoding="utf-8")

    (OUT / "reproducibility.md").write_text("""# Reproducibility

Run from repository root:

```powershell
python stageA/recovery_v0_1_0_2026_11_10/build_recovery_package.py
python stageA/recovery_v0_1_0_2026_11_10/validate_recovery.py
```

The build reads only historical CSV inputs and overwrites only generated files inside this versioned recovery directory.
""", encoding="utf-8")

    (OUT / "FINAL_PROJECT_STATUS.md").write_text(f"""# CookRisk Stage A + Stage C recovery status

## Overall readiness: BLOCKED / RESEARCH PROTOTYPE

- **Scientific validation:** NOT VALIDATED for model-predicted cooking retention.
- **Engineering:** existing Stage C fail-closed integration is conditionally usable for raw-reference and separately labelled measured evidence.
- **Model rebuild:** not performed; no scientifically coherent target dataset is available.
- **Cooked compound exposure from Stage A predictions:** BLOCKED.

`Retention_Final` is predominantly a stored apparent concentration-ratio-like number, not verified total-mass retention. {len(verified)} rows have primary-source traceability as apparent ratios; no row is verified as total-mass retention. The next work item is source-family reconstruction, starting with every force-promoted discrepancy and every demonstrated DOI mismatch.
""", encoding="utf-8")

    manifest = {
        "package": "StageA_StageC_Recovery_v0.1.0_2026-11-10",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_hashes": {str(p.relative_to(ROOT)): sha256(p) for p in (MASTER, MODEL_INPUT, PHASE2)},
        "summary": {"historical_model_rows": len(ledger), "status_counts": status_counts, "target_counts": target_counts, "model_trained": False, "deployment_authorized": False},
    }
    (OUT / "recovery_manifest.json").write_text(json.dumps(manifest, indent=2, default=dict, sort_keys=True) + "\n", encoding="utf-8")
    manifest_files = [p for p in OUT.iterdir() if p.is_file() and p.name != "SHA256SUMS.txt"]
    (OUT / "SHA256SUMS.txt").write_text("".join(f"{sha256(p)}  {p.name}\n" for p in sorted(manifest_files)), encoding="utf-8")


if __name__ == "__main__":
    main()
