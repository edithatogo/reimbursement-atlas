# Platinum Product Projection Alignment

## Overview

Classify dashboards, APIs, packages, Hugging Face outputs, releases, and archives
as Platinum products that require Gold inputs and independent release gates.

## Requirements

- Inventory public products without treating destinations as source truth.
- Bind each Platinum candidate to Gold inputs, current checksums, and product gates.
- Keep repository, evidence, publication, and policy readiness distinct.
- Prevent raw, restricted, Bronze-only, or Silver-only inputs from direct publication promotion.

## Acceptance Criteria

- A deterministic Platinum product manifest and promotion summary exist.
- Dashboard, package, and publication readiness consume medallion decisions.
- No product is approved while required lower-layer or release gates are incomplete.
- Public-data, packaging, dashboard, security, and deterministic gates pass.

## Non-functional Constraints

- No external mutation is performed by this track.
- Papers and preprints remain excluded.

## External Gates

External publication credentials and authorization remain separate and fail closed.

## Out of Scope

- Publishing or replacing any remote artifact.
- DOI changes, papers, or preprints.

## Authoritative Inputs

- `docs/contracts/MEDALLION_ARCHITECTURE_CONTRACT.md` at contract commit `d67bbfac`.
- Current release-readiness, publication-manifest, dashboard, Hugging Face, and Zenodo evidence.
