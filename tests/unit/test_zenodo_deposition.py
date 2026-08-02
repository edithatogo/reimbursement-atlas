from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Self

import pytest

from scripts import zenodo_deposition
from scripts.zenodo_deposition import run, validate_api_url


@pytest.mark.parametrize(
    "url",
    [
        "http://zenodo.org/api",
        "https://example.com/api",
        "https://zenodo.org/api?token=secret",
        "file:///api",
    ],
)
def test_api_url_rejects_token_exfiltration_targets(url: str) -> None:
    with pytest.raises(ValueError, match="Zenodo API URL"):
        validate_api_url(url)


@pytest.mark.parametrize(
    "url",
    ["https://zenodo.org/api", "https://sandbox.zenodo.org/api/"],
)
def test_api_url_accepts_official_endpoints(url: str) -> None:
    assert validate_api_url(url).endswith("/api")


@pytest.mark.parametrize(
    "asset_name",
    [
        "release-manifest.json",
        "cyclonedx-python.json",
        "reimbursement_atlas-0.1.1-py3-none-any.whl.json",
        "reimbursement_atlas-0.1.1-py3-none-any.whl",
        "reimbursement-atlas-v0.1.1.tar.gz",
    ],
)
def test_release_asset_request_declares_octet_stream(
    monkeypatch: pytest.MonkeyPatch,
    asset_name: str,
) -> None:
    captured: urllib.request.Request | None = None

    class Response:
        def __enter__(self) -> Self:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        @staticmethod
        def read() -> bytes:
            return b"{}"

    def fake_urlopen(request: urllib.request.Request, *, timeout: int) -> Response:
        nonlocal captured
        captured = request
        assert timeout == 120
        return Response()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    zenodo_deposition._request(  # ruff:ignore[private-member-access]
        "PUT",
        f"https://zenodo.org/api/files/bucket/{asset_name}",
        "token",
        content=b"{}",
    )

    assert captured is not None
    assert captured.get_header("Content-type") == "application/octet-stream"


@pytest.mark.parametrize(
    ("mode", "confirmation", "deposition_id"),
    [("reserve", "RESERVE_ZENODO_DOI", "123"), ("publish", "PUBLISH_ZENODO_RECORD", "123")],
)
def test_mutating_modes_make_no_http_request_when_archive_gate_is_false(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
    confirmation: str,
    deposition_id: str | None,
) -> None:
    summary = tmp_path / "data/derived/release_readiness/summary.json"
    summary.parent.mkdir(parents=True)
    summary.write_text(
        json.dumps({
            "repository_release_ready": True,
            "evidence_release_ready": False,
            "osf_registration_ready": True,
            "research_publication_ready": True,
        }),
        encoding="utf-8",
    )
    called = False
    credential = tmp_path.as_posix()

    def forbidden_request(*_args: object, **_kwargs: object) -> dict[str, object]:
        nonlocal called
        called = True
        return {}

    monkeypatch.setattr(zenodo_deposition, "_request", forbidden_request)

    with pytest.raises(ValueError, match="full archive publication gate"):
        run(
            tmp_path,
            mode=mode,
            api_url="https://zenodo.org/api",
            token=credential,
            deposition_id=deposition_id,
            confirmation=confirmation,
        )

    assert called is False


