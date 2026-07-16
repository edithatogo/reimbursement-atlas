"""Build a deterministic manifest for tagged software release subjects."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument(
        "--artifact",
        action="append",
        nargs="+",
        required=True,
        help="One or more release subject paths; repeat for each artifact group.",
    )
    return parser.parse_args()


def build_manifest(tag: str, commit: str, artifacts: list[Path]) -> dict[str, object]:
    """Return a deterministic, checksum-bearing release manifest."""
    if not tag.startswith("v") or not tag[1:]:
        message = "tag must be a non-empty version tag beginning with 'v'"
        raise ValueError(message)
    if len(commit) != 40 or any(character not in "0123456789abcdef" for character in commit):
        message = "commit must be a lowercase 40-character Git SHA-1"
        raise ValueError(message)
    if not artifacts:
        message = "at least one release artifact is required"
        raise ValueError(message)

    subjects: list[dict[str, object]] = []
    seen: set[str] = set()
    for path in sorted(artifacts, key=lambda item: item.as_posix()):
        relative = path.as_posix()
        if path.is_absolute() or relative in seen:
            message = f"release artifact paths must be relative and unique: {relative}"
            raise ValueError(message)
        if not path.is_file():
            message = f"release artifact does not exist as a file: {relative}"
            raise ValueError(message)
        seen.add(relative)
        subjects.append({"path": relative, "size": path.stat().st_size, "sha256": _sha256(path)})

    return {
        "schema_version": "release-manifest-v1",
        "repository": "https://github.com/edithatogo/reimbursement-atlas",
        "tag": tag,
        "commit": commit,
        "subjects": subjects,
        "zenodo_deposition": "disabled_pending_publication_approval",
    }


def main() -> None:
    """Write the release manifest without network access or signing side effects."""
    args = _parse_args()
    artifact_paths = [Path(value) for group in args.artifact for value in group]
    payload = build_manifest(args.tag, args.commit, artifact_paths)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
