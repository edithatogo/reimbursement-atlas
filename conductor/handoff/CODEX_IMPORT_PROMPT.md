# Codex handoff prompt: Reimbursement Atlas Conductor

You are Codex working as the lead maintainer, data engineer, research-methods engineer, and repo-automation engineer for the `reimbursement-atlas-conductor` project.

The user has placed the git bundle file in this working folder. Your job is to extract it, organise the repository, inspect the Conductor context-management system, then continue implementing every track that is implementable in this environment. Do not stop after one task; work through the Conductor tracks, generated GitHub issues, final handoff tasks, and release-readiness gates until everything possible is completed. Where a task is blocked by network access, credentials, licence review, ethics/research review, or human judgement, record that explicitly in the repo and continue with the next implementable task.

## 0. Non-negotiable project posture

This project is intended to become a reproducible, evidence-grade reimbursement intelligence platform comparing public reimbursement systems such as US CMS, Australian MBS/PBS/IHACPA, NHS/England, Canada, Taiwan, Japan, Germany, France, New Zealand and further countries/datasets.

Core principles:

1. **Mojo-first performance posture, stable evidence core.** Use Mojo for performance-critical kernels where it is mature enough. Keep Python 3.14-targeted orchestration and Pydantic/Polars/Arrow/DuckDB/LanceDB tooling for reliability, validation and research pipelines.
2. **Raw-source safety.** Never commit raw live source files, licence-gated payloads, confidential material, local absolute paths, secrets or tokens. Raw files belong only in ignored local paths such as `data/raw_live/`.
3. **Derived-only public outputs.** Commit only licence-reviewed derived outputs, provenance, checksums, validation reports, data dictionaries, package manifests, and dashboards.
4. **Everything documented.** Every new function, dataset, analysis, mapping, output, CI/CD improvement, quality gate or publication step must be reflected in Conductor tracks/backlog, generated GitHub issue drafts/project rows, docs, tests and release-readiness/data-quality outputs.
5. **Do not fake green gates.** If a gate is blocked by DNS, credentials, PyPI/GitHub/Hugging Face/OSF access, official Pixi install, Python 3.14 runtime download, or human review, record it as blocked/missing/warn rather than passed.
6. **Research integrity.** OSF protocols and reports must remain draft/not-preregistered until human review approves them. Do not claim evidence-ready status before real reviewed-source bundles exist.
7. **Security posture.** Keep secrets out of logs. Prefer OIDC/trusted publishing, SBOMs, attestations, CodeQL, dependency review, OpenSSF Scorecard, zizmor, SHA-pinned GitHub Actions and least-privilege workflow permissions.

## 1. Extract the repo

If the bundle is in the current folder, restore it with:

```bash
git clone reimbursement-atlas-conductor-v18.git.bundle reimbursement-atlas-conductor
cd reimbursement-atlas-conductor
```

If the bundle has a different name, locate it first:

```bash
ls -lah *.git.bundle *.bundle 2>/dev/null || true
git clone <bundle-file> reimbursement-atlas-conductor
cd reimbursement-atlas-conductor
```

Verify the repo:

```bash
git log --oneline -5
git status --short
```

Create a working branch:

```bash
git switch -c codex/final-tracks-implementation
```

## 2. Read the Conductor context before changing code

Read these files first and use them as the source of truth:

```text
README.md
REQUIREMENTS.md
DESIGN.md
conductor/TRACKS.md
conductor/tracks.yml
conductor/context/CURRENT_FOCUS.md
conductor/DECISION_LOG.md
conductor/backlog.yml
docs/FINAL_HANDOFF.md
docs/SOURCE_CONTRACT_VALIDATION.md
docs/DATA_ACQUISITION_AUTOMATION.md
docs/EVIDENCE_READINESS.md
docs/RELEASE_READINESS.md
docs/OSF_WORKFLOW.md
docs/HUGGINGFACE_PUBLICATION.md
docs/MOJO_AND_PYTHON314_RUNTIME.md
data/derived/final_handoff/summary.json
data/derived/final_handoff/final_handoff_tasks.jsonl
data/derived/release_readiness/summary.json
data/derived/github_project/summary.json
```

Then summarise the current state in your own scratchpad, not as an uncommitted user-facing claim. Identify:

- implementable tasks in the current environment;
- tasks blocked by network/credentials/human review;
- tracks needing code, docs, tests or generated-output updates;
- generated artefacts that must be refreshed after changes.

