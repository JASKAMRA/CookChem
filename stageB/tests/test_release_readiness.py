"""Read-only regression checks for the authoritative Stage B release.

The tests use the actual frozen release for structural checks. Any deliberately
invalid rows are synthetic fixtures created in a temporary directory.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import tempfile
import types
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "stageB" / "release" / "StageB_Final"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
VALIDATOR_PATH = ROOT / "stageB" / "archive" / "scripts" / "validate_final.py"
MANIFEST_INTEGRITY_PATH = RELEASE / "scripts" / "manifest_integrity.py"


def read_csv(relative_path: str) -> tuple[list[str], list[dict[str, str]]]:
    with (RELEASE / relative_path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_validator():
    spec = importlib.util.spec_from_file_location("stageb_release_validator", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the archived Stage B validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_manifest_integrity():
    # Execute the trusted verifier in memory so checking a frozen release cannot
    # create __pycache__ inside the tree being enumerated by the test.
    module = types.ModuleType("stageb_manifest_integrity")
    module.__file__ = str(MANIFEST_INTEGRITY_PATH)
    module.__package__ = ""
    source = MANIFEST_INTEGRITY_PATH.read_bytes()
    exec(compile(source, str(MANIFEST_INTEGRITY_PATH), "exec"), module.__dict__)
    return module


class ReleaseReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.compound_header, cls.compounds = read_csv("data/compound_registry.csv")
        cls.identity_header, cls.identity = read_csv("identity/identity_structure_audit.csv")
        cls.evidence_header, cls.evidence = read_csv("data/interaction_evidence.csv")
        cls.drug_header, cls.drugs = read_csv("data/drug_probe_registry.csv")
        cls.study_header, cls.studies = read_csv("data/study_registry.csv")
        cls.publication_header, cls.publications = read_csv("data/publication_bibliography.csv")
        cls.warning_header, cls.warning_ledger = read_csv("data/warning_ledger.csv")
        cls.source_header, cls.sources = read_csv("provenance/source_audit.csv")
        cls.claim_header, cls.claims = read_csv("provenance/claim_support_and_verification.csv")

    def test_critical_release_outputs_exist(self) -> None:
        required = [
            "manifests/SHA256SUMS.json",
            "README.md",
            "documentation/FINAL_HANDOFF.md",
            "documentation/data_dictionary.md",
            "data/compound_registry.csv",
            "data/interaction_evidence.csv",
            "data/publication_bibliography.csv",
            "data/warning_ledger.csv",
            "identity/identity_structure_audit.csv",
            "provenance/source_audit.csv",
            "provenance/claim_support_and_verification.csv",
            "provenance/food_context_audit.csv",
        ]
        self.assertTrue(all((RELEASE / path).is_file() for path in required))

    def test_compound_registry_has_unique_stable_ids(self) -> None:
        ids = [row["Compound_ID"].strip() for row in self.compounds]
        self.assertTrue(all(ids))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(row["Canonical_Name"].strip() for row in self.compounds))

    def test_identity_audit_preserves_registry_ids_and_core_fields(self) -> None:
        registry = {row["Compound_ID"]: row for row in self.compounds}
        identity = {row["Compound_ID"]: row for row in self.identity}
        self.assertEqual(set(registry), set(identity))
        for compound_id, compound in registry.items():
            audit = identity[compound_id]
            for field in ("Canonical_Name", "PubChem_CID", "SMILES", "InChI"):
                self.assertEqual(audit[field], compound[field], (compound_id, field))
            self.assertEqual(audit["Registry_InChIKey"], compound["InChIKey"], compound_id)

    def test_registry_and_evidence_csv_schemas_have_required_fields(self) -> None:
        self.assertTrue({"Compound_ID", "Canonical_Name", "Aliases", "PubChem_CID", "SMILES", "InChI", "InChIKey", "Identity_Status"}.issubset(self.compound_header))
        self.assertTrue({"Evidence_ID", "Compound_ID", "Study_ID", "PMID", "DOI", "Evidence_Type", "Quantitative_Outcome", "Source_URL", "Source_Locator"}.issubset(self.evidence_header))
        self.assertTrue({"PMID", "Title", "DOI"}.issubset(self.publication_header))

    def test_evidence_ids_and_foreign_keys_resolve(self) -> None:
        evidence_ids = [row["Evidence_ID"].strip() for row in self.evidence]
        compound_ids = {row["Compound_ID"] for row in self.compounds}
        drug_labels = {row["Drug_Probe"] for row in self.drugs}
        study_ids = {row["Study_ID"] for row in self.studies}
        self.assertTrue(all(evidence_ids))
        self.assertEqual(len(evidence_ids), len(set(evidence_ids)))
        self.assertTrue(all(row["Compound_ID"] in compound_ids for row in self.evidence))
        self.assertTrue(all(row["Drug"] in drug_labels for row in self.evidence))
        self.assertTrue(all(row["Study_ID"] in study_ids for row in self.evidence))

    def test_bibliography_integrity(self) -> None:
        pmids = [row["PMID"].strip() for row in self.publications if row["PMID"].strip()]
        self.assertEqual(len(pmids), len(set(pmids)))
        publications = set(pmids)
        self.assertTrue(all(not row["PMID"].strip() or row["PMID"].strip() in publications for row in self.evidence))

    def test_warning_ledger_is_preserved_and_well_formed(self) -> None:
        ids = [row["Warning_ID"].strip() for row in self.warning_ledger]
        self.assertTrue(all(ids))
        self.assertEqual(len(ids), len(set(ids)))
        allowed = {"Unresolved", "Partially resolved", "Resolved", "Not applicable"}
        self.assertTrue(all(row["After"] in allowed for row in self.warning_ledger))
        self.assertTrue({"Warning_ID", "Code", "Description", "Affected", "Classification", "After", "Remaining_Limitations"}.issubset(self.warning_header))

    def test_claim_support_exists_and_source_audit_links_are_valid(self) -> None:
        evidence_ids = {row["Evidence_ID"] for row in self.evidence}
        claim_ids = {row["Evidence_ID"] for row in self.claims}
        source_ids = {row["Evidence_ID"] for row in self.sources}
        self.assertEqual(evidence_ids, claim_ids)
        self.assertTrue(source_ids.issubset(evidence_ids))
        self.assertTrue({"Evidence_ID", "PMID", "Source_URL", "Source_Locator", "Verification_Status"}.issubset(self.source_header))

    def test_missing_values_remain_distinct_from_explicit_zero_synthetic_fixture(self) -> None:
        fixture = FIXTURES / "synthetic_missing_values.csv"
        with fixture.open(encoding="utf-8-sig", newline="") as handle:
            rows = {row["record_id"]: row for row in csv.DictReader(handle)}
        self.assertEqual(rows["synthetic_missing"]["value"], "")
        self.assertEqual(rows["synthetic_zero"]["value"], "0")
        self.assertIn("Synthetic only", rows["synthetic_missing"]["fixture_note"])

    def test_duplicate_detection_flags_synthetic_duplicate_id(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            release = Path(temp)
            tables = {
                "data/compound_registry.csv": ("Compound_ID,Canonical_Name,Food_Context,Selection_Rationale,Origin\nC-SYN,Test,food,test,legacy\nC-SYN,Test duplicate,food,test,legacy\n"),
                "data/interaction_evidence.csv": "Evidence_ID,Compound_ID,Drug,Study_ID,PMID,DOI,Evidence_Type,Source_URL,Source_Locator,Quantitative_Outcome\n",
                "data/drug_probe_registry.csv": "Drug_Probe\n",
                "data/study_registry.csv": "Study_ID,PMID\n",
                "data/publication_bibliography.csv": "PMID\n",
                "data/warning_ledger.csv": "Warning_ID,After\n",
                "identity/identity_structure_audit.csv": "Compound_ID,Registry_InChIKey\n",
                "provenance/selection_decisions.csv": "Candidate\n",
                "provenance/source_audit.csv": "Evidence_ID\n",
                "provenance/claim_support_and_verification.csv": "Evidence_ID\n",
                "data/cooking_retention_evidence.csv": "Evidence_ID\n",
            }
            for rel, text in tables.items():
                path = release / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            errors, _, _ = validator.inspect(release)
        self.assertTrue(any(error["Code"] == "CMP_ID_DUP" for error in errors))

    def test_manifest_entries_exist_and_match_sha256(self) -> None:
        verifier = load_manifest_integrity()
        manifest = verifier.load_manifest(RELEASE)
        actual_paths = {
            path.relative_to(RELEASE).as_posix()
            for path in RELEASE.rglob("*")
            if path.is_file() and path.relative_to(RELEASE).as_posix() != verifier.MANIFEST_RELATIVE_PATH
        }
        self.assertEqual(set(manifest), actual_paths)
        result = verifier.verify_manifest(RELEASE, mode="canonical")
        self.assertEqual(result["status"], "PASS", result)
        self.assertEqual(result["manifest_entries"], result["release_files"])
        self.assertNotIn(verifier.MANIFEST_RELATIVE_PATH, manifest)

    def test_release_reads_do_not_change_authoritative_files(self) -> None:
        paths = [
            RELEASE / "manifests" / "SHA256SUMS.json",
            RELEASE / "data" / "compound_registry.csv",
            RELEASE / "data" / "interaction_evidence.csv",
            RELEASE / "data" / "warning_ledger.csv",
        ]
        before = {path: sha256(path) for path in paths}
        for path in paths:
            with path.open("rb") as handle:
                handle.read(32)
        after = {path: sha256(path) for path in paths}
        self.assertEqual(before, after)

    def test_dataset_ids_have_no_duplicate_rows(self) -> None:
        self.assertFalse([value for value, count in Counter(row["Compound_ID"] for row in self.compounds).items() if count > 1])
        self.assertFalse([value for value, count in Counter(row["Evidence_ID"] for row in self.evidence).items() if count > 1])


if __name__ == "__main__":
    unittest.main()
