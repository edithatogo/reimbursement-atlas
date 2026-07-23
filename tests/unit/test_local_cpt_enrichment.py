import json
from pathlib import Path
from zipfile import ZipFile

import pytest

from reimburse_atlas.local_cpt_enrichment import (
    CptEnrichmentError,
    build_local_cpt_candidates,
)


def _archive(path: Path, *, notice: bool = True) -> None:
    lines = [
        (
            ",,CPT codes and descriptions only are copyright 2026 American Medical "
            "Association. All Rights Reserved."
            if notice
            else ",,missing notice"
        ),
        "HCPCS,MOD,DESCRIPTION,CODE",
        "12345,,Needle biopsy of liver,A",
        "A1234,,Public alpha-numeric supply,A",
    ]
    with ZipFile(path, "w") as package:
        package.writestr("PPRRVU2026_Jul_nonQPP.csv", "\n".join(lines))


def _mbs(path: Path) -> None:
    path.write_text(
        json.dumps({
            "source_id": "au_mbs",
            "item_code": "30001",
            "item_label": "Needle biopsy of liver",
            "item_description": "Percutaneous liver biopsy",
            "domain": "medical_services",
        })
        + "\n",
        encoding="utf-8",
    )


def test_local_cpt_candidates_keep_descriptors_out_of_public_summary(tmp_path: Path) -> None:
    archive = tmp_path / "rvu.zip"
    mbs = tmp_path / "mbs.jsonl"
    _archive(archive)
    _mbs(mbs)

    candidates, summary = build_local_cpt_candidates(
        cms_archive=archive,
        mbs_bundle=mbs,
    )

    assert candidates[0]["right_code"] == "12345"
    assert candidates[0]["right_description"] == "Needle biopsy of liver"
    encoded_summary = json.dumps(summary, sort_keys=True)
    assert "Needle biopsy" not in encoded_summary
    assert str(tmp_path) not in encoded_summary
    assert summary["cpt_record_count"] == 1
    assert summary["descriptor_storage"] == "ignored_local_only"


def test_local_cpt_enrichment_rejects_missing_copyright_notice(tmp_path: Path) -> None:
    archive = tmp_path / "rvu.zip"
    mbs = tmp_path / "mbs.jsonl"
    _archive(archive, notice=False)
    _mbs(mbs)

    with pytest.raises(CptEnrichmentError, match="copyright notice"):
        build_local_cpt_candidates(cms_archive=archive, mbs_bundle=mbs)
