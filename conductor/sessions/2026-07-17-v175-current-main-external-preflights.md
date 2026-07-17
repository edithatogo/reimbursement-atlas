# Conductor session: v175 current-main external preflights

Date: 2026-07-17
Merged commit: `c52e2b4`

## Scope

Refresh the external monitors after the PBS cadence and rolling-retention correction. All
requested workflows were run in read-only or non-depositing mode. No source payloads, secrets,
publication records, repository settings or destination metadata were mutated.

## Results

| Monitor | Run | Result | Boundary |
| --- | --- | --- | --- |
| OSF protocol/report plan | [29576544998](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29576544998) | pass | `osf-cli-go v1.0.0` verified; discovery, provisioning and publication not requested |
| Zenodo preflight | [29576546386](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29576546386) | pass | metadata/readiness validated; no DOI or deposit |
| Source health | [29576550575](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29576550575) | pass | zero operational blockers; six licence-review targets; raw payloads not tracked |
| Hugging Face destination | [29576542896](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29576542896) | fail closed | Space drift: observed `mit`/`gradio`, governed `apache-2.0`/`static`; no mutation |
| GitHub security settings | [29576548821](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29576548821) | blocked permissions | workflow token cannot read security-analysis settings; no mutation |

## Decisions

- Keep HF destination reconciliation disabled until licence, evidence and publication gates pass.
- Keep OSF registration/upload/publication and Zenodo deposit disabled until accountable review and
  approved release artefacts exist.
- Treat the GitHub security monitor's `blocked_permissions` result as an external account/token
  scope blocker, not as evidence that the settings are enabled or disabled.

## Remaining handoff

The repository is software-release ready, but research publication, evidence release, policy claims,
OSF registration, DOI deposit, HF Space reconciliation, source licensing and human mapping/research
review remain blocked. See `docs/FINAL_HANDOFF.md` and the generated release-readiness outputs.
