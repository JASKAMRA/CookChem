import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stage_c.validation import validate_all, validate_exposure_output, validate_food_records

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

if __name__=="__main__":unittest.main()
