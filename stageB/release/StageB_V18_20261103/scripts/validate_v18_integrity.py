from __future__ import annotations
import csv, json, sys
from pathlib import Path
ALLOWED={'RESOLVED','PARTIALLY_RESOLVED','STILL_VALID','NEEDS_MANUAL_REVIEW','NOT_APPLICABLE'}
LEVELS={'1','2','3','4','5','6'}
def read(root, rel):
 with (root/rel).open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))
def check_records(evidence, source_audit, warnings, warning_audit):
 errors=[]
 eids=[r.get('Evidence_ID','').strip() for r in evidence]
 if not all(eids) or len(eids)!=len(set(eids)): errors.append('evidence IDs must be present and unique')
 a_ids=[r.get('Evidence_ID','').strip() for r in source_audit]
 if len(a_ids)!=len(set(a_ids)): errors.append('source-audit Evidence_IDs must be unique')
 if set(a_ids)!=set(eids): errors.append('source-audit IDs must match evidence IDs exactly')
 for row in source_audit:
  if row.get('Verification_Level','') not in LEVELS: errors.append(f"{row.get('Evidence_ID')}: invalid verification level")
  if not row.get('Verification_Status','').strip() or not row.get('Audit_Disposition','').strip(): errors.append(f"{row.get('Evidence_ID')}: missing explicit source disposition")
  if row.get('Audit_Disposition','').endswith('PENDING') and 'not re-opened' not in row.get('Verification_Method','').lower() and 'no source content' not in row.get('Verification_Method','').lower() and 'not independently' not in row.get('Verification_Method','').lower(): errors.append(f"{row.get('Evidence_ID')}: pending disposition lacks review limitation")
 warning_ids=[r.get('Warning_ID','').strip() for r in warnings]
 audit_ids=[r.get('Warning_ID','').strip() for r in warning_audit]
 if len(warning_ids)!=len(set(warning_ids)): errors.append('warning IDs must be unique')
 if len(audit_ids)!=len(set(audit_ids)) or set(warning_ids)!=set(audit_ids): errors.append('warning audit IDs must exactly match warning ledger IDs')
 wa={r.get('Warning_ID'):r for r in warning_audit}
 for warning in warnings:
  wid=warning.get('Warning_ID',''); status=warning.get('Audit_Status','')
  if status not in ALLOWED: errors.append(f'{wid}: invalid warning status')
  if not warning.get('V17_Ledger_Audit_Status','').strip(): errors.append(f'{wid}: original V17 ledger disposition missing')
  if status!=wa.get(wid,{}).get('V18_Audit_Status',''): errors.append(f'{wid}: ledger status differs from audit disposition')
  if status=='RESOLVED':
   audit=wa.get(wid,{})
   if not audit.get('Primary_or_Internal_References','').strip() or not audit.get('V17_Current_Finding','').strip(): errors.append(f'{wid}: resolved warning lacks evidence/rationale')
 return sorted(set(errors))
def validate(root:Path):
 root=Path(root)
 return check_records(read(root,'data/interaction_evidence.csv'),read(root,'provenance/source_audit.csv'),read(root,'data/warning_ledger.csv'),read(root,'validation/V18_warning_by_warning_audit.csv'))
if __name__=='__main__':
 root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
 errors=validate(root)
 meta=json.loads((root/'release_metadata.json').read_text(encoding='utf-8-sig'))
 report={'release':meta.get('release',root.resolve().name),'status':'PASS' if not errors else 'FAIL','errors':errors}
 (root/'validation/V18_integrity_report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report,indent=2))
 raise SystemExit(bool(errors))
