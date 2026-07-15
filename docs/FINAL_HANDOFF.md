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

## Main remaining environment-dependent tasks

1. Complete MBS, historical-source and CMS licence review before derived-data publication
   (`#23`, `#24`, `#26`, `#27`).
2. Acquire and review a PBS monthly extract, then approve historical MBS/PBS scope (`#25`).
3. Approve mapping calibration gold standards and negative controls (`#10`, `#11`).
4. Freeze and approve the OSF protocol, then complete the token-gated registration workflow;
   `OSF_PROJECT_ID` is configured for the private project (`#109`–`#113`, `#134`, `#135`).
5. Run the gated Hugging Face dataset/Space publication workflow after the remaining licence,
   evidence and policy gates pass; `HF_TOKEN` is now configured in GitHub.
6. Complete cross-platform dashboard visual and accessibility review.
7. Regenerate release-readiness after the research, licence and publication gates complete,
   then create the signed release and Zenodo DOI (`#121`).

Source acquisition, the derived MBS bundle, strict software/security gates, GitHub
Pages deployment, OSF CLI v1 verification and the downloadable archive are complete.
Public evidence-release readiness still requires the remaining credential and human
review gates.

Current release posture: the repository is ready for local software release and the
public dashboard is live, while `research_publication_ready`, `evidence_release_ready`
and `policy_claims_ready` remain fail-closed.

The merged release is `38a399073ef4bc5ae6106c05a3b719d32790b361`. The repository-controlled
quality, security, source-contract, package, dashboard, citation and reproducibility gates
are green; the remaining rows above require accountable external or human decisions rather
than additional local implementation.
