# Protocol status gate

The OSF/research workflow is now backed by a generated protocol-completeness table rather than only free-text planning.

```bash
PYTHONPATH=src reimbursement-atlas protocol-status
```

The gate reads `data/seed/research_questions.jsonl`, checks the corresponding files in `protocols/` and `reports/`, and writes:

```text
data/derived/protocols/protocol_status.jsonl
data/derived/protocols/protocol_status.csv
data/derived/protocols/summary.json
```

Each row records:

- whether the protocol and report files exist;
- required protocol sections present/missing;
- protocol/report word counts;
- completeness score;
- OSF readiness flag;
- recommended next step.

The required sections are intentionally generic at this stage: background, research question, datasets, inclusion/exclusion, analysis plan, bias/limitations, outputs and OSF. Research-question-specific checklists can be added once the first real-source ingestion is complete.

## Why this matters

This prevents the project from drifting into dashboard-only exploration. Each policy analysis should have an explicit protocol before policy claims are treated as research outputs, and OSF uploads should reflect that state.
