# OSF destination deprecation

## Overview

Retire OSF as an active registration and publication destination without deleting the immutable
historical registration evidence already used by the project.

## Requirements

- Remove OSF registration from release, evidence, Hugging Face, Zenodo, dashboard and handoff
  readiness dependencies.
- Replace destination-specific protocol readiness terminology with a destination-neutral contract.
- Retire GitHub Actions workflows that authenticate to, mutate or monitor OSF.
- Preserve registration `gqk4z`, its receipts, decisions and drift disclosure as historical
  provenance only.
- Keep source rights, research evidence, policy claims and external publication independently
  fail closed.
- Regenerate Conductor, GitHub Project, dashboard, release and handoff outputs.

## Acceptance criteria

- [ ] Current release-readiness output has no OSF gate or `osf_registration_ready` field.
- [ ] Archive and Hugging Face publication gates do not depend on OSF.
- [ ] Protocol completeness uses destination-neutral `protocol_ready` fields.
- [ ] No enabled GitHub workflow can authenticate to, mutate or monitor OSF.
- [ ] Historical OSF receipts remain tracked and are explicitly marked deprecated.
- [ ] Targeted, deterministic and protected hosted checks pass.
- [ ] Issue #711 and generated Project state are synchronized.

## External gates

No external publication or OSF mutation is part of this track. Repository workflow merge remains
protected by hosted checks.

## Out of scope

- Deleting or altering the immutable remote OSF registration.
- Removing historical receipts, decisions or provenance.
- Weakening licence, evidence, policy-claim, DOI, paper or preprint controls.

## Authoritative inputs

- `data/derived/osf/remote_registration_snapshot.json`
- `data/osf_review/post_registration_evolution.json`
- `src/reimburse_atlas/release_readiness.py`
- `src/reimburse_atlas/archive_publication.py`
- GitHub issue #711
