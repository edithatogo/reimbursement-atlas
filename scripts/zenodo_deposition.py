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
DATACITE_API = "https://api.datacite.org/dois"
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
        with urllib.request.urlopen(  # nosec B310  # ruff:ignore[suspicious-url-open-usage]
            request, timeout=120
        ) as response:
            body = response.read()
    except urllib.error.HTTPError as exc:
        safe_url = url.split("?", maxsplit=1)[0]
        message = f"Zenodo API returned HTTP {exc.code} for {method} {safe_url}"
        raise ZenodoError(message) from exc
    except urllib.error.URLError as exc:
        message = f"Zenodo API request failed for {method} {url.split('?', maxsplit=1)[0]}"
        raise ZenodoError(message) from exc
    return cast("dict[str, Any]", json.loads(body)) if body else {}


def _public_json(url: str) -> tuple[dict[str, Any], str]:
    """Read a credential-free DOI/registry endpoint and return its final URL."""
    request = urllib.request.Request(  # ruff:ignore[suspicious-url-open-usage]
        url, headers={"Accept": "application/vnd.api+json"}, method="GET"
    )
    try:
        with urllib.request.urlopen(  # nosec B310  # ruff:ignore[suspicious-url-open-usage]
            request, timeout=120
        ) as response:
            body = response.read()
            final_url = response.geturl()
    except (urllib.error.HTTPError, urllib.error.URLError) as exc:
        message = "public DOI or DataCite verification failed"
        raise ZenodoError(message) from exc
    value: object = json.loads(body) if body else {}
    return cast("dict[str, Any]", value) if isinstance(value, dict) else {}, final_url


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
    required_roles = set(cast("list[str]", inventory.get("required_roles", [])))
    present_roles = {str(row.get("role", "")) for row in files}
    filenames = [str(row.get("filename", "")) for row in files]
    inventory_errors = (
        inventory.get("schema_version") != "zenodo-release-asset-inventory-v2",
        inventory.get("status") != "frozen",
        inventory.get("missing_roles") != [],
        not required_roles,
        not files,
        not required_roles.issubset(present_roles),
        any(not filename for filename in filenames),
        len(filenames) != len(set(filenames)),
    )
    if any(inventory_errors):
        message = "Zenodo v2 release asset inventory is incomplete or not frozen"
        raise ValueError(message)
    for row in files:
        path = root / str(row["path"])
        sha256 = str(row.get("sha256", ""))
        md5 = str(row.get("md5", ""))
        row_errors = (
            not path.is_file(),
            path.is_file() and path.stat().st_size != int(row["byte_size"]),
            len(sha256) != 64,
            path.is_file() and _sha256(path) != sha256,
            len(md5) != 32,
            path.is_file()
            and hashlib.md5(path.read_bytes(), usedforsecurity=False).hexdigest() != md5,
        )
        if any(row_errors):
            message = f"Zenodo inventory drift: {row['path']}"
            raise ValueError(message)
    return metadata, files


def _require_archive_gate(gate: dict[str, Any], mode: str) -> None:
    if gate.get("status") != "ready":
        missing = ", ".join(cast("list[str]", gate.get("missing_or_false", [])))
        message = f"{mode} requires the full archive publication gate; blocked by: {missing}"
        raise ValueError(message)


def _remote_file_parity(
    local_files: list[dict[str, Any]], remote_files: list[dict[str, Any]]
) -> dict[str, Any]:
    """Compare the frozen local inventory with Zenodo's remote file evidence."""
    expected = {str(row["filename"]): row for row in local_files}
    observed: dict[str, dict[str, Any]] = {}
    for raw in remote_files:
        key = str(raw.get("key") or raw.get("filename") or "")
        if key:
            observed[key] = raw
    mismatches: list[dict[str, str]] = []
    for filename, local in expected.items():
        remote = observed.get(filename)
        if remote is None:
            mismatches.append({"filename": filename, "reason": "missing_remote_file"})
            continue
        if int(remote.get("size", remote.get("filesize", -1))) != int(local["byte_size"]):
            mismatches.append({"filename": filename, "reason": "byte_size_mismatch"})
        checksum = str(remote.get("checksum", ""))
        accepted = {f"md5:{local['md5']}", f"sha256:{local['sha256']}"}
        if checksum not in accepted:
            mismatches.append({"filename": filename, "reason": "checksum_mismatch"})
    for filename in sorted(set(observed) - set(expected)):
        mismatches.append({"filename": filename, "reason": "unexpected_remote_file"})
    return {
        "status": "pass" if not mismatches else "fail",
        "expected_file_count": len(expected),
        "remote_file_count": len(observed),
        "mismatches": mismatches,
    }


