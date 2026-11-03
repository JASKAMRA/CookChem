"""Structural, referential, warning, and V16-baseline checks for V17."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V16 = ROOT.parent / "StageB_V16_20261102"
sys.path.insert(0, str(ROOT / "scripts"))
import validate_v15  # noqa: E402
import validate_v16_warnings  # noqa: E402


def rows(root: Path, rel: str) -> list[dict[str, str]]:
    with (root / rel).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def validate_warning_summary(warnings: list[dict[str, str]], summary: dict) -> list[str]:
    errors: list[str] = []
    ids = [r.get("Warning_ID", "") for r in warnings]
    if len(ids) != len(set(ids)):
        errors.append("warning ledger contains duplicate IDs")
    if set(summary.get("current_warning_ids", [])) != set(ids):
        errors.append("warning summary ID set does not match the ledger")
    actual_counts: dict[str, int] = {}
    actual_severity: dict[str, int] = {}
    for row in warnings:
        status = row.get("Audit_Status", "")
        severity = row.get("Inherited_Severity", "")
        actual_counts[status] = actual_counts.get(status, 0) + 1
        actual_severity[severity] = actual_severity.get(severity, 0) + 1
    if summary.get("current_ledger_status_counts") != actual_counts:
        errors.append("warning summary status counts do not match the ledger")
    if summary.get("all_release_severity_distribution") != actual_severity:
        errors.append("warning summary severity distribution does not match the ledger")
    if summary.get("v17_reaudit_complete") is True and summary.get("v17_reaudited_warning_rows") != 66:
        errors.append("warning summary claims incomplete inherited re-audit is complete")
    if summary.get("inherited_warning_count") != 66 or summary.get("warning_rows_preserved") != len(warnings):
        errors.append("warning summary inherited/total row counts do not reconcile")
    return errors


def validate_warning_audit_report(warnings: list[dict[str, str]], audit: list[dict[str, str]], summary: dict) -> list[str]:
    errors: list[str] = []
    current = {r.get("Warning_ID", ""): r for r in warnings}
    ids = [r.get("Warning_ID", "") for r in audit]
    allowed = {"RESOLVED", "PARTIALLY_RESOLVED", "STILL_VALID", "NEEDS_MANUAL_REVIEW", "NOT_APPLICABLE"}
    if len(ids) != len(set(ids)):
        errors.append("V17 warning audit contains duplicate IDs")
    if set(ids) != set(current):
        errors.append("V17 warning audit IDs do not match the current ledger")
    counts: dict[str, int] = {}
    for row in audit:
        wid = row.get("Warning_ID", "")
        status = row.get("V17_Audit_Status", "")
        counts[status] = counts.get(status, 0) + 1
        if status not in allowed:
            errors.append(f"{wid}: invalid V17 audit status")
        if wid not in current:
            continue
        if row.get("Historical_Status") != current[wid].get("Audit_Status"):
            errors.append(f"{wid}: historical warning disposition changed in V17 report")
        if row.get("Inherited_Severity") != current[wid].get("Inherited_Severity"):
            errors.append(f"{wid}: severity differs from preserved ledger")
        if not row.get("V17_Current_Finding", "").strip() or not row.get("V17_Verification_Work", "").strip():
            errors.append(f"{wid}: V17 audit finding or verification work missing")
        if not row.get("Primary_or_Internal_References", "").strip():
            errors.append(f"{wid}: V17 audit references missing")
        if status == "RESOLVED" and not row.get("Technical_Repair", "").strip():
            errors.append(f"{wid}: resolved V17 warning lacks verified corrective action")
        if status in {"STILL_VALID", "PARTIALLY_RESOLVED", "NEEDS_MANUAL_REVIEW"} and not row.get("Remaining_Limitations", "").strip():
            errors.append(f"{wid}: open V17 warning lacks remaining limitation")
    if summary.get("status_counts") != counts:
        errors.append("V17 warning audit summary status counts do not match the report")
    if summary.get("v17_audited_total_warning_rows") != len(current) or summary.get("v17_reaudit_complete") is not True:
        errors.append("V17 warning summary does not certify the complete current warning set")
    if summary.get("inherited_warnings_audited") != 66 or summary.get("v17_reaudited_warning_rows") != 66:
        errors.append("V17 warning summary inherited audit count does not reconcile")
    return errors


def validate() -> list[str]:
    errors: list[str] = []
    c = rows(ROOT, "data/compound_registry.csv")
    e = rows(ROOT, "data/interaction_evidence.csv")
    s = rows(ROOT, "data/study_registry.csv")
    b = rows(ROOT, "data/publication_bibliography.csv")
    p = rows(ROOT, "data/drug_probe_registry.csv")
    w = rows(ROOT, "data/warning_ledger.csv")
    i = rows(ROOT, "identity/identity_structure_audit.csv")
    food_context = rows(ROOT, "provenance/food_context_audit.csv")
    source_register = rows(ROOT, "provenance/source_register.csv")
    source_audit = rows(ROOT, "provenance/source_audit.csv")
    errors.extend(validate_v15.issues(c, e, s, b, p, w, i))
    errors.extend(validate_v16_warnings.validate(w, c, e, s, b))
    warning_summary = json.loads((ROOT / "validation/V17_warning_audit_status.json").read_text(encoding="utf-8"))
    errors.extend(validate_warning_summary(w, warning_summary))
    warning_audit = rows(ROOT, "validation/V17_warning_by_warning_audit.csv")
    errors.extend(validate_warning_audit_report(w, warning_audit, warning_summary))
    compounds_by_id = {r["Compound_ID"]: r for r in c}
    identities_by_id = {r["Compound_ID"]: r for r in i}
    food_by_compound = {r["Compound_ID"]: r for r in food_context}
    study_ids = {r["Study_ID"] for r in s}
    pmids = {r["PMID"] for r in b if r.get("PMID")}
    probe_labels = {r["Drug_Probe"] for r in p}
    v17_compounds = [r for r in c if r.get("Origin") == "v17_batch_08"]
    v17_evidence = [r for r in e if r.get("Evidence_ID", "") in {f"SB-V17-{n:03d}" for n in range(1, 5)}]
    if v17_compounds:
        if len(v17_compounds) != 4:
            errors.append("V17 batch 8 must admit exactly four compounds")
        if len(v17_evidence) != len(v17_compounds):
            errors.append("each V17 batch 8 compound must have one evidence record")
        for compound in v17_compounds:
            cid = compound["Compound_ID"]
            audit = identities_by_id.get(cid, {})
            if not compound.get("PubChem_CID", "").isdigit() or not compound.get("SMILES") or not compound.get("InChI", "").startswith("InChI=1S/"):
                errors.append(f"V17 compound identity incomplete: {cid}")
            if audit.get("Exact_Key_Match") != "True" or audit.get("Registry_InChIKey") != compound.get("InChIKey"):
                errors.append(f"V17 chemical identity audit mismatch: {cid}")
            food = food_by_compound.get(cid, {})
            if not food.get("Context_Source") or not food.get("Review_Status"):
                errors.append(f"V17 food-context audit missing or incomplete: {cid}")
            elif not any(r.get("Compound") == compound.get("Canonical_Name") and r.get("Primary_source") for r in source_register):
                errors.append(f"V17 food-context source-register link missing: {cid}")
            linked = [r for r in v17_evidence if r.get("Compound_ID") == cid]
            if len(linked) != 1:
                errors.append(f"V17 evidence linkage count invalid: {cid}")
            for record in linked:
                if record.get("Study_ID") not in study_ids or record.get("PMID") not in pmids:
                    errors.append(f"V17 evidence bibliography/study linkage invalid: {record.get('Evidence_ID')}")
                if record.get("Drug") not in probe_labels or record.get("Evidence_Type") != "In vitro":
                    errors.append(f"V17 evidence probe/type invalid: {record.get('Evidence_ID')}")
                if not record.get("Quantitative_Outcome") or not record.get("Source_Locator"):
                    errors.append(f"V17 evidence outcome/source missing: {record.get('Evidence_ID')}")
                if not any(r.get("Evidence_ID") == record.get("Evidence_ID") and r.get("Verification_Status") for r in source_audit):
                    errors.append(f"V17 source audit missing: {record.get('Evidence_ID')}")
        warning_by_id = {r["Warning_ID"]: r for r in w}
        batch_warning = warning_by_id.get("V17-W01", {})
        if batch_warning.get("Audit_Status") != "STILL_VALID" or not batch_warning.get("Audit_Dependencies"):
            errors.append("V17 batch 8 scientific limitation warning must remain open")
    batch9_compounds = [r for r in c if r.get("Origin") == "v17_batch_09"]
    batch9_evidence = [r for r in e if r.get("Release_Origin") == "v17_batch_09"]
    if batch9_compounds:
        if len(batch9_compounds) != 1 or len(batch9_evidence) != len(batch9_compounds):
            errors.append("V17 batch 9 compound/evidence cardinality invalid")
        for compound in batch9_compounds:
            cid = compound["Compound_ID"]
            linked = [r for r in batch9_evidence if r.get("Compound_ID") == cid]
            food = food_by_compound.get(cid, {})
            audit = identities_by_id.get(cid, {})
            if len(linked) != 1 or food.get("Context_Source", "") == "" or audit.get("Exact_Key_Match") != "True":
                errors.append(f"V17 batch 9 identity/evidence/food linkage invalid: {cid}")
            for record in linked:
                if record.get("Study_ID") not in study_ids or record.get("PMID") not in pmids or not record.get("Source_Locator"):
                    errors.append(f"V17 batch 9 bibliography/study/source linkage invalid: {record.get('Evidence_ID')}")
                if not any(r.get("Evidence_ID") == record.get("Evidence_ID") for r in source_audit):
                    errors.append(f"V17 batch 9 source audit missing: {record.get('Evidence_ID')}")
        warning_by_id = {r["Warning_ID"]: r for r in w}
        if warning_by_id.get("V17-W02", {}).get("Audit_Status") != "STILL_VALID":
            errors.append("V17 batch 9 scientific limitation warning must remain open")
    batch10_compounds = [r for r in c if r.get("Origin") == "v17_batch_10"]
    batch10_evidence = [r for r in e if r.get("Release_Origin") == "v17_batch_10"]
    if batch10_compounds:
        if len(batch10_compounds) != 1 or len(batch10_evidence) != 1:
            errors.append("V17 batch 10 compound/evidence cardinality invalid")
        for compound in batch10_compounds:
            linked = [r for r in batch10_evidence if r.get("Compound_ID") == compound.get("Compound_ID")]
            if compound.get("Canonical_Name") != "S-equol" or compound.get("PubChem_CID") != "91469" or compound.get("InChIKey") != "ADFCQWZHKCXPAJ-GFCCVEGCSA-N":
                errors.append("V17 batch 10 stereospecific identity mismatch")
            if len(linked) != 1 or "18.6 ± 5.6 μM" not in linked[0].get("Quantitative_Outcome", ""):
                errors.append("V17 batch 10 quantitative evidence missing or incorrect")
            if linked and (linked[0].get("Study_ID") not in study_ids or linked[0].get("PMID") not in pmids):
                errors.append("V17 batch 10 publication/study linkage invalid")
            if not any(r.get("Compound_ID") == compound.get("Compound_ID") for r in food_context):
                errors.append("V17 batch 10 dietary-metabolite context missing")
        warning_by_id = {r["Warning_ID"]: r for r in w}
        if warning_by_id.get("V17-W03", {}).get("Audit_Status") != "STILL_VALID":
            errors.append("V17 batch 10 scientific/source limitation warning must remain open")
    batch11_compounds = [r for r in c if r.get("Origin") == "v17_batch_11"]
    batch11_evidence = [r for r in e if r.get("Release_Origin") == "v17_batch_11"]
    if batch11_compounds:
        if len(batch11_compounds) != 1 or len(batch11_evidence) != 1:
            errors.append("V17 batch 11 compound/evidence cardinality invalid")
        for compound in batch11_compounds:
            cid = compound.get("Compound_ID")
            linked = [r for r in batch11_evidence if r.get("Compound_ID") == cid]
            audit = identities_by_id.get(cid, {})
            food = food_by_compound.get(cid, {})
            if compound.get("Canonical_Name") != "Phloridzin" or compound.get("PubChem_CID") != "6072" or audit.get("Exact_Key_Match") != "True":
                errors.append("V17 batch 11 chemical identity mismatch")
            if len(linked) != 1 or "IC50=110 μM" not in linked[0].get("Quantitative_Outcome", ""):
                errors.append("V17 batch 11 primary quantitative result missing")
            if linked and (linked[0].get("PMID") != "34396892" or linked[0].get("Study_ID") not in study_ids or linked[0].get("PMID") not in pmids):
                errors.append("V17 batch 11 source/study/bibliography linkage invalid")
            if not food.get("Context_Source") or not any(r.get("Compound") == "Phloridzin" and r.get("Primary_source") for r in source_register):
                errors.append("V17 batch 11 food occurrence/source register linkage missing")
        if {r.get("Warning_ID"): r for r in w}.get("V17-W04", {}).get("Audit_Status") != "STILL_VALID":
            errors.append("V17 batch 11 source limitation warning must remain open")
    for rel, key in (("data/compound_registry.csv", "Compound_ID"), ("data/interaction_evidence.csv", "Evidence_ID")):
        old = {r[key]: r for r in rows(V16, rel)}
        new = {r[key]: r for r in rows(ROOT, rel)}
        if not set(old).issubset(new):
            errors.append(f"inherited V16 {key} rows disappeared")
        for ident, previous in old.items():
            if new.get(ident) != previous:
                errors.append(f"inherited V16 {key} changed: {ident}")
    old_w = {r["Warning_ID"]: r for r in rows(V16, "data/warning_ledger.csv")}
    new_w = {r["Warning_ID"]: r for r in w}
    if not set(old_w).issubset(new_w):
        errors.append("inherited V16 warning disappeared")
    for ident, previous in old_w.items():
        if ident not in new_w:
            errors.append(f"inherited V16 warning disappeared: {ident}")
        elif any(new_w[ident].get(k) != v for k, v in previous.items()):
            errors.append(f"inherited V16 warning history changed: {ident}")
    meta = json.loads((ROOT / "release_metadata.json").read_text(encoding="utf-8"))
    counts = {
        "expected_compounds": len({r["Compound_ID"] for r in c}),
        "expected_evidence": len({r["Evidence_ID"] for r in e}),
        "drug_probe_rows": len(p), "bibliography_rows": len(b),
        "study_rows": len(s), "warning_count": len(w),
    }
    if meta.get("release") != ROOT.name:
        errors.append("release metadata identifier mismatch")
    if meta.get("baseline_release") != V16.name:
        errors.append("release metadata baseline mismatch")
    for key, actual in counts.items():
        if meta.get(key) != actual:
            errors.append(f"metadata count mismatch: {key}")
    if meta.get("target_compounds") != 143:
        errors.append("approved V17 final scope must remain 143 compounds")
    return errors


if __name__ == "__main__":
    found = validate()
    print(json.dumps({"status": "PASS" if not found else "FAIL", "errors": found}, indent=2))
    raise SystemExit(bool(found))
