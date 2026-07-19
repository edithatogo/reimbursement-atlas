from pathlib import Path

from reimburse_atlas.models import ResearchQuestionRecord
from reimburse_atlas.protocols import build_protocol_status


def test_complete_drafted_protocol_is_osf_ready_for_registration_review(tmp_path: Path) -> None:
    required = (
        "background",
        "research question",
        "datasets",
        "inclusion",
        "analysis plan",
        "bias",
        "outputs",
        "osf",
        "estimands and outcomes",
        "source versions and analysis window",
        "missing data and denominator rules",
        "mapping and comparability adjudication",
        "uncertainty multiplicity and sensitivity analyses",
        "negative controls and calibration",
        "deviations amendments and human review",
    )
    protocol = tmp_path / "protocol.md"
    report = tmp_path / "report.md"
    protocol.write_text(
        "\n".join(f"## {section}" for section in required) + "\n" + ("Methods detail " * 700),
        encoding="utf-8",
    )
    report.write_text("Report detail " * 1000, encoding="utf-8")
    question = ResearchQuestionRecord(
        id="rq_test",
        track_id="track_policy_demonstrators",
        question="Test question",
        methods=["test"],
        required_datasets=["source_registry"],
        outputs=["report"],
        protocol_path="protocol.md",
        report_path="report.md",
        osf_component="Test",
        preregistration_status="drafted",
    )

    rows = build_protocol_status([question], root=tmp_path)

    assert rows[0].osf_ready is True
