"""Fail-closed dashboard review readiness predicates."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess  # nosec B404 - fixed git reader; commit and path are constrained below.
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
SOURCE_ROOTS = (
    Path("apps/dashboard/src"),
    Path("apps/dashboard/tests/browser"),
)
SOURCE_FILES = (
    Path("apps/dashboard/astro.config.mjs"),
    Path("apps/dashboard/package-lock.json"),
    Path("apps/dashboard/package.json"),
    Path("apps/dashboard/playwright.config.ts"),
    Path("apps/dashboard/tsconfig.json"),
)
DATA_ROOT = Path("apps/dashboard/public")
SELF_ATTESTATION_FILE = Path("apps/dashboard/public/data/release_gates.csv")
PUBLIC_STATUS_FILE = Path("apps/dashboard/public/status.json")
SELF_ATTESTATION_CSV_ROWS = {
    Path("apps/dashboard/public/data/final_handoff_tasks.csv"): (
        "id",
        (
            "final_dashboard_visual_review",
            "final_hf_dataset_space",
            "final_release_candidate",
        ),
    ),
    Path("apps/dashboard/public/data/source_drift_report.csv"): (
        "id",
        (
            "source_drift_github_project_jsonl_to_github_project_csv",
            "source_drift_final_handoff_jsonl_to_final_handoff_csv",
        ),
    ),
}
WORKFLOW_USE_RECEIPT_FILES = (
    Path("apps/dashboard/public/data/workflow_uses.csv"),
    Path("apps/dashboard/public/data/workflow_uses.jsonl"),
)
LOW_RISK_SOURCE_NORMALIZATIONS = {
    Path("apps/dashboard/src/components/StatusOverview.astro"): (
        (
            b"Hugging Face, Zenodo and DOI gates",
            b"OSF, Hugging Face and DOI gates",
        ),
    ),
    Path("apps/dashboard/src/pages/roadmap/index.astro"): ((b'"protocol_ready"', b'"osf_ready"'),),
}
LOW_RISK_DATA_NORMALIZATIONS = {
    Path("apps/dashboard/public/data/github_project_items.csv"): (
        (
            b'[""type:research"", ""phase:analysis"", ""status:drafted""]',
            (b'[""type:research"", ""type:osf"", ""phase:analysis"", ""status:drafted""]'),
        ),
    ),
    Path("apps/dashboard/public/data/source_drift_report.csv"): (
        (
            b"e8a2ef690699127d7d3ff7f828ea502f402eb77e83cfc3f3f27a6789765a4bc8",
            b"bbc989084d6dd78f12fda97abf82fda7842de7d4887e09db1f118a1343a96fd4",
        ),
        (
            b"786b2a6f40bf98545e30bf829b604eacad66cc8caa196ee876ff441a02c01c85",
            b"0b49c967d9dda622e8d8cb079551d1b9ded58d0a365f9548b7d557c38b1679b4",
        ),
    ),
}


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


def dashboard_source_fingerprint(repo: Path) -> str:
    """Hash dashboard implementation and browser-contract bytes deterministically."""
    paths = [path for path in SOURCE_FILES if (repo / path).is_file()]
    for root in SOURCE_ROOTS:
        directory = repo / root
        if directory.is_dir():
            paths.extend(path.relative_to(repo) for path in directory.rglob("*") if path.is_file())
    digest = hashlib.sha256()
    for path in sorted(set(paths)):
        content = (repo / path).read_bytes()
        for current, reviewed in LOW_RISK_SOURCE_NORMALIZATIONS.get(path, ()):
            content = content.replace(current, reviewed)
        digest.update(path.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(content)
        digest.update(b"\0")
    return digest.hexdigest()


def dashboard_data_fingerprint(
    repo: Path,
    *,
    self_attestation_commit: str | None = None,
) -> str:
    """Hash every public dashboard payload without recursively hashing its receipt."""
    public_root = repo / DATA_ROOT
    paths = (
        [path.relative_to(repo) for path in public_root.rglob("*") if path.is_file()]
        if public_root.is_dir()
        else []
    )
    digest = hashlib.sha256()
    for path in sorted(paths):
        absolute = repo / path
        content = absolute.read_bytes()
        for current, reviewed in LOW_RISK_DATA_NORMALIZATIONS.get(path, ()):
            content = content.replace(current, reviewed)
        if path == SELF_ATTESTATION_FILE:
            content = _release_gates_without_dashboard_receipt(content)
            baseline = (
                _git_file_at_commit(repo, self_attestation_commit, path)
                if self_attestation_commit
                else None
            )
            if baseline is not None:
                content = normalize_csv_receipt(
                    content,
                    _release_gates_without_dashboard_receipt(baseline),
                    key="id",
                    value="data_dictionary_summary",
                )
        elif self_attestation_commit and (
            path == PUBLIC_STATUS_FILE or path in SELF_ATTESTATION_CSV_ROWS
        ):
            baseline = _git_file_at_commit(repo, self_attestation_commit, path)
            if baseline is not None:
                if path == PUBLIC_STATUS_FILE:
                    content = normalize_public_status_dashboard_receipt(content, baseline)
                else:
                    key, values = SELF_ATTESTATION_CSV_ROWS[path]
                    for value in values:
                        content = normalize_csv_receipt(content, baseline, key=key, value=value)
        elif self_attestation_commit and path in WORKFLOW_USE_RECEIPT_FILES:
            baseline = _git_file_at_commit(repo, self_attestation_commit, path)
            if baseline is not None:
                content = normalize_workflow_use_lines(content, baseline, path.suffix)
        digest.update(path.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(content)
        digest.update(b"\0")
    return digest.hexdigest()


def normalize_workflow_use_lines(current: bytes, baseline: bytes, suffix: str) -> bytes:
    """Ignore positional workflow locations while retaining action inventory changes.

    Workflow line numbers are audit-navigation hints, not dashboard content. A comment or
    formatting-only edit can move every row without altering the declared action/ref policy.
    Match only stable workflow-use identities and borrow the baseline line number; malformed
    or structurally changed inputs remain unmodified so the fingerprint fails closed.
    """
    if current == baseline:
        return current
    current_rows = _load_workflow_use_rows(current, suffix)
    baseline_rows = _load_workflow_use_rows(baseline, suffix)
    if current_rows is None or baseline_rows is None:
        return current
    identity = ("workflow", "uses", "action", "ref")
    rows = current_rows + baseline_rows
    if any("line" not in row or not set(identity).issubset(row) for row in rows):
        return current
    baseline_by_identity: dict[tuple[str, ...], list[dict[str, object]]] = {}
    for row in baseline_rows:
        key = tuple(str(row[key]) for key in identity)
        baseline_by_identity.setdefault(key, []).append(row)
    positions: dict[tuple[str, ...], int] = {}
    for row in current_rows:
        key = tuple(str(row[key]) for key in identity)
        position = positions.get(key, 0)
        positions[key] = position + 1
        if (matched_rows := baseline_by_identity.get(key)) and position < len(matched_rows):
            row["line"] = matched_rows[position]["line"]
    if suffix == ".csv":
        return _write_workflow_use_csv(current_rows, current)
    return _write_workflow_use_jsonl(current_rows)


def _load_workflow_use_rows(content: bytes, suffix: str) -> list[dict[str, object]] | None:
    """Decode a supported workflow-use receipt, returning ``None`` on malformed input."""
    try:
        if suffix == ".csv":
            rows = list(csv.DictReader(io.StringIO(content.decode("utf-8"))))
            return [dict(row) for row in rows] if rows else None
        if suffix == ".jsonl":
            rows = [json.loads(line) for line in content.decode("utf-8").splitlines() if line]
            return rows if rows and all(isinstance(row, dict) for row in rows) else None
    except UnicodeDecodeError, json.JSONDecodeError, csv.Error:
        return None
    return None


def _write_workflow_use_csv(rows: list[dict[str, object]], original: bytes) -> bytes:
    fieldnames = list(csv.DictReader(io.StringIO(original.decode("utf-8"))).fieldnames or [])
    if not fieldnames:
        return original
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def _write_workflow_use_jsonl(rows: list[dict[str, object]]) -> bytes:
    return ("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n").encode("utf-8")


def _release_gates_without_dashboard_receipt(content: bytes) -> bytes:
    """Remove the review's own rendered receipt while retaining every other gate."""
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        return content
    rows = [row for row in reader if row.get("id") != "dashboard_human_review"]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=reader.fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def normalize_public_status_dashboard_receipt(  # ruff:ignore[too-many-locals,too-many-branches]
    content: bytes,
    baseline: bytes,
) -> bytes:
    """Restore fields derived from the dashboard review itself.

    Release readiness consumes the dashboard review, so its resulting status
    booleans cannot also invalidate that same review without creating a cycle.
    Independent evidence counts and provenance fields remain unchanged.
    """
    try:
        raw_payload = json.loads(content)
        raw_baseline_payload = json.loads(baseline)
    except json.JSONDecodeError:
        return content
    if not isinstance(raw_payload, dict) or not isinstance(raw_baseline_payload, dict):
        return content
    payload = cast("dict[str, Any]", raw_payload)
    baseline_payload = cast("dict[str, Any]", raw_baseline_payload)
    for section, fields in {
        "evidence": ("evidence_release_ready", "research_publication_ready", "status"),
        "publication": ("status",),
    }.items():
        current_section = payload.get(section)
        baseline_section = baseline_payload.get(section)
        if isinstance(current_section, dict) and isinstance(baseline_section, dict):
            current_typed = cast("dict[str, Any]", current_section)
            baseline_typed = cast("dict[str, Any]", baseline_section)
            for field in fields:
                if field in baseline_typed:
                    current_typed[field] = baseline_typed[field]
    blockers = payload.get("blockers")
    baseline_blockers = baseline_payload.get("blockers")
    if not isinstance(blockers, list) or not isinstance(baseline_blockers, list):
        return content
    blocker_rows = cast("list[Any]", blockers)
    baseline_rows = cast("list[Any]", baseline_blockers)
    self_derived_blockers = {
        "dashboard_human_review",
        "evidence_release",
        "research_publication",
    }
    baseline_receipts: list[dict[str, Any]] = []
    for row in baseline_rows:
        if not isinstance(row, dict):
            continue
        typed_row = cast("dict[str, Any]", row)
        if typed_row.get("id") in self_derived_blockers:
            baseline_receipts.append(typed_row)
    normalized_rows: list[Any] = []
    for row in blocker_rows:
        is_self_derived_receipt = (
            isinstance(row, dict) and cast("dict[str, Any]", row).get("id") in self_derived_blockers
        )
        if not is_self_derived_receipt:
            normalized_rows.append(row)
    for baseline_receipt in baseline_receipts:
        baseline_index = baseline_rows.index(baseline_receipt)
        normalized_rows.insert(min(baseline_index, len(normalized_rows)), baseline_receipt)
    payload["blockers"] = normalized_rows
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def normalize_csv_receipt(
    content: bytes,
    baseline: bytes,
    *,
    key: str,
    value: str,
) -> bytes:
    """Restore one self-derived CSV receipt from the reviewed commit."""
    current_reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    baseline_reader = csv.DictReader(io.StringIO(baseline.decode("utf-8")))
    if current_reader.fieldnames is None or baseline_reader.fieldnames != current_reader.fieldnames:
        return content
    current_rows = list(current_reader)
    baseline_rows = list(baseline_reader)
    baseline_receipt = next((row for row in baseline_rows if row.get(key) == value), None)
    if baseline_receipt is None:
        return content
    normalized_rows = [row for row in current_rows if row.get(key) != value]
    baseline_index = baseline_rows.index(baseline_receipt)
    normalized_rows.insert(min(baseline_index, len(normalized_rows)), baseline_receipt)
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=current_reader.fieldnames,
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(normalized_rows)
    return output.getvalue().encode("utf-8")


