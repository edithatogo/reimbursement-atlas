"""Tests for v9 manual acquisition-pack generation."""

from __future__ import annotations

from reimburse_atlas.acquisition_pack import (
    acquisition_pack_summary,
    build_manual_acquisition_steps,
)
from reimburse_atlas.registry import load_source_files


def test_manual_acquisition_steps_capture_mbs_pair_and_metadata_only() -> None:
    source_files = load_source_files()

    steps = build_manual_acquisition_steps(source_files)

    assert len(steps) == len(source_files)
    mbs_steps = [step for step in steps if step.source_id == "au_mbs"]
    assert mbs_steps
    assert any("reviewed-mbs-txt-pair-bundle" in step.parse_command for step in mbs_steps)
    metadata_steps = [step for step in steps if step.raw_handling == "metadata_only"]
    assert metadata_steps
    assert all(step.snapshot_command.startswith("# Metadata-only") for step in metadata_steps)


def test_acquisition_pack_summary_counts_steps() -> None:
    steps = build_manual_acquisition_steps(load_source_files())

    summary = acquisition_pack_summary(steps)

    assert summary["step_count"] == len(steps)
    assert "licence_gate_counts" in summary
    assert "raw_handling_counts" in summary


def test_write_manual_acquisition_pack_outputs_files(tmp_path) -> None:  # type: ignore[no-untyped-def]
    from reimburse_atlas.acquisition_pack import write_manual_acquisition_pack

    steps = build_manual_acquisition_steps(load_source_files()[:2])

    jsonl_path, csv_path, readme_path, shell_path = write_manual_acquisition_pack(
        steps,
        output_dir=tmp_path,
    )

    assert jsonl_path.exists()
    assert csv_path.exists()
    assert "Manual acquisition pack" in readme_path.read_text(encoding="utf-8")
    assert "reviewed-mbs-txt-pair-bundle" in shell_path.read_text(encoding="utf-8")
