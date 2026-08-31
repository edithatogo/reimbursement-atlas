"""Offline PBS archive preparation. Default: verify receipts and print a dry-run manifest.

Run with PYTHONPATH=src:. python scripts/prepare_pbs_raw_archive.py --help.
--stage creates a NEW ignored directory containing raw/pbs/payloads and raw/pbs/manifest.json.
--readback checks an independently obtained local copy against the acquisition receipts;
the original cache need not remain present. It does not establish remote publication.
Never upload the raw cache
wholesale: only the successfully staged directory is a candidate for later governed upload.
The raw/pbs/ prefix is additive; do not replace a dataset card, configs, or derived manifests.
"""

from __future__ import annotations

# Error strings are stable machine-readable codes, not user-facing exception prose.
# ruff: file-ignore[raw-string-in-exception]
import argparse
import hashlib
import json
import re
import shutil
import subprocess  # nosec B404
from contextlib import suppress
from operator import itemgetter
from pathlib import Path, PurePosixPath
from typing import Any, cast
from urllib.parse import urlsplit

from reimburse_atlas.licence_review import pbs_raw_redistribution_status

RAW = "data/raw_live/historical_sources"
PERMISSION = "data/licence_review/pbs_raw_permission.json"
ARCHIVE_PREFIX = "raw/pbs"
DEFAULT_RECEIPTS = (
    "data/derived/historical_sources/pbs_archive_v1/historical_source_downloads.jsonl",
    "data/derived/historical_sources/pbs_structured_archive_v1/historical_source_downloads.jsonl",
    (
        "data/derived/historical_sources/pbs_archive_verification_v1/"
        "internet_archive_variant_receipts.jsonl"
    ),
)


class ArchiveError(ValueError):
    """A fixed, non-sensitive failure code safe for a manifest."""


def token(value: Any) -> str:
    """Accept identifiers, never paths or free-form diagnostics."""
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_:-]{1,220}", value):
        raise ArchiveError("invalid_identity")
    return value


def safe_path(root: Path, relative: str, *, ignored: bool = True) -> Path:
    """Reject traversal and every symlink component, including ignored-root symlinks."""
    path = PurePosixPath(relative)
    if (
        not relative
        or path.is_absolute()
        or "\\" in relative
        or any(part in {"", ".", ".."} for part in relative.split("/"))
    ):
        raise ArchiveError("unsafe_path")
    current = root
    for part in path.parts:
        current /= part
        if current.is_symlink():
            raise ArchiveError("symlink_path")
    if ignored:
        if path.parts[:2] not in {("data", "raw_live"), ("data", "local")}:
            raise ArchiveError("outside_ignored_root")
        # Fixed, read-only Git argv; no shell or network operation.
        result = subprocess.run(  # nosec B603 B607
            ["git", "check-ignore", "-q", "--", relative],
            cwd=root,
            check=False,
            capture_output=True,
        )
        if result.returncode != 0:
            raise ArchiveError("path_not_ignored")
    return current


def source_url(value: Any) -> str:
    """Bound to public schedule files; do not project credentials or arbitrary queries."""
    if not isinstance(value, str):
        raise ArchiveError("invalid_source_url")
    try:
        parsed = urlsplit(value)
        valid = (
            parsed.scheme in {"http", "https"}
            and parsed.hostname
            in {"pbs.gov.au", "www.pbs.gov.au", "m.pbs.gov.au", "data.pbs.gov.au"}
            and parsed.username is None
            and parsed.password is None
            and parsed.port is None
            and re.fullmatch(r"/publication/schedule/[A-Za-z0-9_./()-]+", parsed.path)
            and ".." not in parsed.path.split("/")
            and parsed.path.lower().endswith((".pdf", ".zip", ".xml", ".csv", ".txt", ".xlsx"))
            and (not parsed.query or re.fullmatch(r"variant=[0-9]+", parsed.query))
            and not parsed.fragment
            and not any(char.isspace() for char in value)
        )
    except ValueError:
        valid = False
    if not valid:
        raise ArchiveError("invalid_source_url")
    return value


def fingerprint(path: Path) -> tuple[int, str]:
    """Stream original bytes without parsing or transforming the source."""
    if not path.is_file():
        raise ArchiveError("missing_payload")
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            size += len(block)
            digest.update(block)
    return size, digest.hexdigest()


def check_bytes(path: Path, row: dict[str, Any]) -> None:
    """Require both exact byte size and SHA-256 from the acquisition receipt."""
    size, digest = fingerprint(path)
    if size != row["byte_size"]:
        raise ArchiveError("size_mismatch")
    if digest != row["checksum_sha256"]:
        raise ArchiveError("sha256_mismatch")


