from pathlib import Path
import sys,importlib.util,json,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;V=O.parent/'release_v5_20261014'
for d in ['audit','outputs','sources','reports']:(O/d).mkdir(exist_ok=True)
def module(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
v=module(V/'validate.py','baseline_v5')
e=v.read(V/'outputs/stageB_food_drug_interactions_v5.csv');r=v.read(V/'outputs/compound_registry.csv');cl=v.read(V/'outputs/claim_support_and_outcome_audit.csv')
# Execute the existing suite and mutations, redirecting only its report writes.
# All input reads remain on the immutable V5 tree; intercept Path.write_text
# only for the two known audit outputs.
original=Path.write_text
def redirected(p,*a,**kw):
 if p in [V/'audit/validation_report.json',V/'audit/mutation_tests.json']:
  p=O/'audit'/('baseline_v5_'+p.name)
 return original(p,*a,**kw)
Path.write_text=redirected
try:v.main()
finally:Path.write_text=original
manifest={str(p.relative_to(O.parents[1])).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in O.parents[1].rglob('*') if p.is_file() and O not in p.parents and '.git' not in p.parts and '__pycache__' not in p.parts}
original(O/'audit/preservation_manifest.json',json.dumps(manifest,indent=2),encoding='utf8')
summary={'anchors':len(r),'records':len(e),'drugs':len({x['Drug'] for x in e}),'publications':len({x['PMID'] for x in e}),'numerical_records':sum(bool(x['Quantitative_Outcome']) for x in e),'classes':{t:sum(x['Evidence_Type']==t for x in e) for t in sorted({x['Evidence_Type'] for x in e})},'inherited_v4':sum(x['Release_Origin']!='v5_20261014' for x in e),'added_v5':sum(x['Release_Origin']=='v5_20261014' for x in e)}
original(O/'audit/baseline_counts.json',json.dumps(summary,indent=2),encoding='utf8');print(summary)
