# Session v44: publication dry validation

## OSF

Workflow run `29444356493` passed the safe path on `main`:

- authenticated project discovery succeeded with only a sanitized artifact;
- the OSF component plan passed with the pinned `osf-cli-go` `v1.0.0` contract;
- fail-closed synchronization validation passed;
- provisioning and publication were skipped.

## Hugging Face

Workflow run `29444461756` passed the non-publishing validation path:

- Python dependencies installed;
- publication manifests regenerated;
- dashboard build passed;
- publication bundle validation passed;
- candidate artifacts uploaded;
- dataset and Space publication jobs were skipped because both flags were `false`.

## Boundary

No external publication, registration, licence approval or human methods review was bypassed.
The remaining publication blockers are unchanged and remain represented in release-readiness,
evidence-readiness and Conductor outputs.