def _normalise_metadata_value(value: object) -> object:
    if isinstance(value, list):
        normalised = [_normalise_metadata_value(item) for item in cast("list[object]", value)]
        return sorted(normalised, key=lambda item: json.dumps(item, sort_keys=True))
    if isinstance(value, dict):
        mapping = cast("dict[str, object]", value)
        return {
            str(key): _normalise_metadata_value(item)
            for key, item in sorted(mapping.items())
            if key != "prereserve_doi"
        }
    return value


def _remote_metadata_parity(local: dict[str, Any], remote: dict[str, Any]) -> dict[str, object]:
    """Compare the publication-critical Zenodo metadata fields."""
    fields = (
        "title",
        "upload_type",
        "description",
        "creators",
        "keywords",
        "license",
        "version",
        "related_identifiers",
    )
    mismatches = [
        field
        for field in fields
        if _normalise_metadata_value(local.get(field))
        != _normalise_metadata_value(remote.get(field))
    ]
    return {"status": "pass" if not mismatches else "fail", "mismatched_fields": mismatches}


def _value_at(value: dict[str, Any], path: str) -> object:
    current: object = value
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = cast("dict[str, object]", current).get(part)
    return current


def _datacite_parity(local: dict[str, Any], payload: dict[str, Any]) -> dict[str, object]:
    attributes = cast(
        "dict[str, Any]", cast("dict[str, Any]", payload.get("data", {})).get("attributes", {})
    )
    titles = cast("list[dict[str, Any]]", attributes.get("titles", []))
    creators = cast("list[dict[str, Any]]", attributes.get("creators", []))
    expected_orcids = {
        str(item.get("orcid", "")).removeprefix("https://orcid.org/")
        for item in cast("list[dict[str, Any]]", local.get("creators", []))
        if item.get("orcid")
    }
    observed_orcids = {
        str(identifier.get("nameIdentifier", "")).removeprefix("https://orcid.org/")
        for creator in creators
        for identifier in cast("list[dict[str, Any]]", creator.get("nameIdentifiers", []))
        if identifier.get("nameIdentifierScheme") == "ORCID"
    }
    checks = {
        "title": bool(titles) and titles[0].get("title") == local.get("title"),
        "publisher": attributes.get("publisher") == "Zenodo",
        "version": str(attributes.get("version")) == str(local.get("version")),
        "resource_type": _value_at(attributes, "types.resourceTypeGeneral") == "Software",
        "creator_orcids": expected_orcids.issubset(observed_orcids),
    }
    return {"status": "pass" if all(checks.values()) else "fail", "checks": checks}


def _require_remote_draft_parity(
    response: dict[str, Any],
    metadata: dict[str, Any],
    files: list[dict[str, Any]],
    *,
    require_reserved_doi: bool,
) -> tuple[dict[str, object], dict[str, object]]:
    file_parity = _remote_file_parity(
        files, cast("list[dict[str, Any]]", response.get("files", []))
    )
    remote_metadata = cast("dict[str, Any]", response.get("metadata", {}))
    metadata_parity = _remote_metadata_parity(metadata, remote_metadata)
    if file_parity["status"] != "pass" or metadata_parity["status"] != "pass":
        message = "Zenodo draft file or metadata parity failed"
        raise ValueError(message)
    if require_reserved_doi and not remote_metadata.get("prereserve_doi"):
        message = "Zenodo publication requires a reserved version DOI"
        raise ValueError(message)
    return file_parity, metadata_parity


