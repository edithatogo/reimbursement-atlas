# GitHub Project export

The repo converts Conductor tracks, generated issue drafts and output plans into GitHub Project import rows. This lets the implementation roadmap move into GitHub Projects once repository credentials are available, without losing the Conductor context.

## Command

```bash
PYTHONPATH=src reimbursement-atlas github-project-export
```

Generated artefacts:

```text
data/derived/github_project/github_project_items.jsonl
data/derived/github_project/github_project_items.csv
data/derived/github_project/summary.json
apps/dashboard/public/data/github_project_items.csv
```

Each project item records:

- issue or track type;
- title;
- generated issue draft path;
- epic and track identifiers;
- status;
- priority;
- labels;
- recommended milestone;
- recommended GitHub Project view.

The generated rows are not a substitute for opening GitHub issues. They are a deterministic import/handoff layer for a credentialed environment.
