"""Structural and provenance checks for the Stage B V14 candidate release."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "stageB" / "release" / "StageB_V14_20261102"
V13 = ROOT / "stageB" / "release" / "StageB_V13_20261102"


def load(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def issues(compounds: list[dict[str, str]], evidence: list[dict[str, str]],
           studies: list[dict[str, str]], bibliography: list[dict[str, str]],
           warnings: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    ids = [r.get("Compound_ID", "") for r in compounds]
    keys = [r.get("InChIKey", "") for r in compounds]
    eids = [r.get("Evidence_ID", "") for r in evidence]
    if len(ids) != len(set(ids)) or "" in ids:
        errors.append("compound IDs are missing or duplicated")
    if len(keys) != len(set(keys)) or "" in keys:
        errors.append("InChIKeys are missing or duplicated")
    if len(eids) != len(set(eids)) or "" in eids:
        errors.append("evidence IDs are missing or duplicated")
    by_id = {r.get("Compound_ID"): r for r in compounds}
    study_ids = {r.get("Study_ID") for r in studies}
    pmids = {r.get("PMID") for r in bibliography if r.get("PMID")}
    warning_ids = [r.get("Warning_ID") for r in warnings]
    if len(warning_ids) != len(set(warning_ids)):
        errors.append("warning IDs are duplicated")
    for row in evidence:
        if row.get("Compound_ID") not in by_id:
            errors.append(f"orphan evidence: {row.get('Evidence_ID')}")
        # Inherited V13 records retain documented historical linkage gaps; newly
        # curated V14 rows must satisfy the stronger linkage contract.
        is_v14 = row.get("Evidence_ID", "").startswith("SB-V14-")
        if is_v14 and (row.get("Study_ID") not in study_ids or row.get("PMID") not in pmids):
            errors.append(f"unresolved source linkage: {row.get('Evidence_ID')}")
        if is_v14 and row.get("PMID") and not row["PMID"].isdigit():
            errors.append(f"invalid PMID: {row.get('Evidence_ID')}")
        if is_v14 and row.get("DOI") and not row["DOI"].startswith("10."):
            errors.append(f"invalid DOI: {row.get('Evidence_ID')}")
        design = row.get("Study_Design", "").lower().replace("-", " ")
        if is_v14 and row.get("Evidence_Type") == "Human pharmacokinetic" and "in vitro" in design:
            errors.append(f"in-vitro study mislabeled as human: {row.get('Evidence_ID')}")
        if is_v14 and row.get("Quantitative_Outcome", "").strip() == "0":
            errors.append(f"missing/negative value may have been converted to zero: {row.get('Evidence_ID')}")
    for row in compounds:
        if row.get("Origin") == "v14_controlled_expansion" and not (row.get("PubChem_CID", "").isdigit() and row.get("Identity_Source", "").startswith("https://pubchem.ncbi.nlm.nih.gov/compound/")):
            errors.append(f"incomplete candidate identity: {row.get('Compound_ID')}")
    return errors


def run() -> dict[str, object]:
    compounds = load(RELEASE / "data" / "compound_registry.csv")
    evidence = load(RELEASE / "data" / "interaction_evidence.csv")
    studies = load(RELEASE / "data" / "study_registry.csv")
    bibliography = load(RELEASE / "data" / "publication_bibliography.csv")
    warnings = load(RELEASE / "data" / "warning_ledger.csv")
    metadata = json.loads((RELEASE / "release_metadata.json").read_text(encoding="utf-8"))
    problems = issues(compounds, evidence, studies, bibliography, warnings)
    cids = {r["Compound_ID"] for r in compounds}
    eids = {r["Evidence_ID"] for r in evidence}
    for rel, key in (("data/compound_registry.csv", "Compound_ID"), ("data/interaction_evidence.csv", "Evidence_ID")):
        old = load(V13 / rel)
        current = {r[key]: r for r in load(RELEASE / rel)}
        if any(current.get(r[key]) != r for r in old):
            problems.append(f"V13 historical {key} records changed")
    if len(cids) != metadata.get("expected_compounds"):
        problems.append("compound count disagrees with release metadata")
    if len(eids) != metadata.get("expected_evidence"):
        problems.append("evidence count disagrees with release metadata")
    if len(warnings) != metadata.get("warning_count"):
        problems.append("warning count disagrees with release metadata")
    result = {"status": "PASS" if not problems else "FAIL", "errors": problems,
              "compound_count": len(cids), "evidence_count": len(eids),
              "bibliography_rows": len(bibliography), "unique_PMIDs": len({r['PMID'] for r in bibliography if r['PMID']}),
              "study_rows": len(studies), "warning_count": len(warnings),
              "identity_checked": sum(1 for r in compounds if r.get("Origin") == "v14_controlled_expansion"),
              "new_evidence_checked": sum(1 for r in evidence if r.get("Evidence_ID", "").startswith("SB-V14-"))}
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    sys.exit(0 if run()["status"] == "PASS" else 1)
