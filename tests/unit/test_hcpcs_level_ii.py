import json
from pathlib import Path
from zipfile import ZipFile

from reimburse_atlas.hcpcs_level_ii import build_hcpcs_level_ii_bundle


def _line(code: str, record_type: str, long: str, short: str = "") -> str:
    return f"{code:<5}{'':5}{record_type}{long:<80}{short:<28}".ljust(320)


def test_bundle_excludes_restricted_descriptors_and_joins_continuations(
    tmp_path: Path,
) -> None:
    archive = tmp_path / "hcpcs.zip"
    with ZipFile(archive, "w") as package:
        package.writestr(
            "HCPC2026_JUL_ANWEB_test.txt",
            "\n".join(
                [
                    _line("A1001", "3", "Permitted first line", "Permitted item"),
                    _line("A1001", "4", "continued"),
                    _line("12345", "3", "Restricted CPT", "CPT"),
                    _line("D0123", "3", "Restricted dental", "Dental"),
                ]
            ),
        )
    bundle = build_hcpcs_level_ii_bundle(archive, tmp_path / "out")
    output = next(bundle.glob("*schedule_items.jsonl")).read_text(encoding="utf-8")
    row = json.loads(output)
    assert row["item_code"] == "A1001"
    assert row["item_description"] == "Permitted first line continued"
    assert "12345" not in output
    assert "D0123" not in output
