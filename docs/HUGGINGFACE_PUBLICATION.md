# Hugging Face publication plan

The repo records two Hugging Face targets:

1. **Dataset**: licence-safe derived metadata and analysis outputs listed in `data/derived/publication_manifest.json`.
2. **Space**: static Astro dashboard built from dashboard-safe CSV files under `apps/dashboard/public/data/`.

The workflow is token-gated through `HF_TOKEN`, `HF_DATASET_REPO` and `HF_SPACE_REPO`. It remains dry-run-safe until licence gates and release-readiness gates pass.

The release candidate bundle also includes `infra/huggingface/DATASET_CARD.md`,
`infra/huggingface/README.md` and `infra/huggingface/SPACE_README.md` so the dataset
card and Space metadata stay versioned with the publication manifest.

Live HF targets currently provisioned from this repository:

- Dataset: `edithatogo/reimbursement-atlas`
- Space: `edithatogo/reimbursement-atlas`

The dataset/Space creation flow is still separate from the GitHub Actions dry-run.
The repository secret is now configured and the dry-run has passed; publication remains
blocked until the workflow's licence, research, evidence and policy gates pass.

## Latest destination verification

The latest read-only Hub inspection on 2026-07-17 reconfirmed the same drift without
using a write token. The dataset `edithatogo/reimbursement-atlas` is reachable and
reports `license: other`; its README links an MIT metadata file. The Space with the
same repository name is reachable and reports `sdk: gradio` and does not expose the
governed `license: apache-2.0` and `sdk: static` candidate metadata. This is a
destination-state observation only: no files, cards, metadata, or settings were
changed.

The read-back is consistent with the credential-free workflow evidence below and does
not upgrade any release gate. The dataset's source-specific licence boundary and the
Space's Apache-2.0 code metadata must be reconciled only by the gated publication path
after the required licence, evidence, research, policy and explicit publication
approvals are present.

On 2026-07-16, the public API confirmed that both configured targets exist. The dataset
currently contains only its README, license and Git attributes, and reports `mit` in its
remote card metadata. The Space is running a Gradio scaffold with `app.py` and also reports
MIT metadata. These destinations do not yet match the governed release candidates: the
dataset card preserves source-specific licences, while the Space candidate is a static
Astro dashboard with Apache-2.0 code metadata. This is destination drift, not publication
evidence. Reconciliation must occur through the gated workflow after licence and research
review; no remote mutation was performed during this verification.
The reconciliation is tracked in GitHub issue [#320](https://github.com/edithatogo/reimbursement-atlas/issues/320)
and remains blocked until the governed licence, research, evidence and policy gates pass.

The scheduled/manual `huggingface-destination.yml` workflow performs a credential-free,
read-only check of the configured dataset and Space API metadata. It records only repository
identities, expected card fields and drift reasons in an artifact; it never clones, writes to
Hugging Face, or authenticates against Hugging Face. A drift result is an observation for issue
#320, not publication approval.

The monitor may update GitHub issue #320 with the same redacted report using `issues: write` and
the workflow token. This is issue evidence synchronization only; it is not a Hugging Face
mutation or publication approval.

Each target record also contains a `remediation` list and the report contains a
`remediation_plan` keyed by dataset and Space. These instructions identify the metadata and
candidate-bundle checks that must be completed before any correction, but they never authorize
remote mutation or replace licence, research, evidence, policy or maintainer approval.

The latest read-only recheck on merged `main` (`fd41112`) was workflow run
[29569184790](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29569184790).
The dataset metadata still matches its governed `other` licence boundary. The Space remains
drifted at `license: mit` and `sdk: gradio` versus the candidate `apache-2.0` and `static`.
No remote mutation was attempted; issue [#320](https://github.com/edithatogo/reimbursement-atlas/issues/320)
contains the dated readback and remains blocked on approval gates. The current repository
commit is `db367f4`; no remote metadata mutation has been performed since that monitor run.

The monitor failed closed because the Space still reports `license: mit` and `sdk: gradio`.
The workflow nevertheless uploaded the redacted report and synchronized issue `#320`, including
the target-specific `remediation_plan`. This is the current evidence on merged `main`; it does not
authorize changing the Space or publishing the candidate bundle.

## Latest non-mutating candidate validation

The latest candidate validation on `main` (`7a6b03f`) was workflow run
`29551588959`. The publication manifest, research package and static dashboard built and
validated successfully; `publish-dataset` and `publish-space` were skipped. The separate
destination metadata check [29551517641](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29551517641)
reported the known two-field Space drift and performed no remote mutation.

The latest validation on `main` (`c7a55b3e4483265ffe60637714e930512ec22cdb`) was workflow
run `29517250473`. The governed publication candidate built and validated successfully;
`publish-dataset` and `publish-space` were skipped, so neither remote target was mutated.
The existing destination metadata drift remains a reconciliation task and does not grant
publication approval.

Workflow run `29475142574` on merged main commit `e8b8a2e` repeated the candidate
validation. The publication manifest, research package and static dashboard built and
validated successfully; `publish-dataset` and `publish-space` were skipped. No Hugging
Face remote repository was mutated. Publication remains blocked by the governed licence,
research, evidence and policy gates, and the existing destination metadata drift remains
an explicit reconciliation task.

Hugging Face workflow run `29473382378` on `main` successfully regenerated the publication
manifest and research package, built the dashboard, and validated the candidate bundle. Both
publish jobs were skipped because `publish_dataset=false` and `publish_space=false`. This is
candidate-build evidence only; it does not approve licences or mutate either remote target.

Before either publication job can mutate a remote repository, the workflow runs
`scripts/check_huggingface_bundle.py`. It verifies the Space metadata, dashboard status contract,
publication manifest and forbidden raw/secret/local-path markers. A passing bundle check does not
grant permission to publish or imply evidence readiness. The mutation jobs also run
`scripts/check_huggingface_publication_gates.py`, which fails closed unless release readiness,
protocol status, source contracts, data quality, licence gates and policy/evidence flags all pass.

No raw restricted schedules, CPT descriptors, local ontology dumps or confidential prices should be published to Hugging Face.
