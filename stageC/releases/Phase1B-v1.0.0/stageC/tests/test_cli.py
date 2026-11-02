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

if __name__=="__main__":unittest.main()
