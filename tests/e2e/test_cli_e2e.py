"""End-to-end CLI tests."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from reimburse_atlas.cli import app


def test_cli_read_only_json_contracts() -> None:
    """Read-only listing commands expose parseable, machine-readable records."""
    runner = CliRunner()
    for command in ("runtime-targets", "sources", "source-status", "source-files", "analyses"):
        result = runner.invoke(app, [command, "--json"])
        assert result.exit_code == 0, result.output
        assert isinstance(json.loads(result.stdout), list)

    roadmap = runner.invoke(app, ["roadmap", "--json"])
    assert roadmap.exit_code == 0, roadmap.output
    roadmap_payload = json.loads(roadmap.stdout)
    assert isinstance(roadmap_payload["tracks"], list)
    assert isinstance(roadmap_payload["function_count"], int)

    for command in ("score-sources", "license-gates"):
        result = runner.invoke(app, [command, "--json"])
        assert result.exit_code == 0, result.output
        assert isinstance(json.loads(result.stdout), list)


def test_cli_validate_e2e() -> None:
    """The validate command should succeed with seed data."""
    result = CliRunner().invoke(app, ["validate"])
    assert result.exit_code == 0
    assert "source_count" in result.output


def test_cli_export_graph_e2e(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """The export-graph command should write node and edge files."""
    result = CliRunner().invoke(app, ["export-graph", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / "graph_nodes.csv").exists()
    assert (tmp_path / "graph_edges.csv").exists()


def test_cli_validate_seed_files_e2e() -> None:
    """The validate-seed-files command should succeed with generated CSV mirrors."""
    result = CliRunner().invoke(app, ["validate-seed-files"])
    assert result.exit_code == 0
    assert "Seed JSONL/CSV sync" in result.output


def test_cli_publication_manifest_e2e(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """The publication-manifest command should write a manifest."""
    target = tmp_path / "publication_manifest.json"
    result = CliRunner().invoke(app, ["publication-manifest", str(target)])
    assert result.exit_code == 0
    assert target.exists()


def test_cli_osf_reconcile_is_dry_run_and_idempotent(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """The OSF planner should report a matching remote file without mutation."""
    manifest = tmp_path / "sync_manifest.jsonl"
    manifest.write_text(
        json.dumps({
            "id": "protocol",
            "local_path": "protocols/example.md",
            "osf_path": "/protocols/example.md",
            "exists": True,
            "byte_size": 10,
            "sha256": "a" * 64,
            "publish_allowed": True,
        })
        + "\n",
        encoding="utf-8",
    )
    remote = tmp_path / "remote.json"
    remote.write_text(
        json.dumps([
            {
                "osf_path": "/protocols/example.md",
                "byte_size": 10,
                "sha256": "a" * 64,
            }
        ]),
        encoding="utf-8",
    )
    output = tmp_path / "report.json"

    result = CliRunner().invoke(
        app,
        [
            "osf-reconcile",
            "--manifest-path",
            str(manifest),
            "--remote-state-path",
            str(remote),
            "--output-path",
            str(output),
        ],
    )

    assert result.exit_code == 0, result.output
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["network_io"] is False
    assert report["mutation_performed"] is False
    assert report["summary"]["skip"] == 1
    assert report["summary"]["create"] == 0


def test_cli_osf_reconcile_rejects_invalid_remote_json(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """Malformed remote snapshots should fail with a parameter error."""
    manifest = tmp_path / "sync_manifest.jsonl"
    manifest.write_text(
        json.dumps({
            "id": "protocol",
            "local_path": "protocols/example.md",
            "osf_path": "/protocols/example.md",
            "exists": False,
            "byte_size": 0,
            "sha256": None,
            "publish_allowed": False,
        })
        + "\n",
        encoding="utf-8",
    )
    remote = tmp_path / "remote.json"
    remote.write_text("not-json", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "osf-reconcile",
            "--manifest-path",
            str(manifest),
            "--remote-state-path",
            str(remote),
        ],
    )

    assert result.exit_code != 0
    assert "remote state contains invalid JSON" in result.output


def test_cli_osf_reconcile_rejects_non_object_manifest_rows(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """Manifest JSONL rows must be objects, not arbitrary JSON values."""
    manifest = tmp_path / "sync_manifest.jsonl"
    manifest.write_text("[]\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        ["osf-reconcile", "--manifest-path", str(manifest)],
    )

    assert result.exit_code != 0


def test_cli_osf_registration_check_is_fail_closed_without_remote(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """Registration checks must not imply readiness without remote evidence."""
    freeze = tmp_path / "freeze.json"
    freeze.write_text(
        json.dumps({
            "schema_version": "osf-registration-snapshot-v1",
            "registration_id": "osf-reg-1",
            "registration_url": "https://osf.io/abc12/",
            "status": "registered",
            "submitted_at": "2026-07-16T00:00:00Z",
            "immutable": True,
            "snapshot_sha256": "a" * 64,
            "protocol_digest": "protocol",
            "analysis_manifest_digest": "manifest",
            "source_cutoff": "2026-07-01",
            "review_approved": True,
        }),
        encoding="utf-8",
    )
    result = CliRunner().invoke(app, ["osf-registration-check", "--freeze-path", str(freeze)])
    assert result.exit_code == 0
    assert '"status": "blocked"' in result.output
    assert "remote_registration_snapshot_missing" in result.output
