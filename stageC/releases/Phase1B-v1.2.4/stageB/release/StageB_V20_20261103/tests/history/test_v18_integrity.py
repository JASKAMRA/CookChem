import unittest
from pathlib import Path
from scripts.validate_v18_integrity import check_records, validate
class V18IntegrityTests(unittest.TestCase):
 def setUp(self):
  self.e=[{'Evidence_ID':'E1'}]
  self.a=[{'Evidence_ID':'E1','Verification_Level':'5','Verification_Status':'Historical status pending','Audit_Disposition':'EXPLICIT_SOURCE_DISPOSITION_RECORDED; CURRENT_SOURCE_REVIEW_PENDING','Verification_Method':'not independently re-opened in V18'}]
  self.w=[{'Warning_ID':'W1','Audit_Status':'NEEDS_MANUAL_REVIEW','V17_Ledger_Audit_Status':'Unresolved'}]
  self.wa=[{'Warning_ID':'W1','V18_Audit_Status':'NEEDS_MANUAL_REVIEW','V17_Current_Finding':'Requires source review','Primary_or_Internal_References':'PMID:1'}]
 def test_accepts_complete_explicit_disposition(self): self.assertEqual(check_records(self.e,self.a,self.w,self.wa),[])
 def test_current_release_integrity(self): self.assertEqual(validate(Path(__file__).resolve().parents[1]),[])
 def test_rejects_missing_source_audit(self): self.assertTrue(any('match evidence IDs' in x for x in check_records(self.e,[],self.w,self.wa)))
 def test_rejects_duplicate_source_audit(self): self.assertTrue(any('must be unique' in x for x in check_records(self.e,self.a+self.a,self.w,self.wa)))
 def test_rejects_invalid_verification_level(self):
  a=[dict(self.a[0],Verification_Level='0')]; self.assertTrue(any('invalid verification level' in x for x in check_records(self.e,a,self.w,self.wa)))
 def test_rejects_pending_without_limitation(self):
  a=[dict(self.a[0],Verification_Method='reviewed')]; self.assertTrue(any('lacks review limitation' in x for x in check_records(self.e,a,self.w,self.wa)))
 def test_rejects_audit_warning_missing(self): self.assertTrue(any('exactly match' in x for x in check_records(self.e,self.a,self.w,[])))
 def test_rejects_silent_warning_status_mismatch(self):
  wa=[dict(self.wa[0],V18_Audit_Status='RESOLVED')]; self.assertTrue(any('differs from audit' in x for x in check_records(self.e,self.a,self.w,wa)))
 def test_rejects_unsupported_warning_status(self):
  w=[dict(self.w[0],Audit_Status='CLEARED')]; wa=[dict(self.wa[0],V18_Audit_Status='CLEARED')]; self.assertTrue(any('invalid warning status' in x for x in check_records(self.e,self.a,w,wa)))
 def test_rejects_resolved_without_support(self):
  w=[dict(self.w[0],Audit_Status='RESOLVED')]; wa=[dict(self.wa[0],V18_Audit_Status='RESOLVED',Primary_or_Internal_References='',V17_Current_Finding='')]; self.assertTrue(any('lacks evidence/rationale' in x for x in check_records(self.e,self.a,w,wa)))
if __name__=='__main__': unittest.main()
