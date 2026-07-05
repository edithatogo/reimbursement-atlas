"""OSF protocol, component and report planning helpers."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.models import OutputArtifactPlanRecord, ResearchQuestionRecord


@dataclass(frozen=True)
class OsfComponentPlan:
    """A planned OSF project component or file group."""

    id: str
    component_title: str
    component_type: str
    local_path: str
    osf_path: str
    required_before_release: bool
    research_question_id: str | None
    notes: str

    def as_row(self) -> dict[str, object]:
        """Return a JSON-serialisable row."""
        return asdict(self)


def build_osf_component_plan(
    questions: list[ResearchQuestionRecord],
    outputs: list[OutputArtifactPlanRecord],
) -> list[OsfComponentPlan]:
    """Build OSF component plan records from research questions and output plans."""
    components: list[OsfComponentPlan] = [
        OsfComponentPlan(
            id="osf_project_root",
            component_title="Reimbursement Atlas research programme",
            component_type="project_root",
            local_path="README.md",
            osf_path="/",
            required_before_release=True,
            research_question_id=None,
            notes="Root OSF project should link GitHub, Hugging Face dataset/Space and releases.",
        ),
        OsfComponentPlan(
            id="osf_methods_papers",
            component_title="Methods papers and preprints",
            component_type="preprints",
            local_path="papers/",
            osf_path="/papers/",
            required_before_release=False,
            research_question_id=None,
            notes="Preprint manuscripts and reviewer response material.",
        ),
    ]
    for question in questions:
        safe_id = question.id.replace("rq_", "osf_")
        components.extend([
            OsfComponentPlan(
                id=f"{safe_id}_protocol",
                component_title=f"Protocol: {question.osf_component}",
                component_type="protocol",
                local_path=question.protocol_path,
                osf_path=f"/protocols/{Path(question.protocol_path).name}",
                required_before_release=True,
                research_question_id=question.id,
                notes=(
                    "Detailed protocol should be reviewed before analysis outputs are interpreted."
                ),
            ),
            OsfComponentPlan(
                id=f"{safe_id}_report",
                component_title=f"Report: {question.osf_component}",
                component_type="report",
                local_path=question.report_path,
                osf_path=f"/reports/{Path(question.report_path).name}",
                required_before_release=False,
                research_question_id=question.id,
                notes="Detailed analysis report populated after derived-data validation.",
            ),
        ])
    for output in outputs:
        if output.target_platform == "osf":
            components.append(
                OsfComponentPlan(
                    id=f"osf_output_{output.id}",
                    component_title=f"Output plan: {output.output_type}",
                    component_type=output.output_type,
                    local_path=output.path,
                    osf_path=f"/{output.output_type}/{Path(output.path).name}",
                    required_before_release=output.output_type in {"protocol", "report"},
                    research_question_id=None,
                    notes=output.notes,
                )
            )
    return components


def write_osf_outputs(
    components: list[OsfComponentPlan],
    *,
    output_dir: Path,
) -> tuple[Path, Path, Path]:
    """Write OSF component plan files and a manifest."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = [component.as_row() for component in components]
    jsonl_path = write_jsonl(rows, output_dir / "component_plan.jsonl")
    csv_path = write_csv(rows, output_dir / "component_plan.csv")
    manifest = {
        "project": "reimbursement-atlas-conductor",
        "osf_use": "protocols, reports, appendices, preregistration material and preprint staging",
        "component_count": len(components),
        "required_before_release": sum(
            1 for component in components if component.required_before_release
        ),
        "raw_data_policy": (
            "Do not upload raw restricted source files to OSF unless licence review explicitly "
            "permits it."
        ),
    }
    manifest_path = output_dir / "osf_publication_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return jsonl_path, csv_path, manifest_path
