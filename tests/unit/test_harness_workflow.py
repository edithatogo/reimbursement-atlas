"""Structural safeguards for the hosted deterministic-regeneration harness."""

from pathlib import Path


def test_harness_reconciles_release_receipts_after_dashboard_inputs_settle() -> None:
    workflow = Path(".github/workflows/harness-assurance.yml").read_text(encoding="utf-8")
    final_pass = [
        "pixi run release-readiness",
        "pixi run final-handoff",
        "pixi run source-drift",
        "pixi run field-lineage",
        "pixi run research-package",
        "pixi run seed-lake",
        "pixi run dashboard-seed",
        "pixi run dashboard-status",
        "pixi run zenodo-draft",
        "pixi run zenodo-deposition-plan",
    ]

    indented_block = "\n".join(f"            {command}" for command in final_pass)
    assert "          for reconciliation_pass in 1 2; do\n" in workflow
    assert workflow.count(indented_block) == 1
    assert "          done\n" in workflow
