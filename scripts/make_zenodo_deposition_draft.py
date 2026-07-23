"""Build deterministic Zenodo and DataCite deposition drafts without network mutation."""

from __future__ import annotations

import hashlib
import json
import tomllib
from collections.abc import Iterable
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.mapping_study_paths import latest_mapping_study_cycle, mapping_study_paths
from reimburse_atlas.registry import project_root

FINAL_DESCRIPTION = (
    "Reproducible, licence-aware software and permitted derived metadata for comparing public "
    "reimbursement schedules, coverage decisions and policy-analysis metadata across "
    "jurisdictions."
)
TEMPORAL_COVERAGE = "2020/2026"
GEOGRAPHIC_COVERAGE = ("Australia", "United States", "United Kingdom")
RELEASE_ASSET_PATTERNS = {
    "wheel": ("dist/*.whl",),
    "sdist": ("dist/*.tar.gz",),
    "source_archive": ("reimbursement-atlas-v*.tar.gz",),
    "python_sbom": ("data/derived/sbom/cyclonedx-python.json",),
    "dashboard_sbom": ("data/derived/sbom/cyclonedx-dashboard.json",),
    "release_manifest": ("release-manifest.json",),
    "attestation_receipt": ("data/derived/attestations/*.json",),
}


def _digests(path: Path) -> tuple[str, str]:
    content = path.read_bytes()
    sha256 = hashlib.sha256(content).hexdigest()
    md5 = hashlib.md5(content, usedforsecurity=False).hexdigest()
    return sha256, md5


def _matches(root: Path, patterns: Iterable[str]) -> list[Path]:
    matches = {
        path.relative_to(root)
        for pattern in patterns
        for path in root.glob(pattern)
        if path.is_file()
    }
    return sorted(
        matches,
        key=Path.as_posix,
    )


def build_release_asset_inventory(root: Path) -> dict[str, Any]:
    """Build a typed, checksum-bound inventory of release and provenance subjects."""
    rows: list[dict[str, Any]] = []
    missing_roles: list[str] = []
    for role, patterns in RELEASE_ASSET_PATTERNS.items():
        matches = _matches(root, patterns)
        if not matches:
            missing_roles.append(role)
        for relative in matches:
            path = root / relative
            sha256, md5 = _digests(path)
            rows.append({
                "role": role,
                "path": relative.as_posix(),
                "filename": path.name,
                "byte_size": path.stat().st_size,
                "sha256": sha256,
                "md5": md5,
            })
    return {
        "schema_version": "zenodo-release-asset-inventory-v2",
        "status": "frozen" if not missing_roles else "blocked_missing_release_assets",
        "required_roles": sorted(RELEASE_ASSET_PATTERNS),
        "missing_roles": missing_roles,
        "files": sorted(rows, key=lambda row: (str(row["role"]), str(row["path"]))),
        "paper_or_preprint_included": False,
    }


