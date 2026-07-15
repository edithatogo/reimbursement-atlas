"""Tests for derived-only reviewed MBS TXT pair bundles."""

from __future__ import annotations

import json
from pathlib import Path

from reimburse_atlas.local_sources import build_mbs_txt_pair_bundle
from reimburse_atlas.registry import project_root


def test_build_mbs_txt_pair_bundle(tmp_path: Path) -> None:
    """The MBS pair bundle snapshots both files and emits derived-only rows."""
    fixtures = project_root() / "tests" / "fixtures" / "mbs_txt"
    result = build_mbs_txt_pair_bundle(
        item_map_path=fixtures / "20260701_MBSONLINE_IMAP_fixture.TXT",
        descriptor_path=fixtures / "20260701_MBSONLINE_DESC_fixture.TXT",
        output_dir=tmp_path,
        retrieved_at="2026-07-04T00:00:00+10:00",
    )

    assert result.source_id == "au_mbs"
    assert result.source_version_id == "au_mbs_20260701_txt_pair"
    assert result.record_count == 3
    assert result.item_map_snapshot_id.startswith("snapshot_au_mbs_20260701_txt_pair_item_map")
    assert result.descriptor_snapshot_id.startswith("snapshot_au_mbs_20260701_txt_pair_descriptor")
    assert result.parsed_jsonl_path.exists()
    assert result.parsed_csv_path.exists()
    assert result.snapshot_jsonl_path.exists()
    snapshot_text = result.snapshot_jsonl_path.read_text(encoding="utf-8")
    assert "20260701_MBSONLINE_IMAP_fixture" not in snapshot_text
    assert '"local_path": null' in snapshot_text

    report = json.loads(result.validation_report_path.read_text(encoding="utf-8"))
    assert report["raw_files_copied_to_bundle"] is False
    assert report["stats"]["joined_rows"] == 2
    assert report["stats"]["descriptor_only_rows"] == 1
    assert "Descriptor-only rows" in " ".join(report["quality_warnings"])

    manifest = json.loads(result.publication_manifest_path.read_text(encoding="utf-8"))
    assert manifest["raw_files_copied"] is False
    assert manifest["record_count"] == 3
    assert len(manifest["snapshot_ids"]) == 2


def test_mbs_pair_bundle_uses_download_sidecar_timestamp(tmp_path: Path) -> None:
    """Sidecar provenance keeps repeated derived bundle generation deterministic."""
    fixtures = project_root() / "tests" / "fixtures" / "mbs_txt"
    item_map = tmp_path / "item_map.TXT"
    descriptor = tmp_path / "descriptor.TXT"
    item_map.write_text(
        (fixtures / "20260701_MBSONLINE_IMAP_fixture.TXT").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    descriptor.write_text(
        (fixtures / "20260701_MBSONLINE_DESC_fixture.TXT").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    sidecar = {"attempted_at": "2026-07-14T14:10:48.615832+00:00"}
    (tmp_path / "item_map.TXT.metadata.json").write_text(json.dumps(sidecar), encoding="utf-8")
    (tmp_path / "descriptor.TXT.metadata.json").write_text(json.dumps(sidecar), encoding="utf-8")

    result = build_mbs_txt_pair_bundle(
        item_map_path=item_map,
        descriptor_path=descriptor,
        output_dir=tmp_path / "bundle",
    )

    rows = [json.loads(line) for line in result.snapshot_jsonl_path.read_text().splitlines()]
    assert {row["retrieved_at"] for row in rows} == {sidecar["attempted_at"]}
