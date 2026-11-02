import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stage_c.cli import build_parser

class CliTests(unittest.TestCase):
    def test_documented_commands_parse(self):
        for argv in (["inspect"],["import-stage-b"],["ingest-food","input.csv"],["map"],["exposure","input.json"],["validate"]):
            with self.subTest(command=argv[0]):self.assertEqual(build_parser().parse_args(argv).command,argv[0])

if __name__=="__main__":unittest.main()
