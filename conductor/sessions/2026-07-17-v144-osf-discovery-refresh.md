# Session v144: OSF read-only discovery refresh

Date: 2026-07-17
Track: `track_research_protocols_osf`
Related issues: #116, #117, #118

## Evidence

- Workflow: https://github.com/edithatogo/reimbursement-atlas/actions/runs/29545432007
- Pinned CLI: `github.com/edithatogo/osf-cli-go/cmd/osf@v1.0.0`
- Discovery result: 28 accessible projects
- Expected project: `q8cnx`, private `Reimbursement Atlas`
- OSF plan and fail-closed sync-manifest checks: passed
- Publication/provisioning/registration/upload: not performed

## Decision

OSF authentication and project configuration are operational. No token, project listing payload or
remote mutation is committed. Keep publication fail-closed until the protocol, licence, methods and
governance review records explicitly approve sync-manifest rows.

## Next action

Complete the human review packet for the protocol/report components, then rerun the OSF plan and
registration drift checks before any token-gated publication workflow.
