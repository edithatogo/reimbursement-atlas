"""Render GitHub issue drafts from the Conductor backlog.

The script intentionally writes markdown issue drafts rather than calling GitHub.
That keeps repository generation deterministic and avoids assuming credentials.
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "conductor" / "backlog.yml"
OUTPUT = ROOT / ".github" / "generated-issues"


@dataclass
class IssueDraft:
    """Minimal issue data parsed from the constrained backlog YAML."""

    epic_id: str
    epic_title: str
    title: str
    labels: list[str] = field(default_factory=list)
    parent_issue: str | None = None
    status: str | None = None


def _strip_quotes(value: str) -> str:
    return value.strip().strip('"')


def parse_backlog(path: Path = BACKLOG) -> list[IssueDraft]:
    """Parse the simple Conductor backlog format into issue drafts."""
    issues: list[IssueDraft] = []
    epic_id = "UNKNOWN"
    epic_title = "Unknown epic"
    current: IssueDraft | None = None

    for line in path.read_text(encoding="utf-8").splitlines():
        if match := re.match(r"^  - id: (.+)$", line):
            epic_id = _strip_quotes(match.group(1))
            continue
        if match := re.match(r"^    title: (.+)$", line):
            epic_title = _strip_quotes(match.group(1))
            continue
        if match := re.match(r"^      - title: (.+)$", line):
            current = IssueDraft(
                epic_id=epic_id,
                epic_title=epic_title,
                title=_strip_quotes(match.group(1)),
            )
            issues.append(current)
            continue
        if current and (match := re.match(r"^        labels: (\[.+\])$", line)):
            parsed = ast.literal_eval(match.group(1))
            current.labels = [str(item) for item in parsed]
            continue
        if current and (match := re.match(r"^        status: (.+)$", line)):
            current.status = _strip_quotes(match.group(1))
    return issues


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    rows: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            loaded = json.loads(line)
            if isinstance(loaded, dict):
                rows.append(cast("dict[str, object]", loaded))
    return rows


def generated_track_issues(
    root: Path = ROOT,
    *,
    parent_issue_titles: set[str] | None = None,
) -> list[IssueDraft]:
    """Generate issue drafts from machine-readable roadmap seed records."""
    seed_dir = root / "data" / "seed"
    tracks = {str(row["id"]): row for row in _read_jsonl(seed_dir / "conductor_tracks.jsonl")}
    issues: list[IssueDraft] = []
    for row in _read_jsonl(seed_dir / "roadmap_functions.jsonl"):
        track_id = str(row.get("track_id", "track_unknown"))
        track = tracks.get(track_id, {})
        issues.append(
            IssueDraft(
                epic_id=track_id.upper(),
                epic_title=str(track.get("title", "Conductor roadmap track")),
                title=str(row.get("github_issue_title", row.get("name", "Roadmap function"))),
                labels=[
                    "type:roadmap-function",
                    f"priority:{row.get('priority', 'unknown')}",
                    f"interface:{row.get('interface', 'unknown')}",
                    f"status:{row.get('status', 'planned')}",
                ],
                parent_issue=(
                    str(track.get("title"))
                    if str(track.get("title")) in (parent_issue_titles or set())
                    else None
                ),
                status=str(row.get("status", "planned")),
            )
        )
    for row in _read_jsonl(seed_dir / "dataset_candidates.jsonl"):
        issues.append(
            IssueDraft(
                epic_id="DATASET-CANDIDATES",
                epic_title="Additional dataset and country onboarding",
                title=f"Onboard dataset candidate: {row.get('name', row.get('id'))}",
                labels=[
                    "type:data-source",
                    f"priority:{row.get('priority', 'unknown')}",
                    "phase:future",
                ],
            )
        )
    for row in _read_jsonl(seed_dir / "research_questions.jsonl"):
        issues.append(
            IssueDraft(
                epic_id="RESEARCH-QUESTIONS",
                epic_title="Protocolled policy research questions",
                title=f"Complete protocol and report: {row.get('id')}",
                labels=["type:research", "type:osf", "phase:analysis"],
            )
        )
    for row in _read_jsonl(seed_dir / "output_artifact_plans.jsonl"):
        issues.append(
            IssueDraft(
                epic_id="OUTPUTS",
                epic_title="Publication and deployment outputs",
                title=f"Implement output plan: {row.get('id')}",
                labels=[
                    "type:publication",
                    f"target:{row.get('target_platform', 'unknown')}",
                ],
            )
        )
    return issues


def render_issue(issue: IssueDraft) -> str:  # noqa: PLR0912,PLR0915 - criteria are explicit per track
    """Render one GitHub issue draft."""
    labels = ", ".join(issue.labels) if issue.labels else "none"
    parent = f"Parent issue: {issue.parent_issue}\n\n" if issue.parent_issue else ""
    if issue.title == "Expand reviewed coverage with historical MBS and PBS bundles":
        acceptance = (
            "- [x] Scope is confirmed: metadata-only inventory automation is implemented; raw "
            "bundle acquisition remains gated.\n"
            "- [x] Licence and data-governance implications are checked: historical targets remain "
            "manual-review only.\n"
            "- [x] Tests or validation evidence are defined: `pixi run historical-sources`, source "
            "validation and source contracts.\n"
            "- [x] Documentation or Conductor context is updated.\n"
            "- [ ] Source-specific licence approval and reviewed PBS extract are complete.\n"
            "- [ ] Historical raw payloads have been acquired into ignored local storage and "
            "promoted "
            "to reviewed derived bundles."
        )
    elif issue.title == "Add URL/licence verification checklist for first-wave sources":
        acceptance = (
            "- [x] Scope is confirmed: source-file and registry URLs for first-wave sources are "
            "listed in a generated checklist.\n"
            "- [x] Licence and data-governance implications are checked: licence gates and "
            "ignored-raw handling are explicit.\n"
            "- [x] Tests or validation evidence are defined: `pixi run "
            "source-url-licence-checklist` "
            "and focused unit tests.\n"
            "- [x] Documentation or Conductor context is updated in the manual acquisition pack "
            "and dashboard.\n"
            "- [ ] Human URL reachability and source-term review is complete."
        )
    elif issue.title == "Implement CMS PFS parser prototype to ScheduleItemRecord":
        acceptance = (
            "- [x] Scope is confirmed: the fixture-backed CMS PFS CSV parser emits "
            "`ScheduleItemRecord` values.\n"
            "- [x] Licence and data-governance implications are checked: CPT descriptors "
            "remain excluded from redistribution.\n"
            "- [x] Tests or validation evidence are defined: focused parser and contract tests.\n"
            "- [x] Documentation or Conductor context is updated in the parser and ingestion "
            "plans.\n"
            "- [ ] Validation against a reviewed RVU26C file is complete."
        )
    elif issue.title == "Add LOINC/HPO/HGNC local-only adapter conventions":
        acceptance = (
            "- [x] Scope is confirmed: local-only terminology adapter conventions are recorded "
            "for LOINC, HPO and HGNC.\n"
            "- [x] Licence and data-governance implications are checked: restricted releases "
            "are not mirrored and synthetic concepts remain labelled.\n"
            "- [x] Tests or validation evidence are defined: ontology registry, mapping template "
            "and seed synchronisation gates.\n"
            "- [x] Documentation or Conductor context is updated in the ontology strategy.\n"
            "- [ ] Human clinical mapping review is complete for real source mappings."
        )
    elif issue.title == "Validate MBS parser against one manually downloaded XML release":
        acceptance = (
            "- [x] Parser contract and synthetic XML fixture are implemented.\n"
            "- [ ] A real manually downloaded XML release is present in ignored local storage.\n"
            "- [ ] Source URL, terms and checksum are recorded by an accountable reviewer.\n"
            "- [ ] Parser output is validated without redistributing restricted descriptors."
        )
    elif issue.title == "Review first real July 2026 MBS TXT pair bundle outputs":
        acceptance = (
            "- [x] July 2026 MBS TXT-pair bundle and validation report are generated locally.\n"
            "- [ ] Human domain/licence review confirms the joined and descriptor-only row "
            "policy.\n"
            "- [ ] Review decision is recorded against the bundle checksums before publication."
        )
    elif issue.title == "Validate PBS API CSV parser against a reviewed monthly public extract":
        acceptance = (
            "- [x] PBS API CSV parser and July 2026 local acquisition evidence exist.\n"
            "- [ ] A human reviews the monthly extract fields, terms and effective-date join.\n"
            "- [ ] The reviewed extract checksum and permitted derived fields are recorded."
        )
    elif issue.title == "Validate CMS ASP parser against July 2026 payment-limit files":
        acceptance = (
            "- [x] CMS ASP parser contract and synthetic fixture are implemented.\n"
            "- [ ] July 2026 payment-limit payload is manually acquired into ignored local "
            "storage.\n"
            "- [ ] Source terms, checksum and permitted payment-limit fields are reviewed.\n"
            "- [ ] Parsed output is validated without treating payment limits as net prices."
        )
    elif issue.title == "Prototype Mojo fuzzy prefilter for large crosswalk candidate sets":
        acceptance = (
            "- [x] Scope is confirmed: candidate generation only, never an equivalence decision.\n"
            "- [x] Licence and data-governance implications are checked for the synthetic local "
            "fixture.\n"
            "- [x] Tests or validation evidence are defined: `pixi run fuzzy-benchmark` records "
            "recall,\n"
            "  precision and specificity at a deterministic threshold.\n"
            "- [x] Documentation or Conductor context is updated.\n"
            "- [ ] Human adjudication of real reviewed mappings is complete.\n\n"
            "Current synthetic fixture evidence: recall `1.0`, precision `1.0`, "
            "specificity `1.0` at\n"
            "threshold `0.2`. This does not establish evidence-grade performance."
        )
    elif issue.title == "Create signed release and Zenodo DOI after publication approval":
        acceptance = (
            "- [x] Scope is confirmed: prepare and validate metadata locally; do not deposit or "
            "mint a DOI.\n"
            "- [ ] Licence and data-governance implications are checked by an accountable human "
            "reviewer.\n"
            "- [x] Tests or validation evidence are defined: `pixi run zenodo-metadata` and "
            "focused unit tests.\n"
            "- [x] Tagged software releases require a least-privilege governance preflight before "
            "asset creation and attestation.\n"
            "- [x] Documentation or Conductor context is updated; external deposition remains "
            "gated."
        )
    elif issue.title == "Add Hugging Face dataset-card contract checks before public release":
        acceptance = (
            "- [x] Scope is confirmed: validate versioned dataset-card metadata before any HF "
            "publication mutation.\n"
            "- [x] Licence and data-governance implications are checked: the card distinguishes "
            "Apache-2.0 code from source-specific data terms.\n"
            "- [x] Tests or validation evidence are defined: `pixi run hf-bundle` and focused "
            "unit tests.\n"
            "- [x] Documentation or Conductor context is updated; the pull-request data-smoke "
            "workflow runs the contract.\n"
            "- [ ] Accountable human source-licence approval and HF publication authorization "
            "are complete."
        )
    elif issue.title == "Add reviewed-source bundle workflow to live-source validation docs":
        acceptance = (
            "- [x] Scope is confirmed: the manual reviewed-source and MBS TXT-pair workflows "
            "are documented.\n"
            "- [x] Licence and data-governance implications are checked: raw payloads remain "
            "ignored and derived bundles remain review-gated.\n"
            "- [x] Tests or validation evidence are defined: source-content, source-contract "
            "and reviewed-bundle validators.\n"
            "- [x] Documentation or Conductor context is updated in the live-source playbook.\n"
            "- [ ] Human source-specific licence review is complete for each candidate bundle."
        )
    elif issue.title == (
        "Generate artifact-level licence review queue bound to publication checksums"
    ):
        acceptance = (
            "- [x] Scope is confirmed: every publication candidate is represented by a generated "
            "queue row.\n"
            "- [x] Licence and data-governance implications are checked: rows are checksum-bound "
            "and fail closed.\n"
            "- [x] Tests or validation evidence are defined: deterministic queue generation and "
            "licence-review validation.\n"
            "- [x] Documentation or Conductor context is updated in the queue README and release "
            "documentation.\n"
            "- [ ] Human decisions are recorded for every candidate before publication."
        )
    elif issue.title == "Expose the checksum-bound licence review queue in the dashboard":
        acceptance = (
            "- [x] Scope is confirmed: the readiness dashboard exposes the generated queue and "
            "checksum/status fields.\n"
            "- [x] Licence and data-governance implications are checked: the view states that "
            "display does not grant approval.\n"
            "- [x] Tests or validation evidence are defined: dashboard build and generated-data "
            "checks.\n"
            "- [x] Documentation or Conductor context is updated in the readiness page.\n"
            "- [ ] Human licence decisions are complete before publication."
        )
    elif issue.title == "Validate human licence decisions against checksum-bound queue rows":
        acceptance = (
            "- [x] Scope is confirmed: validate queue integrity and optional human decision rows; "
            "do not infer approval.\n"
            "- [x] Licence and data-governance implications are checked: decisions require source "
            "terms, attribution, permission, restrictions and evidence.\n"
            "- [x] Tests or validation evidence are defined: `pixi run licence-review-validate` "
            "plus stale-checksum and incomplete-decision tests.\n"
            "- [x] Documentation or Conductor context is updated; CI runs the validator.\n"
            "- [ ] An accountable human has reviewed each candidate artefact before any approval "
            "record is added."
        )
    elif issue.title == "Enable GitHub non-provider secret-pattern scanning and validity checks":
        acceptance = (
            "- [x] Scope is confirmed: request and verify the two distinct GitHub security "
            "settings.\n"
            "- [x] Licence and data-governance implications are checked: no secret values are "
            "recorded in repository artefacts.\n"
            "- [x] Tests or validation evidence are defined: full-history Gitleaks CI and live "
            "repository-settings API evidence.\n"
            "- [x] Documentation or Conductor context is updated.\n"
            "- [ ] GitHub reports `secret_scanning_non_provider_patterns=enabled`.\n"
            "- [ ] GitHub reports `secret_scanning_validity_checks=enabled`; current account state "
            "remains disabled for both."
        )
    elif issue.title == "Schedule source-health and source-drift monitoring with issue escalation":
        acceptance = (
            "- [x] Scope is confirmed: the scheduled monitor runs acquisition, validation, "
            "contract, drift and release-readiness checks without publishing source payloads.\n"
            "- [x] Licence and data-governance implications are checked: raw downloads remain "
            "ephemeral and issue reports contain only derived evidence and secret names.\n"
            "- [x] Tests or validation evidence are defined: source-health workflow policy and "
            "issue-escalation contract tests, plus `pixi run source-health-report`.\n"
            "- [x] Documentation or Conductor context is updated; failure and "
            "incomplete-acquisition "
            "issues are opened or updated, and clear acquisition issues are closed.\n"
            "- [x] Workflow issue mutation is least-privilege and scoped to the source-health job."
        )
    elif issue.title == "Make research package descriptors deterministic and non-self-referential":
        acceptance = (
            "- [x] Scope is confirmed: Frictionless, RO-Crate and DCAT descriptors describe "
            "licence-safe derived artefacts only.\n"
            "- [x] Licence and data-governance implications are checked: descriptor files are "
            "excluded from the candidate manifest and do not change source-data terms.\n"
            "- [x] Tests or validation evidence are defined: deterministic regeneration and "
            "non-self-reference contract tests.\n"
            "- [x] Documentation or Conductor context is updated in the publication-manifest "
            "descriptor-determinism section."
        )
    elif issue.title == "Harden CLI command surface and output contracts":
        acceptance = (
            "- [x] Read-only registry commands preserve Rich tables and expose explicit `--json` "
            "output.\n"
            "- [x] JSON contracts are covered by CLI end-to-end tests and contain derived metadata "
            "only.\n"
            "- [x] CLI/API/MCP documentation records the output contract and licence boundary."
        )
    elif issue.title == (
        "Normalize Apache-2.0 code licence metadata and source-data NOTICE boundary"
    ):
        acceptance = (
            "- [x] Project-owned code and documentation declare Apache-2.0 in `pyproject.toml`, "
            "`CITATION.cff`, `LICENSE`, and `NOTICE`.\n"
            "- [x] `NOTICE` and public-doc freshness checks explicitly preserve provider-specific "
            "terms for source data and third-party materials.\n"
            "- [x] Unit and public documentation validation cover the code/data licence boundary."
        )
    elif issue.title == "Draft read-only MCP server implementation plan":
        acceptance = (
            "- [x] A lazy optional MCP server exposes read-only source, analysis, readiness, and "
            "ingestion-plan resources.\n"
            "- [x] `mcp/tools.seed.json` and `docs/API_MCP_CLI_PLAN.md` document the read-only "
            "tool boundary and no-live-fetch policy.\n"
            "- [x] The optional interface module is import-tested without requiring the MCP SDK "
            "in the default environment."
        )
    elif issue.title == "Add readiness table views to Astro dashboard":
        acceptance = (
            "- [x] The `/readiness/` route renders source, analysis, ingestion, licence, and "
            "release-readiness tables from generated dashboard-safe artefacts.\n"
            "- [x] Route and dashboard asset contracts validate the generated CSV inputs without "
            "including raw restricted payloads.\n"
            "- [x] Readiness views preserve the separation between repository, evidence, and "
            "publication readiness."
        )
    elif issue.title == "Add crosswalk review queue view to Astro dashboard":
        acceptance = (
            "- [x] The `/crosswalks/` route renders candidate mappings, review queue, evidence, "
            "gold-standard, and negative-control tables.\n"
            "- [x] The view labels candidates as requiring domain review and does not imply "
            "mapping approval or evidence readiness.\n"
            "- [x] Generated crosswalk assets are included in dashboard seed synchronisation and "
            "route checks."
        )
    elif issue.title == "Define local adapter contracts for RxNav-in-a-Box style services":
        acceptance = (
            "- [x] Scope is confirmed: a read-only, local-only RxNav-compatible HTTP contract is "
            "defined without bundling RxNorm payloads or credentials.\n"
            "- [x] Licence and data-governance implications are checked: configuration defaults to "
            "local use and returned matches remain machine-generated candidates.\n"
            "- [x] Tests or validation evidence are defined: deterministic URL construction and "
            "minimal response parsing are covered by `tests/unit/test_terminologies_v5.py`.\n"
            "- [x] Documentation or Conductor context is updated in `docs/ONTOLOGY_STRATEGY.md`; "
            "domain review is still required before mapping promotion."
        )
    elif issue.title == "Add source-version schema for MBS, CMS CLFS and NHS genomic directory":
        acceptance = (
            "- [x] Scope is confirmed: exact source versions, effective dates, formats, checksums "
            "and licence gates are represented by the typed source-version contract.\n"
            "- [x] Licence and data-governance implications are checked: the schema stores "
            "metadata and provenance, not raw restricted payloads.\n"
            "- [x] Tests or validation evidence are defined by schema export, seed synchronisation "
            "and registry contract tests.\n"
            "- [x] Documentation or Conductor context is updated; source-specific reuse review is "
            "still required before publication."
        )
    elif issue.title == "Record redacted PBS API multi-endpoint acquisition evidence":
        acceptance = (
            "- [x] Scope is confirmed: schedules, paginated items and fees are represented by "
            "redacted counts, columns, checksums and review status.\n"
            "- [x] Licence and data-governance implications are checked: raw API responses remain "
            "ignored and the subscription key is never recorded.\n"
            "- [x] Tests or validation evidence are defined by PBS acquisition evidence tests and "
            "source-contract validation.\n"
            "- [x] Documentation or Conductor context is updated; derived publication remains "
            "pending source and licence review."
        )
    elif issue.title == "Add synthetic ontology concept seed parser and mapping templates":
        acceptance = (
            "- [x] Scope is confirmed: synthetic concepts and candidate mapping templates are "
            "generated without importing restricted terminology payloads.\n"
            "- [x] Licence and data-governance implications are checked: synthetic fixtures are "
            "clearly labelled and external terminology remains local-only.\n"
            "- [x] Tests or validation evidence are defined by ontology parsing and "
            "mapping-template unit tests plus seed synchronisation.\n"
            "- [x] Documentation or Conductor context is updated; domain adjudication is required "
            "before any mapping becomes evidence."
        )
    elif issue.title == "Public product, citation and dashboard maturity":
        acceptance = (
            "- [x] Scope is confirmed: the Astro dashboard, public status manifest, citation "
            "metadata and release documentation are maintained as one product surface.\n"
            "- [x] Licence and data-governance implications are checked by public-data policy and "
            "publication-manifest gates.\n"
            "- [x] Tests or validation evidence are defined by dashboard build, browser matrix, "
            "citation validation and public documentation checks.\n"
            "- [x] Documentation or Conductor context is updated; evidence and publication claims "
            "remain fail-closed."
        )
    elif issue.title == "Run pip-audit strict in network-enabled CI before public release":
        acceptance = (
            "- [x] Scope is confirmed: CI runs `pip-audit --strict` using the pinned Pixi task.\n"
            "- [x] Licence and data-governance implications are checked: advisory results do not "
            "alter source-data publication terms.\n"
            "- [x] Tests or validation evidence are defined: the protected `python-security` job "
            "and external-quality-gates artefact provide network-enabled evidence.\n"
            "- [x] Documentation or Conductor context is updated; local advisory lookup remains "
            "environment-dependent outside CI."
        )
    elif issue.title == "Gate OSF publication on protocol-status readiness table":
        acceptance = (
            "- [x] Scope is confirmed: OSF mutation commands fail closed when protocol status is "
            "not ready.\n"
            "- [x] Licence and data-governance implications are checked: blocked rows are not "
            "published or silently relabelled.\n"
            "- [x] Tests or validation evidence are defined: protocol-status and OSF sync tests "
            "cover blocked registration and publication actions.\n"
            "- [x] Documentation or Conductor context is updated in `docs/OSF_RECONCILIATION.md`; "
            "registration still requires accountable review."
        )
    elif issue.title == "Expand protocol templates with source-specific sensitivity analyses":
        acceptance = (
            "- [x] Scope is confirmed: all five protocol scaffolds include estimands, missingness, "
            "mapping, uncertainty, sensitivity and amendment sections.\n"
            "- [x] Licence and data-governance implications are checked in each protocol's source "
            "and publication gates.\n"
            "- [x] Tests or validation evidence are defined by protocol-status generation and "
            "release-readiness checks.\n"
            "- [x] Documentation or Conductor context is updated in `protocols/` and the review "
            "checklist; no protocol is treated as approved."
        )
    elif issue.title == "Add reviewer checklist for each protocol before preregistration":
        acceptance = (
            "- [x] Scope is confirmed: the shared checklist is applied to every registered "
            "research "
            "question.\n"
            "- [x] Licence and data-governance implications are explicit checklist decisions.\n"
            "- [x] Tests or validation evidence are defined through protocol-status and OSF "
            "gate outputs.\n"
            "- [x] Documentation or Conductor context is updated in "
            "`docs/RESEARCH_PROTOCOL_REVIEW_CHECKLIST.md`; "
            "all current decisions remain pending human review."
        )
    elif issue.title == "Pin and contract-test the stable OSF CLI command surface":
        acceptance = (
            "- [x] Scope is confirmed: the unauthenticated contract checks the pinned version and "
            "required help markers without mutating OSF.\n"
            "- [x] Licence and data-governance implications are checked; credentials are never "
            "read "
            "by the contract probe.\n"
            "- [x] Tests or validation evidence are defined in "
            "`tests/unit/test_osf_cli_contract.py` "
            "and the `osf-cli-contract` Pixi task.\n"
            "- [x] Documentation or Conductor context is updated; live OSF publication remains "
            "gated."
        )
    elif issue.title == "Expand OSF protocols and report scaffolds with required sections":
        acceptance = (
            "- [x] Scope is confirmed: protocol, report, data-dictionary, source and sensitivity "
            "scaffolds are generated for each research question.\n"
            "- [x] Licence and data-governance implications remain explicit in publication "
            "manifests "
            "and protocol files.\n"
            "- [x] Tests or validation evidence are defined by protocol-status, research-package "
            "and deterministic-regeneration gates.\n"
            "- [x] Documentation or Conductor context is updated; OSF registration is still gated "
            "by accountable review."
        )
    elif issue.title == "Scan complete Git history for committed secrets":
        acceptance = (
            "- [x] Scope is confirmed: the protected security workflow checks full Git history "
            "with "
            "`fetch-depth: 0`.\n"
            "- [x] Licence and data-governance implications are checked; reports do not publish "
            "secret "
            "values.\n"
            "- [x] Tests or validation evidence are defined by the required `secret-history` "
            "Gitleaks "
            "check.\n"
            "- [x] Documentation or Conductor context is updated in the security assurance "
            "workflow."
        )
    elif issue.title == "Verify reproducible Python release artefacts in CI":
        acceptance = (
            "- [x] Scope is confirmed: CI builds twice with a fixed `SOURCE_DATE_EPOCH` and "
            "compares "
            "artifact names and bytes.\n"
            "- [x] Licence and data-governance implications are checked through the release "
            "manifest "
            "and publication policy.\n"
            "- [x] Tests or validation evidence are defined by the required `reproducible-build` "
            "check and uploaded checksum evidence.\n"
            "- [x] Documentation or Conductor context is updated in `docs/RELEASE_VERIFICATION.md`."
        )
    elif issue.title == "Require security and harness contexts in branch protection":
        acceptance = (
            "- [x] Scope is confirmed: strict protection requires the repository's security and "
            "harness contexts.\n"
            "- [x] Licence and data-governance implications are not altered by branch settings.\n"
            "- [x] Tests or validation evidence are defined by the branch-protection drift "
            "validator "
            "and live API read-back.\n"
            "- [x] Documentation or Conductor context is updated; no administrator bypass is used."
        )
    elif issue.title == "Add dashboard table for policy signal matrix and analysis recipes":
        acceptance = (
            "- [x] The `/analyses/` route renders analysis recipes and the policy signal matrix "
            "from generated artefacts.\n"
            "- [x] Columns expose quality gates, caveats, price observability, and restriction "
            "signals without claiming policy evidence readiness.\n"
            "- [x] Dashboard seed synchronisation and browser build cover the published route."
        )
    elif issue.title == "Add source-content validation gate for downloaded public files":
        acceptance = (
            "- [x] Source-content validation is generated for the acquisition registry and runs in "
            "CI and source-health workflows.\n"
            "- [x] Licence-gated, metadata-only, missing, and executable-source states remain "
            "distinct and fail closed.\n"
            "- [x] Validation outputs are checksum/provenance-linked derived artefacts; raw live "
            "payloads remain ignored."
        )
    elif issue.title == "Add dashboard views for source validation and data-quality checks":
        acceptance = (
            "- [x] Public dashboard routes expose source validation, data-quality, and drift "
            "tables from generated artefacts.\n"
            "- [x] Dashboard assets are sanitised and checked for ignored raw-cache paths and "
            "absolute local paths.\n"
            "- [x] CI regenerates and builds the dashboard before protected merges."
        )
    elif issue.title == "Rebind the required zizmor check to the repository-owned workflow app":
        acceptance = (
            "- [x] Scope is confirmed: only the required `zizmor` app binding was changed.\n"
            "- [x] Strict protection and all 20 required status contexts were preserved.\n"
            "- [x] GraphQL and REST read-back confirm `zizmor` is bound to GitHub Actions app "
            "`15368`, not Advanced Security app `57789`.\n"
            "- [x] Conductor, documentation and GitHub issue evidence are updated."
        )
    elif issue.title in {
        "Add architecture-boundary import graph checks to CI",
        "Add release-readiness matrix with required-blocker counts",
        "Add data-quality checks as a release-readiness gate",
        "Add research-question linkage matrix to roadmap and OSF planning",
        "Add source-specific contract validation before reviewed-source bundle parsing",
        "Generate GitHub Project import rows from Conductor tracks and issue drafts",
        "Generate final network credential and review handoff checklist",
        "Expose source contracts GitHub Project rows and final handoff tasks in dashboard",
        "Add Codex import prompt for git bundle restoration and track execution",
        "Verify Codex continuation process regenerates Conductor issue and project outputs",
        "Ensure continuation agents record blockers rather than marking unavailable gates green",
        "Run property integration and end-to-end harnesses as separate CI lanes",
        "Use interpreter-bound module invocation for Pixi Python test tasks",
        "Enforce deterministic generated-output regeneration",
        "Bound mutation testing with timeouts and cancellation",
        "Add tiny permissive parser fixtures with provenance metadata",
        "Implement MBS XML parser prototype to ScheduleItemRecord",
        "Implement CMS CLFS parser prototype to ScheduleItemRecord",
        "Implement NHS genomic directory parser prototype",
        "Implement PBS API CSV parser prototype to ScheduleItemRecord",
        "Implement CMS ASP parser prototype to ScheduleItemRecord",
        "Define genomics/pathology basket and mapping evidence fields",
        "Build candidate crosswalk review queue format",
        "Validate source scoring rubric against first-wave sources",
        "Read generated graph CSV files in Astro dashboard",
        "Convert backlog YAML to GitHub issues",
        "Add SourceSnapshotRecord and local cache provenance schema",
        "Add derived-only MBS TXT pair bundle workflow with path-redacted snapshots",
        "Add public data policy check to CI for raw cache safeguards",
        "Add source-specific content validators for downloaded public files",
        "Add checksum pinning after first reviewed source downloads",
        "Add seed JSONL CSV synchronisation gate to CI",
        "Add candidate publication manifest for Hugging Face dataset release",
        "Add source-specific record-count and schema validators after first real downloads",
    }:
        acceptance = (
            "- [x] Scope is implemented in repository scripts, generated artefacts, documentation, "
            "or protected CI workflows.\n"
            "- [x] The implementation is fail-closed where evidence, review, or external access is "
            "unavailable; it does not convert a blocker into a pass.\n"
            "- [x] Focused tests or CI contracts exercise the implementation, and generated "
            "outputs are regenerated in the repository-defined order.\n"
            "- [x] Conductor backlog, generated issue draft, and GitHub Project row are marked "
            "implemented."
        )
    elif issue.title == (
        "Reconcile Hugging Face destination metadata with governed publication candidate"
    ):
        acceptance = (
            "- [x] Scope is confirmed: read-only verification identifies the configured dataset "
            "and Space and records current destination metadata.\n"
            "- [x] Licence and data-governance implications are checked: remote mutation remains "
            "blocked until the governed candidate gates pass.\n"
            "- [x] Tests or validation evidence are defined: the Hugging Face candidate workflow "
            "builds and validates both bundles with publication flags disabled.\n"
            "- [x] Documentation or Conductor context is updated with the current destination "
            "drift.\n"
            "- [ ] Dataset card and Space metadata match the governed candidate, including the "
            "Apache-2.0 code and source-specific data-licence boundary.\n"
            "- [ ] Licence, research, evidence and policy-claim gates are approved before a "
            "write-enabled reconciliation run."
        )
    else:
        acceptance = """- [ ] Scope is confirmed.
