"""Validate locally prepared Zenodo metadata without contacting Zenodo."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.registry import project_root, repo_relative

REQUIRED_KEYS = ("title", "upload_type", "description", "creators", "license")
ORCID = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
DATACITE_RELATIONS = {
    "IsCitedBy",
    "Cites",
    "IsSupplementTo",
    "IsSupplementedBy",
    "IsContinuedBy",
    "Continues",
    "Describes",
    "IsDescribedBy",
    "HasMetadata",
    "IsMetadataFor",
    "HasVersion",
    "IsVersionOf",
    "IsNewVersionOf",
    "IsPreviousVersionOf",
    "IsPartOf",
    "HasPart",
    "IsPublishedIn",
    "IsReferencedBy",
    "References",
    "IsDocumentedBy",
    "Documents",
    "IsCompiledBy",
    "Compiles",
    "IsVariantFormOf",
    "IsOriginalFormOf",
    "IsIdenticalTo",
    "IsReviewedBy",
    "Reviews",
    "IsDerivedFrom",
    "IsSourceOf",
    "IsRequiredBy",
    "Requires",
    "Obsoletes",
    "IsObsoletedBy",
    "Collects",
    "IsCollectedBy",
}


def _object_list(value: Any) -> list[dict[str, Any]] | None:
    if not isinstance(value, list):
        return None
    if any(not isinstance(item, dict) for item in cast("list[Any]", value)):
        return None
    return cast("list[dict[str, Any]]", value)


def validate_metadata(path: Path) -> list[str]:  # ruff:ignore[too-many-branches]
    """Return validation errors for a local, non-depositing Zenodo record."""
    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read valid JSON metadata: {exc}"]
    if not isinstance(payload, dict):
        return ["metadata must be a JSON object"]
    payload = cast("dict[str, Any]", payload)
    errors = [f"missing required key: {key}" for key in REQUIRED_KEYS if key not in payload]
    if payload.get("upload_type") != "software":
        errors.append("upload_type must be software")
    if payload.get("license") != "Apache-2.0":
        errors.append("software metadata must use Apache-2.0")
    creators = payload.get("creators")
    creator_errors = False
    if isinstance(creators, list):
        creator_errors = not creators
        for creator in cast("list[Any]", creators):
            if not isinstance(creator, dict) or not cast("dict[str, Any]", creator).get("name"):
                creator_errors = True
    else:
        creator_errors = True
    if creator_errors:
        errors.append("creators must contain at least one named creator")
    related = payload.get("related_identifiers", [])
    repository_identifier = False
    if isinstance(related, list):
        for item in cast("list[Any]", related):
            if isinstance(item, dict) and cast("dict[str, Any]", item).get("identifier") == (
                "https://github.com/edithatogo/reimbursement-atlas"
            ):
                repository_identifier = True
                break
    if not repository_identifier:
        errors.append("GitHub repository related identifier is required")
    return errors


def validate_datacite_metadata(payload: Any) -> list[str]:  # ruff:ignore[too-many-branches]
    """Validate the project-required DataCite 4.x metadata surface."""
    if not isinstance(payload, dict):
        return ["DataCite metadata must be a JSON object"]
    record = cast("dict[str, Any]", payload)
    errors: list[str] = []
    if record.get("schemaVersion") != "http://datacite.org/schema/kernel-4":
        errors.append("DataCite schemaVersion must identify kernel-4")
    creators = _object_list(record.get("creators"))
    if not creators:
        errors.append("DataCite creators must contain at least one creator")
    else:
        for creator in creators:
            if not creator.get("name"):
                errors.append("each DataCite creator requires a name")
                continue
            identifiers = _object_list(creator.get("nameIdentifiers"))
            if not identifiers or not all(
                item.get("nameIdentifierScheme") == "ORCID"
                and ORCID.fullmatch(str(item.get("nameIdentifier", "")))
                for item in identifiers
            ):
                errors.append("each DataCite creator requires a valid ORCID")
    rights = _object_list(record.get("rightsList"))
    if not rights or not any(item.get("rightsIdentifier") == "Apache-2.0" for item in rights):
        errors.append("DataCite rightsList must identify Apache-2.0 software rights")
    related = _object_list(record.get("relatedIdentifiers"))
    if not related:
        errors.append("DataCite relatedIdentifiers must not be empty")
    else:
        for item in related:
            if (
                not item.get("relatedIdentifier")
                or item.get("relatedIdentifierType") not in {"DOI", "URL"}
                or item.get("relationType") not in DATACITE_RELATIONS
            ):
                errors.append("DataCite related identifier is incomplete or unsupported")
    funding_raw = record.get("fundingReferences")
    funding = _object_list(funding_raw)
    if funding is None:
        errors.append("DataCite fundingReferences must be an array, including empty")
    elif any(not item.get("funderName") for item in funding):
        errors.append("each DataCite funding reference requires funderName")
    dates = _object_list(record.get("dates"))
    if not dates or not any(item.get("dateType") == "Valid" and item.get("date") for item in dates):
        errors.append("DataCite dates must include temporal coverage with dateType Valid")
    places = _object_list(record.get("geoLocations"))
    if not places or any(not item.get("geoLocationPlace") for item in places):
        errors.append("DataCite geoLocations must identify geographic coverage")
    descriptions = _object_list(record.get("descriptions"))
    if descriptions is None or any(
        "preparation only" in str(item.get("description", "")).lower()
        or "no zenodo deposition" in str(item.get("description", "")).lower()
        for item in descriptions
    ):
        errors.append("final DataCite descriptions must not contain preflight wording")
    return errors


def main() -> None:
    """Validate the repository's prepared metadata and never deposit it."""
    root = project_root()
    path = root / ".zenodo.json"
    errors = validate_metadata(path)
    datacite_path = root / "data/derived/zenodo/datacite_metadata.json"
    if datacite_path.is_file():
        try:
            datacite: Any = json.loads(datacite_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot read valid DataCite JSON metadata: {exc}")
        else:
            errors.extend(validate_datacite_metadata(datacite))
    if errors:
        raise SystemExit("Zenodo metadata validation failed: " + "; ".join(errors))
    print(
        "Zenodo and DataCite metadata validation passed: "
        f"{repo_relative(path)}, {repo_relative(datacite_path)}"
    )


if __name__ == "__main__":
    main()
