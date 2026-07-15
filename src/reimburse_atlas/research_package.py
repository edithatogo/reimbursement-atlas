"""Research data packaging metadata for Frictionless, RO-Crate and DCAT."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from reimburse_atlas.publication import PublicationManifest, build_publication_manifest

DESCRIPTOR_PATHS = frozenset({
    "data/derived/research_package/datapackage.json",
    "data/derived/research_package/ro-crate-metadata.json",
    "data/derived/research_package/dcat.jsonld",
})


def _descriptor_safe_manifest(manifest: PublicationManifest) -> PublicationManifest:
    """Exclude package descriptors so their hashes cannot become self-referential."""
    artifacts = tuple(
        artifact
        for artifact in manifest.artifacts
        if artifact.relative_path not in DESCRIPTOR_PATHS
    )
    return replace(manifest, artifact_count=len(artifacts), artifacts=artifacts)


def _resource_schema(path: str) -> dict[str, Any]:
    """Build a minimal resource schema placeholder."""
    return {"fields": [], "missingValues": [""]} if path.endswith(".csv") else {}


def build_frictionless_package(manifest: PublicationManifest) -> dict[str, Any]:
    """Build a Frictionless Data Package descriptor from publication candidates."""
    resources: list[dict[str, Any]] = []
    for artifact in manifest.artifacts:
        if artifact.file_format not in {"csv", "jsonl", "json"}:
            continue
        resources.append({
            "name": artifact.table_name.replace("_", "-"),
            "path": artifact.relative_path,
            "format": artifact.file_format,
            "bytes": artifact.byte_size,
            "hash": artifact.checksum_sha256,
            "mediatype": "text/csv" if artifact.file_format == "csv" else "application/json",
            "schema": _resource_schema(artifact.relative_path),
            "description": artifact.notes,
        })
    return {
        "profile": "data-package",
        "name": "reimbursement-atlas-conductor",
        "title": "Reimbursement Atlas derived metadata and policy-analysis scaffolds",
        "description": (
            "Licence-safe derived and metadata artefacts for public reimbursement "
            "schedule comparison."
        ),
        "licenses": [{"name": "Apache-2.0", "path": "LICENSE"}],
        "resources": resources,
    }


def build_ro_crate(manifest: PublicationManifest) -> dict[str, Any]:
    """Build a lightweight RO-Crate JSON-LD graph."""
    graph: list[dict[str, Any]] = [
        {
            "@id": "ro-crate-metadata.json",
            "@type": "CreativeWork",
            "about": {"@id": "./"},
            "conformsTo": {"@id": "https://w3id.org/ro/crate/1.2"},
        },
        {
            "@id": "./",
            "@type": "Dataset",
            "name": "Reimbursement Atlas Conductor",
            "description": "Research object for a comparative public reimbursement atlas.",
            "license": "https://www.apache.org/licenses/LICENSE-2.0",
            "hasPart": [{"@id": artifact.relative_path} for artifact in manifest.artifacts],
        },
    ]
    graph.extend(
        {
            "@id": artifact.relative_path,
            "@type": "File",
            "name": artifact.table_name,
            "contentSize": artifact.byte_size,
            "sha256": artifact.checksum_sha256,
            "encodingFormat": artifact.file_format,
            "description": artifact.notes,
        }
        for artifact in manifest.artifacts
    )
    return {"@context": "https://w3id.org/ro/crate/1.2/context", "@graph": graph}


def build_dcat(manifest: PublicationManifest) -> dict[str, Any]:
    """Build a compact DCAT JSON-LD dataset catalogue entry."""
    return {
        "@context": {
            "dcat": "http://www.w3.org/ns/dcat#",
            "dct": "http://purl.org/dc/terms/",
        },
        "@type": "dcat:Dataset",
        "dct:title": "Reimbursement Atlas Conductor derived artefacts",
        "dct:description": (
            "Licence-safe metadata and derived tables for comparative reimbursement research."
        ),
        "dcat:distribution": [
            {
                "@type": "dcat:Distribution",
                "dct:title": artifact.table_name,
                "dcat:downloadURL": artifact.relative_path,
                "dct:format": artifact.file_format,
            }
            for artifact in manifest.artifacts
        ],
    }


def write_research_package(
    output_dir: Path, manifest: PublicationManifest | None = None
) -> tuple[Path, Path, Path]:
    """Write Frictionless, RO-Crate and DCAT descriptors."""
    manifest = _descriptor_safe_manifest(manifest or build_publication_manifest())
    output_dir.mkdir(parents=True, exist_ok=True)
    package_path = output_dir / "datapackage.json"
    crate_path = output_dir / "ro-crate-metadata.json"
    dcat_path = output_dir / "dcat.jsonld"
    package_path.write_text(
        json.dumps(build_frictionless_package(manifest), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    crate_path.write_text(
        json.dumps(build_ro_crate(manifest), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    dcat_path.write_text(
        json.dumps(build_dcat(manifest), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return package_path, crate_path, dcat_path
