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
SHA-256 checksum and keeps all 159 rows pending until an accountable reviewer records
decision evidence. The queue is a review-control artefact, not a licence approval, and
cannot mutate a candidate to approved status.

## Main remaining environment-dependent tasks

1. Review the 159 checksum-bound publication candidates in the licence-review queue, then
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

The current source acquisition run is explicitly classified as partial: the July 2026 MBS
pair and PBS documentation were downloaded, while the remaining executable or credential-gated
targets are not complete. The derived MBS bundle, strict software/security gates, GitHub Pages
deployment, OSF CLI v1 verification and the downloadable archive are complete.
Public evidence-release readiness still requires the remaining credential and human
review gates.

Current release posture: the repository is ready for local software release and the
public dashboard is live, while `research_publication_ready`, `evidence_release_ready`
and `policy_claims_ready` remain fail-closed.

The current merged release is the tip of `main` (resolve it with `git rev-parse main`). The repository-controlled
quality, security, source-contract, package, dashboard, citation and reproducibility gates
are green; the remaining rows above require accountable external or human decisions rather
than additional local implementation.