## 3. Establish the local toolchain

Prefer the project’s intended tooling. Use the latest stable/allowed versions that keep the repo green.

Try:

```bash
python --version
uv --version || curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --all-extras --prerelease=allow
```

Target runtime posture:

```text
Python: 3.14.x target, fallback allowed only if documented by gates
Mojo: latest available compatible mojo/mojo-compiler, currently tracked as 1.0.0b2+
Node: current LTS/current compatible with dashboard lockfile
Astro: latest compatible dashboard stack
Pixi: official Prefix.dev Pixi only; reject unrelated pixi-named executables
```

Run the Mojo smoke gate if possible:

```bash
bash scripts/run_mojo_smoke.sh
```

Do not pretend Python 3.14 or official Pixi passed if they were not actually used.

## 4. Run the baseline gates

Run what the environment supports:

```bash
PYTHONPATH=src uv run --all-extras ruff check .
PYTHONPATH=src uv run --all-extras ruff format --check .
PYTHONPATH=src uv run --all-extras basedpyright
PYTHONPATH=src uv run --all-extras pytest --cov=src/reimburse_atlas --cov-report=term-missing --cov-report=xml --cov-fail-under=90 -q
PYTHONPATH=src uv run --all-extras bandit -q -c pyproject.toml -r src scripts
PYTHONPATH=src uv run --all-extras python -m compileall -q src scripts tests
uv build
```

Dashboard:

```bash
cd apps/dashboard
npm ci
npm audit --omit=dev --audit-level=moderate
npm run build
cd ../..
```

Generated gates:

```bash
PYTHONPATH=src uv run --all-extras python scripts/validate_seed_sync.py
PYTHONPATH=src uv run --all-extras python scripts/check_public_data_policy.py
PYTHONPATH=src uv run --all-extras python -m reimburse_atlas.cli validate
PYTHONPATH=src uv run --all-extras python scripts/run_local_quality_gates.py
PYTHONPATH=src uv run --all-extras python scripts/make_release_readiness.py
PYTHONPATH=src uv run --all-extras python scripts/make_final_handoff.py
```

If a tool is missing and installable, install it. If not installable due to environment constraints, record the blocker in generated quality/handoff artefacts and continue.

## 5. Work through all Conductor tracks

Open `conductor/tracks.yml` and process every track. For each track:

1. Identify existing generated GitHub issues in `.github/generated-issues/` and project rows in `data/derived/github_project/github_project_items.*`.
2. Implement all tasks possible in the current environment.
3. Add or update tests.
4. Update docs.
5. Regenerate seed files, dashboard files, publication manifests, data dictionaries, release-readiness and final-handoff outputs.
6. Commit cohesive changes with clear messages.

Use this regeneration set after track-level changes:

```bash
PYTHONPATH=src uv run --all-extras python scripts/sync_seed_csvs.py
PYTHONPATH=src uv run --all-extras python scripts/create_github_project_items.py
PYTHONPATH=src uv run --all-extras python scripts/make_github_project_export.py
PYTHONPATH=src uv run --all-extras python scripts/make_source_download_plan.py
PYTHONPATH=src uv run --all-extras python scripts/make_source_validation.py
PYTHONPATH=src uv run --all-extras python scripts/make_source_contracts.py
PYTHONPATH=src uv run --all-extras python scripts/make_data_quality_report.py
PYTHONPATH=src uv run --all-extras python scripts/make_roadmap_linkages.py
PYTHONPATH=src uv run --all-extras python scripts/make_evidence_readiness.py
PYTHONPATH=src uv run --all-extras python scripts/make_source_drift_report.py
PYTHONPATH=src uv run --all-extras python scripts/make_data_dictionary.py
PYTHONPATH=src uv run --all-extras python scripts/make_publication_manifest.py
PYTHONPATH=src uv run --all-extras python scripts/make_research_package.py
PYTHONPATH=src uv run --all-extras python scripts/make_osf_plan.py
PYTHONPATH=src uv run --all-extras python scripts/make_graph_seed.py
PYTHONPATH=src uv run --all-extras python scripts/sync_dashboard_seed.py
PYTHONPATH=src uv run --all-extras python -m reimburse_atlas.cli seed-lake data/derived/seed_lake
PYTHONPATH=src uv run --all-extras python scripts/make_release_readiness.py
PYTHONPATH=src uv run --all-extras python scripts/make_final_handoff.py
PYTHONPATH=src uv run --all-extras python scripts/export_json_schema.py
```

