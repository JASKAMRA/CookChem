"""Mutation-oriented tests for the StageB_Final manifest contract."""
from __future__ import annotations

import json
import tempfile
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "stageB" / "release" / "StageB_Final" / "scripts" / "manifest_integrity.py"
def load_source_without_bytecode(path: Path, name: str):
    """Execute trusted source in memory so imports cannot mutate a frozen release."""
    module = types.ModuleType(name)
    module.__file__ = str(path)
    module.__package__ = ""
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


manifest_integrity = load_source_without_bytecode(MODULE_PATH, "stageb_manifest_integrity")


class ManifestIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / "stageB" / "temp")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def add_manifest(self, entries: dict[str, str]) -> None:
        path = self.root / manifest_integrity.MANIFEST_RELATIVE_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(entries), encoding="utf-8")

    def test_build_and_verify_exact_bytes(self) -> None:
        (self.root / "data.csv").write_bytes(b"a,b\n1,2\n")
        (self.root / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00")
        manifest = manifest_integrity.build_manifest(self.root)
        result = manifest_integrity.verify_manifest(self.root, mode="exact")
        self.assertEqual(len(manifest), 2)
        self.assertEqual(result["status"], "PASS")

    def test_source_module_loading_does_not_create_bytecode_in_release(self) -> None:
        source = self.root / "manifest_verifier.py"
        source.write_text("VALUE = 17\n", encoding="utf-8")
        before = {p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file()}
        module = load_source_without_bytecode(source, "synthetic_manifest_verifier")
        after = {p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(17, module.VALUE)
        self.assertEqual(before, after)

    def test_canonical_mode_accepts_checkout_crlf_only(self) -> None:
        (self.root / "notes.txt").write_bytes(b"line 1\nline 2\n")
        manifest_integrity.build_manifest(self.root)
        (self.root / "notes.txt").write_bytes(b"line 1\r\nline 2\r\n")
        result = manifest_integrity.verify_manifest(self.root, mode="canonical")
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["raw_byte_mismatch_count"], 1)

    def test_exact_mode_rejects_line_ending_change(self) -> None:
        (self.root / "notes.csv").write_bytes(b"x\ny\n")
        manifest_integrity.build_manifest(self.root)
        (self.root / "notes.csv").write_bytes(b"x\r\ny\r\n")
        self.assertEqual(manifest_integrity.verify_manifest(self.root, mode="exact")["status"], "FAIL")

    def test_binary_is_never_line_ending_normalized(self) -> None:
        (self.root / "image.png").write_bytes(b"A\r\nB")
        manifest_integrity.build_manifest(self.root)
        (self.root / "image.png").write_bytes(b"A\nB")
        self.assertEqual(manifest_integrity.verify_manifest(self.root, mode="canonical")["status"], "FAIL")

    def test_modified_text_content_is_detected(self) -> None:
        (self.root / "data.csv").write_text("value\n1\n", encoding="utf-8")
        manifest_integrity.build_manifest(self.root)
        (self.root / "data.csv").write_text("value\n2\n", encoding="utf-8")
        self.assertEqual(manifest_integrity.verify_manifest(self.root)["status"], "FAIL")

    def test_modified_image_is_detected(self) -> None:
        (self.root / "audit.png").write_bytes(b"PNG-original")
        manifest_integrity.build_manifest(self.root)
        (self.root / "audit.png").write_bytes(b"PNG-modified")
        result = manifest_integrity.verify_manifest(self.root)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["mismatches"][0]["path"], "audit.png")

    def test_deleted_file_is_reported(self) -> None:
        file = self.root / "data.csv"
        file.write_bytes(b"x\n")
        manifest_integrity.build_manifest(self.root)
        file.unlink()
        self.assertEqual(manifest_integrity.verify_manifest(self.root)["missing"], ["data.csv"])

    def test_unexpected_file_is_reported(self) -> None:
        manifest_integrity.build_manifest(self.root)
        (self.root / "extra.bin").write_bytes(b"unexpected")
        self.assertEqual(manifest_integrity.verify_manifest(self.root)["unexpected"], ["extra.bin"])

    def test_duplicate_manifest_path_is_rejected(self) -> None:
        path = self.root / manifest_integrity.MANIFEST_RELATIVE_PATH
        path.parent.mkdir(parents=True)
        path.write_text('{"a.txt":"' + "0" * 64 + '","a.txt":"' + "0" * 64 + '"}', encoding="utf-8")
        with self.assertRaises(manifest_integrity.ManifestError):
            manifest_integrity.load_manifest(self.root)

    def test_malformed_manifest_is_rejected(self) -> None:
        path = self.root / manifest_integrity.MANIFEST_RELATIVE_PATH
        path.parent.mkdir(parents=True)
        path.write_text("{bad", encoding="utf-8")
        with self.assertRaises(manifest_integrity.ManifestError):
            manifest_integrity.load_manifest(self.root)

    def test_invalid_hash_format_is_rejected(self) -> None:
        self.add_manifest({"a.txt": "xyz"})
        with self.assertRaises(manifest_integrity.ManifestError):
            manifest_integrity.load_manifest(self.root)

    def test_path_traversal_is_rejected(self) -> None:
        self.add_manifest({"../outside.txt": "0" * 64})
        with self.assertRaises(manifest_integrity.ManifestError):
            manifest_integrity.load_manifest(self.root)

    def test_absolute_path_is_rejected(self) -> None:
        self.add_manifest({"C:/outside.txt": "0" * 64})
        with self.assertRaises(manifest_integrity.ManifestError):
            manifest_integrity.load_manifest(self.root)

    def test_backslash_path_is_rejected(self) -> None:
        self.add_manifest({"nested\\file.txt": "0" * 64})
        with self.assertRaises(manifest_integrity.ManifestError):
            manifest_integrity.load_manifest(self.root)

    def test_manifest_cannot_include_itself(self) -> None:
        self.add_manifest({manifest_integrity.MANIFEST_RELATIVE_PATH: "0" * 64})
        with self.assertRaises(manifest_integrity.ManifestError):
            manifest_integrity.load_manifest(self.root)

    def test_empty_release_build_is_deterministic_and_excludes_self(self) -> None:
        first = manifest_integrity.build_manifest(self.root)
        first_bytes = (self.root / manifest_integrity.MANIFEST_RELATIVE_PATH).read_bytes()
        second = manifest_integrity.build_manifest(self.root)
        self.assertEqual(first, second)
        self.assertEqual(first_bytes, (self.root / manifest_integrity.MANIFEST_RELATIVE_PATH).read_bytes())
        self.assertEqual(manifest_integrity.verify_manifest(self.root, mode="exact")["status"], "PASS")
        self.assertNotIn(manifest_integrity.MANIFEST_RELATIVE_PATH, first)

    def test_missing_release_directory_is_rejected(self) -> None:
        missing = self.root / "missing"
        with self.assertRaises(manifest_integrity.ManifestError):
            manifest_integrity.verify_manifest(missing)

    def test_missing_manifest_is_rejected(self) -> None:
        with self.assertRaises(manifest_integrity.ManifestError):
            manifest_integrity.verify_manifest(self.root)

    def test_repeated_verification_is_identical(self) -> None:
        (self.root / "a.json").write_text("{}\n", encoding="utf-8")
        manifest_integrity.build_manifest(self.root)
        self.assertEqual(manifest_integrity.verify_manifest(self.root), manifest_integrity.verify_manifest(self.root))

    def test_unreadable_file_error_is_not_suppressed(self) -> None:
        file = self.root / "data.csv"
        file.write_bytes(b"a\n")
        manifest_integrity.build_manifest(self.root)
        original = Path.read_bytes

        def fail_for_artifact(path: Path) -> bytes:
            if path == file:
                raise OSError("synthetic unreadable-file failure")
            return original(path)

        from unittest.mock import patch
        with patch.object(Path, "read_bytes", fail_for_artifact):
            with self.assertRaises(OSError):
                manifest_integrity.verify_manifest(self.root)


if __name__ == "__main__":
    unittest.main()
