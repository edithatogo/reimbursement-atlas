"""Manual acquisition-pack generation for licence-aware source validation."""

from __future__ import annotations

import json
import shlex
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.models import SourceFileRecord

RawHandling = Literal["local_raw_only", "metadata_only", "public_derived_only"]


@dataclass(frozen=True)
class ManualAcquisitionStep:
    """One reviewed-source acquisition step for a human or future agent."""

    step_id: str
    source_file_id: str
    source_id: str
    source_version_id: str
    file_label: str
    source_url: str
    acquisition_mode: str
    licence_gate: str
    expected_format: str
    suggested_local_path: str
    raw_handling: RawHandling
    snapshot_command: str
    parse_command: str
    notes: str

    def as_row(self) -> dict[str, object]:
        """Return a JSON/CSV-safe representation."""
        return asdict(self)


def build_manual_acquisition_steps(
    source_files: list[SourceFileRecord],
    *,
    raw_root: Path = Path("data/raw_live"),
    derived_root: Path = Path("data/derived/reviewed_sources"),
) -> list[ManualAcquisitionStep]:
    """Build ordered manual acquisition steps from exact source-file records."""
    steps: list[ManualAcquisitionStep] = []
    for index, record in enumerate(source_files, start=1):
        suggested_path = raw_root / record.source_id / record.file_name
        raw_handling = _raw_handling(record)
        snapshot_command = _snapshot_command(record, suggested_path)
        parse_command = _parse_command(record, suggested_path, derived_root)
        steps.append(
            ManualAcquisitionStep(
                step_id=f"step_{index:03d}",
                source_file_id=record.id,
                source_id=record.source_id,
                source_version_id=record.source_version_id,
                file_label=record.file_label,
                source_url=str(record.source_url),
                acquisition_mode=record.acquisition_mode,
                licence_gate=record.licence_gate,
                expected_format=record.expected_format,
                suggested_local_path=str(suggested_path),
                raw_handling=raw_handling,
                snapshot_command=snapshot_command,
                parse_command=parse_command,
                notes=_step_notes(record, raw_handling),
            )
        )
    return steps


def write_manual_acquisition_pack(
    steps: list[ManualAcquisitionStep],
    *,
    output_dir: Path,
) -> tuple[Path, Path, Path, Path]:
    """Write JSONL, CSV, README and shell-command manual acquisition pack."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = [step.as_row() for step in steps]
    jsonl_path = write_jsonl(rows, output_dir / "acquisition_steps.jsonl")
    csv_path = write_csv(rows, output_dir / "acquisition_steps.csv")
    readme_path = output_dir / "README.md"
    readme_path.write_text(_readme(steps), encoding="utf-8")
    shell_path = output_dir / "source_file_commands.sh"
    shell_path.write_text(_shell_commands(steps), encoding="utf-8")
    return jsonl_path, csv_path, readme_path, shell_path


def acquisition_pack_summary(steps: list[ManualAcquisitionStep]) -> dict[str, object]:
    """Return small summary metrics for dashboards and logs."""
    by_handling: dict[str, int] = {}
    by_gate: dict[str, int] = {}
    for step in steps:
        by_handling[step.raw_handling] = by_handling.get(step.raw_handling, 0) + 1
        by_gate[step.licence_gate] = by_gate.get(step.licence_gate, 0) + 1
    return {
        "step_count": len(steps),
        "raw_handling_counts": by_handling,
        "licence_gate_counts": by_gate,
    }


def _raw_handling(record: SourceFileRecord) -> RawHandling:
    if record.file_role in {"landing_page", "licence_gate", "api_endpoint"}:
        return "metadata_only"
    if record.licence_gate == "permissive_candidate":
        return "public_derived_only"
    return "local_raw_only"


def _snapshot_command(record: SourceFileRecord, suggested_path: Path) -> str:
    if _raw_handling(record) == "metadata_only":
        return "# Metadata-only record; review the landing page or endpoint before downloading."
    return " ".join([
        "reimbursement-atlas",
        "snapshot-local-file",
        "--source-version-id",
        shlex.quote(record.source_version_id),
        "--content-type",
        shlex.quote(_content_type(record.expected_format)),
        shlex.quote(str(suggested_path)),
    ])


def _parse_command(record: SourceFileRecord, suggested_path: Path, derived_root: Path) -> str:
    if "parse_mbs_txt_pair" in record.parser_hint:
        return (
            "# Bundle after both MBS TXT files are present: reimbursement-atlas "
            "reviewed-mbs-txt-pair-bundle "
            "data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT "
            "data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT "
            f"--output-dir {shlex.quote(str(derived_root / 'au_mbs_20260701_txt_pair'))}"
        )
    if _raw_handling(record) == "metadata_only":
        return "# No parser runs for metadata-only landing/API records."
    return " ".join([
        "reimbursement-atlas",
        "parse-local-source",
        "--source-version-id",
        shlex.quote(record.source_version_id),
        shlex.quote(str(suggested_path)),
        "--output-dir",
        shlex.quote(str(derived_root / record.source_version_id)),
    ])


def _content_type(expected_format: str) -> str:
    lowered = expected_format.lower()
    if "csv" in lowered:
        return "text/csv"
    if "xml" in lowered:
        return "application/xml"
    if "txt" in lowered or "text" in lowered:
        return "text/plain"
    if "zip" in lowered:
        return "application/zip"
    return "application/octet-stream"


def _step_notes(record: SourceFileRecord, raw_handling: RawHandling) -> str:
    base = record.notes
    if raw_handling == "metadata_only":
        return f"{base} This acquisition-pack row is metadata-only until a human accepts any gate."
    if raw_handling == "local_raw_only":
        return f"{base} Keep the raw file outside git; commit only derived rows and snapshots."
    return (
        f"{base} Treat raw redistribution as a separate licence review even if "
        "derived output is public."
    )


def _readme(steps: list[ManualAcquisitionStep]) -> str:
    summary = acquisition_pack_summary(steps)
    lines = [
        "# Manual acquisition pack",
        "",
        "This folder turns exact source-file records into a reviewed download checklist.",
        "Raw files should remain under `data/raw_live/`, which is ignored by git.",
        "",
        "```json",
        json.dumps(summary, indent=2, sort_keys=True),
        "```",
        "",
        "## Workflow",
        "",
        "1. Review the source URL and licence gate for each row.",
        "2. Save permitted raw files to the suggested local path.",
        "3. Run the snapshot command before parsing.",
        "4. Parse into derived rows and run the public-data policy check.",
        "",
        "## Steps",
        "",
    ]
    for step in steps:
        lines.extend([
            f"### {step.step_id}: {step.file_label}",
            "",
            f"- Source file id: `{step.source_file_id}`",
            f"- URL: {step.source_url}",
            f"- Raw handling: `{step.raw_handling}`",
            f"- Suggested local path: `{step.suggested_local_path}`",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def _shell_commands(steps: list[ManualAcquisitionStep]) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Review URLs/licences manually before downloading. Do not commit raw files.",
        "",
    ]
    for step in steps:
        lines.extend([
            f"# {step.step_id}: {step.file_label}",
            f"# URL: {step.source_url}",
            f"mkdir -p {shlex.quote(str(Path(step.suggested_local_path).parent))}",
            f"# Snapshot: {step.snapshot_command}",
            f"# Parse: {step.parse_command}",
            "",
        ])
    return "\n".join(lines)
