from pathlib import Path
import hashlib,json,zipfile
O=Path(__file__).resolve().parent
def included(p):
 rel=p.relative_to(O).as_posix()
 return not rel.startswith('audit/rebuild_check/') and not rel.startswith('audit/page-') and '__pycache__' not in rel and p.name!='SHA256SUMS.json'
files=sorted(p for p in O.rglob('*') if p.is_file() and included(p))
manifest={p.relative_to(O).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(O/'SHA256SUMS.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
z=O.parent/(O.name+'.zip')
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as f:
 for p in files+[O/'SHA256SUMS.json']:f.write(p,O.name+'/'+p.relative_to(O).as_posix())
with zipfile.ZipFile(z) as f:assert f.testzip() is None;assert len(f.namelist())==len(files)+1
h=hashlib.sha256(z.read_bytes()).hexdigest();z.with_suffix('.zip.sha256').write_text(h+'  '+z.name+'\n',encoding='ascii')
print(json.dumps(dict(package=str(z),files=len(files)+1,bytes=z.stat().st_size,sha256=h),indent=2))
