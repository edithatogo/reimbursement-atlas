from __future__ import annotations

from pathlib import Path

from reimburse_atlas.models import SourceFileRecord
from reimburse_atlas.protocols import build_protocol_status, protocol_summary, write_protocol_status
from reimburse_atlas.registry import load_research_questions
from reimburse_atlas.source_downloads import build_download_plan, write_download_outputs


def _source_file(**overrides: object) -> SourceFileRecord:
    payload: dict[str, object] = {
        "id": "test_file_v15",
        "source_id": "au_mbs",
        "source_version_id": "au_mbs_seed_fixture",
        "file_label": "Test file",
        "file_name": "name with spaces and $danger.csv",
        "source_url": "https://example.org/test file.csv?x=$FILE&y=1",
        "file_role": "primary",
        "expected_format": "text/csv",
        "acquisition_mode": "api_rate_limited",
        "licence_gate": "permissive_candidate",
        "parser_hint": "fixture",
        "expected_record_count": 1,
        "current_observation": "fixture",
        "notes": "fixture",
    }
    payload.update(overrides)
    return SourceFileRecord.model_validate(payload)


def test_download_plan_uses_hardened_quoted_curl_command(tmp_path: Path) -> None:
    plan = build_download_plan(_source_file(), output_dir=tmp_path, preferred_method="curl")
    assert plan.should_execute
    assert "--retry-all-errors" in plan.command
    assert "--continue-at -" not in plan.command
    assert "--dump-header" in plan.command
    assert "--etag-save" in plan.command
    assert "Accept: application/json" in plan.command
    assert "'$FILE" not in plan.command
    assert not plan.supports_resume
    assert plan.captures_headers
    assert plan.metadata_path.endswith(".metadata.json")


def test_download_plan_uses_hardened_wget_command(tmp_path: Path) -> None:
    plan = build_download_plan(_source_file(), output_dir=tmp_path, preferred_method="wget")
    assert plan.should_execute
    assert "wget" in plan.command
    assert "--continue" not in plan.command
    assert "--server-response" in plan.command
    assert not plan.supports_resume
    assert not plan.captures_headers


def test_download_plan_can_opt_in_to_resume_support(tmp_path: Path) -> None:
    plan = build_download_plan(
        _source_file(), output_dir=tmp_path, preferred_method="curl", resume_downloads=True
    )
    assert "--continue-at -" in plan.command
    assert plan.supports_resume


def test_download_script_attempts_all_commands_and_fails_at_end(tmp_path: Path) -> None:
    plans = [
        build_download_plan(_source_file(id="first"), output_dir=tmp_path / "raw"),
        build_download_plan(_source_file(id="second"), output_dir=tmp_path / "raw"),
    ]
    _, _, _, _ = write_download_outputs(plans, [], output_dir=tmp_path / "plans")
    script = (tmp_path / "plans" / "download_commands.sh").read_text(encoding="utf-8")
    assert "failures=0" in script
    assert "download command 1 failed" in script
    assert "download command 2 failed" in script
    assert "inspect source validation and attempt metadata" in script


def test_protocol_status_generation_and_outputs(tmp_path: Path) -> None:
    rows = build_protocol_status(load_research_questions())
    assert rows
    assert all(row.protocol_exists for row in rows)
    summary = protocol_summary(rows)
    assert summary["protocol_count"] == len(rows)
    paths = write_protocol_status(rows, output_dir=tmp_path)
    assert all(path.exists() for path in paths)
