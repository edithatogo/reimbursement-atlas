import json
from pathlib import Path

import pytest

from reimburse_atlas.medallion_federation import (
    CONFIG_INPUTS,
    CONTRACT_FILES,
    build_contract_manifest,
    build_federation_manifest,
    check_live_contract_parity,
    materialise_medallion_federation,
    stage_huggingface_medallion,
)


def test_contract_manifest_is_hash_locked(repo_root: Path) -> None:
    manifest = build_contract_manifest(repo_root)

    assert manifest["authority_model"] == "decentralized_hash_locked"
    assert manifest["runtime_dependency"] is None
    assert manifest["contract_versions"] == ["v1", "v2", "v3"]
    assert len(manifest["files"]) == 5
    assert all(len(row["sha256"]) == 64 for row in manifest["files"])


def test_federation_records_gfjd_adapter_boundary(repo_root: Path) -> None:
    manifest = build_federation_manifest(repo_root)
    states = {row["repository"]: row["conformance"] for row in manifest["repositories"]}

    assert states["edithatogo/reimbursement-atlas"] == "conformant"
    assert states["edithatogo/global-medicines-atlas"] == "conformant"
    assert states["edithatogo/archive-govt-nz"] == "conformant"
    assert states["edithatogo/global-family-justice-data"] == "adapter_required"


def test_federation_reads_external_destination_states(tmp_path: Path) -> None:
    for relative, status in (
        ("data/derived/publication/huggingface_remote_receipt.json", "published"),
        ("data/derived/zenodo/deposition_external_state.json", "draft"),
    ):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({"status": status}), encoding="utf-8")

    manifest = build_federation_manifest(tmp_path)
    states = {row["service"]: row["status"] for row in manifest["destinations"]}

    assert states == {
        "huggingface_dataset": "published",
        "huggingface_space": "published",
        "zenodo": "draft",
    }


def test_huggingface_stage_is_layer_separated_and_allow_listed(
    repo_root: Path, tmp_path: Path
) -> None:
    summary = stage_huggingface_medallion(repo_root, tmp_path)

    assert summary["config_count"] == len(CONFIG_INPUTS)
    assert {row["config_name"] for row in summary["configs"]} == set(CONFIG_INPUTS)
    assert (tmp_path / "medallion_manifest.json").exists()
    for config in CONFIG_INPUTS:
        assert (tmp_path / "data" / "medallion" / config / "data.jsonl").exists()
    staged = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in tmp_path.rglob("*")
        if path.is_file()
    )
    assert "data/raw_live" not in staged
    assert "/Volumes/" not in staged
    assert "/Users/" not in staged


def test_huggingface_stage_rejects_non_allowlisted_input(
    repo_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(CONFIG_INPUTS, "unsafe", Path("data/raw_live/source.csv"))

    with pytest.raises(ValueError, match="not publication allow-listed"):
        stage_huggingface_medallion(repo_root, tmp_path)


def test_huggingface_stage_requires_every_declared_input(
    repo_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(CONFIG_INPUTS, "missing", Path("data/derived/medallion/missing.jsonl"))

    with pytest.raises(FileNotFoundError):
        stage_huggingface_medallion(repo_root, tmp_path)


def test_live_contract_parity_reports_pass_drift_and_unavailable(repo_root: Path) -> None:
    expected = {path.as_posix(): (repo_root / path).read_bytes() for path in CONTRACT_FILES}

    def fetch(url: str) -> bytes:
        relative = url.split("/main/", maxsplit=1)[1]
        if "archive-govt-nz" in url:
            message = "offline"
            raise OSError(message)
        if "global-medicines-atlas" in url and relative == CONTRACT_FILES[0].as_posix():
            return b"drift"
        return expected[relative]

    report = check_live_contract_parity(repo_root, fetch)
    statuses = [row["status"] for row in report["checks"]]

    assert report["status"] == "fail"
    assert statuses.count("pass") == 9
    assert statuses.count("drift") == 1
    assert statuses.count("unavailable") == 5


def test_live_contract_parity_passes_for_matching_bytes(repo_root: Path) -> None:
    expected = {path.as_posix(): (repo_root / path).read_bytes() for path in CONTRACT_FILES}

    report = check_live_contract_parity(
        repo_root, lambda url: expected[url.split("/main/", maxsplit=1)[1]]
    )

    assert report["status"] == "pass"


def test_materialisation_is_deterministic(repo_root: Path) -> None:
    first = materialise_medallion_federation(repo_root)
    first_bytes = {
        path.name: path.read_bytes()
        for path in (repo_root / "data/derived/medallion_federation").glob("*.json")
    }
    second = materialise_medallion_federation(repo_root)
    second_bytes = {
        path.name: path.read_bytes()
        for path in (repo_root / "data/derived/medallion_federation").glob("*.json")
    }

    assert first == second
    assert first_bytes == second_bytes
    assert json.loads((repo_root / "contracts/medallion/manifest.json").read_text())["files"]
