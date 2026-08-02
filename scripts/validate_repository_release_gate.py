"""Fail unless the repository-owned software release gate is ready."""

from __future__ import annotations

import json

from reimburse_atlas.registry import project_root


def main() -> None:
    """Validate the software release gate without asserting research readiness."""
    root = project_root()
    summary_path = root / "data/derived/release_readiness/summary.json"
    if not summary_path.is_file():
        message = f"missing release-readiness summary: {summary_path}"
        raise SystemExit(message)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    result = {
        "status": "ready" if summary.get("repository_release_ready") is True else "blocked",
        "reason_code": (
            "repository_release_gate_pass"
            if summary.get("repository_release_ready") is True
            else "repository_release_gate_pending"
        ),
        "evidence": "data/derived/release_readiness/summary.json",
        "repository_release_ready": summary.get("repository_release_ready"),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "ready":
        message = "repository software release gate is not ready"
        raise SystemExit(message)


if __name__ == "__main__":
    main()
