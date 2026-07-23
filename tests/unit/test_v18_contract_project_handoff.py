from __future__ import annotations

import json
import shutil
from pathlib import Path
from types import SimpleNamespace

from reimburse_atlas.final_handoff import build_final_handoff_tasks, write_final_handoff_tasks
from reimburse_atlas.github_project import build_github_project_items, write_github_project_items
from reimburse_atlas.registry import load_conductor_tracks, load_source_files
from reimburse_atlas.source_contracts import (
    build_source_contract_validations,
    validate_path_against_contract,
    write_source_contract_validations,
)
from scripts.create_github_project_items import (
    IssueDraft,
    deduplicate_issues,
    existing_issue_paths,
    render_issue,
)
from scripts.sync_github_project import (
    _run_gh,  # ruff:ignore[import-private-name] - exercise the bounded CLI retry boundary directly.
    label_names,
    load_issue_drafts,
    normalise_body,
    project_numbers,
    sync_project,
)

ROOT = Path(__file__).resolve().parents[2]


def _source_file(source_file_id: str):
    return next(record for record in load_source_files() if record.id == source_file_id)


def test_huggingface_drift_issue_uses_track_specific_acceptance() -> None:
    issue = IssueDraft(
        epic_id="PUB-001",
        epic_title="Publication and dataset release readiness",
        title="Schedule read-only Hugging Face destination metadata drift monitoring",
        status="implemented",
    )
    body = render_issue(issue)
    assert "synchronizes issue #320" in body
    assert "GitHub issue permission only" in body
    assert "- [ ] Scope is confirmed." not in body


def test_mbs_source_contract_passes_fixture() -> None:
    record = _source_file("au_mbs_20260701_imap_txt")
    fixture = ROOT / "tests" / "fixtures" / "mbs_txt" / "20260701_MBSONLINE_IMAP_fixture.TXT"
    result = validate_path_against_contract(record, fixture)
    assert result.contract_status == "pass"
    assert "item_number" in result.observed_columns
    assert "schedule_fee" in result.observed_columns


def test_source_contracts_use_reviewed_mbs_evidence_when_raw_is_absent(tmp_path: Path) -> None:
    rows = build_source_contract_validations(load_source_files(), raw_dir=tmp_path)
    assert {row.contract_status for row in rows} <= {"pass", "skipped"}
    assert sum(row.contract_status == "pass" for row in rows) == 3
    assert (
        next(row for row in rows if row.source_file_id == "au_mbs_20260701_xml").contract_status
        == "pass"
    )
    assert any(row.contract_status == "skipped" for row in rows)
    paths = write_source_contract_validations(rows, output_dir=tmp_path / "contracts")
    assert all(path.exists() for path in paths)


