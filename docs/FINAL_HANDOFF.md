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

1. Run hardened source downloads with `curl`/`wget` in a network-enabled checkout.
2. Create the reviewed MBS TXT-pair bundle from ignored local raw files.
3. Complete CMS CLFS licence review before parsing or publishing derived fields.
4. Run `pip-audit --strict` with network access to advisory APIs.
5. Resolve GitHub Action references to immutable SHAs.
6. Run token-gated Hugging Face dataset/Space dry runs.
7. Run token-gated OSF protocol/report publication workflow.
8. Regenerate release-readiness after the above gates complete.

The downloadable archive is ready for local continuation. Public-release readiness still requires the network, credential and review gates to be completed.
