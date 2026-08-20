# Approval policy

This repository minimises approval prompts without treating automation as external authorization.
Every gate uses the lowest-friction tier that still fails closed for its risk.

## Tiers

| Tier | Requirement | Examples |
| --- | --- | --- |
| Automatic policy | No accountable prompt. Deterministic checks and repository policy decide. | Apache-2.0 project code, architecture reports, SBOMs, quality reports and release-control metadata. |
| Standing scoped approval | Reuse a prior bounded approval while its immutable scope and machine evidence remain valid. | Dashboard visual/accessibility approval when the reviewed UI fingerprint, routes and browser matrix are unchanged and the current automated, provenance and prohibited-content checks pass. |
| Accountable review | One grouped decision for a material risk boundary. | A new source-rights or derived-field scope, a research or policy claim, a material dashboard UI/scope change, or a protocol interpretation. |
| Explicit external mutation | A separately authorized high-impact action. | Publishing or changing an OSF, Hugging Face, Zenodo, DOI, release or registration record. |

## Reapproval triggers

Accountable reapproval is required only when at least one of these events occurs:

- a source licence, rights scope, permitted field set or restricted-content rule changes;
- a checksum-bound source-derived artefact changes and no standing source-scope contract covers it;
- dashboard implementation bytes, declared routes or browser-project scope change;
- current dashboard automation, provenance parity or prohibited-content checks fail;
- a new or materially changed causal, coverage, price-equivalence, reimbursement or accessibility claim is proposed;
- an external publication target, payload scope or mutation changes.

Commit churn, deterministic regeneration, generated ordering, workflow line-number movement,
project-owned SBOM/architecture updates and readiness receipts do not independently require
accountable approval.

## Dashboard standing approval

The current dashboard validator may carry a prior `approved_within_scope` record forward only when:

1. Git history contains the exact reviewed automated and owner packets.
2. Both historical packet SHA-256 values match the accountable record.
3. Historical and current dashboard source fingerprints match.
4. Historical and current route and browser-project matrices match the declared contract.
5. The current 64-test browser matrix, displayed-data parity, provenance assertions and
   prohibited-content checks pass.

Any failed condition invalidates the standing approval and produces one grouped accountable
review request. A standing approval never establishes universal WCAG conformance or independent
manual assistive-technology review.

## Source-rights boundary

Project-owned operational evidence is Apache-2.0 output and never enters the provider-rights
queue. Source-derived candidates remain checksum-bound and fail closed unless their exact current
checksum has an approved decision. Raw payloads, restricted descriptors, secrets and local paths
remain excluded regardless of approval tier.

## Prompting contract

Routine implementation, regeneration, CI, issue synchronization and read-only verification proceed
without approval prompts. When accountable input is genuinely required, the system presents one
grouped packet containing all current high-risk decisions, exact hashes, recommendation, rationale
and exclusions. Superseded or already satisfied packet requests must not be repeated.