def test_source_contracts_use_local_raw_file_when_present(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw_live"
    target_dir = raw_dir / "au_mbs"
    target_dir.mkdir(parents=True)
    shutil.copy2(
        ROOT / "tests" / "fixtures" / "mbs_txt" / "20260701_MBSONLINE_IMAP_fixture.TXT",
        target_dir / "20260701_MBSONLINE_IMAP.TXT",
    )
    rows = build_source_contract_validations(load_source_files(), raw_dir=raw_dir)
    row = next(item for item in rows if item.source_file_id == "au_mbs_20260701_imap_txt")
    assert row.contract_status == "pass"


def test_historical_mbs_landing_pages_are_manual_review_skips(tmp_path: Path) -> None:
    rows = build_source_contract_validations(load_source_files(), raw_dir=tmp_path)
    historical = {
        "au_mbs_2010_2019_downloads_page",
        "au_mbs_1989_2010_previous_downloads_page",
    }
    observed = {row.source_file_id: row.contract_status for row in rows}
    assert all(observed[source_file_id] == "skipped" for source_file_id in historical)


def test_github_project_export_covers_generated_issues(tmp_path: Path) -> None:
    rows = build_github_project_items(load_conductor_tracks())
    assert len(rows) >= 100
    assert any(row.item_type == "track" for row in rows)
    assert any(row.item_type == "issue" for row in rows)
    assert any(row.project_view == "Sources & ingestion" for row in rows)
    assert all(row.track_id is not None for row in rows if row.item_type == "issue")
    paths = write_github_project_items(rows, output_dir=tmp_path / "project")
    assert all(path.exists() for path in paths)


def test_dataset_candidates_are_explicitly_planned() -> None:
    from scripts.create_github_project_items import generated_track_issues

    candidates = [
        issue for issue in generated_track_issues(ROOT) if issue.epic_id == "DATASET-CANDIDATES"
    ]
    assert candidates
    assert all(issue.status == "planned" for issue in candidates)
    assert all("status:planned" in issue.labels for issue in candidates)


def test_generated_issue_renders_parent_subissue_link() -> None:
    rendered = render_issue(
        IssueDraft(
            epic_id="TRACK_PUBLIC_PRODUCT_CITATION_DASHBOARD",
            epic_title="Public product, citation and dashboard maturity",
            title="Validate citation metadata",
            parent_issue="Public product, citation and dashboard maturity",
        )
    )
    assert "Parent issue: Public product, citation and dashboard maturity" in rendered


def test_backlog_acceptance_criteria_are_preserved_in_generated_issue() -> None:
    """Track-specific backlog criteria must not degrade to generic placeholders."""
    from scripts.create_github_project_items import parse_backlog

    issue = next(
        item
        for item in parse_backlog()
        if item.title == "Complete OSF Preregistration metadata and protocol sections"
    )
    rendered = render_issue(issue)
    assert "Title, description, contributors, licence, subjects and tags are complete." in rendered
    assert "Refine the acceptance criteria" not in rendered


def test_generated_roadmap_issue_preserves_implementation_status() -> None:
    """Roadmap status must be visible in drafts and Project imports."""
    from scripts.create_github_project_items import generated_track_issues

    issues = generated_track_issues(ROOT)
    issue = next(
        item
        for item in issues
        if item.title == "Add dashboard provenance and mapping-evidence drill-down"
    )
    assert issue.status == "implemented"
    assert "status:implemented" in issue.labels
    assert "Status: `implemented`" in render_issue(issue)


def test_generated_output_plan_preserves_status_and_external_gate() -> None:
    """Output drafts must expose both local state and promotion boundaries."""
    from scripts.create_github_project_items import generated_track_issues

    issues = generated_track_issues(ROOT)
    issue = next(
        item for item in issues if item.title == "Implement output plan: out_osf_protocol_pack"
    )
    rendered = render_issue(issue)
    assert issue.status == "drafted"
    assert "status:drafted" in issue.labels
    assert "Status: `drafted`" in rendered
    assert "human or external approval" in rendered
    assert "- [ ]" in rendered


def test_public_product_output_plans_reflect_local_implementation() -> None:
    """Public product outputs must not remain planned after their local gates pass."""
    from scripts.create_github_project_items import generated_track_issues

    issues = generated_track_issues(ROOT)
    expected = {
        "Implement output plan: out_citation_cff",
        "Implement output plan: out_public_dashboard",
        "Implement output plan: out_public_status_manifest",
    }
    observed = {issue.title: issue for issue in issues if issue.title in expected}
    assert set(observed) == expected
    assert all(issue.status == "implemented" for issue in observed.values())
    assert all("status:implemented" in issue.labels for issue in observed.values())
    assert all(
        "separate human or external publication gate remains fail-closed" in render_issue(issue)
        for issue in observed.values()
    )


def test_hugging_face_output_plans_reflect_local_workflow_implementation() -> None:
    """HF publication tooling is implemented even while remote publication is gated."""
    from scripts.create_github_project_items import generated_track_issues

    expected = {
        "Implement output plan: out_hf_dataset",
        "Implement output plan: out_hf_space",
    }
    observed = {
        issue.title: issue for issue in generated_track_issues(ROOT) if issue.title in expected
    }
    assert set(observed) == expected
    assert all(issue.status == "implemented" for issue in observed.values())
    assert all(
        "separate human or external publication gate remains fail-closed" in render_issue(issue)
        for issue in observed.values()
    )


def test_zenodo_metadata_output_is_implemented_without_doi_promotion() -> None:
    """Local Zenodo metadata must not be conflated with DOI deposition."""
    from scripts.create_github_project_items import generated_track_issues

    issues = generated_track_issues(ROOT)
    metadata = next(issue for issue in issues if issue.title == "Implement output plan: out_zenodo")
    doi = next(
        issue for issue in issues if issue.title == "Implement output plan: out_zenodo_release_doi"
    )
    assert metadata.status == "implemented"
    assert "status:implemented" in metadata.labels
    assert doi.status == "planned"
    assert "status:planned" in doi.labels


def test_research_question_issue_exposes_local_scaffolds_and_review_gate() -> None:
    """Research issues must distinguish drafted local work from human approval."""
    from scripts.create_github_project_items import generated_track_issues

    issue = next(
        item
        for item in generated_track_issues(ROOT)
        if item.title == "Complete protocol and report: rq_genomics_coverage_price"
    )
    rendered = render_issue(issue)
    assert issue.status == "drafted"
    assert "status:drafted" in issue.labels
    assert issue.protocol_path == "protocols/genomics_pathology_protocol.md"
    assert issue.report_path == "reports/genomics_pathology_report.md"
    assert "`protocols/genomics_pathology_protocol.md`" in rendered
    assert "`reports/genomics_pathology_report.md`" in rendered
    assert "accountable human completes the protocol review checklist" in rendered
    assert rendered.count("- [ ]") == 2


def test_implemented_roadmap_issue_does_not_render_placeholder_checklist() -> None:
    """Implemented roadmap rows must not look unstarted in GitHub."""
    rendered = render_issue(
        IssueDraft(
            epic_id="TRACK_PUBLIC_PRODUCT_CITATION_DASHBOARD",
            epic_title="Public product, citation and dashboard maturity",
            title="Correct and schema-validate CITATION.cff",
            status="implemented",
        )
    )
    assert "Status: `implemented`" in rendered
    assert "- [ ]" not in rendered
    assert "does not grant external publication or evidence approval" in rendered


def test_project_status_preserves_implemented_licence_gated_controls() -> None:
    """A licence-risk label must not hide a completed local control."""
    from reimburse_atlas.github_project import build_github_project_items
    from reimburse_atlas.registry import load_conductor_tracks

    rows = build_github_project_items(load_conductor_tracks())
    checklist = next(
        row
        for row in rows
        if row.title == "Add URL/licence verification checklist for first-wave sources"
    )
    assert checklist.status == "done"
    blocked = next(
        row
        for row in rows
        if row.title == "Validate PBS API CSV parser against a reviewed monthly public extract"
    )
    assert blocked.status == "blocked"


def test_project_sync_reads_issue_rows_and_project_numbers(tmp_path: Path) -> None:
    """The synchronizer has a typed, duplicate-aware read model."""
    export = tmp_path / "items.jsonl"
    export.write_text(
        json.dumps({"item_type": "issue", "title": "One", "body_path": "one.md"})
        + "\n"
        + json.dumps({"item_type": "track", "title": "Track"})
        + "\n",
        encoding="utf-8",
    )
    assert [row["title"] for row in load_issue_drafts(export)] == ["One"]
    assert project_numbers({
        "items": [{"content": {"number": 326}}, {"content": {"number": 18}}]
    }) == {
        "326",
        "18",
    }
    assert label_names([{"name": "type:automation"}, {"name": ""}]) == {"type:automation"}


def test_project_sync_body_comparison_ignores_github_final_newline() -> None:
    """Generated body reconciliation must not churn on GitHub newline normalisation."""
    assert normalise_body("body\n") == normalise_body("body")
    assert normalise_body("body\n") != normalise_body("different\n")


def test_project_sync_retries_transient_gh_failures(monkeypatch, tmp_path: Path) -> None:
    """Transient GitHub availability failures get bounded retries."""
    attempts = 0

    def fake_run(*args, **kwargs):
        nonlocal attempts
        del args, kwargs
        attempts += 1
        if attempts == 1:
            return SimpleNamespace(returncode=1, stderr="HTTP 504 Gateway Timeout", stdout="")
        return SimpleNamespace(returncode=0, stderr="", stdout='{"ok": true}')

    monkeypatch.setattr("scripts.sync_github_project.shutil.which", lambda _: "/usr/bin/gh")
    monkeypatch.setattr("scripts.sync_github_project.subprocess.run", fake_run)
    monkeypatch.setattr("scripts.sync_github_project.time.sleep", lambda _: None)

    assert _run_gh(["api", "status"], root=tmp_path) == {"ok": True}
    assert attempts == 2


def test_project_sync_dry_run_reports_body_drift(monkeypatch, tmp_path: Path) -> None:
    """Dry-run sync reports body drift without invoking a write command."""
    export_dir = tmp_path / "data" / "derived" / "github_project"
    export_dir.mkdir(parents=True)
    (export_dir / "github_project_items.jsonl").write_text(
        json.dumps({
            "item_type": "issue",
            "title": "One",
            "body_path": "generated/one.md",
        })
        + "\n",
        encoding="utf-8",
    )
    body_path = tmp_path / "generated" / "one.md"
    body_path.parent.mkdir()
    body_path.write_text("new body\n", encoding="utf-8")

    calls: list[list[str]] = []

    def fake_gh(args: list[str], *, root: Path):
        del root
        calls.append(args)
        if args[:2] == ["issue", "list"]:
            return [{"title": "One", "number": 7, "url": "https://example/7", "body": "old"}]
        if args[:2] == ["project", "item-list"]:
            return {"items": []}
        raise AssertionError from None

    monkeypatch.setattr("scripts.sync_github_project._run_gh", fake_gh)
    actions = sync_project(
        root=tmp_path,
        repository="owner/repo",
        owner="owner",
        project_number=18,
        title_filters=("One",),
        apply=False,
    )

    assert {action["action"] for action in actions} == {
        "update_issue_body",
        "add_project_item",
    }
    assert not any(args[:2] == ["issue", "edit"] for args in calls)


def test_generated_issue_drafts_deduplicate_backlog_and_roadmap_rows() -> None:
    issues = [
        IssueDraft(epic_id="LIVE-001", epic_title="Live", title="Same title"),
        IssueDraft(epic_id="TRACK", epic_title="Track", title="same title"),
    ]
    assert len(deduplicate_issues(issues)) == 1


def test_generated_zenodo_issue_records_non_depositing_boundary() -> None:
    """The generated Zenodo issue separates preparation from human approval."""
    rendered = render_issue(
        IssueDraft(
            epic_id="TRACK_DATA_PACKAGING_STANDARDS",
            epic_title="Research-data packaging standards",
            title="Create signed release and Zenodo DOI after publication approval",
        )
    )
    assert "do not deposit or mint a DOI" in rendered
    assert "accountable human reviewer" in rendered


def test_generated_huggingface_issue_records_destination_drift_boundary() -> None:
    rendered = render_issue(
        IssueDraft(
            epic_id="PUB-001",
            epic_title="Publication and dataset release readiness",
            title="Reconcile Hugging Face destination metadata with governed publication candidate",
            status="blocked",
        )
    )
    assert "destination metadata" in rendered
    assert "write-enabled reconciliation run" in rendered
    assert "Status: `blocked`" in rendered


def test_generated_issue_paths_preserve_existing_numeric_prefixes(tmp_path: Path) -> None:
    existing = tmp_path / "042-keep-this-title.md"
    existing.write_text("old draft\n", encoding="utf-8")

    paths = existing_issue_paths(tmp_path)

    assert paths["keep-this-title"] == [existing]


def test_final_handoff_records_environment_bound_tasks(tmp_path: Path) -> None:
    rows = build_final_handoff_tasks()
    assert not any(
        row.id in {"final_pip_audit_strict", "final_action_sha_pinning"}
        and row.status == "blocked_network"
        for row in rows
    )
    assert not any(row.status == "blocked_secret" for row in rows)
    assert any(row.status == "blocked_review" for row in rows)
    cms_task = next(row for row in rows if row.id == "final_cms_clfs_licence_review")
    assert cms_task.status == "complete"
    assert cms_task.reason_code == "checksum_bound_scope_approved"
    assert cms_task.review_record == "data/licence_review/decisions.jsonl"
    assert all(row.reason_code != "unspecified" for row in rows)
    assert all(row.gate_evidence for row in rows)
    assert any("reviewed-mbs-txt-pair-bundle" in row.command for row in rows)
    source_task = next(row for row in rows if row.id == "final_source_downloads")
    assert source_task.status == "partial"
    assert source_task.conductor_track == "track_live_source_ingestion"
    assert source_task.github_issues == (23, 25, 255)
    assert all(row.conductor_track.startswith("track_") for row in rows)
    assert all(row.github_issues for row in rows)
    mbs_task = next(row for row in rows if row.id == "final_mbs_pair_bundle")
    assert mbs_task.status == "complete"
    paths = write_final_handoff_tasks(rows, output_dir=tmp_path / "handoff")
    assert all(path.exists() for path in paths)


def test_final_handoff_review_states_transition_from_evidence(tmp_path: Path) -> None:
    evidence = {
        "data/derived/release_readiness/summary.json": {
            "repository_release_ready": True,
            "research_publication_ready": True,
            "evidence_release_ready": True,
            "policy_claims_ready": True,
        },
        "data/derived/osf/registration_freeze.json": {
            "review_approved": True,
            "source_cutoff_status": "approved",
            "source_cutoff": "2026-07-19T00:00:00Z",
        },
        "data/derived/osf/remote_registration_snapshot.json": {
            "registration_id": "abc12",
            "status": "registered",
        },
        "data/derived/mapping_study/evaluation_summary.json": {
            "status": "accepted",
            "evaluated_once": True,
        },
        "data/derived/historical_sources/summary.json": {
            "review_queue_status": "approved",
            "status": "derived_processing_approved",
        },
        "data/derived/dashboard_review/human_review.json": {
            "status": "approved_within_scope",
            "reviewed_at": "2026-07-22T00:00:00Z",
            "reviewer": "accountable-owner",
            "commit": "a" * 40,
            "scope": {
                "provenance": True,
                "routes": ["/"],
                "browsers": ["Chromium"],
                "operating_systems": ["macOS"],
                "assistive_technology": ["VoiceOver"],
            },
        },
        "data/derived/dashboard_review/automated_review_packet.json": {
            "status": "pass",
            "tested_commit": "a" * 40,
            "screenshot_count": 36,
        },
    }
    for relative, payload in evidence.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")

    rows = {row.id: row for row in build_final_handoff_tasks(tmp_path)}

    assert rows["final_hf_dataset_space"].status == "ready_local"
    assert rows["final_osf_protocol_pack"].status == "ready_local"
    assert rows["final_osf_registration_drift_check"].status == "ready_local"
    assert rows["final_mapping_calibration_review"].status == "complete"
    assert rows["final_historical_source_expansion"].status == "complete"
    assert rows["final_dashboard_visual_review"].status == "complete"
    assert rows["final_release_candidate"].status == "ready_local"


def test_mbs_descriptor_contract_passes_fixture() -> None:
    record = _source_file("au_mbs_20260701_desc_txt")
    fixture = ROOT / "tests" / "fixtures" / "mbs_txt" / "20260701_MBSONLINE_DESC_fixture.TXT"
    result = validate_path_against_contract(record, fixture)
    assert result.contract_status == "pass"
    assert result.observed_columns == ("item_number", "descriptor")


def test_pbs_contract_passes_fixture() -> None:
    record = _source_file("au_pbs_api_v3_documentation")
    fixture = ROOT / "tests" / "fixtures" / "pbs_fixture.csv"
    result = validate_path_against_contract(record, fixture)
    assert result.contract_status == "pass"
    assert "pbs_item_code" in result.observed_columns


def test_contract_detects_html_download(tmp_path: Path) -> None:
    record = _source_file("au_mbs_20260701_imap_txt")
    path = tmp_path / "20260701_MBSONLINE_IMAP.TXT"
    path.write_text("<html><head><title>not data</title></head></html>", encoding="utf-8")
    result = validate_path_against_contract(record, path)
    assert result.contract_status == "fail"
    assert any("HTML" in issue or "html" in issue for issue in result.issues)


def test_contract_detects_empty_file(tmp_path: Path) -> None:
    record = _source_file("au_mbs_20260701_desc_txt")
    path = tmp_path / "empty.TXT"
    path.write_text("", encoding="utf-8")
    result = validate_path_against_contract(record, path)
    assert result.contract_status == "fail"
    assert "empty" in result.issues[0]


def test_zip_contract_handles_valid_and_invalid_archives(tmp_path: Path) -> None:
    import zipfile

    record = _source_file("us_cms_clfs_26clabq3_ama_zip")
    valid_zip = tmp_path / "26clabq3.zip"
    with zipfile.ZipFile(valid_zip, "w") as archive:
        archive.writestr("clfs.csv", "hcpcs,payment_rate\nG0001,1.23\n")
    valid = validate_path_against_contract(record, valid_zip)
    assert valid.contract_status == "pass"
    assert "clfs.csv" in valid.observed_markers

    invalid_zip = tmp_path / "invalid.zip"
    invalid_zip.write_text("not a zip", encoding="utf-8")
    invalid = validate_path_against_contract(record, invalid_zip)
    assert invalid.contract_status == "fail"


def test_github_project_export_handles_empty_issue_dir(tmp_path: Path) -> None:
    rows = build_github_project_items(load_conductor_tracks(), generated_issue_dir=tmp_path)
    assert rows
    assert all(row.item_type == "track" for row in rows)