def receipt_entry(
    root: Path,
    receipt: dict[str, Any],
    parents: dict[str, dict[str, Any]],
    ids: list[str],
    readback: str | None,
) -> tuple[dict[str, Any], str]:
    """Bind one acquisition receipt to source identity, permission and local bytes."""
    identity = token(receipt.get("id"))
    if ids.count(identity) != 1:
        raise ArchiveError("duplicate_identity")
    if receipt.get("status") not in {"cached", "downloaded"}:
        raise ArchiveError("not_acquired")
    size, digest = receipt.get("byte_size"), receipt.get("checksum_sha256")
    if (
        type(size) is not int
        or size <= 0
        or not isinstance(digest, str)
        or not re.fullmatch(r"[0-9a-f]{64}", digest)
    ):
        raise ArchiveError("invalid_receipt_fingerprint")
    variant = "official_source_url" in receipt
    url = source_url(receipt.get("official_source_url" if variant else "source_url"))
    require_permission(root, url)
    parent = parents.get(token(receipt.get("source_id"))) if variant else receipt
    if not parent or parent.get("source_id") != "au_pbs":
        raise ArchiveError("missing_pbs_source_identity")
    version = token(parent.get("source_version_id"))
    citation = token(parent.get("citation_key"))
    row = {
        "id": identity,
        "source_id": "au_pbs",
        "source_version_id": version,
        "citation_key": citation,
        "source_url": url,
        "byte_size": size,
        "checksum_sha256": digest,
        "acquisition_status": receipt["status"],
    }
    if variant:
        if source_url(parent.get("source_url")).split("?")[0] != url.split("?")[0]:
            raise ArchiveError("variant_source_mismatch")
        stamp = receipt.get("archive_timestamp")
        replay = receipt.get("archive_replay_url")
        if not isinstance(stamp, str) or not re.fullmatch(r"[0-9]{14}", stamp):
            raise ArchiveError("invalid_archive_timestamp")
        if (
            replay != f"https://web.archive.org/web/{stamp}id_/{url.split('?')[0]}"
            or receipt.get("archive_digest_verified") is not True
        ):
            raise ArchiveError("unverified_archive_identity")
        row.update(archive_timestamp=stamp, archive_replay_url=replay)
        cache = receipt.get("cache_path", f"{RAW}/pbs_internet_archive_variants/{identity}.pdf")
    else:
        cache = receipt.get("cache_path")
    if not isinstance(cache, str) or not cache.startswith(f"{RAW}/"):
        raise ArchiveError("unsafe_cache_path")
    path = safe_path(root, cache)
    if not readback:
        check_bytes(path, row)
    suffix = Path(urlsplit(url).path).suffix.lower()
    row["archive_path"] = f"{ARCHIVE_PREFIX}/payloads/{identity}/{digest}{suffix}"
    if readback:
        check_bytes(safe_path(root, f"{readback}/{row['archive_path']}"), row)
    return row, cache


def require_permission(root: Path, url: str) -> None:
    """Distinguish out-of-scope artefacts from absent or revoked permission."""
    status = pbs_raw_redistribution_status(url, root=root)
    if status == "outside_pbs_permission_scope":
        raise ArchiveError("outside_pbs_permission_scope")
    if status != "allowed_owner_attested_permission":
        raise ArchiveError("permission_not_accepted")


