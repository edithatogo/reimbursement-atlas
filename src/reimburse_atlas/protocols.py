"""Protocol and report completeness checks for OSF-aligned research questions."""

from __future__ import annotations

import json
import re
from pathlib import Path

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.models import ProtocolStatusRecord, ResearchQuestionRecord
from reimburse_atlas.registry import project_root

REQUIRED_PROTOCOL_SECTIONS = (
    "background",
    "research question",
    "datasets",
    "inclusion",
    "analysis plan",
    "bias",
    "outputs",
    "osf",
)


def _normalised_headings(text: str) -> set[str]:
    """Return normalised Markdown headings for a protocol/report document."""
    headings: set[str] = set()
    for line in text.splitlines():
        if not line.lstrip().startswith("#"):
            continue
        heading = re.sub(r"^#+\s*", "", line.strip()).lower()
        heading = re.sub(r"[^a-z0-9]+", " ", heading).strip()
        if heading:
            headings.add(heading)
    return headings


def _word_count(text: str) -> int:
    """Count simple word tokens in Markdown text."""
    return len(re.findall(r"\b\w+\b", text))


def _section_present(required: str, headings: set[str], text: str) -> bool:
    """Return whether a required section appears in headings or body text."""
    if any(required in heading for heading in headings):
        return True
    return required in text.lower()


def build_protocol_status(
    questions: list[ResearchQuestionRecord],
    *,
    root: Path | None = None,
) -> list[ProtocolStatusRecord]:
    """Build protocol/report completeness status records."""
    repo_root = root or project_root()
    rows: list[ProtocolStatusRecord] = []
    for question in questions:
        protocol_path = repo_root / question.protocol_path
        report_path = repo_root / question.report_path
        protocol_text = protocol_path.read_text(encoding="utf-8") if protocol_path.exists() else ""
        report_text = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
        headings = _normalised_headings(protocol_text)
        missing = tuple(
            section
            for section in REQUIRED_PROTOCOL_SECTIONS
            if not _section_present(section, headings, protocol_text)
        )
        section_count = len(REQUIRED_PROTOCOL_SECTIONS)
        present_count = section_count - len(missing)
        protocol_word_count = _word_count(protocol_text)
        report_word_count = _word_count(report_text)
        score = (
            0.55 * (present_count / section_count)
            + 0.20 * min(protocol_word_count / 1200, 1.0)
            + 0.15 * min(report_word_count / 800, 1.0)
            + 0.10 * (1.0 if question.preregistration_status in {"drafted", "registered"} else 0.0)
        )
        osf_ready = (
            protocol_path.exists()
            and report_path.exists()
            and not missing
            and protocol_word_count >= 1200
            and question.preregistration_status in {"drafted", "registered"}
        )
        if not protocol_path.exists():
            next_step = "Create protocol scaffold."
        elif missing:
            next_step = f"Complete missing protocol sections: {', '.join(missing)}."
        elif protocol_word_count < 1200:
            next_step = "Expand protocol detail before OSF preregistration."
        elif question.preregistration_status == "planned":
            next_step = "Mark protocol as drafted after human review."
        else:
            next_step = "Ready for OSF component upload and preregistration review."
        rows.append(
            ProtocolStatusRecord(
                id=f"protocol_status_{question.id}",
                research_question_id=question.id,
                protocol_path=question.protocol_path,
                report_path=question.report_path,
                protocol_exists=protocol_path.exists(),
                report_exists=report_path.exists(),
                required_section_count=section_count,
                present_section_count=present_count,
                missing_sections=missing,
                protocol_word_count=protocol_word_count,
                report_word_count=report_word_count,
                completeness_score=round(score, 4),
                osf_ready=osf_ready,
                recommended_next_step=next_step,
            )
        )
    return rows


def protocol_summary(rows: list[ProtocolStatusRecord]) -> dict[str, object]:
    """Summarise generated protocol status records."""
    ready = sum(1 for row in rows if row.osf_ready)
    return {
        "protocol_count": len(rows),
        "osf_ready_count": ready,
        "average_completeness_score": round(
            sum(row.completeness_score for row in rows) / len(rows), 4
        )
        if rows
        else 0.0,
        "blocking_missing_section_count": sum(len(row.missing_sections) for row in rows),
    }


def write_protocol_status(
    rows: list[ProtocolStatusRecord],
    *,
    output_dir: Path,
) -> tuple[Path, Path, Path]:
    """Write protocol status rows and summary."""
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = [row.model_dump(mode="json") for row in rows]
    jsonl_path = write_jsonl(payload, output_dir / "protocol_status.jsonl")
    csv_path = write_csv(payload, output_dir / "protocol_status.csv")
    summary_path = output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(protocol_summary(rows), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return jsonl_path, csv_path, summary_path
