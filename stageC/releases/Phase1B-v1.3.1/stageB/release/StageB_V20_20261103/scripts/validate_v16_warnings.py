"""Warning-ledger lifecycle checks for the Stage B V16 release."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"RESOLVED", "PARTIALLY_RESOLVED", "STILL_VALID", "NEEDS_MANUAL_REVIEW", "NOT_APPLICABLE"}
REQUIRED_AUDIT = {"Audit_Status", "Inherited_Severity", "Audit_Rationale", "Audit_Verification_Reference", "Audit_Dependencies"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def validate(warnings: list[dict[str, str]], compounds: list[dict[str, str]], evidence: list[dict[str, str]], studies: list[dict[str, str]], bibliography: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    if not warnings:
        return ["warning ledger is empty"]
    if not REQUIRED_AUDIT.issubset(warnings[0]):
        errors.append("warning audit columns missing")
        return errors
    ids = [r.get("Warning_ID", "") for r in warnings]
    if not all(ids) or len(ids) != len(set(ids)):
        errors.append("warning IDs missing or duplicated")
    cids = {r.get("Compound_ID", "") for r in compounds}
    eids = {r.get("Evidence_ID", "") for r in evidence}
    sids = {r.get("Study_ID", "") for r in studies}
    pmids = {r.get("PMID", "") for r in bibliography}
    for r in warnings:
        wid, status = r.get("Warning_ID", ""), r.get("Audit_Status", "")
        if status not in ALLOWED:
            errors.append(f"{wid}: invalid audit status")
        if not r.get("Description", "").strip() or not r.get("Audit_Rationale", "").strip():
            errors.append(f"{wid}: description or audit rationale missing")
        if r.get("Inherited_Severity") != "NOT_RECORDED":
            errors.append(f"{wid}: inherited severity must remain explicitly unrecorded")
        if status == "RESOLVED" and (not r.get("Audit_Verification_Reference", "").strip() or not r.get("Audit_Rationale", "").strip()):
            errors.append(f"{wid}: resolved warning lacks evidence/rationale")
        if status in {"STILL_VALID", "NEEDS_MANUAL_REVIEW", "PARTIALLY_RESOLVED"} and not r.get("Audit_Dependencies", "").strip():
            errors.append(f"{wid}: open/partial warning lacks dependency or remaining limitation")
        # Validate explicit identifier tokens; free-text scope warnings are allowed.
        affected = r.get("Affected", "")
        for token in affected.replace("|", " ").replace(";", " ").split():
            token = token.strip(" ,")
            if token.startswith("SB-") and token not in eids:
                errors.append(f"{wid}: unknown evidence reference {token}")
            elif token.startswith("MOL-") and token not in cids:
                errors.append(f"{wid}: unknown compound reference {token}")
            elif token.startswith("PMID:") and token[5:] not in pmids:
                errors.append(f"{wid}: unknown PMID reference {token}")
            elif token.isdigit() and len(token) >= 7 and token not in pmids:
                errors.append(f"{wid}: unknown PMID reference {token}")
    return errors


def main() -> int:
    w = rows(ROOT / "data/warning_ledger.csv")
    errors = validate(w, rows(ROOT / "data/compound_registry.csv"), rows(ROOT / "data/interaction_evidence.csv"), rows(ROOT / "data/study_registry.csv"), rows(ROOT / "data/publication_bibliography.csv"))
    print("PASS" if not errors else "FAIL")
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
