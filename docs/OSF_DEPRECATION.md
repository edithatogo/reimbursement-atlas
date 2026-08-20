# OSF destination deprecation

## Decision

As of 2026-08-20, OSF is not an active registration, protocol-hosting, publication or archive
destination for Reimbursement Atlas. No current release, evidence, Hugging Face, Zenodo,
dashboard or handoff gate depends on OSF state.

## Preserved historical evidence

The repository retains registration `gqk4z`, project `q8cnx`, checksum-bound decisions, redacted
receipts, the canonical remote snapshot and the post-registration evolution disclosure. These
records document what was submitted and how later work diverged from that immutable scope. They
must not be deleted, regenerated as current approval, or represented as covering later analyses.

Authoritative historical paths:

- `data/derived/osf/remote_registration_receipt.json`
- `data/derived/osf/remote_registration_snapshot.json`
- `data/derived/osf/registration_freeze.json`
- `data/osf_review/registration_decision.json`
- `data/osf_review/post_registration_evolution.json`
- `docs/OSF_WORKFLOW.md`

## Automation boundary

The credentialed OSF publication workflow and scheduled registration monitor are retired. OSF
planning and CLI-contract tasks are not part of default QA. Local parsing and reconciliation code
remains available only to validate the preserved historical evidence.

## Remaining independent gates

Source rights, protocol completeness, research evidence, policy claims, Hugging Face mutation,
Zenodo/DOI mutation, software release, papers and preprints retain their own controls. Deprecating
OSF does not grant publication permission or weaken any of those gates.
