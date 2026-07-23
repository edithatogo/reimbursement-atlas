from __future__ import annotations

import json
from pathlib import Path

from reimburse_atlas.archive_publication import archive_publication_gate


def _summary(root: Path, **values: bool) -> None:
    path = root / "data/derived/release_readiness/summary.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(values), encoding="utf-8")


def test_archive_gate_requires_each_independent_readiness_flag(tmp_path: Path) -> None:
    _summary(
        tmp_path,
        repository_release_ready=True,
        evidence_release_ready=True,
        osf_registration_ready=False,
        research_publication_ready=True,
    )

    gate = archive_publication_gate(tmp_path)

    assert gate["status"] == "blocked"
    assert gate["missing_or_false"] == ["osf_registration_ready"]


def test_archive_gate_does_not_require_manuscript_publication_readiness(tmp_path: Path) -> None:
    _summary(
        tmp_path,
        repository_release_ready=True,
        evidence_release_ready=True,
        osf_registration_ready=True,
        research_publication_ready=False,
    )

    assert archive_publication_gate(tmp_path)["status"] == "ready"
