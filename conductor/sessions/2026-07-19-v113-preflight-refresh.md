# Conductor session v113: post-merge preflight refresh

## Scope

Refresh the merged v112 handoff after the historical CMS CLFS catalogue landed, and
re-run non-mutating publication, toolchain, security, source-health and mapping
preflights.

## Evidence

- The official `osf-cli-go` `v1.0.0` binary was installed at
  `~/.local/bin/osf`; the explicit OSF CLI contract passed.
- Hugging Face dataset metadata is aligned, but the reachable Space remains drifted:
  observed `license=mit`, `sdk=gradio`; governed values are `apache-2.0` and `static`.
  No remote mutation was attempted because licence, evidence and publication gates
  remain blocking.
- The TypeScript compatibility canary reports current `typescript=6.0.3`, candidate
  `7.0.2`, and `@astrojs/check=0.9.9` peer support `^5.0.0 || ^6.0.0`; TypeScript 7
  adoption remains blocked without a supported checker contract.
- Mapping calibration remains `review_required` with two gold-standard and two
  negative-control cases; automated evidence is not a substitute for adjudication.
- Source health remains `review_required` with zero operational blockers and six
  review-only source decisions.
- Citation, public documentation, dashboard routes, policy demonstrator generation,
  Zenodo metadata validation, Mojo parity, and the Hugging Face candidate bundle
  checks passed locally.

## Decision

Regenerate the OSF registration packet and publication manifest from the merged
historical-source catalogue. Keep Hugging Face reconciliation, OSF mutation,
publication, evidence release, policy claims and licence decisions fail-closed.

## Follow-up

The next human or credentialed actions are licence review, mapping adjudication,
research-methods approval, and publication destination authorization. No raw source
payloads or credentials are added to the repository.
