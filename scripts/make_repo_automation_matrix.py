"""Generate repository automation and GitHub workflow policy artefacts."""

from __future__ import annotations

import json

from reimburse_atlas.automation import (
    automation_control_records,
    scan_workflow_uses,
    workflow_policy_records,
    workflow_policy_summary,
)
from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.registry import project_root


def main() -> None:
    """Write workflow-use, workflow-policy and automation-control tables."""
    root = project_root()
    out_dir = root / "data" / "derived" / "repo_automation"
    out_dir.mkdir(parents=True, exist_ok=True)

    uses = [record.as_row() for record in scan_workflow_uses(root)]
    policy_records = workflow_policy_records(root)
    policies = [record.as_row() for record in policy_records]
    controls = [record.as_row() for record in automation_control_records(root)]
    sha_pin_plan = [
        {
            **row,
            "priority": "high" if row["pin_class"] in {"floating", "unknown"} else "medium",
            "recommended_action": (
                "Resolve the action tag to a 40-character commit SHA and preserve the "
                "human-readable version as a trailing comment."
            ),
        }
        for row in uses
        if row["pin_class"] not in {"sha", "local", "docker"}
    ]
    summary = workflow_policy_summary(policy_records)

    write_jsonl(uses, out_dir / "workflow_uses.jsonl")
    write_csv(uses, out_dir / "workflow_uses.csv")
    write_jsonl(policies, out_dir / "workflow_policy.jsonl")
    write_csv(policies, out_dir / "workflow_policy.csv")
    write_jsonl(controls, out_dir / "automation_controls.jsonl")
    write_csv(controls, out_dir / "automation_controls.csv")
    write_jsonl(sha_pin_plan, out_dir / "action_sha_pin_plan.jsonl")
    write_csv(sha_pin_plan, out_dir / "action_sha_pin_plan.csv")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "workflow_uses": len(uses),
                "workflow_policy_records": len(policies),
                "automation_controls": len(controls),
                "action_sha_pin_plan": len(sha_pin_plan),
                "summary": summary,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
