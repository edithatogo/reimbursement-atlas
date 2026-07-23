"""Plan, create, reserve, publish, or verify a gated Zenodo deposition."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.archive_publication import archive_publication_gate
from reimburse_atlas.registry import project_root

DEFAULT_API = "https://zenodo.org/api"
ALLOWED_API_HOSTS = {"zenodo.org", "sandbox.zenodo.org"}
EVIDENCE = Path("data/derived/zenodo/external_state.json")


class ZenodoError(RuntimeError):
    """Raised for a redacted Zenodo API failure."""


def _request(
    method: str,
    url: str,
    token: str,
    payload: dict[str, Any] | None = None,
    content: bytes | None = None,
) -> dict[str, Any]:
    data = (
        content
        if content is not None
        else (json.dumps(payload).encode() if payload is not None else None)
    )
    headers = {"Authorization": f"Bearer {token}"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(  # ruff:ignore[suspicious-url-open-usage]
        url, data=data, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:  # ruff:ignore[suspicious-url-open-usage]
            body = response.read()
    except urllib.error.HTTPError as exc:
        safe_url = url.split("?", maxsplit=1)[0]
        message = f"Zenodo API returned HTTP {exc.code} for {method} {safe_url}"
        raise ZenodoError(message) from exc
    except urllib.error.URLError as exc:
        message = f"Zenodo API request failed for {method} {url.split('?', maxsplit=1)[0]}"
        raise ZenodoError(message) from exc
    return cast("dict[str, Any]", json.loads(body)) if body else {}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_api_url(api_url: str) -> str:
    """Allow credentials only on official HTTPS Zenodo API endpoints."""
    parsed = urllib.parse.urlsplit(api_url)
    if (
        parsed.scheme != "https"
        or parsed.hostname not in ALLOWED_API_HOSTS
        or parsed.query
        or parsed.fragment
        or parsed.path.rstrip("/") != "/api"
    ):
        message = "Zenodo API URL must be the HTTPS /api endpoint on Zenodo or its sandbox"
        raise ValueError(message)
    return api_url.rstrip("/")


def _load_inputs(root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    metadata = cast(
        "dict[str, Any]",
        json.loads(
            (root / "data/derived/zenodo/deposition_metadata.json").read_text(encoding="utf-8")
        ),
    )
    inventory = cast(
        "dict[str, Any]",
        json.loads((root / "data/derived/zenodo/file_inventory.json").read_text(encoding="utf-8")),
    )
    files = cast("list[dict[str, Any]]", inventory.get("files", []))
    if inventory.get("status") != "frozen" or not files:
        message = "Zenodo file inventory is not frozen"
        raise ValueError(message)
    for row in files:
        path = root / str(row["path"])
        if (
            not path.is_file()
            or path.stat().st_size != int(row["byte_size"])
            or _sha256(path) != row["sha256"]
        ):
            message = f"Zenodo inventory drift: {row['path']}"
            raise ValueError(message)
    return metadata, files


def _write_evidence(root: Path, payload: dict[str, Any]) -> None:
    path = root / EVIDENCE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(
    root: Path,
    *,
    mode: str,
    api_url: str,
    token: str | None,
    deposition_id: str | None,
    confirmation: str | None,
) -> dict[str, Any]:
    """Execute one explicit, fail-closed deposition transition."""
    api_url = validate_api_url(api_url)
    metadata, files = _load_inputs(root)
    gate = archive_publication_gate(root)
    result: dict[str, Any] = {
        "schema_version": "zenodo-external-state-v1",
        "mode": mode,
        "api_url": api_url,
        "publication_gate": gate,
        "mutation_performed": False,
        "paper_or_preprint_included": False,
    }
    if mode == "plan":
        result["status"] = (
            "ready_for_draft" if gate["summary"]["repository_release_ready"] else ("blocked")
        )
        return result
    if not token:
        message = "ZENODO_TOKEN is required for mutating or remote verification modes"
        raise ValueError(message)
    if mode == "draft":
        if confirmation != "CREATE_ZENODO_DRAFT":
            message = "draft mode requires --confirm CREATE_ZENODO_DRAFT"
            raise ValueError(message)
        response = _request("POST", f"{api_url}/deposit/depositions", token, {"metadata": metadata})
        bucket = str(cast("dict[str, Any]", response["links"])["bucket"])
        for row in files:
            path = root / str(row["path"])
            _request("PUT", f"{bucket}/{path.name}", token, content=path.read_bytes())
        result.update({
            "status": "draft_created",
            "mutation_performed": True,
            "deposition_id": str(response["id"]),
            "draft_url": cast("dict[str, Any]", response["links"]).get("html"),
            "uploaded_files": files,
        })
        return result
    if not deposition_id:
        message = "--deposition-id is required for reserve, publish, and verify"
        raise ValueError(message)
    endpoint = f"{api_url}/deposit/depositions/{deposition_id}"
    if mode == "reserve":
        if gate["status"] != "ready" or confirmation != "RESERVE_ZENODO_DOI":
            message = "DOI reservation requires all upstream gates and exact confirmation"
            raise ValueError(message)
        reserved = {**metadata, "prereserve_doi": True}
        response = _request("PUT", endpoint, token, {"metadata": reserved})
        result.update({
            "status": "doi_reserved",
            "mutation_performed": True,
            "deposition_id": deposition_id,
            "reserved_doi": cast("dict[str, Any]", response.get("metadata", {})).get(
                "prereserve_doi"
            ),
        })
        return result
    if mode == "publish":
        if gate["status"] != "ready" or confirmation != "PUBLISH_ZENODO_RECORD":
            message = "publication requires all upstream gates and exact confirmation"
            raise ValueError(message)
        response = _request("POST", f"{endpoint}/actions/publish", token)
        result.update({
            "status": "published",
            "mutation_performed": True,
            "deposition_id": deposition_id,
            "doi": response.get("doi"),
            "record_url": response.get("record_url"),
        })
        return result
    response = _request("GET", endpoint, token)
    result.update({
        "status": "verified",
        "deposition_id": deposition_id,
        "submitted": response.get("submitted"),
        "doi": response.get("doi"),
        "record_url": response.get("record_url"),
        "remote_file_count": len(cast("list[Any]", response.get("files", []))),
    })
    return result


def main() -> None:
    """Run one explicit Zenodo transition and retain redacted evidence."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("plan", "draft", "reserve", "publish", "verify"))
    parser.add_argument("--api-url", default=os.getenv("ZENODO_API_URL", DEFAULT_API))
    parser.add_argument("--deposition-id")
    parser.add_argument("--confirm")
    args = parser.parse_args()
    root = project_root()
    result = run(
        root,
        mode=args.mode,
        api_url=args.api_url.rstrip("/"),
        token=os.getenv("ZENODO_TOKEN"),
        deposition_id=args.deposition_id,
        confirmation=args.confirm,
    )
    _write_evidence(root, result)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