def _write_evidence(root: Path, payload: dict[str, Any]) -> None:
    path = root / EVIDENCE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(  # ruff:ignore[too-many-locals,too-many-branches,too-many-statements]
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
        result["status"] = "ready_for_draft" if gate["status"] == "ready" else "blocked"
        return result
    if mode in {"draft", "reserve", "publish"}:
        _require_archive_gate(gate, mode)
    if not token:
        message = "ZENODO_TOKEN is required for mutating or remote verification modes"
        raise ValueError(message)
    metadata, files = _load_inputs(root)
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
        if confirmation != "RESERVE_ZENODO_DOI":
            message = "DOI reservation requires all upstream gates and exact confirmation"
            raise ValueError(message)
        draft = _request("GET", endpoint, token)
        file_parity, metadata_parity = _require_remote_draft_parity(
            draft, metadata, files, require_reserved_doi=False
        )
        reserved = {**metadata, "prereserve_doi": True}
        response = _request("PUT", endpoint, token, {"metadata": reserved})
        result.update({
            "status": "doi_reserved",
            "mutation_performed": True,
            "deposition_id": deposition_id,
            "reserved_doi": cast("dict[str, Any]", response.get("metadata", {})).get(
                "prereserve_doi"
            ),
            "remote_file_parity": file_parity,
            "remote_metadata_parity": metadata_parity,
        })
        return result
    if mode == "publish":
        if confirmation != "PUBLISH_ZENODO_RECORD":
            message = "publication requires all upstream gates and exact confirmation"
            raise ValueError(message)
        draft = _request("GET", endpoint, token)
        file_parity, metadata_parity = _require_remote_draft_parity(
            draft, metadata, files, require_reserved_doi=True
        )
        response = _request("POST", f"{endpoint}/actions/publish", token)
        result.update({
            "status": "published",
            "mutation_performed": True,
            "deposition_id": deposition_id,
            "doi": response.get("doi"),
            "record_url": response.get("record_url"),
            "remote_file_parity": file_parity,
            "remote_metadata_parity": metadata_parity,
        })
        return result
    response = _request("GET", endpoint, token)
    remote_files = cast("list[dict[str, Any]]", response.get("files", []))
    parity = _remote_file_parity(files, remote_files)
    metadata_parity = _remote_metadata_parity(
        metadata, cast("dict[str, Any]", response.get("metadata", {}))
    )
    if parity["status"] != "pass" or metadata_parity["status"] != "pass":
        message = "Zenodo remote verification parity failed"
        raise ValueError(message)
    result.update({
        "status": "verified",
        "deposition_id": deposition_id,
        "submitted": response.get("submitted"),
        "doi": response.get("doi"),
        "record_url": response.get("record_url"),
        "remote_file_count": len(remote_files),
        "remote_checksum_parity": parity,
        "remote_metadata_parity": metadata_parity,
    })
    if response.get("submitted") is True and isinstance(response.get("doi"), str):
        doi = str(response["doi"])
        if not doi.startswith("10."):
            message = "Zenodo returned an invalid DOI"
            raise ValueError(message)
        quoted_doi = urllib.parse.quote(doi, safe="/")
        _, resolved_url = _public_json(f"https://doi.org/{quoted_doi}")
        datacite, _ = _public_json(f"{DATACITE_API}/{quoted_doi}")
        datacite_parity = _datacite_parity(metadata, datacite)
        if datacite_parity["status"] != "pass":
            message = "DataCite metadata parity failed"
            raise ValueError(message)
        result.update({
            "status": "verified_public",
            "public_doi_resolution": {
                "status": "pass",
                "doi": doi,
                "resolved_url": resolved_url,
            },
            "datacite_parity": datacite_parity,
            "version_doi": doi,
            "concept_doi": cast("dict[str, Any]", response.get("metadata", {})).get("conceptdoi"),
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
