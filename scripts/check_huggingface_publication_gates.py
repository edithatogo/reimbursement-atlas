"""Fail closed before mutating a Hugging Face dataset or Space."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.registry import project_root


def _read_json(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError, ValueError:
        return {}
    return cast("dict[str, Any]", value) if isinstance(value, dict) else {}


def publication_gate_failures(root: Path | None = None) -> list[str]:
    """Return every licence, research or release gate blocking HF mutation."""
    repo = root or project_root()
    failures: list[str] = []
    release = _read_json(repo, "data/derived/release_readiness/summary.json")
    for key in (
        "repository_release_ready",
        "research_publication_ready",
        "evidence_release_ready",
        "policy_claims_ready",
    ):
        if release.get(key) is not True:
            failures.append(f"release readiness flag is not true: {key}")

    protocol = _read_json(repo, "data/derived/protocols/summary.json")
    if int(protocol.get("osf_ready_count", 0)) < int(protocol.get("protocol_count", 0)):
        failures.append("not every protocol is OSF-ready")

    contracts = _read_json(repo, "data/derived/source_contracts/summary.json")
    if any(int(contracts.get(key, 0)) for key in ("fail", "missing", "blocking_failures")):
        failures.append("source-contract validation has failures, missing records or blockers")

    quality = _read_json(repo, "data/derived/data_quality/summary.json")
    if any(int(quality.get(key, 0)) for key in ("fail", "missing", "blocking_failures")):
        failures.append("data-quality validation has failures, missing records or blockers")

    manifest_path = repo / "data" / "derived" / "publication_manifest.json"
    manifest: dict[str, Any]
    try:
        value = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest = cast("dict[str, Any]", value) if isinstance(value, dict) else {}
    except OSError, ValueError:
        manifest = {}
    raw_artifacts = manifest.get("artifacts", [])
    if isinstance(raw_artifacts, list):
        artifacts = cast("list[dict[str, Any]]", raw_artifacts)
    else:
        artifacts = []
    if not artifacts:
        failures.append("publication manifest has no artefacts")
    for artifact in artifacts:
        if artifact.get("contains_raw_source_payload") is True:
            failures.append(
                f"raw source payload marked for publication: {artifact.get('relative_path')}"
            )
        if artifact.get("licence_gate") != "permissive_candidate":
            failures.append(
                f"licence review is incomplete: {artifact.get('relative_path')} "
                f"({artifact.get('licence_gate')})"
            )
    return failures


def main() -> None:
    """Exit non-zero when any publication mutation gate is unresolved."""
    failures = publication_gate_failures()
    if failures:
        print("Hugging Face publication blocked; no remote mutation permitted:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("Hugging Face publication gates passed; remote mutation is permitted.")


if __name__ == "__main__":
    main()