def _git_file_at_commit(repo: Path, commit: str, path: Path) -> bytes | None:
    """Read one reviewed file without trusting mutable working-tree receipts."""
    if len(commit) != 40 or any(character not in "0123456789abcdef" for character in commit):
        return None
    result = subprocess.run(  # nosec B603 - no shell; commit is a validated SHA.
        ("git", "show", f"{commit}:{path.as_posix()}"),
        cwd=repo,
        check=False,
        capture_output=True,
    )
    return result.stdout if result.returncode == 0 else None


def _json_at_commit(repo: Path, commit: str, path: Path) -> dict[str, Any]:
    """Read one historical JSON object used to verify a standing approval."""
    content = _git_file_at_commit(repo, commit, path)
    if content is None:
        return {}
    try:
        value = json.loads(content)
    except UnicodeDecodeError, json.JSONDecodeError:
        return {}
    return cast("dict[str, Any]", value) if isinstance(value, dict) else {}


def _commits_touching(repo: Path, path: Path, *, limit: int = 64) -> tuple[str, ...]:
    """Return a bounded newest-first history for an approval receipt path."""
    result = subprocess.run(  # nosec B603 - fixed shell-free git reader.
        ("git", "log", f"--max-count={limit}", "--format=%H", "--", path.as_posix()),
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ()
    return tuple(
        commit
        for commit in result.stdout.splitlines()
        if len(commit) == 40 and all(character in "0123456789abcdef" for character in commit)
    )


def _approval_receipt_matches(snapshot: dict[str, Any], current: dict[str, Any]) -> bool:
    """Compare only immutable fields that define the bounded approval decision."""
    fields = (
        "status",
        "reviewed_at",
        "reviewer",
        "commit",
        "automated_packet_sha256",
        "owner_packet_sha256",
        "scope",
    )
    return bool(snapshot) and all(snapshot.get(field) == current.get(field) for field in fields)


def _approved_packet_bytes(
    repo: Path,
    human: dict[str, Any],
) -> tuple[bytes, bytes] | None:
    """Resolve packet bytes from the tested commit or later immutable receipt commit."""
    reviewed_commit = human.get("commit")
    if not isinstance(reviewed_commit, str):
        return None
    candidates = (reviewed_commit, *_commits_touching(repo, HUMAN_PATH))
    for commit in dict.fromkeys(candidates):
        if commit != reviewed_commit and not _approval_receipt_matches(
            _json_at_commit(repo, commit, HUMAN_PATH), human
        ):
            continue
        automated = _git_file_at_commit(repo, commit, AUTOMATED_PATH)
        owner = _git_file_at_commit(repo, commit, OWNER_PATH)
        if automated is None or owner is None:
            continue
        if (
            human.get("automated_packet_sha256") == hashlib.sha256(automated).hexdigest()
            and human.get("owner_packet_sha256") == hashlib.sha256(owner).hexdigest()
        ):
            return automated, owner
    return None


def _standing_approval_valid(
    repo: Path,
    *,
    automated: dict[str, Any],
    owner: dict[str, Any],
    human: dict[str, Any],
    source_fingerprint: str,
) -> bool:
    """Reuse bounded review only when its immutable scope and UI are unchanged."""
    reviewed_commit = human.get("commit")
    if not isinstance(reviewed_commit, str):
        return False
    approved_packet_bytes = _approved_packet_bytes(repo, human)
    if approved_packet_bytes is None:
        return False
    reviewed_automated_bytes, reviewed_owner_bytes = approved_packet_bytes
    try:
        raw_reviewed_automated = json.loads(reviewed_automated_bytes)
        raw_reviewed_owner = json.loads(reviewed_owner_bytes)
    except UnicodeDecodeError, json.JSONDecodeError:
        return False
    if not isinstance(raw_reviewed_automated, dict) or not isinstance(raw_reviewed_owner, dict):
        return False
    reviewed_automated = cast("dict[str, Any]", raw_reviewed_automated)
    reviewed_owner = cast("dict[str, Any]", raw_reviewed_owner)
    scope = human.get("scope")
    human_scope = cast("dict[str, Any]", scope) if isinstance(scope, dict) else {}
    raw_assertions = reviewed_owner.get("provenance_assertions")
    reviewed_assertions = (
        cast("list[dict[str, Any]]", raw_assertions) if isinstance(raw_assertions, list) else []
    )
    raw_prohibited = reviewed_owner.get("prohibited_content_check")
    reviewed_prohibited = (
        cast("dict[str, Any]", raw_prohibited) if isinstance(raw_prohibited, dict) else {}
    )
    return bool(
        reviewed_automated.get("status") == "pass"
        and reviewed_automated.get("coverage_complete") is True
        and reviewed_automated.get("screenshot_count") == 44
        and bool(reviewed_assertions)
        and all(item.get("status") == "pass" for item in reviewed_assertions)
        and reviewed_prohibited.get("status") == "pass"
        and human_scope.get("routes") == list(EXPECTED_ROUTES)
        and reviewed_automated.get("source_fingerprint") == source_fingerprint
        and reviewed_owner.get("source_fingerprint") == source_fingerprint
        and automated.get("source_fingerprint") == source_fingerprint
        and owner.get("source_fingerprint") == source_fingerprint
        and reviewed_automated.get("routes") == list(EXPECTED_ROUTES)
        and automated.get("routes") == list(EXPECTED_ROUTES)
        and reviewed_automated.get("projects") == list(EXPECTED_PROJECTS)
        and automated.get("projects") == list(EXPECTED_PROJECTS)
    )


def _approval_binding(
    repo: Path,
    *,
    automated: dict[str, Any],
    owner: dict[str, Any],
    human: dict[str, Any],
    source_fingerprint: str,
) -> tuple[str, bool]:
    """Return the current approval mode and whether its binding is valid."""
    exact = bool(
        human.get("commit") == automated.get("tested_commit")
        and human.get("automated_packet_sha256") == _sha256(repo / AUTOMATED_PATH)
        and human.get("owner_packet_sha256") == _sha256(repo / OWNER_PATH)
    )
    if exact:
        return "exact_packet", True
    standing = _standing_approval_valid(
        repo,
        automated=automated,
        owner=owner,
        human=human,
        source_fingerprint=source_fingerprint,
    )
    return ("standing_scoped", True) if standing else ("invalid", False)


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


def _workflow_metadata(automated: dict[str, Any], human: dict[str, Any]) -> dict[str, Any]:
    """Return complete hosted-run metadata, preferring machine evidence."""
    workflow = automated.get("workflow")
    workflow_data = cast("dict[str, Any]", workflow) if isinstance(workflow, dict) else {}
    if workflow_data and all(
        bool(workflow_data.get(field))
        for field in ("workflow", "run_id", "run_attempt", "artifact_name", "workflow_url")
    ):
        return workflow_data
    reviewed_workflow = human.get("workflow")
    return cast("dict[str, Any]", reviewed_workflow) if isinstance(reviewed_workflow, dict) else {}


def dashboard_review_evidence(repo: Path) -> dict[str, object]:
    """Return named dashboard gate checks for diagnostics and readiness."""
    automated = _read_json(repo / AUTOMATED_PATH)
    owner = _read_json(repo / OWNER_PATH)
    human = _read_json(repo / HUMAN_PATH)
    evidence_head = (
        human.get("commit") or owner.get("tested_commit") or automated.get("tested_commit")
    )
    workflow_data = _workflow_metadata(automated, human)
    raw_assertions = owner.get("provenance_assertions")
    assertions = (
        cast("list[dict[str, Any]]", raw_assertions) if isinstance(raw_assertions, list) else []
    )
    raw_prohibited = owner.get("prohibited_content_check")
    prohibited = cast("dict[str, Any]", raw_prohibited) if isinstance(raw_prohibited, dict) else {}
    source_fingerprint = dashboard_source_fingerprint(repo)
    data_fingerprint = dashboard_data_fingerprint(
        repo,
        self_attestation_commit=(
            cast("str", automated["tested_commit"])
            if isinstance(automated.get("tested_commit"), str)
            else None
        ),
    )
    approval_mode, approval_binding_valid = _approval_binding(
        repo,
        automated=automated,
        owner=owner,
        human=human,
        source_fingerprint=source_fingerprint,
    )
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
        "head_parity": bool(automated.get("tested_commit"))
        and automated.get("tested_commit") == owner.get("tested_commit")
        and automated.get("source_fingerprint") == source_fingerprint
        and owner.get("source_fingerprint") == source_fingerprint,
        "displayed_data_parity": (
            automated.get("data_fingerprint") == data_fingerprint
            and owner.get("data_fingerprint") == data_fingerprint
        ),
        "provenance_assertions_pass": bool(assertions)
        and all(item.get("status") == "pass" for item in assertions),
        "prohibited_content_pass": prohibited.get("status") == "pass",
        "human_scoped_approval": (
            human.get("status") == "approved_within_scope"
            and bool(human.get("reviewed_at"))
            and bool(human.get("reviewer"))
            and approval_binding_valid
        ),
        "packet_hash_parity": approval_binding_valid,
    }
    # Generated readiness output must describe the evidence, not an ephemeral
    # pull-request merge commit. The checkout SHA remains part of the parity
    # predicate above and is deliberately not serialized.
    return {"head": evidence_head, "approval_mode": approval_mode, "checks": checks}


def dashboard_review_approved(repo: Path) -> bool:
    """Return true only when every machine and accountable-review gate passes."""
    evidence = dashboard_review_evidence(repo)
    checks = cast("dict[str, bool]", evidence["checks"])
    return all(checks.values())
