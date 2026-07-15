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

1. Complete MBS, historical-source and CMS licence review before derived-data publication.
2. Approve mapping calibration gold standards and negative controls.
3. Freeze and approve the OSF protocol, configure `OSF_PROJECT_ID`, then run the token-gated workflow.
4. Run the gated Hugging Face dataset/Space publication workflow after the remaining licence,
   evidence and policy gates pass; `HF_TOKEN` is now configured in GitHub.
5. Complete cross-platform dashboard visual and accessibility review.
6. Regenerate release-readiness after the research, licence and publication gates complete.

Source acquisition, the derived MBS bundle, strict software/security gates, GitHub
Pages deployment, OSF CLI v1 verification and the downloadable archive are complete.
Public evidence-release readiness still requires the remaining credential and human
review gates.

Current release posture: the repository is ready for local software release and the
public dashboard is live, while `research_publication_ready`, `evidence_release_ready`
and `policy_claims_ready` remain fail-closed.
