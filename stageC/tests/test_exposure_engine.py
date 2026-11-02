import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from stage_c.exposure_engine import calculate_exposure, aggregate_exposures
from stage_c.validation import validate_exposure_output

COMPOUNDS={"C-1":{"Compound_ID":"C-1","Canonical_Name":"Test compound"}}
FOOD={"F-1":{"food_record_id":"F-1","reported_concentration":"5","reported_unit":"mg/kg","normalized_concentration":"5","normalized_unit":"mg/kg","raw_or_processed_state":"raw","food_use_classification":"ordinary food","moisture_basis":"wet weight","source_verification_status":"Verified","source_classification":"Primary analytical measurement","source_title":"Synthetic fixture","source_url":"https://example.invalid/source"}}
MAP=[{"mapping_id":"MAP-1","food_record_id":"F-1","compound_id":"C-1","mapping_status":"Exact identity match","rationale":"synthetic direct match"}]
def item(**kw):
 row={"estimate_id":"E-1","compound_id":"C-1","food_record_id":"F-1","ingredient_quantity":"0.2","ingredient_unit":"kg","serving_mass":"0.2","serving_unit":"kg","consumed_fraction":"1","period_id":"meal-1"};row.update(kw);return row

class ExposureEngineTests(unittest.TestCase):
    def test_independent_formula_concentration_times_mass(self):
        r=calculate_exposure(item(),FOOD,MAP,COMPOUNDS,timestamp="2026-01-01T00:00:00Z")
        self.assertEqual(r["initial_compound_amount"],"1.0")
        self.assertEqual(r["compound_per_serving"],"1.0")
        self.assertEqual(r["estimated_consumed_amount"],"1.0")
        self.assertEqual(r["calculation_status"],"Complete");self.assertEqual(validate_exposure_output(r),[])

    def test_consumed_fraction_is_applied(self):
        r=calculate_exposure(item(consumed_fraction="0.25"),FOOD,MAP,COMPOUNDS)
        self.assertEqual(r["estimated_consumed_amount"],"0.250")

    def test_deterministic_estimate_id_excludes_timestamp(self):
        a=calculate_exposure(item(estimate_id=""),FOOD,MAP,COMPOUNDS,timestamp="one")
        b=calculate_exposure(item(estimate_id=""),FOOD,MAP,COMPOUNDS,timestamp="two")
        self.assertEqual(a["estimate_id"],b["estimate_id"]);self.assertNotEqual(a["calculation_timestamp"],b["calculation_timestamp"])

    def test_fraction_out_of_range_is_invalid(self):
        r=calculate_exposure(item(consumed_fraction="1.01"),FOOD,MAP,COMPOUNDS)
        self.assertEqual(r["calculation_status"],"Invalid input");self.assertEqual(r["estimated_consumed_amount"],"")

    def test_missing_concentration_yields_no_numeric_result(self):
        blank={"F-1":{**FOOD["F-1"],"normalized_concentration":"","reported_concentration":""}}
        r=calculate_exposure(item(),blank,MAP,COMPOUNDS)
        self.assertEqual(r["calculation_status"],"Incomplete: missing concentration");self.assertEqual(r["estimated_consumed_amount"],"")

    def test_unverified_concentration_withheld(self):
        unverified={"F-1":{**FOOD["F-1"],"source_verification_status":"unverified"}}
        r=calculate_exposure(item(),unverified,MAP,COMPOUNDS)
        self.assertEqual(r["calculation_status"],"Unverified input");self.assertEqual(r["estimated_consumed_amount"],"")

    def test_supplement_concentration_is_not_ordinary_food_exposure(self):
        supplement={"F-1":{**FOOD["F-1"],"food_use_classification":"supplement"}}
        r=calculate_exposure(item(),supplement,MAP,COMPOUNDS)
        self.assertEqual(r["calculation_status"],"Unverified input");self.assertEqual(r["estimated_consumed_amount"],"")

    def test_verified_food_ingredient_is_eligible_without_processing_adjustment(self):
        ingredient={"F-1":{**FOOD["F-1"],"food_use_classification":"food ingredient","raw_or_processed_state":"dried"}}
        r=calculate_exposure(item(),ingredient,MAP,COMPOUNDS)
        self.assertEqual(r["calculation_status"],"Complete")
        self.assertEqual(r["estimated_consumed_amount"],"1.0")

    def test_prepared_beverage_uses_reported_food_mass_basis(self):
        beverage={"F-1":{**FOOD["F-1"],"food_use_classification":"prepared beverage","raw_or_processed_state":"processed","moisture_basis":"as-consumed beverage; USDA reports per 100g (100ml)"}}
        r=calculate_exposure(item(),beverage,MAP,COMPOUNDS)
        self.assertEqual(r["calculation_status"],"Complete")
        self.assertEqual(r["estimated_consumed_amount"],"1.0")

    def test_pending_stage_b_identity_is_withheld(self):
        pending={"C-1":{**COMPOUNDS["C-1"],"StageC_Identity_Verification_Status":"Source transcription; independent chemical parser/adjudication pending"}}
        r=calculate_exposure(item(),FOOD,MAP,pending)
        self.assertEqual(r["calculation_status"],"Incomplete: unresolved identity")

    def test_inherited_warning_ids_reach_estimate(self):
        warned={"C-1":{**COMPOUNDS["C-1"],"StageC_Warning_Identifiers":["V3-W01"]}}
        r=calculate_exposure(item(),FOOD,MAP,warned)
        self.assertEqual(r["warning_identifiers"],["V3-W01"])

    def test_multi_ingredient_aggregation_and_duplicate_guard(self):
        a=calculate_exposure(item(estimate_id="E1"),FOOD,MAP,COMPOUNDS)
        b=calculate_exposure(item(estimate_id="E2",ingredient_quantity="0.1",serving_mass="0.1"),FOOD,MAP,COMPOUNDS)
        self.assertEqual(aggregate_exposures([a,b])[0]["estimated_consumed_amount"],"1.5")
        with self.assertRaises(ValueError):aggregate_exposures([a,a])

    def test_phase1_never_applies_retention(self):
        r=calculate_exposure(item(),FOOD,MAP,COMPOUNDS)
        self.assertIn("excluded",r["warnings"][0].lower());self.assertNotIn("retention",r["calculation_method"].lower())

if __name__ == "__main__": unittest.main()
