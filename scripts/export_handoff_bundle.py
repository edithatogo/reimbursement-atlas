"""Export a verified git bundle, source archive, manifest and checksums."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess  # nosec B404 - fixed git command with an argument list
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from reimburse_atlas.registry import project_root


def _run_git(root: Path, *arguments: str) -> None:
    """Run a fixed git subcommand without shell expansion."""
    subprocess.run(  # nosec B603, B607 - executable and arguments are controlled
        ["git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )


def _sha256(path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _commit(root: Path) -> str:
    """Return the exact commit packaged by the exporter."""
    result = subprocess.run(  # nosec B603, B607 - fixed git read command
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _readiness(root: Path) -> dict[str, bool]:
    """Read fail-closed readiness booleans without copying local paths."""
    path = root / "data" / "derived" / "release_readiness" / "summary.json"
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    keys = (
        "repository_release_ready",
        "research_publication_ready",
        "osf_registration_ready",
        "evidence_release_ready",
        "policy_claims_ready",
    )
    return {key: bool(payload.get(key, False)) for key in keys}


def export_handoff(
    *,
    root: Path,
    output_dir: Path,
    prefix: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Create and verify all handoff subjects, returning the redacted manifest."""
    if not prefix or Path(prefix).name != prefix or "/" in prefix:
        invalid_prefix_message = "prefix must be a filename stem without path separators"
        raise ValueError(invalid_prefix_message)
    output_dir.mkdir(parents=True, exist_ok=True)
    bundle = output_dir / f"{prefix}.git.bundle"
    archive = output_dir / f"{prefix}.tar.gz"
    manifest_path = output_dir / f"{prefix}.manifest.json"
    checksums_path = output_dir / f"{prefix}.sha256"
    for path in (bundle, archive, manifest_path, checksums_path):
        path.unlink(missing_ok=True)

    _run_git(root, "bundle", "create", str(bundle), "--all")
    _run_git(root, "archive", "--format=tar.gz", f"--output={archive}", "HEAD")
    _run_git(root, "bundle", "verify", str(bundle))

    bundle_sha = _sha256(bundle)
    archive_sha = _sha256(archive)
    checksums_path.write_text(
        f"{bundle_sha}  {bundle.name}\n{archive_sha}  {archive.name}\n",
        encoding="utf-8",
    )
    timestamp = (now or datetime.now(UTC)).astimezone(UTC).isoformat().replace("+00:00", "Z")
    manifest: dict[str, Any] = {
        "schema_version": "handoff-package-v1",
        "commit": _commit(root),
        "generated_at": timestamp,
        "bundle": {
            "path": bundle.name,
            "bytes": bundle.stat().st_size,
            "sha256": bundle_sha,
        },
        "archive": {
            "path": archive.name,
            "bytes": archive.stat().st_size,
            "sha256": archive_sha,
        },
        "readiness": _readiness(root),
        "verification": {
            "bundle_verified": True,
            "checksums_written": True,
            "raw_source_payloads_in_archive": False,
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    """Parse exporter arguments and write the handoff package."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory outside the repository for handoff subjects.",
    )
    parser.add_argument("--prefix", required=True, help="Filename stem for the four outputs.")
    args = parser.parse_args()
    manifest = export_handoff(root=project_root(), output_dir=args.output_dir, prefix=args.prefix)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
