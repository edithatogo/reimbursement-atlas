"""Cross-repository medallion contracts and publication staging."""

from __future__ import annotations

import hashlib
import json
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Final
from urllib.parse import urlsplit
from urllib.request import urlopen

from reimburse_atlas.registry import project_root

GENERATED_AT: Final = "1970-01-01T00:00:00Z"
CONTRACT_FILES: Final = (
    Path("contracts/medallion/v1/medallion-conformance.schema.json"),
    Path("contracts/medallion/v1/fixtures/valid.json"),
    Path("contracts/medallion/v1/fixtures/invalid-missing-gate.json"),
    Path("contracts/medallion/v2/field-lineage.schema.json"),
    Path("contracts/medallion/v3/backfill-replay.schema.json"),
)
CONFORMANT_REPOSITORIES: Final = (
    "edithatogo/reimbursement-atlas",
    "edithatogo/global-medicines-atlas",
    "edithatogo/archive-govt-nz",
)
PUBLICATION_PREFIXES: Final = (
    Path("data/derived/medallion"),
    Path("data/derived/field_lineage"),
)
CONFIG_INPUTS: dict[str, Path] = {
    "catalogue_b0": Path("data/derived/medallion/bronze_source_index.jsonl"),
    "acquisition_b1": Path("data/derived/medallion/bronze_acquisition_ledger.jsonl"),
    "evidence_b2": Path("data/derived/medallion/bronze_evidence.jsonl"),
    "silver": Path("data/derived/medallion/medallion_artifacts.jsonl"),
    "gold": Path("data/derived/medallion/medallion_artifacts.jsonl"),
    "platinum": Path("data/derived/medallion/medallion_artifacts.jsonl"),
    "lineage": Path("data/derived/field_lineage/field_lineage.jsonl"),
    "promotion_decisions": Path("data/derived/medallion/promotion_decisions.jsonl"),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_contract_manifest(root: Path | None = None) -> dict[str, object]:
    """Return the immutable local contract inventory."""
    repo = (root or project_root()).resolve()
    files = [
        {
            "path": path.as_posix(),
            "sha256": _sha256(repo / path),
            "version": path.parts[2],
        }
        for path in CONTRACT_FILES
    ]
    return {
        "schema_version": "medallion-contract-manifest-v1",
        "generated_at": GENERATED_AT,
        "authority_model": "decentralized_hash_locked",
        "proposed_distribution_authority": "edithatogo/repository-standards",
        "authority_transition_status": "not_yet_hosted",
        "runtime_dependency": None,
        "contract_versions": ["v1", "v2", "v3"],
        "files": files,
    }


def _external_status(root: Path, relative: str) -> str:
    path = root / relative
    if not path.exists():
        return "not_recorded"
    payload = json.loads(path.read_text(encoding="utf-8"))
    status = payload.get("status")
    return status if isinstance(status, str) else "unknown"


def build_federation_manifest(root: Path | None = None) -> dict[str, object]:
    """Return repository, destination, rights and compatibility relationships."""
    repo = (root or project_root()).resolve()
    repositories = [
        {
            "repository": name,
            "role": "control_plane",
            "conformance": "conformant",
            "contract_versions": ["v1", "v2", "v3"],
        }
        for name in CONFORMANT_REPOSITORIES
    ]
    repositories.append({
        "repository": "edithatogo/global-family-justice-data",
        "role": "federated_control_plane",
        "conformance": "adapter_required",
        "contract_versions": [],
        "reason_code": "bronze_b0_b1_semantics_conflict_with_shared_b0_b1_b2",
    })
    return {
        "schema_version": "medallion-federation-manifest-v1",
        "generated_at": GENERATED_AT,
        "canonical_repository": "edithatogo/reimbursement-atlas",
        "repositories": repositories,
        "destinations": [
            {
                "service": "huggingface_dataset",
                "identifier": "edithatogo/reimbursement-atlas",
                "role": "derived_distribution",
                "status": _external_status(
                    repo, "data/derived/publication/huggingface_remote_receipt.json"
                ),
            },
            {
                "service": "huggingface_space",
                "identifier": "edithatogo/reimbursement-atlas",
                "role": "platinum_dashboard",
                "status": _external_status(
                    repo, "data/derived/publication/huggingface_remote_receipt.json"
                ),
            },
            {
                "service": "zenodo",
                "identifier": "21759294",
                "role": "immutable_release_archive",
                "status": _external_status(
                    repo, "data/derived/zenodo/deposition_external_state.json"
                ),
            },
        ],
        "layer_semantics": {
            "catalogue_b0": "catalogue_only_not_acquisition",
            "acquisition_b1": "append_only_acquisition_events",
            "evidence_b2": "immutable_bytes_or_rights_constrained_reference",
            "silver": "source_faithful_typed_records",
            "gold": "reviewed_cross_source_evidence",
            "platinum": "explicitly_promoted_public_product",
        },
        "rights_boundary": "derived_and_public_metadata_only",
        "raw_payloads_included": False,
        "publication_authority": "external_token_gated_workflow",
    }


def _is_allowlisted(relative: Path) -> bool:
    return any(relative == prefix or prefix in relative.parents for prefix in PUBLICATION_PREFIXES)


def _filtered_layer_bytes(path: Path, layer: str) -> bytes:
    rows = [
        row
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
        for row in [json.loads(line)]
        if row.get("layer") == layer
    ]
    return b"".join((json.dumps(row, sort_keys=True) + "\n").encode("utf-8") for row in rows)


def stage_huggingface_medallion(
    root: Path | None,
    destination: Path,
) -> dict[str, object]:
    """Stage only allow-listed medallion outputs for a Hugging Face dataset."""
    repo = (root or project_root()).resolve()
    configs: list[dict[str, object]] = []
    for config, relative in CONFIG_INPUTS.items():
        if not _is_allowlisted(relative):
            message = f"{relative.as_posix()} is not publication allow-listed"
            raise ValueError(message)
        source = repo / relative
        if not source.is_file():
            raise FileNotFoundError(source)
        target = destination / "data" / "medallion" / config / "data.jsonl"
        target.parent.mkdir(parents=True, exist_ok=True)
        if config in {"silver", "gold", "platinum"}:
            target.write_bytes(_filtered_layer_bytes(source, config))
        else:
            shutil.copyfile(source, target)
        configs.append({
            "config_name": config,
            "path": target.relative_to(destination).as_posix(),
            "sha256": _sha256(target),
            "row_count": sum(1 for line in target.read_text().splitlines() if line.strip()),
            "source_path": relative.as_posix(),
        })
    manifest: dict[str, object] = {
        "schema_version": "huggingface-medallion-stage-v1",
        "generated_at": GENERATED_AT,
        "config_count": len(configs),
        "configs": configs,
        "rights_boundary": "derived_and_public_metadata_only",
        "raw_payloads_included": False,
    }
    _write_json(destination / "medallion_manifest.json", manifest)
    return manifest


def check_live_contract_parity(
    root: Path | None = None,
    fetch: Callable[[str], bytes] | None = None,
) -> dict[str, object]:
    """Compare public sibling contract bytes with the local immutable manifest."""
    repo = (root or project_root()).resolve()

    def _fetch_url(url: str) -> bytes:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.hostname != "raw.githubusercontent.com":
            message = "live conformance fetch rejected a non-allowlisted URL"
            raise ValueError(message)
        # The scheme and hostname are fixed above; repository and path values are constants.
        return urlopen(url, timeout=30).read()  # ruff: ignore[suspicious-url-open-usage]  # nosec B310

    fetch_bytes: Callable[[str], bytes] = fetch or _fetch_url
    expected = {path.as_posix(): _sha256(repo / path) for path in CONTRACT_FILES}
    checks: list[dict[str, object]] = []
    for repository in CONFORMANT_REPOSITORIES:
        for relative, expected_sha in expected.items():
            url = f"https://raw.githubusercontent.com/{repository}/main/{relative}"
            try:
                actual_sha = hashlib.sha256(fetch_bytes(url)).hexdigest()
                status = "pass" if actual_sha == expected_sha else "drift"
                error = None
            except OSError as exc:
                actual_sha = None
                status = "unavailable"
                error = type(exc).__name__
            checks.append({
                "repository": repository,
                "path": relative,
                "expected_sha256": expected_sha,
                "actual_sha256": actual_sha,
                "status": status,
                "error": error,
            })
    return {
        "schema_version": "medallion-live-conformance-v1",
        "checked_at": GENERATED_AT,
        "checks": checks,
        "status": "pass" if all(row["status"] == "pass" for row in checks) else "fail",
    }


def materialise_medallion_federation(root: Path | None = None) -> dict[str, object]:
    """Write deterministic local federation and publication manifests."""
    repo = (root or project_root()).resolve()
    contract = build_contract_manifest(repo)
    federation = build_federation_manifest(repo)
    configs = {
        "schema_version": "huggingface-medallion-configs-v1",
        "generated_at": GENERATED_AT,
        "configs": [
            {
                "config_name": name,
                "data_files": f"data/medallion/{name}/data.jsonl",
                "source_path": path.as_posix(),
            }
            for name, path in CONFIG_INPUTS.items()
        ],
    }
    _write_json(repo / "contracts/medallion/manifest.json", contract)
    output = repo / "data/derived/medallion_federation"
    _write_json(output / "contract_manifest.json", contract)
    _write_json(output / "federation_manifest.json", federation)
    _write_json(output / "huggingface_configs.json", configs)
    return {
        "contract_file_count": len(CONTRACT_FILES),
        "repository_count": len(CONFORMANT_REPOSITORIES) + 1,
        "huggingface_config_count": len(CONFIG_INPUTS),
        "gfjd_conformance": "adapter_required",
    }
