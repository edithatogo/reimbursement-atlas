"""Native source-record checks without regenerating global projections."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import yaml

from reimburse_atlas.registry import load_conductor_tracks, load_roadmap_functions
from scripts.create_github_project_items import (
    deduplicate_issues,
    generated_track_issues,
    parse_backlog,
    render_issue,
)

ROOT = Path(__file__).resolve().parents[2]
TRACK = "track_pbs_raw_archive_20260831"
PERMISSION = "pbs_raw_permission_20260831"
TITLE = "Complete residual historical MBS/PBS acquisition breadth and evidence promotion"
STAGE_SHA = "569d18a843791e666be9e878e52859355d48f8cce76cabf1f7b97034c7ae12ff"


def test_native_seed_models_link_source_scope_and_permission_closeout() -> None:
    tracks = {
        row.id: row for row in load_conductor_tracks(ROOT / "data/seed/conductor_tracks.jsonl")
    }
    assert tracks[TRACK].github_project_status == "done"
    assert tracks[TRACK].phase == "archived"
    assert tracks[TRACK].depends_on == (PERMISSION,)
    assert tracks[PERMISSION].phase == "archived"
    assert tracks[PERMISSION].github_project_status == "done"
    functions = load_roadmap_functions(ROOT / "data/seed/roadmap_functions.jsonl")
    source = next(row for row in functions if row.id == "func_historical_mbs_pbs_bundles")
    assert source.track_id == TRACK
    assert source.status == "blocked"


def test_registry_paths_and_permission_delivery_evidence() -> None:
    registry = yaml.safe_load((ROOT / "conductor/tracks.yml").read_text())
    tracks = {row["id"]: row for row in registry["tracks"]}
    for track_id, directory in ((TRACK, "archive"), (PERMISSION, "archive")):
        path = ROOT / "conductor" / directory / track_id
        assert tracks[track_id]["spec"] == str((path / "spec.md").relative_to(ROOT))
        assert tracks[track_id]["plan"] == str((path / "plan.md").relative_to(ROOT))
        for name in ("index.md", "spec.md", "plan.md", "metadata.json", "evidence.jsonl"):
            assert (path / name).is_file()
    permission = json.loads((ROOT / "conductor/archive" / PERMISSION / "metadata.json").read_text())
    assert permission["status"] == "completed"
    assert permission["merge_commit"] == "02116d73da8a8f5dee96009b1ec33691d2704062"
    assert permission["validated_tree"] == "999415853772673847aed633f6e35f118e0e4204"
    assert permission["hosted_successful_checks"] == 25
    assert not (ROOT / "conductor/tracks" / PERMISSION).exists()
    registry_md = (ROOT / "conductor/TRACKS.md").read_text()
    assert "[x] **Track: PBS owner-attested raw redistribution**" in registry_md
    assert f"./archive/{PERMISSION}/index.md" in registry_md
    assert "[x] **Track: PBS source archive staging and early-schema evidence**" in registry_md


def test_changed_seed_rows_match_csv_in_all_fields() -> None:
    for table, ids in (
        ("conductor_tracks", {TRACK, PERMISSION}),
        ("roadmap_functions", {"func_historical_mbs_pbs_bundles"}),
    ):
        rows: dict[str, dict[str, Any]] = {}
        for line in (ROOT / f"data/seed/{table}.jsonl").read_text().splitlines():
            row = json.loads(line)
            if row["id"] in ids:
                rows[row["id"]] = row
        with (ROOT / f"data/seed/{table}.csv").open(newline="") as handle:
            mirrored = {row["id"]: row for row in csv.DictReader(handle) if row["id"] in ids}
        assert set(rows) == set(mirrored) == ids
        for identity, row in rows.items():
            for key, value in row.items():
                actual = mirrored[identity][key]
                assert (json.loads(actual) if isinstance(value, list) else actual) == value


def test_project_issue_rendering_retains_remaining_source_and_transfer_gates() -> None:
    backlog = parse_backlog(ROOT / "conductor/backlog.yml")
    generated_issues = generated_track_issues(ROOT)
    assert not any(row.title == TITLE for row in backlog)
    issues = deduplicate_issues([*backlog, *generated_issues])
    matches = [row for row in issues if row.title == TITLE]
    assert len(matches) == 1
    issue = matches[0]
    assert issue.status == "blocked"
    rendered = render_issue(issue)
    for text in (
        "1,707 of 1,709",
        "At those dry runs, no actual staging or upload occurred",
        "Subsequently verify the orchestrator's local stage",
        "independent fixed-revision remote readback verified all raw bytes",
        STAGE_SHA,
        "two early schema",
        "eight derived configs",
        "canonical URL returned HTTP 404",
        "variant returned HTTP 403",
        "reading-room-only physical access",
        "target issue remains uninspected",
        "no publisher/library contact is claimed",
        "checksum-bound gap search",
        "FlashPaper views, not structured releases",
    ):
        assert text in rendered
    assert "- [x] Transfer raw PBS" in rendered
    generated = next(row for row in generated_track_issues(ROOT) if row.title == TITLE)
    assert generated.epic_id == TRACK.upper()
    assert generated.status == "blocked"
    drafts = list(
        (ROOT / ".github/generated-issues").glob(
            "*-complete-residual-historical-mbs-pbs-acquisition-breadth-and-evidence-promotion.md"
        )
    )
    assert len(drafts) == 1
    assert drafts[0].read_text() == rendered


def test_current_source_status_matches_all_track_projections() -> None:
    seed = next(
        row
        for row in load_conductor_tracks(ROOT / "data/seed/conductor_tracks.jsonl")
        if row.id == TRACK
    )
    assert "Global generation complete" in seed.notes
    assert "independent archive-contract review PASS" in seed.notes
    assert "Local stage verified: 1707 payloads" in seed.notes
    assert STAGE_SHA in seed.notes
    assert "published_verified" in seed.notes
    assert "#255 and #362 remain open" in seed.notes
    for relative in (
        "data/seed/conductor_tracks.csv",
        "data/derived/seed_lake/conductor_tracks/conductor_tracks.csv",
        "apps/dashboard/public/data/conductor_tracks.csv",
    ):
        with (ROOT / relative).open(newline="") as handle:
            row = next(row for row in csv.DictReader(handle) if row["id"] == TRACK)
        assert row["notes"] == seed.notes
        assert row["github_project_status"] == "done"
    lake = next(
        row
        for row in load_conductor_tracks(
            ROOT / "data/derived/seed_lake/conductor_tracks/conductor_tracks.jsonl"
        )
        if row.id == TRACK
    )
    assert lake == seed
    backlog = yaml.safe_load((ROOT / "conductor/backlog.yml").read_text())
    epic = next(row for row in backlog["epics"] if row.get("track_id") == TRACK)
    assert epic["existing_github_issue"] == 255
    assert epic["issues"] == []
    assert STAGE_SHA in " ".join(epic["scope"])
    assert "Deferred generation" not in " ".join(epic["blockers"])


def test_hf_card_keeps_eight_explicit_derived_configs_and_conditional_archive() -> None:
    card = (ROOT / "infra/huggingface/DATASET_CARD.md").read_text()
    metadata = yaml.safe_load(card.split("---")[1])
    assert metadata["license"] == "other"
    assert [row["config_name"] for row in metadata["configs"]] == [
        "catalogue_b0",
        "acquisition_b1",
        "evidence_b2",
        "silver",
        "gold",
        "platinum",
        "lineage",
        "promotion_decisions",
    ]
    assert all(row["data_files"].startswith("data/medallion/") for row in metadata["configs"])
    assert "When present" in card
    assert "not a ninth derived" in card
    assert "not an independently verified publisher grant" in card


def test_source_evidence_retains_initial_omissions_and_superseding_report() -> None:
    path = ROOT / "conductor/archive" / TRACK / "evidence.jsonl"
    events = [json.loads(line) for line in path.read_text().splitlines()]
    initial = next(row for row in events if row["event"] == "initial_actual_cache_dry_run")
    updated = next(row for row in events if row["event"] == "superseding_actual_cache_dry_run")
    assert initial["verified_files"] == 1706
    assert initial["failures"] == 3
    assert updated["verified_files"] == 1707
    assert len(updated["failures"]) == 2
    assert updated["verified_bytes"] == 9216771435
    assert updated["status"] == initial["status"] == "blocked"
    assert updated["publication_state"] == initial["publication_state"] == "not_asserted"
    for evidence in events:
        text = json.dumps(evidence)
        assert "/Users/" not in text
        assert "/Volumes/" not in text