def build_draft(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Return Zenodo metadata, DataCite metadata and a frozen file inventory."""
    base = cast("dict[str, Any]", json.loads((root / ".zenodo.json").read_text(encoding="utf-8")))
    project = cast(
        "dict[str, Any]",
        tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"],
    )
    version = str(project["version"])
    mapping_cycle = latest_mapping_study_cycle(root)
    mapping_summary = mapping_study_paths(mapping_cycle).derived / "candidate_frame_summary.json"
    creators = cast("list[dict[str, Any]]", base.get("creators", []))
    missing_orcid = [str(item.get("name", "unnamed")) for item in creators if not item.get("orcid")]
    inventory = build_release_asset_inventory(root)
    preflight_inputs = {
        "metadata_source": ".zenodo.json",
        "mapping_summary": mapping_summary.as_posix(),
        "mapping_summary_present": (root / mapping_summary).is_file(),
        "source_description": str(base.get("description", "")),
    }
    zenodo = {
        **base,
        "description": FINAL_DESCRIPTION,
        "version": version,
        "notes": (
            "Apache-2.0 applies to software only. Derived data retain source-specific rights; "
            "raw and restricted source payloads are excluded."
        ),
        "grants": base.get("grants", []),
        "related_identifiers": base.get("related_identifiers", []),
    }
    datacite = {
        "schemaVersion": "http://datacite.org/schema/kernel-4",
        "types": {"resourceTypeGeneral": "Software"},
        "titles": [{"title": base["title"]}],
        "creators": [
            {
                "name": creator["name"],
                **(
                    {
                        "nameIdentifiers": [
                            {
                                "nameIdentifier": creator["orcid"],
                                "nameIdentifierScheme": "ORCID",
                                "schemeUri": "https://orcid.org",
                            }
                        ]
                    }
                    if creator.get("orcid")
                    else {}
                ),
            }
            for creator in creators
        ],
        "publisher": "Zenodo",
        "publicationYear": "2026",
        "dates": [
            {"date": TEMPORAL_COVERAGE, "dateType": "Valid"},
        ],
        "geoLocations": [{"geoLocationPlace": place} for place in GEOGRAPHIC_COVERAGE],
        "fundingReferences": [
            {
                "funderName": item["funder_name"],
                **({"awardNumber": item["award_number"]} if item.get("award_number") else {}),
                **({"awardTitle": item["award_title"]} if item.get("award_title") else {}),
            }
            for item in cast("list[dict[str, Any]]", base.get("funding", []))
        ],
        "version": version,
        "subjects": [{"subject": keyword} for keyword in base.get("keywords", [])],
        "descriptions": [
            {"description": FINAL_DESCRIPTION, "descriptionType": "Abstract"},
            {
                "description": (
                    "Apache-2.0 applies to software only. Derived data retain source-specific "
                    "rights recorded in the provenance and licensing manifests."
                ),
                "descriptionType": "TechnicalInfo",
            },
        ],
        "rightsList": [
            {
                "rights": "Apache License 2.0 (software only)",
                "rightsIdentifier": "Apache-2.0",
                "rightsIdentifierScheme": "SPDX",
            },
            {"rights": "Derived data retain source-specific rights recorded in provenance."},
        ],
        "relatedIdentifiers": [
            {
                "relatedIdentifier": item["identifier"],
                "relatedIdentifierType": "URL",
                "relationType": _datacite_relation(str(item["relation"])),
            }
            for item in cast("list[dict[str, Any]]", base.get("related_identifiers", []))
        ],
    }
    preflight = {
        "schema_version": "zenodo-deposition-preflight-v2",
        "status": (
            "ready_for_draft_deposit"
            if inventory["status"] == "frozen"
            and not missing_orcid
            and preflight_inputs["mapping_summary_present"]
            else "blocked_metadata_identity"
            if missing_orcid
            else "blocked_missing_mapping_evidence"
            if not preflight_inputs["mapping_summary_present"]
            else inventory["status"]
        ),
        "mutation_performed": False,
        "doi_reserved": False,
        "published": False,
        "missing_creator_orcids": missing_orcid,
        "preflight_inputs": preflight_inputs,
        "paper_or_preprint_submission_allowed": False,
        "required_upstream_gates": [
            "mapping_study_human_review",
            "dashboard_human_review",
            "osf_registration",
            "release_readiness",
        ],
    }
    return zenodo, datacite, {"inventory": inventory, "preflight": preflight}


def _datacite_relation(value: str) -> str:
    """Translate Zenodo's lower-camel relation spelling to DataCite."""
    if not value or not value.startswith("is"):
        message = f"unsupported related-identifier relation: {value}"
        raise ValueError(message)
    return f"Is{value[2:]}"


def main() -> None:
    """Write local non-depositing release metadata."""
    root = project_root()
    output = root / "data/derived/zenodo"
    output.mkdir(parents=True, exist_ok=True)
    zenodo, datacite, evidence = build_draft(root)
    for name, payload in (
        ("deposition_metadata.json", zenodo),
        ("datacite_metadata.json", datacite),
        ("file_inventory.json", evidence["inventory"]),
        ("preflight.json", evidence["preflight"]),
    ):
        (output / name).write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(json.dumps(evidence["preflight"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
