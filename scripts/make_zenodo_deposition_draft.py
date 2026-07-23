"""Build deterministic Zenodo and DataCite deposition drafts without network mutation."""

from __future__ import annotations

import hashlib
import json
import tomllib
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.mapping_study_paths import latest_mapping_study_cycle, mapping_study_paths
from reimburse_atlas.registry import project_root

FILES = (
    Path("README.md"),
    Path("LICENSE"),
    Path("CITATION.cff"),
    Path(".zenodo.json"),
    Path("data/derived/publication_manifest.json"),
    Path("data/derived/sbom/cyclonedx-python.json"),
    Path("data/derived/sbom/cyclonedx-dashboard.json"),
    Path("docs/SOURCE_PROVENANCE_AND_TRANSFORMATIONS.md"),
    Path("docs/LICENSING.md"),
)


def build_draft(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Return Zenodo metadata, DataCite metadata and a frozen file inventory."""
    base = cast("dict[str, Any]", json.loads((root / ".zenodo.json").read_text(encoding="utf-8")))
    project = cast(
        "dict[str, Any]",
        tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"],
    )
    version = str(project["version"])
    mapping_cycle = latest_mapping_study_cycle(root)
    files = (
        *FILES,
        mapping_study_paths(mapping_cycle).derived / "candidate_frame_summary.json",
    )
    creators = cast("list[dict[str, Any]]", base.get("creators", []))
    missing_orcid = [str(item.get("name", "unnamed")) for item in creators if not item.get("orcid")]
    inventory_rows: list[dict[str, Any]] = []
    for relative in files:
        path = root / relative
        if path.is_file():
            inventory_rows.append({
                "path": relative.as_posix(),
                "byte_size": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            })
    inventory: dict[str, Any] = {
        "schema_version": "zenodo-file-inventory-v1",
        "status": "frozen" if len(inventory_rows) == len(files) else "blocked_missing_files",
        "files": inventory_rows,
        "paper_or_preprint_included": False,
    }
    zenodo = {
        **base,
        "version": version,
        "notes": (
            "Apache-2.0 applies to software only. Derived data retain source-specific rights; "
            "raw and restricted source payloads are excluded."
        ),
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
        "version": version,
        "subjects": [{"subject": keyword} for keyword in base.get("keywords", [])],
        "descriptions": [
            {"description": base["description"], "descriptionType": "Abstract"},
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
            if inventory["status"] == "frozen" and not missing_orcid
            else "blocked_metadata_identity"
            if missing_orcid
            else inventory["status"]
        ),
        "mutation_performed": False,
        "doi_reserved": False,
        "published": False,
        "missing_creator_orcids": missing_orcid,
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
