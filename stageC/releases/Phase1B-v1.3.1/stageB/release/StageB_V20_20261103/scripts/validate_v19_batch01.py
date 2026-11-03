from __future__ import annotations
import csv,json,sys
from pathlib import Path
REVIEWED={'SB-0012':'24398010','SB-0037':'28533679','SB-0067':'24369535'}
def read(root,rel):
 with (root/rel).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def validate_records(root,evidence,audits,warnings,warning_audit):
 root=Path(root);errors=[]
 eid=[r.get('Evidence_ID','') for r in evidence];aid=[r.get('Evidence_ID','') for r in audits]
 if len(eid)!=len(set(eid)):errors.append('duplicate evidence IDs')
 if len(aid)!=len(set(aid)):errors.append('duplicate source-audit Evidence_IDs')
 if set(eid)!=set(aid):errors.append('source-audit Evidence_IDs do not exactly match evidence IDs')
 eb={r['Evidence_ID']:r for r in evidence};ab={r['Evidence_ID']:r for r in audits}
 for rec,pmid in REVIEWED.items():
  a=ab.get(rec,{})
  if a.get('PMID')!=pmid:errors.append(f'{rec}: primary source PMID mismatch')
  if a.get('Verification_Level')!='1':errors.append(f'{rec}: verified full text must use tier 1')
  if 'V19_TIER_1_FULL_TEXT_REVIEWED' not in a.get('Audit_Disposition',''):errors.append(f'{rec}: review disposition missing')
  source=a.get('Source_Cache','')
  if not source or not (root/'provenance'/source).is_file():errors.append(f'{rec}: reviewed source file unavailable')
  else:
   content=(root/'provenance'/source).read_text(encoding='utf-8',errors='replace')
   if pmid not in content:errors.append(f'{rec}: source file does not contain the asserted PMID')
   if a.get('DOI','') and a['DOI'].lower() not in content.lower():errors.append(f'{rec}: source file does not contain the asserted DOI')
  if not a.get('Verification_Date') or not a.get('Source_Locator') or not a.get('Numerical_Outcome_Verified'):errors.append(f'{rec}: incomplete record-level review trail')
 p=eb.get('SB-0012',{})
 if '20 total healthy volunteers' not in p.get('Population','') or 'n=20 per group' not in p.get('Population',''):errors.append('SB-0012: total sample and group-size inconsistency must both be represented')
 if 'unit not stated in source' not in p.get('Quantitative_Outcome',''):errors.append('SB-0012: unreported AUC unit must not be inferred')
 if '411.1 ± 235.4' not in p.get('Quantitative_Outcome','') or '495, 9 ± 273' not in p.get('Quantitative_Outcome',''):errors.append('SB-0012: source-reported AUC values missing')
 if 'clearance' not in p.get('Limitations','').lower() or 'three post-dose concentrations' not in p.get('Limitations',''):errors.append('SB-0012: clearance/model limitations missing')
 g=eb.get('SB-0037',{}).get('Quantitative_Outcome','')
 if '0.81 (90% CI 0.67-0.97)' not in g or '0.85 (0.70-1.04' not in g:errors.append('SB-0037: Table 2 GMR/CI values missing')
 ap=eb.get('SB-0067',{})
 if ap.get('Evidence_Type')!='Animal' or '90.988 +/- 11.585' not in ap.get('Quantitative_Outcome',''):errors.append('SB-0067: animal scope or Table 1 value mismatch')
 expected_source_values={'SB-0012':['411.1','495, 9','188','33.62'],'SB-0037':['0.81','0.85','0.89'],'SB-0067':['90.988','127.514','10.1155/2013/789184']}
 for rec,terms in expected_source_values.items():
  a=ab.get(rec,{})
  f=root/'provenance'/a.get('Source_Cache','')
  if f.is_file():
   content=f.read_text(encoding='utf-8',errors='replace')
   for term in terms:
    if term not in content:errors.append(f'{rec}: asserted source text lacks {term}')
 wids=[r.get('Warning_ID','') for r in warnings];waids=[r.get('Warning_ID','') for r in warning_audit]
 if len(wids)<80 or len(wids)!=len(set(wids)):errors.append('warning ledger must preserve 70 inherited IDs plus V19-W01 through V19-W10')
 if not {f'V19-W{i:02d}' for i in range(1,11)} <= set(wids):errors.append('one or more documented V19 source warnings are missing')
 if len(waids)!=len(set(waids)) or set(wids)!=set(waids):errors.append('V19 warning audit IDs must match ledger exactly')
 wb={r['Warning_ID']:r for r in warnings};wab={r['Warning_ID']:r for r in warning_audit}
 for wid,row in wb.items():
  if row.get('Audit_Status')!=wab[wid].get('V19_Status'):errors.append(f'{wid}: V19 audit and ledger statuses differ')
 return sorted(set(errors))
def validate(root):
 root=Path(root);return validate_records(root,read(root,'data/interaction_evidence.csv'),read(root,'provenance/source_audit.csv'),read(root,'data/warning_ledger.csv'),read(root,'validation/V19_warning_audit.csv'))
if __name__=='__main__':
 root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.');errs=validate(root);m=json.loads((root/'release_metadata.json').read_text(encoding='utf-8-sig'))
 report={'release':m.get('release'),'status':'PASS' if not errs else 'FAIL','batch':'V19-001','reviewed_records':3,'errors':errs}
 (root/'validation/V19_integrity_results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2));raise SystemExit(bool(errs))
