"""Structural, identity-linkage and provenance checks for V15."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V14 = ROOT.parent / "StageB_V14_20261102"
V13 = ROOT.parent / "StageB_V13_20261102"
KEY_RE = re.compile(r"^[A-Z]{14}-[A-Z]{10}-[A-Z]$")


def load(rel: str, base: Path = ROOT) -> list[dict[str, str]]:
    with (base / rel).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def issues(compounds, evidence, studies, bibliography, probes, warnings, identity):
    errors: list[str] = []
    cids = [r.get("Compound_ID", "") for r in compounds]
    keys = [r.get("InChIKey", "") for r in compounds]
    pubchem = [r.get("PubChem_CID", "") for r in compounds if r.get("PubChem_CID")]
    eids = [r.get("Evidence_ID", "") for r in evidence]
    wids = [r.get("Warning_ID", "") for r in warnings]
    if not all(cids) or len(cids) != len(set(cids)): errors.append("compound IDs missing or duplicated")
    if not all(keys) or len(keys) != len(set(keys)): errors.append("InChIKeys missing or duplicated")
    if len(pubchem) != len(set(pubchem)): errors.append("PubChem CIDs duplicated")
    if not all(KEY_RE.fullmatch(k) for k in keys): errors.append("malformed InChIKey")
    if not all(eids) or len(eids) != len(set(eids)): errors.append("Evidence_ID missing or duplicated")
    if len(wids) != len(set(wids)): errors.append("Warning_ID duplicated")
    cby = {r["Compound_ID"]: r for r in compounds}
    study_ids = {r["Study_ID"] for r in studies}
    pmids = {r["PMID"] for r in bibliography}
    probe_labels = {r["Drug_Probe"] for r in probes}
    for r in evidence:
        if r.get("Compound_ID") not in cby: errors.append(f"orphan evidence: {r.get('Evidence_ID')}")
        if r.get("Evidence_ID", "").startswith("SB-V15-"):
            if r.get("Study_ID") not in study_ids or r.get("PMID") not in pmids: errors.append(f"unresolved source linkage: {r.get('Evidence_ID')}")
            if not r.get("PMID", "").isdigit(): errors.append(f"invalid PMID: {r.get('Evidence_ID')}")
            if not r.get("DOI", "").startswith("10."): errors.append(f"invalid DOI: {r.get('Evidence_ID')}")
            if "no clinical extrapolation" not in r.get("Clinical_Extrapolation", "").lower(): errors.append(f"clinical limit absent: {r.get('Evidence_ID')}")
            if r.get("Drug") not in probe_labels: errors.append(f"unregistered probe: {r.get('Evidence_ID')}")
            if r.get("Evidence_Type") != "In vitro": errors.append(f"in-vitro evidence misclassified: {r.get('Evidence_ID')}")
            if not r.get("Source_Locator") or not r.get("Quantitative_Outcome"): errors.append(f"outcome/source locator missing: {r.get('Evidence_ID')}")
            if r.get("Outcome") == "null_finding" and r.get("Quantitative_Outcome", "").strip() == "0": errors.append(f"null converted to zero: {r.get('Evidence_ID')}")
    iby = {r.get("Compound_ID"): r for r in identity}
    for r in compounds:
        if r.get("Origin") == "v15_controlled_expansion":
            aud = iby.get(r["Compound_ID"], {})
            if r.get("PubChem_CID", "").isdigit() is False or not r.get("SMILES") or not r.get("InChI", "").startswith("InChI=1S/"):
                errors.append(f"incomplete chemical identity: {r['Compound_ID']}")
            if aud.get("Exact_Key_Match") != "True" or aud.get("Registry_InChIKey") != r.get("InChIKey"):
                errors.append(f"identity audit mismatch: {r['Compound_ID']}")
    return errors


def run() -> dict[str, object]:
    compounds = load("data/compound_registry.csv")
    evidence = load("data/interaction_evidence.csv")
    studies = load("data/study_registry.csv")
    bibliography = load("data/publication_bibliography.csv")
    probes = load("data/drug_probe_registry.csv")
    warnings = load("data/warning_ledger.csv")
    identity = load("identity/identity_structure_audit.csv")
    errors = issues(compounds, evidence, studies, bibliography, probes, warnings, identity)
    metadata = json.loads((ROOT / "release_metadata.json").read_text(encoding="utf-8"))
    for rel, key in (("data/compound_registry.csv", "Compound_ID"), ("data/interaction_evidence.csv", "Evidence_ID"), ("data/warning_ledger.csv", "Warning_ID")):
        current = {r[key]: r for r in load(rel)}
        if any(current.get(r[key]) != r for r in load(rel, V14)):
            errors.append(f"V14 inherited {key} records changed")
    expected = {"expected_compounds": len(set(r["Compound_ID"] for r in compounds)), "expected_evidence": len(set(r["Evidence_ID"] for r in evidence)), "warning_count": len(warnings), "drug_probe_rows": len(probes), "bibliography_rows": len(bibliography), "study_rows": len(studies)}
    for k, n in expected.items():
        if metadata.get(k) != n: errors.append(f"metadata mismatch: {k}")
    result = {"status": "PASS" if not errors else "FAIL", "errors": errors, **expected,
              "unique_PMIDs": len({r["PMID"] for r in bibliography if r.get("PMID")}),
              "new_compounds": sum(r.get("Origin") == "v15_controlled_expansion" for r in compounds),
              "new_evidence": sum(r.get("Evidence_ID", "").startswith("SB-V15-") for r in evidence)}
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    raise SystemExit(0 if run()["status"] == "PASS" else 1)
