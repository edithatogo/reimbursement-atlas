"""PBS source permission stays distinct from publication and other source rights."""

from pathlib import Path

import pytest

from reimburse_atlas.licence_review import pbs_raw_redistribution_status


@pytest.mark.parametrize("host", ["www.pbs.gov.au", "m.pbs.gov.au", "data.pbs.gov.au"])
def test_owner_attestation_allows_pbs_without_per_file_approval(host: str) -> None:
    assert pbs_raw_redistribution_status(f"https://{host}/publication/schedule/file.pdf") == (
        "allowed_owner_attested_permission"
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://www.cms.gov/file.pdf",
        "https://www.mbsonline.gov.au/file.pdf",
        "https://www.pbs.gov.au.example.com/file.pdf",
        "https://www.pbs.gov.au@evil.example/file.pdf",
        "file:///data/raw_live/file.pdf",
        "https://user:secret@www.pbs.gov.au/file.pdf",
    ],
)
def test_permission_does_not_clear_other_sources_or_credentials(url: str) -> None:
    assert pbs_raw_redistribution_status(url) == "outside_pbs_permission_scope"


def test_missing_permission_record_is_not_approval(tmp_path: Path) -> None:
    assert pbs_raw_redistribution_status("https://www.pbs.gov.au/file.pdf", root=tmp_path) == (
        "blocked_pending_explicit_permission"
    )


@pytest.mark.parametrize("content", ["invalid", "[]", "{}", '{"decision":"revoked"}'])
def test_malformed_or_revoked_permission_is_not_approval(tmp_path: Path, content: str) -> None:
    path = tmp_path / "data/licence_review/pbs_raw_permission.json"
    path.parent.mkdir(parents=True)
    path.write_text(content)
    assert pbs_raw_redistribution_status("https://www.pbs.gov.au/file.pdf", root=tmp_path) == (
        "blocked_pending_explicit_permission"
    )
