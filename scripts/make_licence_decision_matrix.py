"""Generate grouped licence decisions with provenance and transformation boundaries."""

# The declarative decision text is intentionally verbose; keep it readable as a matrix.
# ruff:file-ignore[line-too-long]

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from reimburse_atlas.registry import project_root, repo_relative

CATALOGUE = project_root() / "data/derived/historical_sources/historical_source_catalog.jsonl"
JSON_OUTPUT = project_root() / "docs/LICENCE_DECISION_MATRIX.json"
MARKDOWN_OUTPUT = project_root() / "docs/LICENCE_DECISION_MATRIX.md"

GROUPS: tuple[dict[str, Any], ...] = (
    {
        "id": "code_and_documentation",
        "title": "Project code and documentation",
        "status": "decided",
        "simple_question": "May project-owned code and documentation be distributed under Apache-2.0?",
        "recommended_outcome": "Yes, for material the project owns or is authorized to license.",
        "source_ids": [],
        "allowed_fields": ["project-owned source, schemas, tests, docs and automation"],
        "excluded_fields": [
            "third-party data, descriptors, ontologies, trademarks and provider documentation"
        ],
        "transformation_reference": "docs/LICENSING.md",
        "provenance_required": "Preserve third-party notices and source-specific terms.",
        "evidence_reference": "LICENSE; docs/LICENSING.md",
    },
    {
        "id": "au_mbs",
        "title": "Australian MBS",
        "status": "pending_human_review",
        "simple_question": "May the specified derived MBS fields be redistributed under the applicable Commonwealth terms?",
        "recommended_outcome": "Publish only permitted derived fields with attribution; retain raw XML/TXT locally and review descriptor-only rows separately.",
        "source_ids": ["au_mbs"],
        "allowed_fields": [
            "item code",
            "category/group",
            "approved label fields",
            "effective date",
            "schedule fee when permitted",
        ],
        "excluded_fields": [
            "raw XML",
            "raw TXT",
            "unrestricted descriptors",
            "descriptor-only rows without separate approval",
        ],
        "transformation_reference": "docs/SOURCE_PROVENANCE_AND_TRANSFORMATIONS.md#current-source-transformations",
        "provenance_required": "Provider URL, release ID, retrieval timestamp, SHA-256, parser version, output checksum and attribution.",
        "evidence_reference": "docs/SOURCE_LICENCE_EVIDENCE.md; issue #23; data/derived/reviewed_source_bundles/",
    },
    {
        "id": "au_pbs",
        "title": "Australian PBS",
        "status": "pending_human_review",
        "simple_question": "May the selected PBS schedule, item and fee fields be redistributed?",
        "recommended_outcome": "Publish reviewed derived schedule/list or payment values with PBS attribution; never publish raw responses, headers or credentials.",
        "source_ids": ["au_pbs"],
        "allowed_fields": [
            "schedule code",
            "item code",
            "effective date",
            "reviewed schedule/list or payment value",
        ],
        "excluded_fields": [
            "raw API/CSV payloads",
            "request headers",
            "API keys",
            "unreviewed monthly extracts",
            "net-price claims",
        ],
        "transformation_reference": "docs/SOURCE_PROVENANCE_AND_TRANSFORMATIONS.md#current-source-transformations; docs/PBS_API_ACQUISITION.md",
        "provenance_required": "Endpoint or catalogue URL, key provenance without the secret, retrieval timestamp, checksum, parser version and source terms.",
        "evidence_reference": "data/derived/source_downloads/pbs_api_acquisition.jsonl; issue #25",
    },
    {
        "id": "us_cms",
        "title": "US CMS CLFS, PFS and ASP",
        "status": "pending_human_review",
        "simple_question": "Which numeric CMS payment fields may be retained and published without redistributing restricted descriptors?",
        "recommended_outcome": "Permit only reviewed numeric/payment fields and permitted metadata; exclude CPT descriptors, restricted crosswalks and unsupported coverage or net-price claims.",
        "source_ids": ["us_cms_clfs", "us_cms_pfs", "us_cms_asp"],
        "allowed_fields": [
            "reviewed numeric payment/RVU fields",
            "effective dates",
            "permitted locality or payment metadata",
        ],
        "excluded_fields": [
            "CPT descriptors",
            "AMA-gated ZIP contents",
            "restricted crosswalks",
            "coverage claims",
            "net-price claims",
        ],
        "transformation_reference": "docs/SOURCE_PROVENANCE_AND_TRANSFORMATIONS.md#current-source-transformations; data/derived/processes/historical_source_transformation.bpmn",
        "provenance_required": "Exact CMS URL, release ID, access date, checksum, permitted-field decision, parser version, excluded-field record and attribution.",
        "evidence_reference": "data/derived/source_contracts/source_contract_validation.jsonl; data/derived/source_url_licence_checklist/",
    },
    {
        "id": "uk_genomic",
        "title": "NHS England genomic directories",
        "status": "pending_human_review",
        "simple_question": "May transformed genomic-directory metadata be redistributed under NHS terms?",
        "recommended_outcome": "Publish only reviewed directory metadata and preserve provider attribution and version identifiers.",
        "source_ids": ["uk_genomic_test_directory"],
        "allowed_fields": [
            "reviewed test metadata",
            "directory version",
            "effective date",
            "source link",
        ],
        "excluded_fields": [
            "unreviewed raw workbooks",
            "unnecessary personal or restricted content",
            "unsupported coverage claims",
        ],
        "transformation_reference": "docs/SOURCE_PROVENANCE_AND_TRANSFORMATIONS.md#current-source-transformations",
        "provenance_required": "Official publication URL, file checksum, directory version, parser version, field exclusions and attribution.",
        "evidence_reference": "data/derived/historical_sources/historical_source_catalog.jsonl; data/derived/source_url_licence_checklist/",
    },
    {
        "id": "generated_research_governance",
        "title": "Generated research and governance artefacts",
        "status": "pending_human_review",
        "simple_question": "May project-generated provenance, quality, protocol, dictionary and research-package artefacts be published?",
        "recommended_outcome": "Publish project-owned artefacts under Apache-2.0 or an explicitly recorded compatible metadata licence, while preserving embedded source restrictions.",
        "source_ids": [],
        "allowed_fields": [
            "schemas",
            "provenance",
            "data dictionaries",
            "quality reports",
            "protocol scaffolds",
            "SBOMs",
            "research-package metadata",
        ],
        "excluded_fields": [
            "raw source payloads",
            "credentials",
            "request headers",
            "restricted source content",
            "unapproved policy claims",
        ],
        "transformation_reference": "docs/SOURCE_PROVENANCE_AND_TRANSFORMATIONS.md; data/derived/processes/historical_source_transformation.bpmn",
        "provenance_required": "Repository commit, source IDs, input checksums, transformation version, output checksum and licence decision.",
        "evidence_reference": "data/derived/publication_manifest.json; data/derived/research_package/; data/derived/licence_review/",
    },
)


