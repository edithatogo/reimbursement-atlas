"""Offline, fail-closed tests for PBS raw archive preparation."""

from __future__ import annotations

import base64
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, BinaryIO

import pytest

from reimburse_atlas import licence_review
from scripts import prepare_pbs_raw_archive as archive


@pytest.fixture
def case(tmp_path: Path) -> tuple[Path, dict[str, Any]]:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text("data/raw_live/\ndata/local/\n")
    permission = tmp_path / archive.PERMISSION
    permission.parent.mkdir(parents=True)
    # Match the complete permission record to the helper actually selected by PYTHONPATH.
    helper_root = Path(licence_review.__file__).resolve().parents[2]
    shutil.copyfile(helper_root / archive.PERMISSION, permission)
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
        "failed_operations": 0,
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
    assert result["files"][1]["original_source_filename"] == ("2020-01-01-general-schedule.pdf")
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


@pytest.fixture
def canonical_case(case: tuple[Path, dict[str, Any]]) -> tuple[Path, dict[str, Any], str]:
    root, receipt = case
    receipt["retrieval_metadata"] = {"checked": True}
    omitted = {**receipt, "id": "au_pbs_missing", "status": "download_failed"}
    for relative, rows in zip(archive.DEFAULT_RECEIPTS, ([receipt], [omitted], []), strict=True):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(row) + "\n" for row in rows))
    selection = "data/local/selection.jsonl"
    (root / selection).parent.mkdir(parents=True, exist_ok=True)
    (root / selection).write_text(json.dumps(receipt) + "\n")
    return root, receipt, selection


def test_exact_subset_is_canonical_and_full_batch_keeps_omissions(
    canonical_case: tuple[Path, dict[str, Any], str],
) -> None:
    root, receipt, selection = canonical_case
    (root / selection).write_text(
        json.dumps(dict(reversed(list(receipt.items()))), indent=0).replace("\n", " ") + "\n"
    )
    assert archive.load_bound_receipts(root, [selection]) == [receipt]
    assert len(archive.load_bound_receipts(root)) == 2
    assert archive.prepare(root, archive.load_bound_receipts(root))["status"] == "blocked"
    assert (
        archive.prepare(root, archive.load_bound_receipts(root, [selection]))["status"]
        == "verified"
    )


@pytest.mark.parametrize(
    "change", ["unknown_id", "url", "size", "checksum", "extra", "missing", "nested", "bool_number"]
)
def test_selected_full_row_must_be_unchanged(
    canonical_case: tuple[Path, dict[str, Any], str],
    change: str,
) -> None:
    root, receipt, selection = canonical_case
    edited = json.loads(json.dumps(receipt))
    if change == "unknown_id":
        edited["id"] = "au_pbs_invented"
    elif change == "url":
        edited["source_url"] = receipt["source_url"].replace("2020/01", "2020/02")
    elif change == "size":
        edited["byte_size"] += 1
    elif change == "checksum":
        edited["checksum_sha256"] = "a" * 64
    elif change == "extra":
        edited["invented_provenance"] = "not acquired"
    elif change == "missing":
        del edited["retrieval_metadata"]
    else:
        edited["retrieval_metadata"]["checked"] = 1 if change == "bool_number" else False
    (root / selection).write_text(json.dumps(edited) + "\n")
    with pytest.raises(archive.ArchiveError, match="selection_not_canonical"):
        archive.load_bound_receipts(root, [selection])


