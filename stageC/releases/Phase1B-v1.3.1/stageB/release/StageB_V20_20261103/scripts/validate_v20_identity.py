#!/usr/bin/env python3
import csv,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT.parent/"StageB_V19_20261103"
LEGACY=ROOT.parent/"StageB_Final"
def rows(p):
    with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
errors=[]
reg=rows(ROOT/"data/compound_registry.csv"); oldreg=rows(PARENT/"data/compound_registry.csv")
legacyreg=rows(LEGACY/"data/compound_registry.csv")
aud=rows(ROOT/"identity/identity_structure_audit.csv"); oldaud=rows(PARENT/"identity/identity_structure_audit.csv")
if len(reg)!=143 or len(aud)!=143: errors.append("registry/audit compound count mismatch")
if {r["Compound_ID"] for r in reg}!={r["Compound_ID"] for r in oldreg}: errors.append("compound ID set changed")
if {r["Compound_ID"] for r in aud}!={r["Compound_ID"] for r in oldaud}: errors.append("identity audit ID set changed")
complete={r["Compound_ID"] for r in aud if r["Status"]=="Complete"}
pending={r["Compound_ID"] for r in aud if r["Status"]!="Complete"}
if len(complete)!=130 or len(pending)!=13: errors.append(f"identity status counts wrong: {len(complete)} complete/{len(pending)} pending")
for rel in ["data/interaction_evidence.csv","data/warning_ledger.csv","data/drug_probe_registry.csv","data/study_registry.csv","data/publication_bibliography.csv","provenance/source_audit.csv"]:
    a=ROOT/rel;b=PARENT/rel
    if a.read_bytes()!=b.read_bytes(): errors.append("protected evidence changed: "+rel)
# Original StageB_Final 119 IDs and all V19 IDs remain present.
old119={r["Compound_ID"] for r in legacyreg}
if not old119.issubset({r["Compound_ID"] for r in reg}): errors.append("legacy IDs lost")
# Exact manifest check and inventory check.
manifest=json.loads((ROOT/"manifests/SHA256SUMS.json").read_text())
actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file() and p!=ROOT/"manifests/SHA256SUMS.json" and "__pycache__" not in p.parts and p.suffix!=".pyc"}
if actual!=set(manifest): errors.append(f"manifest inventory mismatch: extra={len(actual-set(manifest))} missing={len(set(manifest)-actual)}")
for rel,digest in manifest.items():
    p=ROOT/rel
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest: errors.append("manifest hash mismatch: "+rel)
if errors:
    print(json.dumps({"status":"FAIL","errors":errors},indent=2));sys.exit(1)
print(json.dumps({"status":"PASS","compound_count":len(reg),"identity_complete":len(complete),"identity_pending":len(pending),"manifest_files":len(manifest),"protected_evidence":"byte-identical"},indent=2))
