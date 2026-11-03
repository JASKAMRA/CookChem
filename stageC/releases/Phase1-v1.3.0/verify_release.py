#!/usr/bin/env python3
"""Verify exact package contents and SHA-256 values for Phase1-v1.3.0."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parent
manifest_path=ROOT/"CHECKSUMS.json"
digest_path=ROOT/"CHECKSUMS.sha256"
try:
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    actual_digest=hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    expected_digest=digest_path.read_text(encoding="utf-8").split()[0]
except Exception as exc:
    print(json.dumps({"status":"FAIL","error":str(exc)}));sys.exit(1)
errors=[]
if manifest.get("release_id")!="Phase1-v1.3.0": errors.append("wrong release_id")
if actual_digest!=expected_digest: errors.append("CHECKSUMS.json detached digest mismatch")
expected={}
for item in manifest.get("artifacts",[]):
    name=item.get("path","")
    rel=PurePosixPath(name)
    if not name or rel.is_absolute() or any(part in {"",".",".."} for part in rel.parts) or name!=rel.as_posix():
        errors.append(f"unsafe path: {name!r}");continue
    if name in expected: errors.append(f"duplicate path: {name}")
    expected[name]=item
actual=set()
for path in ROOT.rglob("*"):
    if path.is_symlink(): errors.append(f"symlink not permitted: {path.relative_to(ROOT)}");continue
    if path.is_file():
        rel=path.relative_to(ROOT).as_posix()
        if rel not in {"CHECKSUMS.json","CHECKSUMS.sha256"} and "__pycache__" not in path.parts and path.suffix!=".pyc": actual.add(rel)
if actual!=set(expected):
    errors.extend(f"missing: {x}" for x in sorted(set(expected)-actual))
    errors.extend(f"unexpected: {x}" for x in sorted(actual-set(expected)))
for name,item in expected.items():
    path=ROOT/name
    if not path.is_file(): continue
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=item.get("sha256"): errors.append(f"hash mismatch: {name}")
    if len(raw)!=item.get("bytes"): errors.append(f"size mismatch: {name}")
if errors:
    print(json.dumps({"status":"FAIL","artifact_count":len(expected),"errors":errors},indent=2));sys.exit(1)
print(json.dumps({"status":"PASS","release_id":manifest["release_id"],"artifact_count":len(expected),"manifest_sha256":actual_digest},indent=2))
