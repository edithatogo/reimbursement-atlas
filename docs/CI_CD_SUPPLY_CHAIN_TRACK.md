# CI/CD supply-chain track boundary

Repository-owned validation currently covers 104 workflow-policy records, 130
workflow references, zero unresolved action-pin migrations, deterministic
CycloneDX SBOMs for Python and dashboard dependencies, release-manifest and
attestation contracts, branch-protection contracts, CodeQL/dependency-review
workflow declarations, secret-history scanning and zizmor policy.

The local security-settings inspector is intentionally fail closed when it
cannot identify a GitHub `owner/name` repository. Account-level Advanced
Security settings, hosted required-check completion and branch-protection
mutation are external GitHub state; local generation never reports those as
passing. The hosted workflows remain the authoritative enforcement layer.
