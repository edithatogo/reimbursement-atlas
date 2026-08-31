"""Offline, fail-closed tests for PBS raw archive preparation."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, BinaryIO

import pytest

from scripts import prepare_pbs_raw_archive as archive


@pytest.fixture
def case(tmp_path: Path) -> tuple[Path, dict[str, Any]]:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text("data/raw_live/\ndata/local/\n")
    permission = tmp_path / archive.PERMISSION
    permission.parent.mkdir(parents=True)
    shutil.copyfile(Path(__file__).resolve().parents[2] / archive.PERMISSION, permission)
    payload = b"%PDF-1.7 original PBS copyright and disclaimer\n"
    cache = f"{archive.RAW}/pbs_archive/au_pbs_test.pdf"
    path = tmp_path / cache
    path.parent.mkdir(parents=True)
    path.write_bytes(payload)
    return tmp_path, {
        "id": "au_pbs_test",
        "source_id": "au_pbs",
        "source_version_id": "au_pbs_20200101",
        "citation_key": "atlas:au_pbs_20200101",
        "source_url": (
            "https://www.pbs.gov.au/publication/schedule/2020/01/"
            "2020-01-01-general-schedule.pdf?variant=3"
        ),
        "status": "cached",
        "cache_path": cache,
        "byte_size": len(payload),
        "checksum_sha256": hashlib.sha256(payload).hexdigest(),
    }


def error(root: Path, receipt: dict[str, Any]) -> str:
    result = archive.prepare(root, [receipt], stage="data/local/stage")
    assert result["status"] == "blocked"
    assert not (root / "data/local/stage").exists()
    return result["errors"][0]["error"]


def test_dry_run_deterministic_and_no_false_publication(case: tuple[Path, dict[str, Any]]) -> None:
    root, receipt = case
    receipt.update(publication_state="published", published=True, detail=f"{root}/secret")
    second = {**receipt, "id": "au_pbs_second"}
    one = archive.prepare(root, [receipt, second])
    two = archive.prepare(root, [second, receipt])
    assert archive.serialize(one) == archive.serialize(two)
    assert one["status"] == "verified"
    assert one["publication_state"] == "not_asserted"
    assert one["network_publication_performed"] is False
    output = archive.serialize(one)
    assert str(root) not in output
    assert "secret" not in output
    assert '"published"' not in output
    assert "cache_path" not in output
    assert not (root / "data/local").exists()


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("byte_size", 123, "size_mismatch"),
        ("checksum_sha256", "0" * 64, "sha256_mismatch"),
        ("byte_size", True, "invalid_receipt_fingerprint"),
        ("byte_size", None, "invalid_receipt_fingerprint"),
        ("checksum_sha256", "xyz", "invalid_receipt_fingerprint"),
        ("status", "download_failed", "not_acquired"),
        ("status", "published", "not_acquired"),
        ("source_id", "au_mbs", "missing_pbs_source_identity"),
        ("source_version_id", None, "invalid_identity"),
        ("citation_key", None, "invalid_identity"),
    ],
)
def test_bad_receipts(
    case: tuple[Path, dict[str, Any]], field: str, value: object, expected: str
) -> None:
    root, receipt = case
    receipt[field] = value
    assert error(root, receipt) == expected


@pytest.mark.parametrize(
    "path",
    [
        "/outside/payload.pdf",
        "data/raw_live/historical_sources/../../../secret",
        "data/raw_live/historical_sources/./payload.pdf",
        "data/raw_live/historical_sources/a\\b",
        "data/derived/payload.pdf",
    ],
)
def test_traversal(case: tuple[Path, dict[str, Any]], path: str) -> None:
    root, receipt = case
    receipt["cache_path"] = path
    assert error(root, receipt) in {"unsafe_path", "unsafe_cache_path"}


@pytest.mark.parametrize("component", ["file", "directory", "root"])
def test_symlink_escape(case: tuple[Path, dict[str, Any]], component: str, tmp_path: Path) -> None:
    root, receipt = case
    payload = root / receipt["cache_path"]
    if component == "file":
        payload.unlink()
        payload.symlink_to(root / ".gitignore")
    else:
        directory = payload.parent if component == "directory" else root / "data/raw_live"
        shutil.rmtree(directory)
        directory.symlink_to(tmp_path.parent, target_is_directory=True)
    assert error(root, receipt) == "symlink_path"


def test_missing_payload_and_permission(case: tuple[Path, dict[str, Any]]) -> None:
    root, receipt = case
    (root / receipt["cache_path"]).unlink()
    assert error(root, receipt) == "missing_payload"
    (root / archive.PERMISSION).unlink()
    assert error(root, receipt) == "permission_not_accepted"


@pytest.mark.parametrize(
    "url",
    [
        "https://www.pbs.gov.au.evil.example/publication/schedule/a.pdf",
        "https://user:secret@www.pbs.gov.au/publication/schedule/a.pdf",
        "https://www.pbs.gov.au/publication/schedule/a.pdf?api_key=secret",
        "https://www.pbs.gov.au/publication/schedule/a.pdf#secret",
        "https://www.pbs.gov.au/publication/schedule/../secret.pdf",
        "https://www.pbs.gov.au/publication/schedule/%2e%2e/secret.pdf",
        "https://www.pbs.gov.au/api/a.pdf",
        "https://[broken",
    ],
)
def test_source_scope_and_secrets(case: tuple[Path, dict[str, Any]], url: str) -> None:
    root, receipt = case
    receipt["source_url"] = url
    assert error(root, receipt) == "invalid_source_url"
    assert "secret" not in archive.serialize(archive.prepare(root, [receipt]))


def test_stage_preserves_bytes_and_readback_detects_corruption(
    case: tuple[Path, dict[str, Any]],
) -> None:
    root, receipt = case
    staged = archive.prepare(root, [receipt], stage="data/local/stage")
    assert staged["status"] == "verified"
    target = root / "data/local/stage" / staged["files"][0]["archive_path"]
    original = (root / receipt["cache_path"]).read_bytes()
    assert target.read_bytes() == original
    assert json.loads((root / "data/local/stage/raw/pbs/manifest.json").read_text()) == staged
    assert not (root / "data/local/stage/README.md").exists()
    assert all(row["archive_path"].startswith("raw/pbs/") for row in staged["files"])
    shutil.copytree(root / "data/local/stage", root / "data/local/readback")
    (root / receipt["cache_path"]).unlink()
    result = archive.prepare(root, [receipt], readback="data/local/readback")
    assert result["status"] == "verified"
    assert result["publication_state"] == "not_asserted"
    copy = root / "data/local/readback" / staged["files"][0]["archive_path"]
    copy.write_bytes(b"X" * len(original))
    result = archive.prepare(root, [receipt], readback="data/local/readback")
    assert result["errors"][0]["error"] == "sha256_mismatch"
    with pytest.raises(archive.ArchiveError, match="stage_already_exists"):
        archive.prepare(root, [receipt], stage="data/local/stage")


def test_batch_failure_stages_nothing(case: tuple[Path, dict[str, Any]]) -> None:
    root, receipt = case
    missing = {**receipt, "id": "missing", "cache_path": f"{archive.RAW}/missing.pdf"}
    result = archive.prepare(root, [receipt, missing], stage="data/local/stage")
    assert result["status"] == "blocked"
    assert result["coverage"] == {
        "requested_receipts": 2,
        "verified_files": 1,
        "failed_receipts": 1,
        "complete_for_requested_batch": False,
        "historical_completeness_asserted": False,
    }
    assert not (root / "data/local/stage").exists()
    assert archive.prepare(root, [])["status"] == "blocked"
    assert archive.prepare(root, [receipt, receipt])["errors"][0]["error"] == "duplicate_identity"


def test_output_must_be_ignored_and_not_symlinked(case: tuple[Path, dict[str, Any]]) -> None:
    root, receipt = case
    with pytest.raises(archive.ArchiveError, match="outside_ignored_root"):
        archive.prepare(root, [receipt], stage="data/derived/stage")
    (root / "data/local").symlink_to(root / "data/raw_live", target_is_directory=True)
    with pytest.raises(archive.ArchiveError, match="symlink_path"):
        archive.prepare(root, [receipt], stage="data/local/stage")
    (root / "data/local").unlink()
    (root / ".gitignore").write_text("")
    with pytest.raises(archive.ArchiveError, match="path_not_ignored"):
        archive.prepare(root, [receipt], stage="data/local/stage")


def test_source_identified_variant(case: tuple[Path, dict[str, Any]]) -> None:
    root, receipt = case
    url = receipt["source_url"].split("?")[0]
    variant = {
        **receipt,
        "id": "au_pbs_variant",
        "source_id": receipt["id"],
        "official_source_url": url,
        "archive_timestamp": "20200101000000",
        "archive_replay_url": f"https://web.archive.org/web/20200101000000id_/{url}",
        "archive_digest_verified": True,
    }
    del variant["cache_path"]
    path = root / archive.RAW / "pbs_internet_archive_variants/au_pbs_variant.pdf"
    path.parent.mkdir()
    shutil.copyfile(root / receipt["cache_path"], path)
    result = archive.prepare(root, [receipt, variant])
    assert result["status"] == "verified"
    assert result["files"][1]["source_version_id"] == receipt["source_version_id"]
    assert archive.prepare(root, [variant])["status"] == "blocked"
    variant["archive_replay_url"] = str(variant["archive_replay_url"]) + "?secret=abc"
    assert (
        archive.prepare(root, [receipt, variant])["errors"][0]["error"]
        == "unverified_archive_identity"
    )


def test_cli_missing_receipts_fails_without_path_leak(
    case: tuple[Path, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root, _ = case
    monkeypatch.setattr("sys.argv", ["prepare", "--root", str(root), "--receipts", "missing.jsonl"])
    assert archive.main() == 1
    output = capsys.readouterr().out
    assert str(root) not in output
    assert json.loads(output)["publication_state"] == "not_asserted"


def test_structured_package_is_not_extracted(case: tuple[Path, dict[str, Any]]) -> None:
    root, receipt = case
    receipt["source_url"] = (
        "https://www.pbs.gov.au/publication/schedule/2020/01/2020-01-01-xml-V3.zip"
    )
    payload = b"PK\x03\x04 synthetic unchanged package"
    (root / receipt["cache_path"]).write_bytes(payload)
    receipt.update(byte_size=len(payload), checksum_sha256=hashlib.sha256(payload).hexdigest())
    result = archive.prepare(root, [receipt], stage="data/local/package")
    assert result["status"] == "verified"
    staged = root / "data/local/package" / result["files"][0]["archive_path"]
    assert staged.suffix == ".zip"
    assert staged.read_bytes() == payload


def test_tracked_raw_file_is_rejected(case: tuple[Path, dict[str, Any]]) -> None:
    root, receipt = case
    subprocess.run(["git", "add", "-f", "--", receipt["cache_path"]], cwd=root, check=True)
    assert error(root, receipt) == "path_not_ignored"


def test_revoked_permission_is_rejected(case: tuple[Path, dict[str, Any]]) -> None:
    root, receipt = case
    path = root / archive.PERMISSION
    permission = json.loads(path.read_text())
    permission["decision"] = "revoked"
    path.write_text(json.dumps(permission))
    assert error(root, receipt) == "permission_not_accepted"


def test_copy_corruption_cleans_only_new_stage(
    case: tuple[Path, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, receipt = case
    original = (root / receipt["cache_path"]).read_bytes()

    def corrupt(_source: BinaryIO, output: BinaryIO) -> None:
        output.write(b"bad copy")

    monkeypatch.setattr(archive.shutil, "copyfileobj", corrupt)
    result = archive.prepare(root, [receipt], stage="data/local/stage")
    assert result["status"] == "blocked"
    assert result["errors"] == [{"id": "batch", "error": "staging_failed"}]
    assert not (root / "data/local/stage").exists()
    assert (root / receipt["cache_path"]).read_bytes() == original


def test_permission_helper_is_authoritative_for_format_notices(
    case: tuple[Path, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, receipt = case
    receipt["source_url"] = (
        "https://www.pbs.gov.au/publication/schedule/2020/01/updated-pbs-text-files.pdf"
    )
    observed: list[tuple[str, Path]] = []

    def reject_notice(source_url: str, *, root: Path) -> str:
        observed.append((source_url, root))
        return "outside_pbs_permission_scope"

    monkeypatch.setattr(archive, "pbs_raw_redistribution_status", reject_notice)
    assert error(root, receipt) == "outside_pbs_permission_scope"
    assert observed == [(receipt["source_url"], root.resolve())]
    result = archive.prepare(root, [receipt])
    assert result["errors"][0]["source_url"] == receipt["source_url"]
    assert result["coverage"]["complete_for_requested_batch"] is False
