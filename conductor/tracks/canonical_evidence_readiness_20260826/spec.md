# Canonical Evidence-Release Readiness Semantics

## Overview

Remove the medallion projection's partial evidence-readiness inference and derive
global evidence-release readiness from the complete release gate matrix.

## Requirements

- Use one canonical readiness result for medallion and release summaries.
- Evaluate current-run medallion evidence rather than a stale summary.
- Keep all Platinum candidates fail closed while any canonical evidence gate is incomplete.
- Preserve deterministic generated outputs and architecture boundaries.

## Acceptance Criteria

- Both generated summaries report the same `evidence_release_ready` value.
- A narrowly ready research-question summary cannot bypass other evidence gates.
- Repeated medallion and release generation produces no further diff.
- Local and hosted quality, security, browser, readiness, and generation checks pass.

## External Gates

No external mutation or new accountable approval is required.

## Out of Scope

- Changing the underlying mapping, dashboard, licence, or research gate decisions.
- Publishing datasets, archives, papers, or preprints.
