"""Guard the Stage A Python 3.12 runtime dependency lock against drift."""
from __future__ import annotations

import importlib.metadata
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE_A = ROOT / "stageA"
DIRECT_REQUIREMENTS = STAGE_A / "stageA_requirements.txt"
RUNTIME_LOCK = STAGE_A / "stageA-requirements-py312.lock"

# These are the distributions recorded by the run manifest as affecting the
# benchmark implementation. Packaging tools themselves are not model inputs.
MANIFEST_DISTRIBUTIONS = {
    "numpy": "numpy",
    "pandas": "pandas",
    "scikit-learn": "scikit-learn",
    "xgboost": "xgboost",
    "scipy": "scipy",
    "joblib": "joblib",
    "cloudpickle": "cloudpickle",
    "narwhals": "narwhals",
    "python-dateutil": "python-dateutil",
    "threadpoolctl": "threadpoolctl",
    "tzdata": "tzdata",
}


def read_exact_pins(path: Path) -> dict[str, str]:
    pins: dict[str, str] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([A-Za-z0-9][A-Za-z0-9_.+-]*)", line)
        if not match:
            raise AssertionError(f"{path.name}:{line_number} is not an exact package pin: {line!r}")
        name, version = match.groups()
        normalized = re.sub(r"[-_.]+", "-", name).lower()
        if normalized in pins:
            raise AssertionError(f"{path.name}:{line_number} duplicates package {name!r}")
        pins[normalized] = version
    return pins


class StageADependencyLockContractTests(unittest.TestCase):
    def test_python_runtime_and_manifest_distributions_match_exact_lock(self) -> None:
        self.assertEqual(sys.version_info[:3], (3, 12, 14))

        locked = read_exact_pins(RUNTIME_LOCK)
        direct = read_exact_pins(DIRECT_REQUIREMENTS)
        for name, version in direct.items():
            with self.subTest(direct_package=name):
                self.assertEqual(locked.get(name), version)

        for distribution in MANIFEST_DISTRIBUTIONS.values():
            normalized = re.sub(r"[-_.]+", "-", distribution).lower()
            with self.subTest(runtime_distribution=distribution):
                self.assertIn(normalized, locked)
                self.assertEqual(importlib.metadata.version(distribution), locked[normalized])


if __name__ == "__main__":
    unittest.main()