def prepare(
    root: Path,
    receipts: list[dict[str, Any]],
    *,
    stage: str | None = None,
    readback: str | None = None,
) -> dict[str, Any]:
    """Validate every receipt; any failure prevents staging the entire batch.

    Input matches historical_source_downloads.jsonl and variant receipts. Variants
    require their official parent receipt in the same batch. Output is an explicit
    allowlist, not a copy of receipt diagnostics, local paths, or publication claims.
    This is a single-writer local utility, not a defense against concurrent hostile
    filesystem mutation. Staging paths must be new and remain under caller control.
    """
    root = root.resolve()
    if stage and readback:
        raise ArchiveError("conflicting_modes")
    destination = safe_path(root, stage) if stage else None
    if destination and destination.exists():
        raise ArchiveError("stage_already_exists")
    if readback:
        safe_path(root, readback)
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    files: dict[str, str] = {}
    ids = [str(row.get("id", "")) for row in receipts]
    parents = {
        row["id"]: row
        for row in receipts
        if row.get("source_id") == "au_pbs" and isinstance(row.get("id"), str)
    }
    for receipt in receipts:
        identity = "invalid_identity"
        try:
            identity = token(receipt.get("id"))
            row, cache = receipt_entry(root, receipt, parents, ids, readback)
            files[identity] = cache
            rows.append(row)
        except ArchiveError as exc:
            errors.append({"id": identity, "error": str(exc)})
        except OSError, ValueError, TypeError:
            errors.append({"id": identity, "error": "unreadable_or_invalid_input"})
    if not receipts:
        errors.append({"id": "batch", "error": "empty_receipt_batch"})
    for issue in errors:
        receipt = next(
            (item for item in receipts if item.get("id") == issue["id"]), dict[str, Any]()
        )
        with suppress(ArchiveError):
            issue["source_url"] = source_url(
                receipt.get("official_source_url", receipt.get("source_url"))
            )
    manifest = {
        "schema_version": "pbs-raw-archive-staging-v1",
        "mode": "readback" if readback else "stage" if stage else "dry_run",
        "status": "blocked" if errors else "verified",
        "publication_state": "not_asserted",
        "network_publication_performed": False,
        "archive_prefix": ARCHIVE_PREFIX,
        "coverage": {
            "requested_receipts": len(receipts),
            "verified_files": len(rows),
            "failed_receipts": len(errors),
            "complete_for_requested_batch": not errors,
            "historical_completeness_asserted": False,
        },
        "permission_record": PERMISSION,
        "permission_basis": "owner_attestation",
        "attribution": "Australian Government Pharmaceutical Benefits Scheme (PBS).",
        "rights_source": "https://www.pbs.gov.au/info/general/copyright",
        "preservation": (
            "Original bytes, embedded notices and disclaimers preserved; no transformation."
        ),
        "licence": "Source-specific PBS permission; software Apache-2.0 does not apply.",
        "files": sorted(rows, key=itemgetter("id")),
        "errors": sorted(errors, key=itemgetter("id", "error")),
    }
    if destination and not errors:
        destination.mkdir(parents=True, exist_ok=False)
        try:
            for row in rows:
                copy_payload(root, str(stage), files[row["id"]], row)
            (destination / ARCHIVE_PREFIX / "manifest.json").write_text(
                serialize(manifest), encoding="utf-8"
            )
        except OSError, ArchiveError:
            # Only this invocation's newly created staging tree is removed.
            shutil.rmtree(destination)
            manifest["status"] = "blocked"
            errors.append({"id": "batch", "error": "staging_failed"})
            manifest["errors"] = errors
    return manifest


def copy_payload(root: Path, stage: str, cache: str, row: dict[str, Any]) -> None:
    """Copy exclusively, then verify the staged bytes against the receipt again."""
    target = safe_path(root, f"{stage}/{row['archive_path']}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with safe_path(root, cache).open("rb") as source, target.open("xb") as output:
        shutil.copyfileobj(source, output)
    check_bytes(target, row)


def serialize(manifest: dict[str, Any]) -> str:
    """Produce stable JSON with no clock, host, absolute paths or arbitrary receipt fields."""
    return json.dumps(manifest, indent=2, sort_keys=True) + "\n"


def load_receipts(root: Path, paths: list[str]) -> list[dict[str, Any]]:
    """Require every requested receipt file and reject malformed JSONL rows."""
    receipts: list[dict[str, Any]] = []
    for relative in paths:
        path = safe_path(root.resolve(), relative, ignored=False)
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ArchiveError("invalid_receipt_object")
                receipts.append(cast("dict[str, Any]", row))
    return receipts


def main() -> int:
    """CLI: print only bounded metadata; return nonzero for every blocked batch."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--receipts", action="append", help="Repo-relative JSONL; repeat for variants and parents"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--stage", help="New ignored repo-relative output directory")
    mode.add_argument(
        "--readback", help="Ignored repo-relative independently retrieved payload tree"
    )
    args = parser.parse_args()
    try:
        receipts = load_receipts(args.root, args.receipts or list(DEFAULT_RECEIPTS))
        manifest = prepare(args.root, receipts, stage=args.stage, readback=args.readback)
    except OSError, ValueError:
        print(
            serialize({
                "status": "blocked",
                "error": "invalid_input_or_path",
                "publication_state": "not_asserted",
            }),
            end="",
        )
        return 1
    print(serialize(manifest), end="")
    return int(manifest["status"] == "blocked")


if __name__ == "__main__":
    raise SystemExit(main())
