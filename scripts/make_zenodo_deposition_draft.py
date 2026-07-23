"""Build deterministic Zenodo and DataCite deposition drafts without network mutation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.registry import project_root

FILES = (
    Path("README.md"),
    Path("LICENSE"),
    Path("CITATION.cff"),
    Path(".zenodo.json"),
    Path("data/derived/publication_manifest.json"),
    Path("data/derived/mapping_study/candidate_frame_summary.json"),
)


def build_draft(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Return Zenodo metadata, DataCite metadata and a frozen file inventory."""
    base = cast("dict[str, Any]", json.loads((root / ".zenodo.json").read_text(encoding="utf-8")))
    creators = cast("list[dict[str, Any]]", base.get("creators", []))
    missing_orcid = [str(item.get("name", "unnamed")) for item in creators if not item.get("orcid")]
    inventory_rows: list[dict[str, Any]] = []
    for relative in FILES:
        path = root / relative
        if path.is_file():
            inventory_rows.append({
                "path": relative.as_posix(),
                "byte_size": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            })
    inventory: dict[str, Any] = {
        "schema_version": "zenodo-file-inventory-v1",
        "status": "frozen" if len(inventory_rows) == len(FILES) else "blocked_missing_files",
        "files": inventory_rows,
        "paper_or_preprint_included": False,
    }
    zenodo = {
        **base,
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
                "relationType": "IsIdenticalTo",
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
