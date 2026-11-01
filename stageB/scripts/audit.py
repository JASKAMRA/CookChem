"""Verify authoritative release checksums and report core dataset counts."""
from pathlib import Path
import csv, hashlib, json
ROOT=Path(__file__).resolve().parents[1]; RELEASE=ROOT/"release"/"StageB_Final"
def main():
    manifest=json.loads((RELEASE/"manifests"/"SHA256SUMS.json").read_text(encoding="utf-8"))
    mismatches=[]
    for rel,expected in manifest.items():
        p=RELEASE/rel
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected: mismatches.append(rel)
    counts={}
    for rel,label in (("data/compound_registry.csv","anchors"),("data/interaction_evidence.csv","evidence_records"),("data/drug_probe_registry.csv","drug_probe_labels"),("data/warning_ledger.csv","warning_rows")):
        with (RELEASE/rel).open(encoding="utf-8-sig",newline="") as f: counts[label]=sum(1 for _ in csv.DictReader(f))
    result={"release":RELEASE.relative_to(ROOT.parent).as_posix(),"manifest_entries":len(manifest),"manifest_mismatches":mismatches,"status":"PASS" if not mismatches else "FAIL","counts":counts}
    (ROOT/"validation"/"release_audit.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2)); return 1 if mismatches else 0
if __name__=="__main__": raise SystemExit(main())
