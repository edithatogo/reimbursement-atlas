# Release readiness

Release snapshot reference: `d58af03116c792f092146d15e849af048709cdbb` (2026-07-20).
Regenerate this document after any further merge and before release review.
The last merged-main repository release gate summary was 36/36 passing; the current
branch must rerun the complete matrix before this state can be considered current.
research publication, OSF registration, evidence release and policy claims remain
fail-closed. The latest non-mutating monitor evidence was collected on this
snapshot: OSF `29595536363`, Zenodo `29595536320`, source health
`29595536399`, Hugging Face destination `29595536385`, and GitHub security
settings `29595536535`.

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
11 currently blocked artifact candidates remain pending. This includes project metadata, governance outputs,
and source-derived candidates; the source-derived subset still requires human Commonwealth,
provider-licence and domain review before external publication.

## Current merged state

Historical monitor snapshots below are retained for auditability. They are not the current
release state; use the current merged-main reference above and the generated readiness outputs
as the source of truth.

As of 2026-07-17, the historical `main` snapshot was `41d8a94` (the squash merge of the final external-monitor evidence
record in PR #429). The repository release gates are green. The current PBS v3 schedule,
items and fees acquisition is `acquired_unreviewed` from an ephemeral official catalogue key.
Source-health is `review_required` with zero operational blockers: the MBS and PBS responses
exist in ignored local raw storage, while six historical/CMS targets remain gated by
licence/review controls.

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
The latest local acquisition retry is a separate evidence record: it revalidated the MBS
pair and PBS v3 responses, skipped six licence-gated targets and classified source-health as
`review_required` with zero operational blockers. The generated source-health report is the
authoritative status for that local environment.
The governed source-health run [29574452434](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29574452434)
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

The merged commit `fd41112` also passed all repository-protected checks. Its manual
Hugging Face destination monitor run `29569184790` intentionally failed closed on the known
Space metadata drift, uploaded redacted evidence and synchronized issue `#320`; it performed no
Hugging Face mutation. No newer OSF or Zenodo mutation-capable run has been performed on
that commit, so the latest OSF and Zenodo records above remain operational evidence from earlier
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

## Latest Current-Main Preflights

The latest non-mutating refresh on current merged `main` (`3754028`) completed as follows:
OSF run [29571893420](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29571893420)
passed the pinned OSF CLI plan and discovered 28 accessible projects, including the private
`Reimbursement Atlas` project `q8cnx`; provisioning and publication were skipped. Zenodo run
[29571894944](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29571894944)
passed non-depositing validation. Source-health run
[29571899135](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29571899135)
completed with six licence-review targets and credentialed PBS acquisition evidence. The
Hugging Face destination monitor
[29571896396](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29571896396)
failed closed on the known Space metadata drift without mutation. GitHub security settings
run [29571897692](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29571897692)
confirmed the monitor's token-scope limitation; repository API readback remains authoritative
for the core controls and the two account/plan-gated controls.

## Latest Current-Main External Preflight Refresh

The latest read-only refresh ran before the current merge at `c52e2b4`. OSF run
[29576544998](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29576544998)
passed the pinned `osf-cli-go v1.0.0` plan and fail-closed synchronization checks; discovery,
provisioning, registration, upload and publication were not requested. Zenodo run
[29576546386](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29576546386)
passed non-depositing validation and created no DOI. Source-health run
[29576550575](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29576550575)
passed with zero operational blockers and six licence-review targets; no raw payloads were
tracked. The Hugging Face destination monitor
[29576542896](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29576542896)
failed closed on the known Space metadata drift (`mit`/`gradio` versus governed
`apache-2.0`/`static`) without mutation. GitHub security readback
[29576548821](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29576548821)
passed as a monitor but reported `blocked_permissions` because its workflow token could not read
security-analysis settings. These runs refresh operational evidence only and do not change the
currently false research-publication, OSF-registration, evidence-release or policy-claim readiness
flags.

The v177 refresh on validated commit `5833b35` reconfirmed the same external boundaries:
OSF [29577726446](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29577726446),
Zenodo [29577728066](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29577728066)
and source-health [29577731251](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29577731251)
passed without publication or raw-payload mutation. Hugging Face
[29577724648](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29577724648)
failed closed on the unchanged Space drift, and GitHub security
[29577729670](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29577729670)
reported `blocked_permissions`; neither monitor mutated its target.

## Final merged-main monitor refresh

The final merged commit `3d48d4e` was rechecked without publication or destination mutation.
The [OSF plan](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29580009614) and
[Zenodo preflight](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29580011165)
passed in non-mutating modes. [Source health](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29580013970)
downloaded only to ignored local storage, validated the reviewed MBS pair and PBS response
schemas, and retained six licence-review targets. The [Hugging Face monitor](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29580012461)
failed closed on Space metadata drift (`mit`/`gradio` versus governed `apache-2.0`/`static`),
without mutation. The [GitHub security readback](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29580015474)
reported `blocked_permissions` because the workflow token cannot read security-analysis settings.
These results refresh evidence only; research, evidence, policy, licence and publication gates
remain unchanged.

The current merged commit `41d8a94` also passed CI, security, release readiness, browser validation,
and GitHub Pages build, deploy and live smoke in run
[29580400871](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29580400871).

## Latest current-main external refresh

Read-only monitors on current `main` `6d27f63` produced the same fail-closed boundary. OSF
[29581492342](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29581492342),
Zenodo [29581493945](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29581493945),
source health [29581497364](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29581497364)
and GitHub security [29581498956](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29581498956)
completed successfully without external mutation. Hugging Face
[29581495755](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29581495755)
failed closed on the unchanged Space metadata drift. These checks do not grant licence,
research, evidence, policy or publication approval.

The current merged `main` `431cff9` was rechecked with non-mutating monitors: OSF plan
[29583980320](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29583980320),
Hugging Face candidate validation
[29583983277](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29583983277),
Zenodo preflight
[29583985161](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29583985161),
GitHub security readback
[29583987148](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29583987148),
and source health
[29583989402](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29583989402)
all passed. Publication, deposit, provisioning and destination mutation jobs were skipped by
explicit false inputs. These operational passes do not change the false licence, evidence,
research, policy or publication readiness flags.

The destination monitor on current `main` `dfd9e18` [29584493383](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29584493383)
confirmed the Hugging Face dataset metadata passes (`license=other`) while the reachable Space
has governed metadata drift (`license=mit`, `sdk=gradio`; expected `apache-2.0` and `static`).
It failed closed with `mutation_performed=false`; no destination change was attempted.

## v189 Current Source-Health Acceptance Run

The merged `main` commit `48d61d2` was validated by source-health run
[29587300544](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29587300544).
The hardened workflow recorded `monitor_run_status.json`, generated source validation,
source contracts, source drift, release-readiness and final-handoff evidence, and uploaded
the redacted artifact. It reported `acquisition_outcome=success`, zero return codes for all
four downstream gates, zero operational blockers and six licence-review targets. It performed
no publication, licence approval, destination mutation or raw-payload commit.

## v190 Current Main Handoff Refresh

The current handoff is maintained on merged `main`; resolve the exact current commit with
`git rev-parse main`. Protected CI and the GitHub Pages build, deploy and live smoke gates passed for the merged
documentation refresh. Source-health acceptance run
[29587300544](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29587300544)
remains the latest live acquisition evidence: `acquisition_outcome=success`, all four
downstream gate return codes are zero, zero operational blockers and six licence-review
targets. Issue [#439](https://github.com/edithatogo/reimbursement-atlas/issues/439) is
resolved as an obsolete acquisition-outage escalation; the six review-only targets remain
publication-blocking and are not treated as approvals.
