import csv,unittest
from pathlib import Path
from scripts.validate_v19_batch01 import validate,validate_records
class V19Batch01Tests(unittest.TestCase):
 def setUp(self):
  self.root=Path(__file__).resolve().parents[1]
  def rows(p):
   with (self.root/p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
  self.e=rows('data/interaction_evidence.csv');self.a=rows('provenance/source_audit.csv');self.w=rows('data/warning_ledger.csv');self.wa=rows('validation/V19_warning_audit.csv')
 def test_actual_batch_and_release_pass(self):self.assertEqual(validate(self.root),[])
 def test_source_audit_coverage_missing_record_detected(self):self.assertTrue(any('exactly match' in x for x in validate_records(self.root,self.e,self.a[:-1],self.w,self.wa)))
 def test_duplicate_source_audit_detected(self):self.assertTrue(any('duplicate source-audit' in x for x in validate_records(self.root,self.e,self.a+[self.a[0]],self.w,self.wa)))
 def test_warning_disposition_drift_detected(self):
  wa=[dict(x) for x in self.wa];wa[0]['V19_Status']='RESOLVED' if wa[0]['V19_Status']!='RESOLVED' else 'STILL_VALID'
  self.assertTrue(any('statuses differ' in x for x in validate_records(self.root,self.e,self.a,self.w,wa)))
 def test_unsupported_tier_detected(self):
  a=[dict(x) for x in self.a];a[next(i for i,x in enumerate(a) if x['Evidence_ID']=='SB-0012')]['Verification_Level']='3'
  self.assertTrue(any('tier 1' in x for x in validate_records(self.root,self.e,a,self.w,self.wa)))
 def test_unreported_auc_unit_not_filled(self):
  e=[dict(x) for x in self.e];i=next(i for i,x in enumerate(e) if x['Evidence_ID']=='SB-0012');e[i]['Quantitative_Outcome']=e[i]['Quantitative_Outcome'].replace('(unit not stated in source)','ng·h/mL')
  self.assertTrue(any('unit must not be inferred' in x for x in validate_records(self.root,e,self.a,self.w,self.wa)))
 def test_wrong_but_existing_source_file_detected(self):
  a=[dict(x) for x in self.a];a[next(i for i,x in enumerate(a) if x['Evidence_ID']=='SB-0012')]['Source_Cache']='source_archive/c6b139ea17adea65810da9c0cebb5481e94d521933bb87b77140fc3297028944_PMC5431696.xml'
  self.assertTrue(any('does not contain the asserted PMID' in x for x in validate_records(self.root,self.e,a,self.w,self.wa)))
 def test_missing_source_file_detected(self):
  a=[dict(x) for x in self.a];a[next(i for i,x in enumerate(a) if x['Evidence_ID']=='SB-0067')]['Source_Cache']='missing.xml'
  self.assertTrue(any('source file unavailable' in x for x in validate_records(self.root,self.e,a,self.w,self.wa)))
if __name__=='__main__':unittest.main()
