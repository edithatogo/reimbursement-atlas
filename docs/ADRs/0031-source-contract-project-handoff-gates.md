# ADR 0031: Source contracts, GitHub Project export and final handoff gates

## Status

Accepted.

## Context

The repository had strong source, protocol, evidence-readiness and publication scaffolding, but the remaining implementation work needed to be made more explicit for a network-enabled local or GitHub environment. Generic source validation was not sufficient before parser execution, and GitHub issue drafts needed a project-level import layer.

## Decision

Add three generated gates:

1. `source-contracts` for source-specific markers and expected parser columns.
2. `github-project-export` for Conductor/GitHub Project import rows.
3. `final-handoff` for commands and unblock conditions that remain environment-dependent.

These gates are included in local-quality, release-readiness, dashboard seed synchronisation, seed lake and publication manifests.

## Consequences

The repo is now easier to continue locally: a maintainer can download the archive, run the final handoff commands, and know which artefacts should change. The contract layer should reduce accidental parsing of landing pages, HTML errors, wrong files or unexpectedly changed schedule layouts.
