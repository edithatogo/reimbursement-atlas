# Final handoff checklist

The repo now generates a concrete handoff table for the remaining tasks that cannot be completed inside the sandbox. These are not vague TODOs: each row includes the required environment, command, evidence path, unblock condition and recommended action.

## Command

```bash
PYTHONPATH=src reimbursement-atlas final-handoff
```

Generated artefacts:

```text
data/derived/final_handoff/final_handoff_tasks.jsonl
data/derived/final_handoff/final_handoff_tasks.csv
data/derived/final_handoff/summary.json
apps/dashboard/public/data/final_handoff_tasks.csv
```

The artifact-level licence-review queue is generated separately at
`data/derived/licence_review/`. It binds every publication candidate to its current
SHA-256 checksum and keeps all 161 rows pending until an accountable reviewer records
decision evidence. The queue is a review-control artefact, not a licence approval, and
cannot mutate a candidate to approved status.

## Main remaining environment-dependent tasks

1. Review the 161 checksum-bound publication candidates in the licence-review queue, then
   complete MBS, historical-source and CMS licence review before derived-data publication
   (`#23`, `#24`, `#26`, `#27`). The official MBS copyright notice is recorded in
   [`docs/SOURCE_LICENCE_EVIDENCE.md`](SOURCE_LICENCE_EVIDENCE.md); it is not an open
   redistribution licence and requires written approval for redistribution.
2. Acquire and review a PBS monthly extract, then approve historical MBS/PBS scope (`#25`,
   [#255](https://github.com/edithatogo/reimbursement-atlas/issues/255)).
3. Approve mapping calibration gold standards and negative controls (`#10`, `#11`).
4. Freeze and approve the OSF protocol, then complete the token-gated registration workflow;
   `OSF_PROJECT_ID` is configured for the private project (`#109`–`#113`, `#134`, `#135`).
5. Run the gated Hugging Face dataset/Space publication workflow after the remaining licence,
   evidence and policy gates pass; `HF_TOKEN` is now configured in GitHub.
6. Complete cross-platform dashboard visual and accessibility review.
7. Regenerate release-readiness after the research, licence and publication gates complete,
   then create the signed release and Zenodo DOI (`#121`,
   [#256](https://github.com/edithatogo/reimbursement-atlas/issues/256)).
8. Revisit TypeScript 7 after `@astrojs/check` declares peer support; the current canary observes
   TypeScript `7.0.2` but `@astrojs/check 0.9.9` accepts only TypeScript 5 or 6 (`#362`).

The current source acquisition run is explicitly classified as review-required: the July 2026
MBS pair and PBS schedule were revalidated into ignored local raw storage, six targets remain
licence-gated, and the PBS monthly extract remains acquired-unreviewed. The derived MBS bundle,
strict software/security gates, GitHub Pages deployment,
OSF CLI v1 verification and the downloadable archive are complete.
Public evidence-release readiness still requires the remaining credential and human
review gates.

Current release posture: the repository is ready for local software release and the
public dashboard is live, while `research_publication_ready`, `evidence_release_ready`
and `policy_claims_ready` remain fail-closed.

The current merged release is `41d8a94` (resolve the current value with `git rev-parse main`). The repository-controlled
quality, security, source-contract, package, dashboard, citation and reproducibility gates
are green; the remaining rows above require accountable external or human decisions rather
than additional local implementation.

Latest read-only external evidence before `41d8a94`: OSF plan run
[29576544998](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29576544998) passed;
Zenodo non-depositing preflight [29576546386](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29576546386)
passed; source-health [29576550575](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29576550575)
passed with six licence-review targets and zero operational blockers; HF destination verification
[29576542896](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29576542896) failed
closed on the known Space metadata drift without mutation; and GitHub security readback
[29576548821](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29576548821) reported
`blocked_permissions` for security-analysis settings. No external publication, DOI deposit, licence
approval or security-setting mutation was performed.

The final merged-main monitor refresh on `3d48d4e` is recorded in the release-readiness section:
OSF and Zenodo passed non-mutating plans, source health retained six licence-review targets,
Hugging Face failed closed on Space metadata drift, and GitHub security readback remained
blocked by token/API visibility. No external publication, DOI deposit, licence approval or
security-setting mutation was performed.

The current `main` commit `41d8a94` passed the complete protected workflow and GitHub Pages
build, deploy and live smoke in run
[29580400871](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29580400871).

The latest read-only monitor refresh on `main` `6d27f63` is also recorded: OSF, Zenodo, source
health and GitHub security passed without mutation; Hugging Face remained fail-closed on the
known Space metadata drift. Runs: `29581492342`, `29581493945`, `29581497364`, `29581495755`,
`29581498956`.

The latest v177 read-only refresh on commit `5833b35` reconfirmed this boundary. OSF run
[29577726446](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29577726446),
Zenodo run [29577728066](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29577728066)
and source-health run [29577731251](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29577731251)
passed without mutation. HF run
[29577724648](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29577724648)
failed closed on Space metadata drift; GitHub security run
[29577729670](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29577729670)
reported `blocked_permissions`.

The v178 external-quality refresh also passed strict `pip-audit`, dashboard `npm audit`, Pixi
availability/reachability, zizmor, the repository automation matrix and Mojo availability. The
derived evidence is in `data/derived/external_quality_gates.{json,csv}`; these checks do not
constitute licence, research, evidence or publication approval.

The latest current-main external refresh is on `431cff9`: OSF plan
[29583980320](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29583980320),
Hugging Face candidate validation
[29583983277](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29583983277),
Zenodo preflight
[29583985161](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29583985161),
GitHub security readback
[29583987148](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29583987148),
and source health
[29583989402](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29583989402)
passed. All publication and mutation-capable jobs were skipped; no external state was changed.
