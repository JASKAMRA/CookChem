#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/"manifests/SHA256SUMS.json"
items={}
for p in sorted(ROOT.rglob("*")):
    if not p.is_file() or p==out or "__pycache__" in p.parts or p.suffix==".pyc": continue
    items[p.relative_to(ROOT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
out.write_text(json.dumps(items,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(f"{len(items)} files in exact V20 manifest")