def _catalogue_counts(root: Path) -> dict[str, int]:
    """Count historical catalogue records by source ID."""
    path = root / "data/derived/historical_sources/historical_source_catalog.jsonl"
    if not path.is_file():
        return {}
    counts: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        source_id = str(json.loads(line).get("source_id", ""))
        if source_id:
            counts[source_id] = counts.get(source_id, 0) + 1
    return counts


def build_matrix(root: Path | None = None) -> dict[str, Any]:
    """Build a deterministic grouped decision matrix from committed source metadata."""
    repo = root or project_root()
    counts = _catalogue_counts(repo)
    groups: list[dict[str, Any]] = []
    for group in GROUPS:
        row = dict(group)
        row["source_record_count"] = sum(
            counts.get(source_id, 0) for source_id in row["source_ids"]
        )
        row["release_gate"] = (
            "human_licence_review" if row["status"] != "decided" else "project_licence_decision"
        )
        groups.append(row)
    return {
        "schema_version": "licence-decision-matrix-v1",
        "generated_from": repo_relative(CATALOGUE, repo),
        "source_catalogue_scope": (
            "Counts are historical_source_catalogue records only; a zero count means "
            "the source is governed elsewhere and is not evidence of source absence."
        ),
        "source_catalogue_counts": counts,
        "groups": groups,
        "approval_rule": "A group recommendation never grants approval; every approved or blocked artefact must retain a checksum-bound human decision.",
    }


def render_markdown(matrix: dict[str, Any]) -> str:
    """Render the machine-readable matrix as concise reviewer instructions."""
    lines = [
        "# Licence Decision Matrix",
        "",
        "This file is generated from `docs/LICENCE_DECISION_MATRIX.json`. It groups the",
        "the current candidate artefact decisions into simple human decisions. It does",
        "not grant approval. Exact file decisions remain checksum-bound in the generated",
        "licence review queue.",
        "",
        "| Group | Status | Simple decision | Recommended outcome | Historical catalogue records |",
        "| --- | --- | --- | --- | ---: |",
    ]
    for group in matrix["groups"]:
        question = str(group["simple_question"]).replace("|", "\\|")
        recommendation = str(group["recommended_outcome"]).replace("|", "\\|")
        lines.append(
            f"| {group['title']} | `{group['status']}` | {question} | {recommendation} | {group['source_record_count']} |"
        )
    lines.extend([
        "",
        "## Required evidence for every decision",
        "",
        "Record the exact candidate path and SHA-256, source terms, attribution,",
        "redistribution permission, restrictions, reviewer, review time and evidence URL.",
        "Link the decision to the provider source, parser/transform version, excluded",
        "fields and generated output checksum. Passing computational gates is not licence",
        "approval, research approval or publication authorization.",
        "",
        "## Transformation references",
        "",
        "- `docs/SOURCE_PROVENANCE_AND_TRANSFORMATIONS.md` defines the source boundaries.",
        "- `data/derived/processes/historical_source_transformation.bpmn` defines the fail-closed process.",
        "- `data/derived/publication_manifest.json` binds candidate outputs to checksums.",
        "- `data/derived/licence_review/licence_review_queue.jsonl` contains the exact review rows.",
    ])
    return "\n".join(lines) + "\n"


def main() -> None:
    """Write the reproducible JSON and Markdown matrix."""
    root = project_root()
    matrix = build_matrix(root)
    JSON_OUTPUT.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MARKDOWN_OUTPUT.write_text(render_markdown(matrix), encoding="utf-8")
    print(
        f"Wrote licence decision matrix: {repo_relative(JSON_OUTPUT)}, {repo_relative(MARKDOWN_OUTPUT)}"
    )


if __name__ == "__main__":
    main()
