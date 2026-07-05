from pathlib import Path

from reimburse_atlas.parsers.mbs_txt import (
    fixed_width_tokenize,
    parse_mbs_txt_pair,
    parse_stats,
    tokenize_mbs_txt_line,
)
from reimburse_atlas.registry import load_source_files, load_source_versions, project_root
from reimburse_atlas.toolchain import classify_gate_result


def test_source_files_reference_known_versions() -> None:
    files = load_source_files()
    versions = {version.id for version in load_source_versions()}
    assert {source_file.source_version_id for source_file in files} <= versions
    assert any(
        source_file.acquisition_mode == "licence_clickthrough_manual" for source_file in files
    )


def test_mbs_txt_pair_parser_joins_descriptors() -> None:
    fixtures = project_root() / "tests" / "fixtures" / "mbs_txt"
    records = parse_mbs_txt_pair(
        fixtures / "20260701_MBSONLINE_IMAP_fixture.TXT",
        fixtures / "20260701_MBSONLINE_DESC_fixture.TXT",
    )
    by_code = {record.item_code: record for record in records}
    assert by_code["73358"].payment_amount == 1200.0
    assert by_code["73358"].item_label.startswith("Whole exome")
    assert by_code["99999"].payment_amount is None
    assert by_code["99999"].provenance.source_version == "au_mbs_20260701_txt_pair"


def test_mbs_txt_pair_parse_stats() -> None:
    fixtures = Path("tests/fixtures/mbs_txt")
    stats = parse_stats(
        fixtures / "20260701_MBSONLINE_IMAP_fixture.TXT",
        fixtures / "20260701_MBSONLINE_DESC_fixture.TXT",
    )
    assert stats.item_map_rows == 2
    assert stats.descriptor_rows == 3
    assert stats.joined_rows == 2
    assert stats.descriptor_only_rows == 1


def test_mbs_txt_tokenizers_cover_delimited_and_fixed_width_inputs() -> None:
    assert fixed_width_tokenize("ABCDE12345", widths=(5, 5)) == ("ABCDE", "12345")
    assert tokenize_mbs_txt_line("a|b|c", delimiter="|") == ("a", "b", "c")
    fallback = tokenize_mbs_txt_line("ABCDE12345", delimiter=None)
    assert fallback[0] == "ABCDE"
    assert fallback[1] == "12"
    assert len(fallback) == 7


def test_external_gate_classifier_identifies_network_block() -> None:
    outcome = classify_gate_result(
        1,
        "",
        "NameResolutionError: Temporary failure in name resolution for pypi.org",
    )
    assert outcome == "blocked_network"
