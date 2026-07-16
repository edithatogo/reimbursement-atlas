"""Verify a downloaded deterministic release manifest and its local subjects."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, NoReturn, cast


class ReleaseManifestError(ValueError):
    """Raised when a release manifest or subject fails verification."""


def _fail(message: str) -> NoReturn:
    """Raise the verifier's stable fail-closed exception."""
    raise ReleaseManifestError(message)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        message = f"cannot read release manifest: {exc}"
        raise ReleaseManifestError(message) from exc
    if not isinstance(payload, dict):
        _fail("release manifest must be a JSON object")
    return cast("dict[str, Any]", payload)


def verify_manifest(  # noqa: PLR0912
    manifest_path: Path,
    root: Path,
    *,
    expected_tag: str | None = None,
    expected_commit: str | None = None,
) -> int:
    """Verify manifest metadata and return the number of verified subjects."""
    manifest = _load_manifest(manifest_path)
    if manifest.get("schema_version") != "release-manifest-v1":
        _fail("unsupported release manifest schema")
    if manifest.get("repository") != "https://github.com/edithatogo/reimbursement-atlas":
        _fail("release manifest repository does not match the project")
    tag = manifest.get("tag")
    commit = manifest.get("commit")
    if not isinstance(tag, str) or not tag.startswith("v"):
        _fail("release manifest tag is invalid")
    if (
        not isinstance(commit, str)
        or len(commit) != 40
        or any(character not in "0123456789abcdef" for character in commit)
    ):
        _fail("release manifest commit is invalid")
    if expected_tag is not None and tag != expected_tag:
        message = f"release manifest tag mismatch: expected {expected_tag}, got {tag}"
        _fail(message)
    if expected_commit is not None and commit != expected_commit:
        _fail("release manifest commit mismatch")

    subjects = manifest.get("subjects")
    if not isinstance(subjects, list) or not subjects:
        _fail("release manifest subjects must be a non-empty list")
    root_resolved = root.resolve()
    verified = 0
    seen: set[str] = set()
    for raw_subject in cast("list[Any]", subjects):
        if not isinstance(raw_subject, dict):
            _fail("release manifest subject must be an object")
        subject = cast("dict[str, Any]", raw_subject)
        relative_path = subject.get("path")
        digest = subject.get("sha256")
        if (
            not isinstance(relative_path, str)
            or not relative_path
            or Path(relative_path).is_absolute()
        ):
            _fail("release subject paths must be relative")
        if relative_path in seen or ".." in Path(relative_path).parts:
            message = f"release subject path is unsafe or duplicated: {relative_path}"
            _fail(message)
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
        ):
            message = f"release subject has an invalid SHA-256: {relative_path}"
            _fail(message)
        subject_path = (root_resolved / relative_path).resolve()
        if root_resolved not in subject_path.parents:
            message = f"release subject escapes verification root: {relative_path}"
            _fail(message)
        if not subject_path.is_file():
            message = f"release subject is missing: {relative_path}"
            _fail(message)
        if _sha256(subject_path) != digest:
            message = f"release subject checksum mismatch: {relative_path}"
            _fail(message)
        seen.add(relative_path)
        verified += 1
    return verified


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--expected-tag")
    parser.add_argument("--expected-commit")
    return parser.parse_args()


def main() -> None:
    """Verify local release subjects without network IO."""
    args = _parse_args()
    count = verify_manifest(
        args.manifest,
        args.root,
        expected_tag=args.expected_tag,
        expected_commit=args.expected_commit,
    )
    print(f"Verified {count} release subjects from {args.manifest}")


if __name__ == "__main__":
    main()
