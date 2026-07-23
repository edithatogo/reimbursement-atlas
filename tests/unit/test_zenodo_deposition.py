from __future__ import annotations

import json
from pathlib import Path

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
    ("mode", "confirmation", "deposition_id"),
    [
        ("draft", "CREATE_ZENODO_DRAFT", None),
        ("reserve", "RESERVE_ZENODO_DOI", "123"),
        ("publish", "PUBLISH_ZENODO_RECORD", "123"),
    ],
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
    failing = zenodo_deposition._remote_file_parity(  # ruff:ignore[private-member-access]
        local,
        [
            {"key": "package.whl", "size": 4, "checksum": f"md5:{'c' * 32}"},
            {"key": "extra.txt", "size": 1, "checksum": f"md5:{'d' * 32}"},
        ],
    )

    assert passing["status"] == "pass"
    assert failing["status"] == "fail"
    assert {row["reason"] for row in failing["mismatches"]} == {
        "byte_size_mismatch",
        "checksum_mismatch",
        "unexpected_remote_file",
    }


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
