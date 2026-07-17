from pathlib import Path

from reimburse_atlas.automation import automation_control_records


def test_sbom_control_requires_both_generated_sboms(tmp_path: Path) -> None:
    root = tmp_path
    sbom_dir = root / "data" / "derived" / "sbom"
    sbom_dir.mkdir(parents=True)

    control = next(
        item for item in automation_control_records(root) if item.id == "sbom_generation"
    )
    assert control.status == "planned"
    assert control.maturity == "prototype"

    (sbom_dir / "cyclonedx-python.json").write_text("{}\n", encoding="utf-8")
    (sbom_dir / "cyclonedx-dashboard.json").write_text("{}\n", encoding="utf-8")

    control = next(
        item for item in automation_control_records(root) if item.id == "sbom_generation"
    )
    assert control.status == "implemented"
    assert control.maturity == "advanced"
