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

## Live board verification

The repository's live board is [Reimbursement Atlas Conductor project #18](https://github.com/users/edithatogo/projects/18).
On 2026-07-16, the authenticated project audit found six repository issues missing from
the board and added them without changing issue content: #131, #140, #237, #255, #256 and
#275. Closed issues #131, #140 and #275 are `Done`; active source/release issues #237, #255
and #256 are `Todo`. The local generated export remains the deterministic source for future
reconciliation, while the live board is the user-facing execution view.
