#!/usr/bin/env python3
"""Build the exact SHA-256 manifest for Phase1-v1.3.0."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
EXCLUDED={"CHECKSUMS.json","CHECKSUMS.sha256"}
artifacts=[]
for path in sorted(ROOT.rglob("*")):
    if path.is_symlink(): raise SystemExit(f"symlink not permitted: {path}")
    if not path.is_file() or path.name in EXCLUDED or "__pycache__" in path.parts or path.suffix==".pyc": continue
    rel=path.relative_to(ROOT).as_posix()
    raw=path.read_bytes()
    artifacts.append({"path":rel,"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)})
manifest={"release_id":"Phase1-v1.3.0","algorithm":"SHA-256","excluded_files":sorted(EXCLUDED),"artifact_count":len(artifacts),"artifacts":artifacts}
payload=(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n").encode("utf-8")
(ROOT/"CHECKSUMS.json").write_bytes(payload)
digest=hashlib.sha256(payload).hexdigest()
(ROOT/"CHECKSUMS.sha256").write_text(f"{digest}  CHECKSUMS.json\n",encoding="utf-8")
print(f"{len(artifacts)} artifacts; CHECKSUMS.json sha256={digest}")
