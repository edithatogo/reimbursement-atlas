# Approval policy

## Owner delegation effective 2026-08-30 (supersedes stricter wording below)

`data/licence_review/standing_scope.json` records the owner's explicit delegation:
the 19 approved metadata paths renew automatically within their enumerated fields,
source families, risk-bearing values and rights-evidence contract. Checksum churn
is provenance, not a reason to ask again. New paths, fields, sources or changed
rights evidence require one grouped material-scope decision. No raw rights are granted.

Passing dashboard reruns within the approved route/browser scope renew automatically,
including routine UI and dependency changes. The historical owner receipt remains
immutable; renewal is automation, not another human review. Failed checks require
remediation; missing or stale packets require fresh hosted evidence, not owner sign-off.
Expanded claims, routes/browser scope, restricted content and unauthorized external
mutations remain gated. Universal accessibility and manual VoiceOver are not claimed.

This repository minimises approval prompts without treating automation as external authorization.
Every gate uses the lowest-friction tier that still fails closed for its risk.

## Tiers

| Tier | Requirement | Examples |
| --- | --- | --- |
| Automatic policy | No accountable prompt. Deterministic checks and repository policy decide. | Apache-2.0 project code, architecture reports, SBOMs, quality reports and release-control metadata. |
| Standing scoped approval | Reuse an owner-delegated contract while scope and machine evidence remain valid. | Enumerated metadata renewal and passing dashboard reruns within the approved route/browser scope. |
| Accountable review | One grouped decision for a material risk boundary. | A new source-rights or derived-field scope, a research or policy claim, an expanded dashboard scope, or a protocol interpretation. |
| Explicit external mutation | A separately authorized high-impact action. | Publishing or changing a Hugging Face, Zenodo, DOI, release or registration record. OSF is retained as historical evidence only. |

## Reapproval triggers

Accountable reapproval is required only when at least one of these events occurs:

- a source licence, rights scope, permitted field set or restricted-content rule changes;
- a checksum-bound source-derived artefact changes and no standing source-scope contract covers it;
- declared routes, browser-project scope or claim scope expands;
- a new or materially changed causal, coverage, price-equivalence, reimbursement or accessibility claim is proposed;
- an external publication target, payload scope or mutation changes.

Commit churn, deterministic regeneration, generated ordering, workflow line-number movement,
project-owned SBOM/architecture updates and readiness receipts do not independently require
accountable approval.

## Dashboard standing approval

The current dashboard validator may carry a prior `approved_within_scope` record forward only when:

1. Git history contains the exact reviewed automated and owner packets.
2. Both historical packet SHA-256 values match the accountable record.
3. Historical and current dashboard source fingerprints match, or the owner delegates
   renewal to passing automation through the integrity-bound standing scope contract.
4. Historical and current route and browser-project matrices match the declared contract.
5. The current 64-test browser matrix, displayed-data parity, provenance assertions and
   prohibited-content checks pass.

Failed automation requires remediation, not approval. Stale packets require automatic refresh.
Only a material scope change produces a grouped accountable request.
A standing approval never establishes universal WCAG conformance or independent
manual assistive-technology review.

## Source-rights boundary

Project-owned operational evidence is Apache-2.0 output and never enters the provider-rights
queue. Other source-derived candidates remain checksum-bound; enumerated standing metadata
renews under the field/source/rights contract above. Raw payloads, restricted descriptors, secrets and local paths
remain excluded regardless of approval tier.

Content-bearing strings are constrained by field-specific hashes from the approved
artifacts; typed counters, timestamps and SHA-256 values may refresh automatically.
Duplicate CSV headers and JSON keys are rejected before parsing can hide values.
Unexpected text is a content-validation failure to investigate, not an instruction
to request another routine owner approval or to broaden the contract automatically.

## Prompting contract

Routine implementation, regeneration, CI, issue synchronization and read-only verification proceed
without approval prompts. When accountable input is genuinely required, the system presents one
grouped packet containing all current high-risk decisions, exact hashes, recommendation, rationale
and exclusions. Superseded or already satisfied packet requests must not be repeated.

The dashboard browser workflow emits both checksum-bound review packets with its screenshots.
Agents must ingest those hosted packets and apply standing scoped approval before requesting a new
owner decision. A new prompt is warranted only when the reapproval triggers above remain after that
automated reconciliation.
