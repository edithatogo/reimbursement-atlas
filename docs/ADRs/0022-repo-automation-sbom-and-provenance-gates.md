# ADR 0022: Repository automation, SBOM and provenance gates

## Status

Accepted.

## Context

The project is moving from design scaffolding toward reviewed live-source ingestion. The codebase already has strict Python checks and dashboard builds, but the GitHub automation surface itself is now part of the threat model. A compromised action, excessive permission grant or accidental raw-data publication could undermine trust in derived reimbursement outputs.

## Decision

Add repo-native automation metadata and supply-chain gates:

- scan GitHub Actions `uses:` references and workflow permission posture;
- emit workflow policy and action SHA-pinning queues as derived artefacts;
- add OpenSSF Scorecard and zizmor workflow-security jobs;
- add generated CycloneDX-style SBOMs for Python and dashboard dependencies;
- attest release artefacts and SBOMs through GitHub artifact attestations;
- add Dependabot cooldown and dependency grouping;
- include automation/SBOM outputs in the dashboard, seed lake and publication manifest.

## Consequences

The repository now treats CI/CD posture as a first-class dataset. Maintainers can review warnings before making gates blocking. The main remaining warning is action tag pinning. This is deliberate: the current environment cannot safely resolve all action tags to SHAs, so v11 emits an action SHA pin plan rather than fabricating commit hashes.
