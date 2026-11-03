import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stage_c.cli import STAGE, _portable_artifact_path, build_parser

class CliTests(unittest.TestCase):
    def test_documented_commands_parse(self):
        for argv in (["inspect"],["import-stage-b"],["ingest-food","input.csv"],["map"],["exposure","input.json"],["validate"]):
            with self.subTest(command=argv[0]):self.assertEqual(build_parser().parse_args(argv).command,argv[0])

    def test_validation_artifact_path_is_portable(self):
        self.assertEqual(_portable_artifact_path(STAGE/"data"/"compound_food_mapping.csv"),"data/compound_food_mapping.csv")
        self.assertEqual(_portable_artifact_path(Path("/tmp/rebuilt_mapping.csv")),"rebuilt_mapping.csv")

    def test_json_schema_documents_parse_and_declare_draft(self):
        schemas=sorted((STAGE/"schemas").glob("*.json"))
        self.assertGreaterEqual(len(schemas),8)
        for path in schemas:
            with self.subTest(schema=path.name):
                schema=json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(schema.get("$schema"),"https://json-schema.org/draft/2020-12/schema")
                self.assertIn(schema.get("type"),{"object","array"})

    def test_mapping_rebuild_defaults_outside_preserved_phase1b_file(self):
        args=build_parser().parse_args(["map"])
        self.assertNotEqual(args.output,STAGE/"data"/"compound_food_mapping"/"compound_food_mapping.csv")

if __name__=="__main__":unittest.main()
