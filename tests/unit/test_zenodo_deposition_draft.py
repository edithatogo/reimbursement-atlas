from __future__ import annotations

from pathlib import Path

from scripts.make_zenodo_deposition_draft import (
    RELEASE_ASSET_PATTERNS,
    build_draft,
    build_release_asset_inventory,
)


def test_zenodo_draft_separates_software_and_data_rights() -> None:
    zenodo, datacite, evidence = build_draft(Path.cwd())

    assert zenodo["license"] == "Apache-2.0"
    assert zenodo["version"]
    assert "software only" in zenodo["notes"]
    assert datacite["version"] == zenodo["version"]
    assert datacite["subjects"]
    assert evidence["inventory"]["status"] == "blocked_missing_release_assets"
    assert evidence["inventory"]["missing_roles"]
    relations = {
        row["relatedIdentifier"]: row["relationType"] for row in datacite["relatedIdentifiers"]
    }
    assert relations["https://github.com/edithatogo/reimbursement-atlas"] == "IsIdenticalTo"
    assert relations["https://osf.io/q8cnx/"] == "IsSupplementedBy"
    assert len(datacite["rightsList"]) == 2
    assert evidence["inventory"]["paper_or_preprint_included"] is False
    assert evidence["preflight"]["paper_or_preprint_submission_allowed"] is False
    assert evidence["preflight"]["mutation_performed"] is False
    assert "preparation only" not in zenodo["description"].lower()
    assert datacite["dates"]
    assert datacite["geoLocations"]
    assert datacite["fundingReferences"] == []


def test_release_inventory_requires_every_release_and_provenance_role(tmp_path: Path) -> None:
    for role, patterns in RELEASE_ASSET_PATTERNS.items():
        relative = {
            "wheel": Path("dist/package.whl"),
            "sdist": Path("dist/package.tar.gz"),
            "source_archive": Path("reimbursement-atlas-v1.0.0.tar.gz"),
            "python_sbom": Path("data/derived/sbom/cyclonedx-python.json"),
            "dashboard_sbom": Path("data/derived/sbom/cyclonedx-dashboard.json"),
            "release_manifest": Path("release-manifest.json"),
            "attestation_receipt": Path("data/derived/attestations/package.json"),
        }[role]
        assert any(relative.match(pattern) for pattern in patterns)
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(role.encode())

    inventory = build_release_asset_inventory(tmp_path)

    assert inventory["status"] == "frozen"
    assert inventory["missing_roles"] == []
    assert {row["role"] for row in inventory["files"]} == set(RELEASE_ASSET_PATTERNS)
    assert all(len(row["sha256"]) == 64 and len(row["md5"]) == 32 for row in inventory["files"])


def test_draft_requires_explicit_release_asset_discovery() -> None:
    root = Path.cwd()

    _, _, evidence = build_draft(root)

    assert evidence["inventory"]["status"] == "blocked_missing_release_assets"
    assert evidence["inventory"]["files"] == []