@pytest.mark.parametrize("mode", ["--stage", "--readback"])
def test_cli_rejects_self_consistent_arbitrary_payload_selection(
    canonical_case: tuple[Path, dict[str, Any], str],
    mode: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root, receipt, selection = canonical_case
    arbitrary = b"Not an acquired PBS payload\n"
    cache = f"{archive.RAW}/pbs_archive/invented.pdf"
    (root / cache).write_bytes(arbitrary)
    edited = {
        **receipt,
        "cache_path": cache,
        "byte_size": len(arbitrary),
        "checksum_sha256": hashlib.sha256(arbitrary).hexdigest(),
    }
    (root / selection).write_text(json.dumps(edited) + "\n")
    monkeypatch.setattr(
        "sys.argv",
        ["prepare", "--root", str(root), "--receipts", selection, mode, "data/local/stage"],
    )
    assert archive.main() == 1
    output = capsys.readouterr().out
    assert json.loads(output)["status"] == "blocked"
    assert json.loads(output)["publication_state"] == "not_asserted"
    assert str(root) not in output
    assert not (root / "data/local/stage").exists()


@pytest.mark.parametrize("missing", archive.DEFAULT_RECEIPTS)
def test_selection_requires_every_canonical_collection(
    canonical_case: tuple[Path, dict[str, Any], str],
    missing: str,
) -> None:
    root, _, selection = canonical_case
    (root / missing).unlink()
    with pytest.raises(FileNotFoundError):
        archive.load_bound_receipts(root, [selection])


@pytest.mark.parametrize("conflicting", [False, True])
def test_duplicate_canonical_identity_blocks_even_an_unselected_row(
    canonical_case: tuple[Path, dict[str, Any], str],
    conflicting: bool,
) -> None:
    root, receipt, selection = canonical_case
    duplicate: dict[str, Any] = {**receipt, "id": "au_pbs_missing", "status": "download_failed"}
    if conflicting:
        duplicate["byte_size"] += 1
    (root / archive.DEFAULT_RECEIPTS[2]).write_text(json.dumps(duplicate) + "\n")
    with pytest.raises(archive.ArchiveError, match="duplicate_canonical_receipt_identity"):
        archive.load_bound_receipts(root, [selection])


def test_repeated_selected_identity_across_files_is_rejected(
    canonical_case: tuple[Path, dict[str, Any], str],
) -> None:
    root, _, selection = canonical_case
    with pytest.raises(archive.ArchiveError, match="duplicate_selected_receipt_identity"):
        archive.load_bound_receipts(root, [selection, selection])


@pytest.mark.parametrize("canonical", [False, True])
@pytest.mark.parametrize("prefix", [True, False])
def test_selection_binding_rejects_duplicate_json_keys_in_both_sources(
    canonical_case: tuple[Path, dict[str, Any], str],
    canonical: bool,
    prefix: bool,
) -> None:
    root, receipt, selection = canonical_case
    content = json.dumps(receipt)
    content = (
        '{"status":"download_failed",' + content[1:]
        if prefix
        else content[:-1] + ',"status":"download_failed"}'
    )
    path = archive.DEFAULT_RECEIPTS[0] if canonical else selection
    (root / path).write_text(content + "\n")
    with pytest.raises(archive.ArchiveError, match="duplicate_json_key"):
        archive.load_bound_receipts(root, [selection])


@pytest.mark.parametrize("mode", ["stage", "readback"])
def test_bound_cli_preserves_manifest_bytes(
    canonical_case: tuple[Path, dict[str, Any], str],
    mode: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root, receipt, selection = canonical_case
    expected = archive.prepare(root, [receipt], stage="data/local/existing-stage")
    manifest = root / "data/local/existing-stage/raw/pbs/manifest.json"
    before = manifest.read_bytes()
    monkeypatch.setattr(
        "sys.argv",
        [
            "prepare",
            "--root",
            str(root),
            "--receipts",
            selection,
            f"--{mode}",
            "data/local/existing-stage" if mode == "readback" else "data/local/new-stage",
        ],
    )
    assert archive.main() == 0
    assert json.loads(capsys.readouterr().out) == {**expected, "mode": mode}
    assert manifest.read_bytes() == before
    if mode == "stage":
        assert (root / "data/local/new-stage/raw/pbs/manifest.json").read_bytes() == before


def test_documented_cli_uses_the_prepared_selection() -> None:
    doc = (Path(__file__).resolve().parents[2] / "docs/PBS_RAW_ARCHIVE_STAGING.md").read_text()
    assert "pbs-eligible-receipts.jsonl" not in doc
    assert doc.count("--receipts data/local/pbs-raw-archive-selected-20260831T044559Z.jsonl") == 2


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
    assert result["files"][0]["original_source_filename"] == "2020-01-01-xml-V3.zip"
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
    assert result["coverage"]["failed_receipts"] == 0
    assert result["coverage"]["failed_operations"] == 1
    assert result["coverage"]["complete_for_requested_batch"] is False
    assert result["coverage"]["verified_files"] == 1
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


def test_permission_checksum_binds_complete_record_bytes(case: tuple[Path, dict[str, Any]]) -> None:
    root, receipt = case
    permission = root / archive.PERMISSION
    original = permission.read_bytes()
    result = archive.prepare(root, [receipt])
    assert result["permission_record_checksum_sha256"] == hashlib.sha256(original).hexdigest()
    assert result["permission_record"] == archive.PERMISSION
    assert result["publication_state"] == "not_asserted"

    # Even JSON whitespace changes affect the binding: hash exact complete bytes,
    # not a selected subset of permission fields or reserialized JSON.
    permission.write_bytes(original + b"\n ")
    staged = archive.prepare(root, [receipt], stage="data/local/stage")
    checksum = hashlib.sha256(permission.read_bytes()).hexdigest()
    assert staged["permission_record_checksum_sha256"] == checksum
    assert checksum != result["permission_record_checksum_sha256"]
    manifest = json.loads((root / "data/local/stage/raw/pbs/manifest.json").read_text())
    assert manifest == staged
    verified = archive.prepare(root, [receipt], readback="data/local/stage")
    assert verified["permission_record_checksum_sha256"] == checksum
    assert verified["publication_state"] == "not_asserted"
    assert str(root) not in archive.serialize(staged)


def test_original_source_filename_retained(case: tuple[Path, dict[str, Any]]) -> None:
    root, receipt = case
    filename = "2020-01-01-general-schedule.PDF"
    receipt["file_name"] = filename
    receipt["source_url"] = (
        f"https://www.pbs.gov.au/publication/schedule/2020/01/{filename}?variant=3"
    )
    result = archive.prepare(root, [receipt], stage="data/local/stage")
    assert result["status"] == "verified"
    row = result["files"][0]
    assert row["original_source_filename"] == filename
    assert row["archive_path"].endswith(".pdf")
    assert receipt["cache_path"].split("/")[-1] != filename
    manifest = json.loads((root / "data/local/stage/raw/pbs/manifest.json").read_text())
    assert manifest["files"][0]["original_source_filename"] == filename


def test_conflicting_source_filename_fails_closed(case: tuple[Path, dict[str, Any]]) -> None:
    root, receipt = case
    receipt["file_name"] = "different-schedule.pdf"
    assert error(root, receipt) == "source_filename_mismatch"


def test_blocked_batch_does_not_assert_permission_checksum(
    case: tuple[Path, dict[str, Any]],
) -> None:
    root, receipt = case
    (root / archive.PERMISSION).unlink()
    result = archive.prepare(root, [receipt])
    assert result["status"] == "blocked"
    assert result["permission_record_checksum_sha256"] is None


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize(
    ("key", "other"),
    [
        ("status", "download_failed"),
        ("source_id", "au_mbs"),
        ("byte_size", 0),
        ("checksum_sha256", "0" * 64),
        ("cache_path", "data/raw_live/../../secret"),
        ("archive_digest_verified", False),
    ],
)
def test_duplicate_receipt_keys_rejected_in_both_orders(
    case: tuple[Path, dict[str, Any]],
    key: str,
    other: Any,
    reverse: bool,
) -> None:
    root, receipt = case
    receipt["archive_digest_verified"] = True
    duplicate = f"{json.dumps(key)}:{json.dumps(other)}"
    body = json.dumps(receipt)[1:-1]
    content = "{" + (f"{duplicate},{body}" if reverse else f"{body},{duplicate}") + "}\n"
    (root / "receipts.jsonl").write_text(content)
    with pytest.raises(archive.ArchiveError, match="duplicate_json_key"):
        archive.load_receipts(root, ["receipts.jsonl"])


@pytest.mark.parametrize(
    "content",
    [
        '{"metadata":{"status":"failed","status":"cached"}}',
        '{"metadata":{"status":"cached","status":"failed"}}',
        '{"status":"cached","sta\\u0074us":"cached"}',
    ],
)
def test_duplicate_nested_or_escaped_keys_rejected(tmp_path: Path, content: str) -> None:
    (tmp_path / "receipts.jsonl").write_text(content)
    with pytest.raises(archive.ArchiveError, match="duplicate_json_key"):
        archive.load_receipts(tmp_path, ["receipts.jsonl"])


def test_cli_duplicate_keys_do_not_stage(
    case: tuple[Path, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root, receipt = case
    (root / "receipts.jsonl").write_text('{"status":"download_failed",' + json.dumps(receipt)[1:])
    monkeypatch.setattr(
        "sys.argv",
        [
            "prepare",
            "--root",
            str(root),
            "--receipts",
            "receipts.jsonl",
            "--stage",
            "data/local/stage",
        ],
    )
    assert archive.main() == 1
    assert json.loads(capsys.readouterr().out)["status"] == "blocked"
    assert not (root / "data/local/stage").exists()


def assert_readback_blocked(result: dict[str, Any], error: str) -> None:
    assert result["status"] == "blocked"
    assert result["errors"] == [{"id": "batch", "error": error}]
    assert result["coverage"]["failed_receipts"] == 0
    assert result["coverage"]["failed_operations"] == 1
    assert result["coverage"]["complete_for_requested_batch"] is False
    assert result["publication_state"] == "not_asserted"


def test_readback_missing_manifest(case: tuple[Path, dict[str, Any]]) -> None:
    root, receipt = case
    archive.prepare(root, [receipt], stage="data/local/stage")
    (root / "data/local/stage/raw/pbs/manifest.json").unlink()
    assert_readback_blocked(
        archive.prepare(root, [receipt], readback="data/local/stage"), "readback_manifest_missing"
    )


@pytest.mark.parametrize(
    "field",
    [
        "attribution",
        "permission_record_checksum_sha256",
        "publication_state",
        "source_url",
        "original_source_filename",
        "checksum_sha256",
        "coverage",
        "extra_key",
        "file_order",
    ],
)
def test_readback_tampered_manifest(case: tuple[Path, dict[str, Any]], field: str) -> None:
    root, receipt = case
    receipts = [receipt, {**receipt, "id": "au_pbs_other"}]
    manifest = archive.prepare(root, receipts, stage="data/local/stage")
    if field in {"source_url", "original_source_filename", "checksum_sha256"}:
        manifest["files"][0][field] = "tampered"
    elif field == "coverage":
        manifest["coverage"]["complete_for_requested_batch"] = 1
    elif field == "file_order":
        manifest["files"].reverse()
    else:
        manifest[field] = "tampered"
    (root / "data/local/stage/raw/pbs/manifest.json").write_text(archive.serialize(manifest))
    assert_readback_blocked(
        archive.prepare(root, receipts, readback="data/local/stage"), "readback_manifest_mismatch"
    )


def test_readback_binds_current_complete_permission_record(
    case: tuple[Path, dict[str, Any]],
) -> None:
    root, receipt = case
    archive.prepare(root, [receipt], stage="data/local/stage")
    path = root / archive.PERMISSION
    path.write_bytes(path.read_bytes() + b"\n")
    assert_readback_blocked(
        archive.prepare(root, [receipt], readback="data/local/stage"), "readback_manifest_mismatch"
    )


@pytest.mark.parametrize("reverse", [False, True])
def test_readback_rejects_duplicate_manifest_keys(
    case: tuple[Path, dict[str, Any]],
    reverse: bool,
) -> None:
    root, receipt = case
    manifest = archive.prepare(root, [receipt], stage="data/local/stage")
    body = json.dumps(manifest)[1:-1]
    duplicate = '"publication_state":"published"'
    content = "{" + (f"{duplicate},{body}" if reverse else f"{body},{duplicate}") + "}"
    (root / "data/local/stage/raw/pbs/manifest.json").write_text(content)
    assert_readback_blocked(
        archive.prepare(root, [receipt], readback="data/local/stage"), "duplicate_json_key"
    )


@pytest.mark.parametrize("extra", ["extra.txt", "raw/pbs/extra.txt", "raw/pbs/payloads/extra.txt"])
def test_readback_rejects_extra_files(case: tuple[Path, dict[str, Any]], extra: str) -> None:
    root, receipt = case
    archive.prepare(root, [receipt], stage="data/local/stage")
    (root / "data/local/stage" / extra).write_text("not in manifest")
    assert_readback_blocked(
        archive.prepare(root, [receipt], readback="data/local/stage"), "readback_inventory_mismatch"
    )


@pytest.mark.parametrize("kind", ["manifest_symlink", "extra_symlink", "extra_directory"])
def test_readback_rejects_unsafe_inventory(case: tuple[Path, dict[str, Any]], kind: str) -> None:
    root, receipt = case
    archive.prepare(root, [receipt], stage="data/local/stage")
    directory = root / "data/local/stage"
    if kind == "manifest_symlink":
        path = directory / "raw/pbs/manifest.json"
        backup = root / "manifest-backup.json"
        path.rename(backup)
        path.symlink_to(backup)
    elif kind == "extra_symlink":
        (directory / "extra").symlink_to(root, target_is_directory=True)
    else:
        (directory / "extra").mkdir()
    expected = "readback_inventory_mismatch" if kind == "extra_directory" else "symlink_path"
    assert_readback_blocked(archive.prepare(root, [receipt], readback="data/local/stage"), expected)


def test_readback_accepts_manifest_whitespace_only(case: tuple[Path, dict[str, Any]]) -> None:
    root, receipt = case
    staged = archive.prepare(root, [receipt], stage="data/local/stage")
    (root / "data/local/stage/raw/pbs/manifest.json").write_text(json.dumps(staged))
    result = archive.prepare(root, [receipt], readback="data/local/stage")
    assert result["status"] == "verified"
    assert result["coverage"]["failed_operations"] == 0


@pytest.mark.parametrize("mutation", ["missing", "tampered"])
def test_readback_requires_bound_archive_readme(
    case: tuple[Path, dict[str, Any]],
    mutation: str,
) -> None:
    root, receipt = case
    result = archive.prepare(root, [receipt], stage="data/local/stage")
    readme = root / "data/local/stage/raw/pbs/README.md"
    assert (
        result["archive_readme_checksum_sha256"] == hashlib.sha256(readme.read_bytes()).hexdigest()
    )
    assert "not an independently verified" in readme.read_text()
    if mutation == "missing":
        readme.unlink()
    else:
        readme.write_text("Published without gaps")
    assert_readback_blocked(
        archive.prepare(root, [receipt], readback="data/local/stage"), "readback_readme_mismatch"
    )


@pytest.fixture
def scheme_variant(case: tuple[Path, dict[str, Any]]) -> tuple[Path, list[dict[str, Any]]]:
    root, parent = case
    original = parent["source_url"].split("?")[0].replace("https://", "http://", 1)
    payload = (root / parent["cache_path"]).read_bytes()
    digest = base64.b32encode(hashlib.sha1(payload, usedforsecurity=False).digest()).decode()
    stamp = "20200101000000"
    variant = {
        **parent,
        "id": "au_pbs_http_variant",
        "source_id": parent["id"],
        "official_source_url": parent["source_url"].split("?")[0],
        "archive_timestamp": stamp,
        "archive_replay_url": f"https://web.archive.org/web/{stamp}id_/{original}",
        "archive_digest_verified": True,
        "archive_checksum_sha1_base32": digest,
        "checksum_sha1_base32": digest,
    }
    observation = {
        "original": original,
        "timestamp": stamp,
        "digest": digest,
        "statuscode": "200",
        "mimetype": "application/pdf",
        "length": "123",
    }
    cdx = root / archive.CDX_OBSERVATIONS
    cdx.parent.mkdir(parents=True)
    cdx.write_text(json.dumps(observation) + "\n")
    return root, [parent, variant]


def test_scheme_difference_requires_exact_cdx_and_actual_digests(
    scheme_variant: tuple[Path, list[dict[str, Any]]],
) -> None:
    root, receipts = scheme_variant
    result = archive.prepare(root, receipts, stage="data/local/stage")
    assert result["status"] == "verified"
    row = next(item for item in result["files"] if "archive_original_url" in item)
    assert row["archive_original_url"].startswith("http://")
    assert row["source_url"].startswith("https://")
    assert row["archive_identity_basis"] == "exact_cdx_capture_and_payload_digests"
    observation = json.loads((root / archive.CDX_OBSERVATIONS).read_text())
    assert (
        row["archive_cdx_observation_checksum_sha256"]
        == hashlib.sha256(archive.serialize(observation).encode()).hexdigest()
    )
    assert archive.prepare(root, receipts, readback="data/local/stage")["status"] == "verified"


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_cdx",
        "duplicate_capture",
        "timestamp",
        "original",
        "digest",
        "statuscode",
        "mimetype",
        "receipt_digest",
        "payload_digest",
        "host",
        "path",
        "query",
    ],
)
def test_scheme_difference_is_not_blind_normalization(
    scheme_variant: tuple[Path, list[dict[str, Any]]],
    mutation: str,
) -> None:
    root, receipts = scheme_variant
    parent, variant = receipts
    path = root / archive.CDX_OBSERVATIONS
    observation = json.loads(path.read_text())
    if mutation == "missing_cdx":
        path.unlink()
    elif mutation == "duplicate_capture":
        path.write_text(path.read_text() * 2)
    elif mutation in {"timestamp", "original", "digest", "statuscode", "mimetype"}:
        observation[mutation] = "invalid"
        path.write_text(json.dumps(observation))
    elif mutation == "receipt_digest":
        variant["checksum_sha1_base32"] = "A" * 32
    elif mutation == "payload_digest":
        payload = b"%PDF-1.7 different bytes with a self-consistent SHA256 receipt"
        (root / parent["cache_path"]).write_bytes(payload)
        for receipt in receipts:
            receipt.update(
                byte_size=len(payload), checksum_sha256=hashlib.sha256(payload).hexdigest()
            )
    else:
        old, new = {
            "host": ("www.pbs.gov.au", "m.pbs.gov.au"),
            "path": ("general-schedule.pdf", "dental-book.pdf"),
            "query": ("general-schedule.pdf", "general-schedule.pdf?variant=3"),
        }[mutation]
        variant["archive_replay_url"] = variant["archive_replay_url"].replace(old, new)
    result = archive.prepare(root, receipts, stage="data/local/stage")
    assert result["status"] == "blocked"
    assert not (root / "data/local/stage").exists()
    assert result["publication_state"] == "not_asserted"
