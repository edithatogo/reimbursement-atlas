"""Historical acquisition aliases require matching immutable evidence."""

import json
from pathlib import Path
from typing import Any

import pytest

from reimburse_atlas.historical_source_reconciliation import build_reconciliation


def _write(root: Path, name: str, rows: list[dict[str, Any]]) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


@pytest.fixture
def frame(tmp_path: Path) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    target = {"id": "target", "source_id": "au_mbs", "file_name": "20260701_MBSONLINE_IMAP.TXT"}
    source = dict(target, id="au_mbs_20260701_imap_txt", source_version_id="v1")
    snapshot = {
        "id": "snapshot",
        "source_id": "au_mbs",
        "source_version_id": "v1",
        "checksum_sha256": "a" * 64,
        "byte_size": 100,
    }
    validation = dict(
        snapshot,
        source_file_id=source["id"],
        validation_status="pass",
        local_target_ref="reviewed_bundle:data/derived/reviewed_source_bundles/test",
    )
    _write(tmp_path, "data/seed/source_files.jsonl", [source])
    _write(tmp_path, "data/derived/source_validation/source_content_validation.jsonl", [validation])
    _write(tmp_path, "data/derived/reviewed_source_bundles/test/source_snapshots.jsonl", [snapshot])
    _write(
        tmp_path,
        "data/derived/historical_sources/historical_source_downloads.jsonl",
        [
            dict(target, status="upstream_unavailable"),
        ],
    )
    return tmp_path, target, snapshot


def test_reconciles_without_rewriting_failure(
    frame: tuple[Path, dict[str, Any], dict[str, Any]],
) -> None:
    root, target, _ = frame
    receipt = root / "data/derived/historical_sources/historical_source_downloads.jsonl"
    before = receipt.read_bytes()
    result = build_reconciliation(root, [target])
    assert result == build_reconciliation(root, [target])
    assert result["acquisition_evidenced_target_count"] == 1
    assert result["direct_download_receipt_count"] == 0
    assert result["reviewed_snapshot_alias_count"] == 1
    assert result["current_raw_availability"] == "not_asserted"
    assert result["publication_effect"] == "none"
    assert receipt.read_bytes() == before
    assert str(root) not in json.dumps(result)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("checksum_sha256", "b" * 64),
        ("byte_size", 101),
        ("source_id", "another"),
        ("source_version_id", "v2"),
    ],
)
def test_mismatch_fails_closed(
    frame: tuple[Path, dict[str, Any], dict[str, Any]],
    field: str,
    value: object,
) -> None:
    root, target, snapshot = frame
    snapshot[field] = value
    _write(root, "data/derived/reviewed_source_bundles/test/source_snapshots.jsonl", [snapshot])
    assert build_reconciliation(root, [target])["unresolved_target_ids"] == ["target"]


def test_missing_evidence_and_unknown_identity(tmp_path: Path) -> None:
    target = {"id": "unknown", "file_name": "unknown.TXT", "source_id": "au_mbs"}
    assert build_reconciliation(tmp_path, [target])["unresolved_target_ids"] == ["unknown"]
    with pytest.raises(ValueError, match="Duplicate"):
        build_reconciliation(tmp_path, [target, target])


def test_rejects_external_bundle(frame: tuple[Path, dict[str, Any], dict[str, Any]]) -> None:
    root, target, snapshot = frame
    validation = dict(
        snapshot,
        source_file_id="au_mbs_20260701_imap_txt",
        validation_status="pass",
        local_target_ref="reviewed_bundle:../../outside",
    )
    _write(root, "data/derived/source_validation/source_content_validation.jsonl", [validation])
    assert build_reconciliation(root, [target])["unresolved_target_ids"] == ["target"]


def test_issue_projection_preserves_precise_source_gap() -> None:
    root = Path(__file__).parents[2]
    draft = (
        root
        / ".github/generated-issues"
        / ("245-complete-residual-historical-mbs-pbs-acquisition-breadth-and-evidence-promotion.md")
    )
    text = draft.read_text(encoding="utf-8")
    assert "December 2006-March 2007 XML" in text
    assert "schema/DTD/XSL" in text
    assert "mbs_identity_reconciliation.json" in text
    assert "341 of 343 MBS targets are acquired" not in text


@pytest.mark.parametrize("changed", [None, "file_name", "source_id", "file_url"])
def test_direct_receipt_requires_full_identity(tmp_path: Path, changed: str | None) -> None:
    target = {
        "id": "direct",
        "source_id": "au_mbs",
        "file_name": "a.csv",
        "file_url": "https://www.mbsonline.gov.au/a.csv",
    }
    receipt = dict(
        target,
        status="downloaded",
        source_url=target["file_url"],
        checksum_sha256="a" * 64,
        byte_size=42,
    )
    if changed:
        target[changed] = "changed"
    _write(tmp_path, "data/derived/historical_sources/historical_source_downloads.jsonl", [receipt])
    result = build_reconciliation(tmp_path, [target])
    assert result["direct_download_receipt_count"] == (0 if changed else 1)
