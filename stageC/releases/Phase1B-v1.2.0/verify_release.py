#!/usr/bin/env python3
"""Verify every file listed in the Phase 1B SHA-256 package manifest."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
manifest_path = ROOT / "CHECKSUMS.json"
digest_path = ROOT / "CHECKSUMS.sha256"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
expected_digest = digest_path.read_text(encoding="utf-8").split()[0]
errors = []
if digest != expected_digest:
    errors.append("CHECKSUMS.json digest does not match CHECKSUMS.sha256")
for item in manifest["artifacts"]:
    path = ROOT / item["path"]
    if not path.is_file():
        errors.append(f"missing: {item['path']}")
        continue
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    if h != item["sha256"]:
        errors.append(f"hash mismatch: {item['path']}")
    if path.stat().st_size != item["bytes"]:
        errors.append(f"size mismatch: {item['path']}")
if errors:
    print(json.dumps({"status":"FAIL","artifact_count":len(manifest["artifacts"]),"errors":errors},indent=2))
    sys.exit(1)
print(json.dumps({"status":"PASS","release_id":manifest["release_id"],"artifact_count":len(manifest["artifacts"]),"manifest_sha256":digest},indent=2))
