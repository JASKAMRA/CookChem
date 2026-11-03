#!/usr/bin/env python3
"""Regenerate the deterministic SHA-256 manifest for this package."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXCLUDE = {"CHECKSUMS.json", "CHECKSUMS.sha256"}
artifacts = []
for path in sorted(p for p in ROOT.rglob("*") if p.is_file()):
    rel = path.relative_to(ROOT).as_posix()
    if rel in EXCLUDE or "__pycache__" in path.parts or path.suffix == ".pyc":
        continue
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    artifacts.append({"path":rel,"sha256":digest,"bytes":path.stat().st_size})
manifest = {"release_id":"Phase1B-v1.2.7","algorithm":"SHA-256","excluded_files":sorted(EXCLUDE),"artifact_count":len(artifacts),"artifacts":artifacts}
payload = (json.dumps(manifest,indent=2,ensure_ascii=False)+"\n").encode("utf-8")
(ROOT/"CHECKSUMS.json").write_bytes(payload)
digest = hashlib.sha256(payload).hexdigest()
(ROOT/"CHECKSUMS.sha256").write_text(f"{digest}  CHECKSUMS.json\n",encoding="utf-8")
print(f"{len(artifacts)} artifacts; CHECKSUMS.json sha256={digest}")
