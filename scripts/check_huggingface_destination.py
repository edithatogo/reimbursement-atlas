"""Read-only verification of Hugging Face dataset and Space metadata."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from reimburse_atlas.registry import project_root

DEFAULT_DATASET_REPO = "edithatogo/reimbursement-atlas"
DEFAULT_SPACE_REPO = "edithatogo/reimbursement-atlas"
API_ROOT = "https://huggingface.co/api"
Fetcher = Callable[[str], tuple[dict[str, Any], str | None]]


def _fetch_json(url: str) -> tuple[dict[str, Any], str | None]:
    """Fetch public repository metadata without credentials or mutation."""
    if not url.startswith(f"{API_ROOT}/"):
        return {}, "refusing to request a URL outside the fixed Hugging Face API"
    request = Request(  # noqa: S310 - URL is constrained to the public HTTPS API below
        url,
        headers={"Accept": "application/json", "User-Agent": "reimbursement-atlas"},
    )
    try:
        with urlopen(request, timeout=20) as response:  # nosec B310 - fixed HTTPS API endpoint
            raw_payload: object = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        return {}, str(exc)
    if not isinstance(raw_payload, dict):
        return {}, "Hugging Face API response was not a JSON object"
    payload = cast("dict[str, Any]", raw_payload)
    return payload, None


def _card_value(payload: dict[str, Any], key: str) -> str | None:
    """Read a card field from cardData or top-level metadata."""
    card = payload.get("cardData")
    if isinstance(card, dict):
        card_data = cast("dict[str, Any]", card)
        if card_data.get(key) is not None:
            return str(card_data[key]).strip().lower()
    value = payload.get(key)
    return str(value).strip().lower() if value is not None else None


def _target(
    kind: str,
    repo: str,
    expected: dict[str, str],
    fetcher: Fetcher,
) -> dict[str, Any]:
    """Return a redacted verification record for one public target."""
    encoded_repo = quote(repo, safe="/")
    url = f"{API_ROOT}/{kind}/{encoded_repo}"
    payload, error = fetcher(url)
    remote_id = str(payload.get("id", "")).strip() or None
    observed = {key: _card_value(payload, key) for key in expected}
    mismatches: list[str] = []
    if error:
        mismatches.append(f"metadata request failed: {error}")
    if remote_id != repo:
        mismatches.append(f"remote id is {remote_id!r}, expected {repo!r}")
    for key, expected_value in expected.items():
        if observed[key] != expected_value:
            mismatches.append(
                f"{key} is {observed[key]!r}, expected governed value {expected_value!r}"
            )
    return {
        "kind": kind,
        "repo": repo,
        "endpoint": url,
        "reachable": not bool(error),
        "remote_id": remote_id,
        "observed": observed,
        "expected": expected,
        "mismatches": mismatches,
        "status": "pass" if not mismatches else "drift",
    }


def destination_report(
    dataset_repo: str,
    space_repo: str,
    fetcher: Fetcher = _fetch_json,
) -> dict[str, Any]:
    """Build a read-only destination report without raw card or file payloads."""
    dataset = _target("datasets", dataset_repo, {"license": "other"}, fetcher)
    space = _target("spaces", space_repo, {"license": "apache-2.0", "sdk": "static"}, fetcher)
    mismatches = [*dataset["mismatches"], *space["mismatches"]]
    return {
        "schema_version": "huggingface-destination-check-v1",
        "mutation_performed": False,
        "candidate_contract": {
            "dataset_license": "other",
            "space_license": "apache-2.0",
            "space_sdk": "static",
            "source_data_license_boundary": "source-specific",
            "evidence_path": "docs/HUGGINGFACE_PUBLICATION.md",
        },
        "targets": {"dataset": dataset, "space": space},
        "status": "pass" if not mismatches else "drift",
        "mismatch_count": len(mismatches),
    }


def _args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset-repo",
        default=os.environ.get("HF_DATASET_REPO", DEFAULT_DATASET_REPO),
    )
    parser.add_argument(
        "--space-repo",
        default=os.environ.get("HF_SPACE_REPO", DEFAULT_SPACE_REPO),
    )
    parser.add_argument("--output", type=Path, help="Write the redacted JSON report to this path.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the read-only check and fail when live metadata drifts."""
    args = _args(argv)
    report = destination_report(args.dataset_repo, args.space_repo)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else project_root() / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if report["status"] != "pass":
        print(
            "Hugging Face destination metadata drift detected; no remote mutation was attempted.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
