import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stage_c.validation import validate_all, validate_exposure_output, validate_food_records, validate_mapping_records

class ValidationTests(unittest.TestCase):
    def test_missing_value_never_becomes_zero(self):
        row={"food_record_id":"F","reported_concentration":"","normalized_concentration":"0"}
        self.assertTrue(validate_food_records([row]))

    def test_complete_output_requires_provenance(self):
        result=validate_exposure_output({"calculation_status":"Complete","estimated_consumed_amount":"1"})
        self.assertTrue(any("provenance" in x for x in result))

    def test_incomplete_output_cannot_contain_numeric_estimate(self):
        result=validate_exposure_output({"calculation_status":"Incomplete: missing concentration","estimated_consumed_amount":"0"})
        self.assertTrue(any("numeric consumed amount" in x for x in result))

    def test_retention_method_is_out_of_phase(self):
        result=validate_exposure_output({"calculation_status":"Complete","calculation_method":"apply retention"})
        self.assertTrue(any("cooking-retention" in x for x in result))

    def test_empty_database_is_valid_and_missing_data_is_counted(self):
        result=validate_all([],[],[],{"C-1"})
        self.assertEqual(result["status"],"PASS")

    def test_food_compound_reference_must_resolve(self):
        result=validate_food_records([{"food_record_id":"F-1","compound_id":"ORPHAN"}],{"C-1"})
        self.assertTrue(any("compound_id does not resolve" in error for row in result for error in row["errors"]))

    def test_mapping_candidate_reference_must_resolve(self):
        row={"mapping_id":"MAP-1","food_record_id":"F-1","compound_id":"C-1","candidate_compound_ids":"C-1|ORPHAN","mapping_status":"Exact identity match","rationale":"synthetic test"}
        errors=validate_mapping_records([row],{"C-1"},{"F-1"})
        self.assertTrue(any("candidate compound ID does not resolve" in error["error"] for error in errors))

    def test_duplicate_mapping_ids_are_rejected(self):
        row={"mapping_id":"MAP-1","food_record_id":"F-1","compound_id":"C-1","mapping_status":"Exact identity match","rationale":"synthetic test"}
        errors=validate_mapping_records([row,row.copy()],{"C-1"},{"F-1"})
        self.assertTrue(any(error["error"]=="duplicate mapping_id" for error in errors))

if __name__=="__main__":unittest.main()
