import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stage_c.provenance import calculation_provenance, deterministic_id

class ProvenanceTests(unittest.TestCase):
    def test_deterministic_id_and_input_sensitivity(self):
        self.assertEqual(deterministic_id("EST",{"b":2,"a":1}),deterministic_id("EST",{"a":1,"b":2}))
        self.assertNotEqual(deterministic_id("EST",{"a":1}),deterministic_id("EST",{"a":2}))

    def test_provenance_reconstructs_inputs_and_source(self):
        row={"estimate_id":"EST-1","compound_id":"C-1","food_record_id":"F-1","source_concentration":"5","source_unit":"mg/kg","normalized_concentration":"5","normalized_unit":"mg/kg","ingredient_quantity":"0.2","ingredient_unit":"kg","consumed_fraction":"0.5","calculation_method":"formula","input_source_ids":["F-1","MAP-1"],"software_version":"1.0.0"}
        p=calculation_provenance(row,"StageB_FINALIZED","abc123")
        self.assertEqual(p["stage_b_manifest_sha256"],"abc123");self.assertEqual(p["formula"],"formula");self.assertEqual(p["input_source_ids"],["F-1","MAP-1"])

if __name__=="__main__":unittest.main()
