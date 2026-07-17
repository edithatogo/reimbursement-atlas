"""Tests for the metadata-only historical MBS archive inventory."""

from pathlib import Path

from scripts import make_historical_source_index as historical_index


def test_historical_period_extracts_calendar_year() -> None:
    assert historical_index.extract_period("2007-11-MBS.pdf") == "2007"
    assert historical_index.extract_period("MBS%20Book%201%20July%202025.PDF") == "2025"
    assert historical_index.extract_period("RVG%20file%2020250701.TXT") == "2025"
    assert historical_index.extract_period("MBSOnline_REUSE_IMAP.TXT") == "unknown"


def test_historical_file_filter_accepts_public_archive_formats() -> None:
    assert historical_index.is_archive_file("https://www.mbsonline.gov.au/archive/2007-MBS.pdf")
    assert historical_index.is_archive_file("https://www.mbsonline.gov.au/archive/2020-items.txt")
    assert not historical_index.is_archive_file("https://www.mbsonline.gov.au/archive/index.html")


def test_historical_url_filter_is_official_https_only() -> None:
    base = "https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/Content/Prev-Downloads"
    assert historical_index.official_url(base, "2007-MBS.pdf") is not None
    assert historical_index.official_url(base, "https://example.com/file.pdf") is None
    assert historical_index.official_url(base, "http://www.mbsonline.gov.au/file.pdf") is None


def test_historical_inventory_workflow_exposes_src_on_python_path() -> None:
    workflow = (
        Path(__file__).parents[2] / ".github/workflows/historical-source-inventory.yml"
    ).read_text(encoding="utf-8")
    assert "      PYTHONPATH: src" in workflow


def test_historical_review_queue_stays_pending_without_approval(tmp_path: Path) -> None:
    seed = tmp_path / "targets.jsonl"
    seed.write_text(
        '{"archive_page":"https://www.mbsonline.gov.au/archive/index.html",'
        '"file_name":"2007-MBS.pdf","file_url":"https://www.mbsonline.gov.au/archive/2007-MBS.pdf",'
        '"id":"au_mbs_historical_0001","licence_gate":"public_reuse_review",'
        '"download_policy":"manual_review_only"}\n',
        encoding="utf-8",
    )
    output_dir = tmp_path / "derived"
    rows = [historical_index.json.loads(line) for line in seed.read_text().splitlines()]
    historical_index.write_rows(rows, seed_path=seed, output_dir=output_dir)
    review = (output_dir / "historical_mbs_review_queue.jsonl").read_text(encoding="utf-8")
    assert '"review_status": "pending_human_review"' in review
    assert '"reviewer": ""' in review
    assert '"decision_evidence": ""' in review
    assert '"licence_gate": "public_reuse_review"' in review
