"""Deterministic SHA-256 manifest support for StageB_Final.

Text artifacts are hashed after CRLF-to-LF canonicalization so Git's
core.autocrlf checkout conversion does not alter the release identity.
Binary artifacts are always hashed as exact bytes.  ``mode='exact'`` is
available when the caller requires raw-byte equality for every artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any

MANIFEST_RELATIVE_PATH = "manifests/SHA256SUMS.json"
TEXT_SUFFIXES = frozenset({
    ".csv", ".json", ".md", ".txt", ".py", ".yaml", ".yml", ".toml",
    ".ini", ".xml", ".html", ".tsv", ".log",
})
HASH_RE = re.compile(r"^[0-9a-f]{64}$")


class ManifestError(ValueError):
    """Raised when a manifest or release tree is malformed."""


def _safe_relative_path(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ManifestError(f"invalid manifest path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ManifestError(f"unsafe manifest path: {value!r}")
    if ":" in path.parts[0] or value != path.as_posix():
        raise ManifestError(f"non-portable manifest path: {value!r}")
    if value == MANIFEST_RELATIVE_PATH:
        raise ManifestError("manifest must not include itself")
    return value


def _object_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ManifestError(f"duplicate manifest path: {key}")
        result[key] = value
    return result


def load_manifest(root: Path) -> dict[str, str]:
    manifest_path = root / MANIFEST_RELATIVE_PATH
    try:
        document = json.loads(
            manifest_path.read_text(encoding="utf-8-sig"),
            object_pairs_hook=_object_no_duplicates,
        )
    except ManifestError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"cannot read manifest: {exc}") from exc
    if not isinstance(document, dict):
        raise ManifestError("manifest must be a JSON object mapping paths to SHA-256 hashes")
    parsed: dict[str, str] = {}
    for raw_path, digest in document.items():
        path = _safe_relative_path(raw_path)
        if not isinstance(digest, str) or not HASH_RE.fullmatch(digest):
            raise ManifestError(f"invalid SHA-256 for {path}")
        parsed[path] = digest
    return parsed


def artifact_paths(root: Path) -> set[str]:
    """Return all files covered by the release contract, excluding only self."""
    root = root.resolve()
    if not root.exists() or not root.is_dir():
        raise ManifestError(f"release directory is missing or not a directory: {root}")
    paths: set[str] = set()
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ManifestError(f"symlinks are not allowed in a release: {path.relative_to(root)}")
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            if relative != MANIFEST_RELATIVE_PATH:
                paths.add(_safe_relative_path(relative))
    return paths


def _artifact_bytes(path: Path, *, canonical_text: bool) -> bytes:
    data = path.read_bytes()
    if canonical_text and path.suffix.lower() in TEXT_SUFFIXES:
        return data.replace(b"\r\n", b"\n")
    return data


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_manifest(root: Path) -> dict[str, str]:
    """Build a sorted manifest using canonical LF text and exact binary bytes."""
    root = root.resolve()
    paths = artifact_paths(root)
    result = {rel: _sha256(_artifact_bytes(root / rel, canonical_text=True)) for rel in sorted(paths)}
    manifest_path = root / MANIFEST_RELATIVE_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    manifest_path.write_bytes(encoded)
    return result


def verify_manifest(root: Path, *, mode: str = "canonical") -> dict[str, Any]:
    """Verify a release in canonical-text or strict exact-byte mode.

    Canonical mode permits only CRLF/LF checkout conversion for recognized
    text suffixes. It never normalizes binary artifacts.
    """
    if mode not in {"canonical", "exact"}:
        raise ManifestError("mode must be 'canonical' or 'exact'")
    root = root.resolve()
    manifest = load_manifest(root)
    actual_paths = artifact_paths(root)
    missing = sorted(set(manifest) - actual_paths)
    unexpected = sorted(actual_paths - set(manifest))
    mismatches: list[dict[str, str]] = []
    raw_mismatches: list[str] = []
    for relative in sorted(set(manifest) & actual_paths):
        path = root / relative
        if not path.resolve().is_relative_to(root):
            raise ManifestError(f"manifest path escapes release root: {relative}")
        raw_digest = _sha256(_artifact_bytes(path, canonical_text=False))
        if raw_digest != manifest[relative]:
            raw_mismatches.append(relative)
        digest = _sha256(_artifact_bytes(path, canonical_text=(mode == "canonical")))
        if digest != manifest[relative]:
            mismatches.append({"path": relative, "expected": manifest[relative], "actual": digest})
    passed = not (missing or unexpected or mismatches)
    return {
        "status": "PASS" if passed else "FAIL",
        "mode": mode,
        "manifest_entries": len(manifest),
        "release_files": len(actual_paths),
        "missing": missing,
        "unexpected": unexpected,
        "mismatches": mismatches,
        "raw_byte_mismatch_count": len(raw_mismatches),
        "raw_byte_mismatches": raw_mismatches,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build_parser = sub.add_parser("build", help="write deterministic SHA256SUMS.json")
    build_parser.add_argument("release_dir", type=Path)
    verify_parser = sub.add_parser("verify", help="verify a release manifest")
    verify_parser.add_argument("release_dir", type=Path)
    verify_parser.add_argument("--mode", choices=("canonical", "exact"), default="canonical")
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            result = {"status": "PASS", "manifest_entries": len(build_manifest(args.release_dir))}
        else:
            result = verify_manifest(args.release_dir, mode=args.mode)
    except (ManifestError, OSError) as exc:
        result = {"status": "FAIL", "error": str(exc)}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
