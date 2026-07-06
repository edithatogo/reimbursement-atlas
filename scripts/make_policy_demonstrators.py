"""Generate the first policy demonstrator briefs from local fixtures."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import cast

from reimburse_atlas.demonstrators import build_policy_demonstrator_briefs
from reimburse_atlas.io import pydantic_rows, write_csv, write_jsonl
from reimburse_atlas.parsers import (
    parse_cms_asp_csv,
    parse_cms_clfs_csv,
    parse_cms_pfs_csv,
    parse_mbs_xml,
    parse_nhs_genomic_directory_csv,
    parse_pbs_csv,
)
from reimburse_atlas.registry import project_root


def _render_markdown(
    briefs: Sequence[Mapping[str, object]],
    summary: Mapping[str, int | Sequence[str]],
) -> str:
    lines = ["# Policy demonstrators", ""]
    lines.extend([
        (
            "Generated from local fixture sources only. Missing fixture coverage is listed "
            "in the brief caveats."
        ),
        "",
        f"- Brief count: {summary['brief_count']}",
        f"- Source count: {summary['source_count']}",
        "",
    ])
    for brief in briefs:
        lines.extend([
            f"## {brief['title']}",
            "",
            f"- Demonstrator: `{brief['demonstrator_id']}`",
            f"- Sources compared: {brief['sources_compared']}",
            f"- Item count: {brief['item_count']}",
            f"- Metric summary: {brief['metric_summary']}",
            "- Caveats:",
        ])
        caveats = cast("Sequence[str]", brief["caveats"])
        for caveat in caveats:
            lines.append(f"  - {caveat}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    """Parse local fixtures and write policy-demonstrator artefacts."""
    root = project_root()
    fixtures = root / "tests" / "fixtures"
    output_dir = root / "data" / "derived" / "policy_demonstrators"
    parsed_sources = {
        "au_mbs": parse_mbs_xml(fixtures / "mbs_fragment.xml"),
        "us_cms_clfs": parse_cms_clfs_csv(fixtures / "cms_clfs_fixture.csv"),
        "us_cms_pfs": parse_cms_pfs_csv(fixtures / "cms_pfs_fixture.csv"),
        "au_pbs": parse_pbs_csv(fixtures / "pbs_fixture.csv"),
        "us_cms_asp": parse_cms_asp_csv(fixtures / "cms_asp_fixture.csv"),
        "uk_genomic_test_directory": parse_nhs_genomic_directory_csv(
            fixtures / "nhs_genomic_directory_fixture.csv"
        ),
    }
    briefs = build_policy_demonstrator_briefs(parsed_sources)
    brief_rows = pydantic_rows(briefs)
    summary = {
        "brief_count": len(briefs),
        "source_count": len(parsed_sources),
        "brief_ids": [brief.demonstrator_id for brief in briefs],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(brief_rows, output_dir / "policy_briefs.jsonl")
    write_csv(brief_rows, output_dir / "policy_briefs.csv")
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "policy_briefs.md").write_text(
        _render_markdown(brief_rows, summary),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                **summary,
                "output_dir": str(output_dir),
                "paths": [
                    str(output_dir / "policy_briefs.jsonl"),
                    str(output_dir / "policy_briefs.csv"),
                    str(output_dir / "policy_briefs.md"),
                    str(output_dir / "summary.json"),
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