- [ ] Licence and data-governance implications are checked.
- [ ] Tests or validation evidence are defined.
- [ ] Documentation or Conductor context is updated."""
    status_line = f"Status: `{issue.status}`\n\n" if issue.status else ""
    return f"""# {issue.title}

Epic: `{issue.epic_id}` — {issue.epic_title}

{parent}Labels: {labels}

{status_line}## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

{acceptance}
"""


def deduplicate_issues(issues: list[IssueDraft]) -> list[IssueDraft]:
    """Keep one generated draft when backlog and roadmap rows share a title."""
    unique: list[IssueDraft] = []
    seen_titles: set[str] = set()
    for issue in issues:
        key = issue.title.casefold()
        if key in seen_titles:
            continue
        seen_titles.add(key)
        unique.append(issue)
    return unique


def slug(value: str) -> str:
    """Create a filesystem-safe slug."""
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "issue"


def existing_issue_paths(output: Path = OUTPUT) -> dict[str, list[Path]]:
    """Index existing drafts so adding a new issue does not renumber old ones."""
    paths: dict[str, list[Path]] = {}
    for path in output.glob("*.md"):
        match = re.match(r"^\d+-(.+)\.md$", path.name)
        if match:
            paths.setdefault(match.group(1), []).append(path)
    for path_list in paths.values():
        path_list.sort()
    return paths


def main() -> None:
    """Write issue drafts to `.github/generated-issues`."""
    OUTPUT.mkdir(parents=True, exist_ok=True)
    stable_paths = existing_issue_paths()
    used_numbers = {
        int(match.group(1))
        for path in OUTPUT.glob("*.md")
        if (match := re.match(r"^(\d+)-", path.name))
    }
    next_number = max(used_numbers, default=0) + 1
    for existing in OUTPUT.glob("*.md"):
        existing.unlink()
    backlog_issues = parse_backlog()
    parent_issue_titles = {issue.title for issue in backlog_issues}
    generated_issues = generated_track_issues(parent_issue_titles=parent_issue_titles)
    all_issues = deduplicate_issues([*backlog_issues, *generated_issues])
    for issue in all_issues:
        issue_slug = slug(issue.title)
        existing_paths = stable_paths.get(issue_slug, [])
        path = existing_paths.pop(0) if existing_paths else None
        if path is None:
            while next_number in used_numbers:
                next_number += 1
            path = OUTPUT / f"{next_number:03d}-{issue_slug}.md"
            used_numbers.add(next_number)
            next_number += 1
        path.write_text(render_issue(issue), encoding="utf-8")
    print(f"Wrote {len(all_issues)} issue drafts to {OUTPUT}")


if __name__ == "__main__":
    main()
