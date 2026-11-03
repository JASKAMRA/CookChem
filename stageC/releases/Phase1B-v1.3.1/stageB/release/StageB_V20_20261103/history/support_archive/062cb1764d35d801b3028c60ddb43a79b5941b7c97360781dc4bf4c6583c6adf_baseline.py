from pathlib import Path
import csv,json,hashlib,collections,sys,importlib.util,subprocess,shutil
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;V=O.parent/'release_v7_20261015_clean';R=O.parents[1]
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2),encoding='utf8')
mf=json.loads((V/'audit/release_manifest_sha256.json').read_text(encoding='utf8'));bad=[p for p,h in mf.items() if not (V/p).exists() or sha(V/p)!=h];assert not bad,bad
save(O/'audit/v7_manifest_verification.json',dict(files=len(mf),mismatches=bad))
e=read(V/'outputs/stageB_food_drug_interactions_v7.csv');r=read(V/'outputs/compound_registry.csv');reviews=read(V/'outputs/all_record_review_audit.csv');warn=read(V/'outputs/warning_resolution_ledger.csv')
s=dict(anchors=len(r),records=len(e),publications=len({x['PMID'] for x in e}),drugs=len({x['Drug'] for x in e}),numerical_records=sum(bool(x['Quantitative_Outcome']) for x in e),classes=dict(collections.Counter(x['Evidence_Type'] for x in e)),verification=dict(collections.Counter(x['Verification_Level'] for x in reviews)),open_warnings=sum(x['After'] in ['Unresolved','Partially resolved'] for x in warn),warning_codes=len({x['Code'] for x in warn if x['After'] in ['Unresolved','Partially resolved']}))
save(O/'audit/baseline_counts.json',s)
# Run original V7 validation read-only. Its rebuild executes in an isolated copy
# with the same directory basename, and is independently byte-compared to V7.
scratch=O/'audit/rebuild_check'/V.name
shutil.copytree(V,scratch,ignore=shutil.ignore_patterns('*.zip','previews','__pycache__'),dirs_exist_ok=True)
sys.path.insert(0,str(V));sp=importlib.util.spec_from_file_location('v7_validator',V/'validate.py');v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v);import build
def isolated():
 subprocess.run([sys.executable,'-B',str(scratch/'build.py')],check=True,stdout=subprocess.DEVNULL)
 matches={p.name:sha(p)==sha(scratch/'outputs'/p.name) for p in (V/'outputs').glob('*') if p.is_file()};assert all(matches.values()),matches
 save(O/'audit/baseline_isolated_rebuild.json',dict(passed=all(matches.values()),files=len(matches)))
build.main=isolated;original=Path.write_text
def redirected(p,*a,**kw):
 if p.parent==V/'audit' and p.name in ['validation_report.json','mutation_tests.json','rebuild_verification.json']:p=O/'audit'/('baseline_v7_'+p.name)
 return original(p,*a,**kw)
Path.write_text=redirected
try:v.main()
finally:Path.write_text=original
freeze={p.relative_to(R).as_posix():sha(p) for p in R.rglob('*') if p.is_file() and O not in p.parents and '.git' not in p.parts and '__pycache__' not in p.parts}
save(O/'audit/preservation_manifest.json',freeze);print(s);print('Frozen prior files',len(freeze))
