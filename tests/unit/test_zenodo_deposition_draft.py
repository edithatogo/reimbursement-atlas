from __future__ import annotations

from pathlib import Path

from scripts.make_zenodo_deposition_draft import build_draft


def test_zenodo_draft_separates_software_and_data_rights() -> None:
    zenodo, datacite, evidence = build_draft(Path.cwd())

    assert zenodo["license"] == "Apache-2.0"
    assert zenodo["version"]
    assert "software only" in zenodo["notes"]
    assert datacite["version"] == zenodo["version"]
    assert datacite["subjects"]
    assert len(evidence["inventory"]["files"]) == 10
    relations = {
        row["relatedIdentifier"]: row["relationType"] for row in datacite["relatedIdentifiers"]
    }
    assert relations["https://github.com/edithatogo/reimbursement-atlas"] == "IsIdenticalTo"
    assert relations["https://osf.io/q8cnx/"] == "IsSupplementedBy"
    assert len(datacite["rightsList"]) == 2
    assert evidence["inventory"]["paper_or_preprint_included"] is False
    assert evidence["preflight"]["paper_or_preprint_submission_allowed"] is False
    assert evidence["preflight"]["mutation_performed"] is False
