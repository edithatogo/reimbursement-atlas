"""Fail-closed dashboard review readiness predicates."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

AUTOMATED_PATH = Path("data/derived/dashboard_review/automated_review_packet.json")
OWNER_PATH = Path("data/derived/dashboard_review/owner_review_packet.json")
HUMAN_PATH = Path("data/derived/dashboard_review/human_review.json")
EXPECTED_ROUTES = (
    "/",
    "/analyses/",
    "/analyses/cognitive_vs_procedural_ratio/",
    "/automation/",
    "/crosswalks/",
    "/demonstrators/",
    "/ontologies/",
    "/readiness/",
    "/roadmap/",
    "/sources/",
    "/sources/au_mbs/",
)
EXPECTED_PROJECTS = (
    "desktop-chromium",
    "mobile-chromium",
    "desktop-firefox",
    "desktop-webkit",
)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return cast("dict[str, Any]", value) if isinstance(value, dict) else {}


def _sha256(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def resolve_repo_head(repo: Path) -> str | None:
    """Resolve the checked-out commit from a normal repository or worktree."""
    dot_git = repo / ".git"
    if not dot_git.exists():
        return None
    git_dir = dot_git
    if dot_git.is_file():
        marker = dot_git.read_text(encoding="utf-8").strip()
        if not marker.startswith("gitdir: "):
            return None
        git_dir = (repo / marker.removeprefix("gitdir: ")).resolve()
    head = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
    if not head.startswith("ref: "):
        return head
    ref = head.removeprefix("ref: ")
    search_dirs = [git_dir]
    if (git_dir / "commondir").is_file():
        search_dirs.append(
            (git_dir / (git_dir / "commondir").read_text(encoding="utf-8").strip()).resolve()
        )
    for directory in search_dirs:
        loose = directory / ref
        if loose.is_file():
            return loose.read_text(encoding="utf-8").strip()
        packed = directory / "packed-refs"
        if packed.is_file():
            for line in packed.read_text(encoding="utf-8").splitlines():
                if line and not line.startswith(("#", "^")):
                    commit, name = line.split(" ", maxsplit=1)
                    if name == ref:
                        return commit
    return None


def dashboard_review_evidence(repo: Path) -> dict[str, object]:
    """Return named dashboard gate checks for diagnostics and readiness."""
    automated_path = repo / AUTOMATED_PATH
    owner_path = repo / OWNER_PATH
    automated = _read_json(automated_path)
    owner = _read_json(owner_path)
    human = _read_json(repo / HUMAN_PATH)
    head = resolve_repo_head(repo)
    workflow = automated.get("workflow")
    workflow_data = cast("dict[str, Any]", workflow) if isinstance(workflow, dict) else {}
    raw_assertions = owner.get("provenance_assertions")
    assertions = (
        cast("list[dict[str, Any]]", raw_assertions) if isinstance(raw_assertions, list) else []
    )
    raw_prohibited = owner.get("prohibited_content_check")
    prohibited = cast("dict[str, Any]", raw_prohibited) if isinstance(raw_prohibited, dict) else {}
    checks = {
        "automated_pass": automated.get("status") == "pass",
        "coverage_complete": (
            automated.get("coverage_complete") is True
            and automated.get("routes") == list(EXPECTED_ROUTES)
            and automated.get("projects") == list(EXPECTED_PROJECTS)
            and automated.get("screenshot_count") == 44
        ),
        "workflow_attributed": all(
            bool(workflow_data.get(field))
            for field in ("workflow", "run_id", "run_attempt", "artifact_name", "workflow_url")
        ),
        "head_parity": bool(head)
        and automated.get("tested_commit") == head
        and owner.get("tested_commit") == head
        and owner.get("current_head") == head
        and owner.get("commit_parity") is True,
        "provenance_assertions_pass": bool(assertions)
        and all(item.get("status") == "pass" for item in assertions),
        "prohibited_content_pass": prohibited.get("status") == "pass",
        "human_scoped_approval": (
            human.get("status") == "approved_within_scope"
            and bool(human.get("reviewed_at"))
            and bool(human.get("reviewer"))
            and human.get("commit") == head
        ),
        "packet_hash_parity": (
            human.get("automated_packet_sha256") == _sha256(automated_path)
            and human.get("owner_packet_sha256") == _sha256(owner_path)
        ),
    }
    return {"head": head, "checks": checks}


def dashboard_review_approved(repo: Path) -> bool:
    """Return true only when every machine and accountable-review gate passes."""
    evidence = dashboard_review_evidence(repo)
    checks = cast("dict[str, bool]", evidence["checks"])
    return all(checks.values())