## 6. Download public source data where the environment allows

Use the hardened source-download layer. Do not manually paste raw source content into tracked files.

```bash
PYTHONPATH=src reimbursement-atlas source-download-plan --method curl
bash data/derived/source_downloads/download_commands.sh
PYTHONPATH=src reimbursement-atlas source-validation
PYTHONPATH=src reimbursement-atlas source-contracts
```

If downloads succeed, create reviewed-source bundles. For MBS:

```bash
PYTHONPATH=src reimbursement-atlas reviewed-mbs-txt-pair-bundle \
  data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT \
  data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT
```

Then commit only derived, licence-reviewed outputs and regenerated metadata. Before committing, run:

```bash
PYTHONPATH=src python scripts/check_public_data_policy.py
git status --short
```

Reject any commit containing `data/raw_live/`, raw source ZIPs/TXT/CSV payloads that are not explicitly permitted, local absolute source paths, tokens or secrets.

## 7. GitHub Issues and Projects

The repo intentionally generates issue drafts and project import rows without assuming credentials.

Refresh them:

```bash
PYTHONPATH=src python scripts/create_github_project_items.py
PYTHONPATH=src reimbursement-atlas github-project-export
```

Once the repository is pushed to GitHub and `gh` is authenticated, create real GitHub Issues and Projects from the generated drafts/project rows. Keep the source of truth in Conductor tracks/backlog and regenerate the issue/project exports after changes.

Do not delete generated issue drafts unless replacing them with an audited sync process.

## 8. Hugging Face and OSF

Hugging Face dataset and Spaces deployment are recorded and scaffolded. Use token-gated workflows only.

Expected secrets:

```text
HF_TOKEN
HF_DATASET_REPO
HF_SPACE_REPO
OSF_TOKEN or equivalent OSF auth
```

Before any publication:

```bash
PYTHONPATH=src reimbursement-atlas protocol-status
PYTHONPATH=src reimbursement-atlas data-quality
PYTHONPATH=src reimbursement-atlas evidence-readiness
PYTHONPATH=src reimbursement-atlas release-readiness
```

Do not publish to OSF or Hugging Face if protocol status, data-quality, licence gates, source contracts, publication manifest, or human review gates are blocking.

## 9. Further implementation priorities

If the environment supports network and credentials, prioritise:

1. Python 3.14 runtime install and full gate run under 3.14.
2. Mojo 1.0+ smoke/performance kernels beyond the tokenizer fixture.
3. Official Pixi installation and Pixi task parity.
4. `pip-audit --strict` with network access.
5. GitHub Action SHA resolution and action pinning.
6. Make `zizmor` blocking after SHA pinning.
7. Real MBS reviewed-source bundle.
8. Real PBS reviewed extract.
9. CMS CLFS/MCD reviewed-source ingestion respecting AMA/CPT/licence restrictions.
10. Frictionless/RO-Crate/DCAT/Hugging Face/OSF package dry run.
11. First policy demonstrator: genomics/pathology coverage-price-restriction linkage.
12. Human-in-the-loop mapping workbench with adjudication states.
13. Read-only API/MCP interfaces once core data contracts are stable.

If the environment does not support network/credentials, prioritise:

1. More source-specific validators and parser fixtures.
2. Mapping-review schema and dashboard UI.
3. Protocol/report expansion.
4. Additional countries/datasets as seed records.
5. More tests, especially property/fuzz/golden-file tests.
6. More Mojo kernels using safe synthetic fixtures.
7. Stronger data package metadata.
8. Documentation and generated GitHub issue/project traceability.

## 10. Acceptance criteria before telling the user it is ready

The repo can be called locally ready only when:

- all implementable tests/gates pass in the current environment;
- all non-implementable tasks are recorded in final handoff/release-readiness with blocker reasons;
- Conductor tracks/backlog and generated GitHub issues/project rows reflect new work;
- dashboard builds;
- seed sync passes;
- public-data policy passes;
- no raw source data, secrets, local absolute paths or licence-gated payloads are tracked;
- a new git bundle/archive and manifest/checksums are produced for the user.

Finish by giving the user the bundle/archive links, the commit hash, validation summary, and remaining handoff blockers.
