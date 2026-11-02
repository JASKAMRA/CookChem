import csv
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from stage_c.exceptions import ValidationError
from stage_c.food_composition import FIELDS, normalize_record, validate_food_record, ingest_food_data

class FoodCompositionTests(unittest.TestCase):
    def record(self, **changes):
        row={k:"" for k in FIELDS}; row.update({"food_record_id":"FC-1","food_name":"Test food","compound_name":"Test compound","food_use_classification":"ordinary food","source_classification":"Primary analytical measurement","source_verification_status":"Verified","source_title":"Synthetic test fixture","reported_concentration":"5","reported_unit":"mg/kg","raw_or_processed_state":"raw","moisture_basis":"wet weight"}); row.update(changes); return row

    def setUp(self):
        self.temp_root=Path(__file__).resolve().parents[1]/"reports"/"testing";self.temp_root.mkdir(parents=True,exist_ok=True)

    def test_normalizes_without_overwriting_source_value(self):
        row=normalize_record(self.record(reported_unit="mg/100 g"))
        self.assertEqual(row["reported_concentration"],"5");self.assertEqual(row["reported_unit"],"mg/100 g")
        self.assertEqual(row["normalized_concentration"],"50");self.assertEqual(row["normalized_unit"],"mg/kg")

    def test_missing_is_preserved_not_zero(self):
        row=normalize_record(self.record(reported_concentration="",reported_unit=""))
        self.assertEqual(row["normalized_concentration"],"");self.assertEqual(row["reported_concentration"],"")

    def test_rejects_unverified_record_masquerading_as_verified(self):
        row=self.record(source_verification_status="unverified")
        self.assertTrue(any("explicit verified status" in x for x in validate_food_record(row)))

    def test_backward_compatible_food_ingredient_classification(self):
        self.assertEqual(validate_food_record(self.record(food_use_classification="food ingredient")),[])

    def test_prepared_beverage_classification(self):
        self.assertEqual(validate_food_record(self.record(food_use_classification="prepared beverage")),[])

    def test_ingestion_manifest_checksums_and_count(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as td:
            source=Path(td)/"in.csv"; output=Path(td)/"out.csv"; manifest=Path(td)/"manifest.json"
            with source.open("w",newline="",encoding="utf-8") as f:
                w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerow(self.record())
            result=ingest_food_data(source,output,manifest)
            self.assertEqual(result["record_count"],1);self.assertTrue(result["source_sha256"]);self.assertTrue(manifest.exists())

    def test_rejects_duplicate_ids(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as td:
            source=Path(td)/"in.csv"
            with source.open("w",newline="",encoding="utf-8") as f:
                w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerow(self.record());w.writerow(self.record())
            with self.assertRaises(ValidationError):ingest_food_data(source,Path(td)/"out.csv",Path(td)/"m.json")

if __name__ == "__main__": unittest.main()