def test_draft_requires_repository_release_gate_but_not_evidence_gate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A private draft can stage a released inventory before evidence publication."""
    summary = tmp_path / "data/derived/release_readiness/summary.json"
    summary.parent.mkdir(parents=True)
    summary.write_text(
        json.dumps({"repository_release_ready": True, "evidence_release_ready": False}),
        encoding="utf-8",
    )
    monkeypatch.setattr(zenodo_deposition, "_load_inputs", lambda _root: ({}, []))
    calls: list[str] = []

    def request(method: str, *_args: object, **_kwargs: object) -> dict[str, object]:
        calls.append(method)
        return {"id": 123, "links": {"bucket": "https://zenodo.org/api/files/123"}}

    monkeypatch.setattr(zenodo_deposition, "_request", request)
    credential = tmp_path.as_posix()
    result = run(
        tmp_path,
        mode="draft",
        api_url="https://zenodo.org/api",
        token=credential,
        deposition_id=None,
        confirmation="CREATE_ZENODO_DRAFT",
    )
    assert result["status"] == "draft_created"
    assert result["mode"] == "draft"
    assert calls == ["POST"]


def test_plan_is_non_mutating_and_does_not_require_inputs_or_token(tmp_path: Path) -> None:
    result = run(
        tmp_path,
        mode="plan",
        api_url="https://zenodo.org/api",
        token=None,
        deposition_id=None,
        confirmation=None,
    )

    assert result["status"] == "blocked"
    assert result["mutation_performed"] is False


def test_plan_preserves_terminal_external_receipt(tmp_path: Path) -> None:
    evidence = tmp_path / "data/derived/zenodo/external_state.json"
    evidence.parent.mkdir(parents=True)
    evidence.write_text(
        json.dumps({
            "status": "draft_created",
            "deposition_id": "21759294",
            "mutation_performed": True,
            "uploaded_file_count": 12,
        }),
        encoding="utf-8",
    )

    result = run(
        tmp_path,
        mode="plan",
        api_url="https://zenodo.org/api",
        token=None,
        deposition_id=None,
        confirmation=None,
    )

    assert result["status"] == "draft_created"
    assert result["deposition_id"] == "21759294"
    assert result["mutation_performed"] is True


def test_remote_file_parity_checks_names_sizes_and_checksums() -> None:
    local = [
        {
            "filename": "package.whl",
            "byte_size": 3,
            "sha256": "a" * 64,
            "md5": "b" * 32,
        }
    ]

    passing = zenodo_deposition._remote_file_parity(  # ruff:ignore[private-member-access]
        local,
        [{"key": "package.whl", "size": 3, "checksum": f"md5:{'b' * 32}"}],
    )
    bare_md5_passing = zenodo_deposition._remote_file_parity(  # ruff:ignore[private-member-access]
        local,
        [{"key": "package.whl", "size": 3, "checksum": "b" * 32}],
    )
    failing = zenodo_deposition._remote_file_parity(  # ruff:ignore[private-member-access]
        local,
        [
            {"key": "package.whl", "size": 4, "checksum": f"md5:{'c' * 32}"},
            {"key": "extra.txt", "size": 1, "checksum": f"md5:{'d' * 32}"},
        ],
    )

    assert passing["status"] == "pass"
    assert bare_md5_passing["status"] == "pass"
    assert failing["status"] == "fail"
    assert {row["reason"] for row in failing["mismatches"]} == {
        "byte_size_mismatch",
        "checksum_mismatch",
        "unexpected_remote_file",
    }


def test_remote_metadata_parity_checks_publication_critical_fields() -> None:
    local = {
        "title": "Atlas",
        "upload_type": "software",
        "description": "Description",
        "creators": [{"name": "Mordaunt, Dylan", "orcid": "0000-0002-9775-0603"}],
        "keywords": ["health economics", "reimbursement"],
        "license": "Apache-2.0",
        "version": "0.1.0",
        "related_identifiers": [
            {"identifier": "https://example.test", "relation": "isIdenticalTo"}
        ],
    }
    remote = {**local, "keywords": list(reversed(local["keywords"]))}

    passing = zenodo_deposition._remote_metadata_parity(local, remote)  # ruff:ignore[private-member-access]
    remote["license"] = "apache2.0"
    remote["creators"] = [{**local["creators"][0], "affiliation": None}]
    remote["related_identifiers"] = [{**local["related_identifiers"][0], "scheme": "url"}]
    equivalent = zenodo_deposition._remote_metadata_parity(  # ruff:ignore[private-member-access]
        local, remote
    )
    remote["version"] = "0.2.0"
    failing = zenodo_deposition._remote_metadata_parity(local, remote)  # ruff:ignore[private-member-access]

    assert passing["status"] == "pass"
    assert equivalent["status"] == "pass"
    assert failing == {
        "status": "fail",
        "mismatched_fields": ["version"],
        "mismatch_details": [{"field": "version", "expected": "0.1.0", "observed": "0.2.0"}],
    }


def test_parity_failure_message_distinguishes_checksums_and_metadata() -> None:
    message = zenodo_deposition._parity_failure_message(  # ruff:ignore[private-member-access]
        "remote verification",
        {
            "status": "fail",
            "mismatches": [
                {"filename": "package.whl", "reason": "checksum_mismatch"},
                {"filename": "manifest.json", "reason": "byte_size_mismatch"},
            ],
        },
        {"status": "fail", "mismatched_fields": ["version", "license"]},
    )

    assert message == (
        "Zenodo remote verification parity failed: checksum mismatch for files: package.whl; "
        "file parity mismatch for files: manifest.json; "
        "metadata mismatch in fields: license, version; "
        'mismatch_details=[{"filename": "package.whl", "reason": "checksum_mismatch"}, '
        '{"filename": "manifest.json", "reason": "byte_size_mismatch"}]'
    )


def test_parity_failure_message_identifies_metadata_only_failure() -> None:
    message = zenodo_deposition._parity_failure_message(  # ruff:ignore[private-member-access]
        "draft",
        {"status": "pass", "mismatches": []},
        {"status": "fail", "mismatched_fields": ["description"]},
    )

    assert message == "Zenodo draft parity failed: metadata mismatch in fields: description"


def test_publish_requires_remote_parity_and_reserved_doi() -> None:
    metadata = {
        "title": "Atlas",
        "upload_type": "software",
        "description": "Description",
        "creators": [],
        "keywords": [],
        "license": "Apache-2.0",
        "version": "0.1.0",
        "related_identifiers": [],
    }
    files = [{"filename": "package.whl", "byte_size": 3, "sha256": "a" * 64, "md5": "b" * 32}]
    response = {
        "metadata": metadata,
        "files": [{"key": "package.whl", "size": 3, "checksum": f"md5:{'b' * 32}"}],
    }

    with pytest.raises(ValueError, match="reserved version DOI"):
        zenodo_deposition._require_remote_draft_parity(  # ruff:ignore[private-member-access]
            response, metadata, files, require_reserved_doi=True
        )
    response["metadata"] = {**metadata, "prereserve_doi": {"doi": "10.5281/zenodo.123"}}
    file_parity, metadata_parity = zenodo_deposition._require_remote_draft_parity(  # ruff:ignore[private-member-access]
        response, metadata, files, require_reserved_doi=True
    )
    assert file_parity["status"] == "pass"
    assert metadata_parity["status"] == "pass"


def test_datacite_parity_requires_identity_and_orcid() -> None:
    local = {
        "title": "Atlas",
        "version": "0.1.0",
        "creators": [{"orcid": "0000-0002-9775-0603"}],
    }
    payload = {
        "data": {
            "attributes": {
                "titles": [{"title": "Atlas"}],
                "publisher": "Zenodo",
                "version": "0.1.0",
                "types": {"resourceTypeGeneral": "Software"},
                "creators": [
                    {
                        "nameIdentifiers": [
                            {
                                "nameIdentifier": "https://orcid.org/0000-0002-9775-0603",
                                "nameIdentifierScheme": "ORCID",
                            }
                        ]
                    }
                ],
            }
        }
    }

    assert zenodo_deposition._datacite_parity(local, payload)["status"] == "pass"  # ruff:ignore[private-member-access]
    payload["data"]["attributes"]["version"] = "0.2.0"
    assert zenodo_deposition._datacite_parity(local, payload)["status"] == "fail"  # ruff:ignore[private-member-access]


def test_load_inputs_rejects_legacy_frozen_inventory(tmp_path: Path) -> None:
    output = tmp_path / "data/derived/zenodo"
    output.mkdir(parents=True)
    (output / "deposition_metadata.json").write_text("{}\n", encoding="utf-8")
    (output / "file_inventory.json").write_text(
        json.dumps({
            "schema_version": "zenodo-file-inventory-v1",
            "status": "frozen",
            "files": [{"path": "README.md", "byte_size": 1, "sha256": "a" * 64}],
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="v2 release asset inventory"):
        zenodo_deposition._load_inputs(tmp_path)  # ruff:ignore[private-member-access]
