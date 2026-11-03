"""Structural, linkage, metadata, and inherited-record checks for V16."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V15 = ROOT.parent / "StageB_V15_20261102"
sys.path.insert(0, str(V15 / "scripts"))
import validate_v15  # noqa: E402


def load(root: Path, rel: str) -> list[dict[str, str]]:
    with (root / rel).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def validate() -> list[str]:
    errors: list[str] = []
    c = load(ROOT, "data/compound_registry.csv")
    e = load(ROOT, "data/interaction_evidence.csv")
    s = load(ROOT, "data/study_registry.csv")
    b = load(ROOT, "data/publication_bibliography.csv")
    p = load(ROOT, "data/drug_probe_registry.csv")
    w = load(ROOT, "data/warning_ledger.csv")
    i = load(ROOT, "identity/identity_structure_audit.csv")
    errors.extend(validate_v15.issues(c, e, s, b, p, w, i))
    for rel, key in (("data/compound_registry.csv", "Compound_ID"), ("data/interaction_evidence.csv", "Evidence_ID")):
        old = {r[key]: r for r in load(V15, rel)}
        new = {r[key]: r for r in load(ROOT, rel)}
        if not set(old).issubset(new):
            errors.append(f"V15 {key} rows disappeared")
        for ident, previous in old.items():
            current = new.get(ident, {})
            allowed = {"DOI", "Notes"} if ident == "SB-0021" else set()
            if any(current.get(k) != value for k, value in previous.items() if k not in allowed):
                errors.append(f"inherited {key} changed beyond approved DOI correction: {ident}")
    old_w = {r["Warning_ID"]: r for r in load(V15, "data/warning_ledger.csv")}
    new_w = {r["Warning_ID"]: r for r in w}
    if not set(old_w).issubset(new_w):
        errors.append("inherited V15 warning disappeared")
    for ident, previous in old_w.items():
        if any(new_w[ident].get(k) != v for k, v in previous.items()):
            errors.append(f"inherited warning history changed: {ident}")
    metadata = json.loads((ROOT / "release_metadata.json").read_text(encoding="utf-8"))
    counts = {"expected_compounds": len({r["Compound_ID"] for r in c}), "expected_evidence": len({r["Evidence_ID"] for r in e}), "drug_probe_rows": len(p), "bibliography_rows": len(b), "study_rows": len(s), "warning_count": len(w)}
    for key, actual in counts.items():
        if metadata.get(key) != actual:
            errors.append(f"metadata count mismatch: {key}")
    return errors


if __name__ == "__main__":
    found = validate()
    print(json.dumps({"status": "PASS" if not found else "FAIL", "errors": found}, indent=2))
    raise SystemExit(bool(found))
