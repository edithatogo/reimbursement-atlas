# Conductor context index

Conductor is the repository's project memory and agent handoff system.

Future agents should read these files before implementation:

1. `conductor/context/PROJECT_BRIEF.md`
2. `conductor/context/CANONICAL_CONTEXT.md`
3. `conductor/context/STACK.md`
4. `conductor/context/SOURCE_MAP.md`
5. `conductor/context/ANALYSIS_MAP.md`
6. `conductor/context/OPEN_QUESTIONS.md`
7. `conductor/DECISION_LOG.md`
8. `conductor/context/CURRENT_FOCUS.md`
9. `conductor/backlog.yml`
10. `conductor/risk_register.yml`
11. `conductor/quality_gates.yml`
12. `conductor/interfaces.yml`
13. `conductor/roadmap.yml`
14. `conductor/checklists/AGENT_HANDOFF.md`

## Operating rule

Before changing architecture, add or update an ADR. Before adding a source, update the source registry and licence notes. Before adding an analysis, update the analysis catalogue.

## Current executable layer

The context system now has code-backed outputs: `reimbursement-atlas snapshot`, `reimbursement-atlas score-sources` and `reimbursement-atlas export-graph`. Future agents should run `snapshot` before substantial work.
