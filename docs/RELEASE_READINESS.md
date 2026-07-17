# Release readiness

The release-readiness matrix consolidates local quality evidence, security gates, source-data governance, workflow policy, SBOMs, dashboard build status and architecture boundaries.

It is intentionally stricter than a normal CI job: it distinguishes *failed*, *blocked by network*, *missing tool* and *warning* states so a sandbox or local workstation does not falsely claim public-release readiness.

## Command

```bash
PYTHONPATH=src reimbursement-atlas release-readiness --allow-blockers
```

Outputs:

- `data/derived/release_readiness/release_gates.{jsonl,csv}`
- `data/derived/release_readiness/summary.json`

The summary contains `required_blocker_count` and `public_release_ready`. Public release should only proceed when `required_blocker_count == 0`.

The release matrix also verifies that `data/derived/licence_review/summary.json` exists,
contains checksum-bound candidate rows, and explicitly has
`approval_mutation_allowed: false`. This verifies the review-control mechanism only; the
161 artifact candidates remain pending. This includes project metadata, governance outputs,
and source-derived candidates; the source-derived subset still requires human Commonwealth,
provider-licence and domain review before external publication.

## Current merged state

As of 2026-07-17, `main` is at `fd41112` (the squash merge of the gated Hugging Face remediation plan).
The repository release gates are green, the current PBS v3 schedule acquisition is
recorded as `acquired_unreviewed`, and source-health is intentionally `partial`: MBS
and PBS evidence exists in ignored local raw storage, while CMS and historical targets
remain skipped behind licence/review gates. This is not a missing PBS credential state.

## Current blocker pattern

As of 2026-07-17, the managed Python 3.14, official Pixi, Node/dashboard,
SBOM, architecture, public-data, action-pinning, CodeQL, dependency-review,
zizmor and branch-protection gates pass. The public GitHub Pages dashboard is
deployed and its machine-readable status contract remains explicitly gated for
research evidence and policy claims.

Remaining blockers are external or require accountable human judgement:

- MBS and historical-source reuse terms require licence review before public
  derived-data publication.
- CMS CLFS/PFS/ASP fields require source-specific licence decisions.
- OSF registration requires an approved protocol freeze and write-authorized
  credentials; repository configuration alone does not authorize publication.
- Hugging Face publication requires the configured `HF_TOKEN` and target repository variables,
  but publication remains disabled until review gates pass.

The latest recorded preflights completed successfully without mutating external services.
The governed source-health run [29551222886](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29551222886)
also acquired and schema-validated 14,840 PBS item records and 17 PBS fee records while keeping
the evidence `acquired_unreviewed`.
The PBS acquisition refresh is now merged to `main`; the older preflight identifiers below
remain historical evidence only:
OSF discovery/plan run `29492178596`, Hugging Face candidate validation run
`29492180053`, and Zenodo non-depositing preflight run `29492181534`. The PBS public
API runtime probe returned HTTP 200 without recording the subscription key. The
latest merged-main preflight IDs above remain historical evidence only.
These runs validate automation and preserve fail-closed publication boundaries; they do not
constitute human licence, research, evidence, policy or publication approval. The required
`zizmor` branch-protection check is now bound to GitHub Actions app `15368`; the prior queued
Advanced Security binding was resolved through repository-admin GraphQL settings.
- Mapping calibration, cross-platform dashboard visual review and policy claims
  require human adjudication.

The newest read-only preflight set on `main` (`c7a55b3e4483265ffe60637714e930512ec22cdb`)
also passed: OSF run `29517248071`, Hugging Face run `29517250473`, and Zenodo run
`29517252716`. All publication/provisioning mutation jobs were skipped. These runs confirm
automation and candidate validity only; they do not change the false research, evidence,
policy-claim or publication-readiness flags.

These states are tracked as evidence rather than hidden in prose.

The latest read-only external refresh on this commit passed OSF discovery and the OSF component
plan in workflow run
[29565049272](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29565049272).
It found the existing private `Reimbursement Atlas` OSF project `q8cnx`; provisioning,
registration, upload and publication were skipped. The Hugging Face destination check
[29565126096](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29565126096)
reconfirmed the known Space metadata drift (`mit`/`gradio` versus governed
`apache-2.0`/`static`) without mutation.

The current merged-main refresh is workflow run
[29567562072](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29567562072) on
`fa5b042`. OSF discovery and the component plan passed, confirming 28 accessible projects and
the private `Reimbursement Atlas` project `q8cnx`; all OSF mutation jobs were skipped. This
refresh updates operational evidence only and does not change the false research-publication,
OSF-registration, evidence-release or policy-claim readiness flags.

The latest non-depositing Zenodo preflight on merged `main` (`efd835e`) was run
`29552003859`; metadata and repository-readiness validation passed and no DOI deposit or
external mutation was performed.

The current merged commit `fd41112` also passed all repository-protected checks. Its manual
Hugging Face destination monitor run `29569184790` intentionally failed closed on the known
Space metadata drift, uploaded redacted evidence and synchronized issue `#320`; it performed no
Hugging Face mutation. No newer OSF or Zenodo mutation-capable run has been performed on
`fd41112`, so the latest OSF and Zenodo records above remain operational evidence from earlier
merged commits, not publication approval.

After the documentation merge to `fc47649`, the current non-mutating preflights were rerun:
OSF run [29569972259](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29569972259)
passed discovery and the fail-closed component plan, finding 28 accessible projects and the
private `Reimbursement Atlas` project `q8cnx`; Zenodo run
[29569972301](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29569972301)
passed metadata and repository-readiness validation. OSF provisioning, registration, upload,
publication and Zenodo deposit were not performed.

## Source contract posture

`source_contract_validation_summary` is now expected to pass when the reviewed MBS bundle
is present and landing-page/manual-extract records are intentionally skipped. A warning
there now means a real contract regression, not a placeholder for missing live evidence.
