# Final handoff checklist

## Current working snapshot (2026-07-19)

The current continuation branch is `codex/provenance-decision-matrix` at commit
`39e8415`. The authoritative generated release summary reports repository software
release readiness `36/36` and `repository_release_ready=true`; research publication,
OSF registration, evidence release and policy-claim readiness remain fail-closed.
The current handoff table contains 12 tasks: 3 complete, 1 partial and 8 blocked by
human review or external publication decisions. The checksum-bound licence queue has
177 approved decision records, and the mapping calibration fixture remains 4 cases for
smoke testing only. Use the generated files below as the source of truth; older commit
and count references later in this document are retained historical audit notes.

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

## Release snapshot state (2026-07-19)

This handoff describes current merged `main` snapshot
`89127e48ba0035a330aafa950c1bed0476ad0077`.
Regenerate this document after any further merge and before release review.
The historical MBS inventory contains 343 metadata-only targets across 32 archive
pages, and the target-level review packet is available under
`data/derived/historical_sources/historical_mbs_review_queue.{csv,jsonl}`. All
targets remain `pending_human_review`; no historical payload is approved or
tracked.

The current read-only monitor refresh on this snapshot recorded OSF discovery and
plan success (run `29595536363`), Zenodo non-depositing validation success
(`29595536320`), source-health success with review-only targets and zero
operational blockers (`29595536399`), Hugging Face destination drift without
mutation (`29595536385`), and GitHub security readback
`blocked_permissions` because the workflow token cannot read account-level
security-analysis settings (`29595536535`). These runs do not grant licence,
research, evidence, policy or publication approval.

The artifact-level licence-review queue is generated separately at
`data/derived/licence_review/`. It binds every publication candidate to its current
SHA-256 checksum and keeps all 163 rows pending until an accountable reviewer records
decision evidence. The queue is a review-control artefact, not a licence approval, and
cannot mutate a candidate to approved status.

## Latest current-main external refresh

The merged `main` commit `89127e4` was rechecked without publication or destination mutation.
OSF discovery [29596947892](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29596947892)
passed and found the configured private project; Zenodo preflight
[29596947909](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29596947909)
passed in non-depositing mode; source health
[29596947921](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29596947921)
completed successfully with no operational blockers; and the Hugging Face destination monitor
[29596947958](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29596947958)
failed closed on the known Space drift (`mit`/`gradio` versus governed `apache-2.0`/`static`).
The GitHub security-settings monitor
[29596744210](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29596744210)
reported `blocked_permissions` because the default workflow token cannot read the security
analysis object. No external publication, DOI deposit, licence approval or destination mutation
was performed.

## Main remaining environment-dependent tasks

1. Review the 163 checksum-bound publication candidates in the licence-review queue, then
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

Historical monitor snapshots below are retained for auditability. They are not the current
release state; use the current merged-main block above and the generated readiness outputs as
the source of truth.

The current merged release is `e639490` (resolve the current value with `git rev-parse main`). The repository-controlled
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

The current Hugging Face destination readback [29584493383](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29584493383)
passes for the dataset (`license=other`) but fails closed for the Space because it reports
`license=mit` and `sdk=gradio` rather than governed `apache-2.0` and `static`. The monitor made
no remote mutation and synchronized issue [#320](https://github.com/edithatogo/reimbursement-atlas/issues/320).

The current merged `main` commit `48d61d2` passed the protected workflow and GitHub Pages
build, deploy and live smoke. Source-health acceptance run
[29587300544](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29587300544)
completed with `acquisition_outcome=success`, downstream validation/contract/drift/readiness
return codes of zero, zero operational blockers and six licence-review targets. The workflow
uploaded redacted evidence and performed no publication, licence approval, destination mutation
or raw-payload commit.

The current handoff is maintained on merged `main`; resolve the exact current commit with
`git rev-parse main`. The source-health outage escalation
[#439](https://github.com/edithatogo/reimbursement-atlas/issues/439) was superseded by the
successful acceptance evidence above and is closed as resolved operationally. The six
licence-review targets, human mapping/research review, OSF/Hugging Face/Zenodo publication
approval, and account-level GitHub security settings remain open and fail-closed.
