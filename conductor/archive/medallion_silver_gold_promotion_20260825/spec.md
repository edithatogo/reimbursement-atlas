# Silver and Gold Promotion Alignment

## Overview

Classify source-faithful reviewed records as Silver and adjudicated cross-source
evidence as Gold, with explicit checksum-bound promotion decisions.

## Requirements

- Inventory reviewed source bundles as Silver candidates without rewriting them.
- Inventory mapping-study evidence as Gold candidates only when its Silver inputs exist.
- Require parser, schema, rights, provenance, quality, and review gates.
- Block layer skipping and preserve failed decisions.

## Acceptance Criteria

- Deterministic Silver and Gold artifact manifests exist.
- Promotion decisions identify every required and passed gate.
- Gold cannot be approved from Bronze inputs or incomplete mapping evidence.
- Existing source and mapping gates remain authoritative and all repository gates pass.

## Non-functional Constraints

- No inferred equivalence, coverage, or reimbursement claim.
- Existing frozen holdout evidence is not re-evaluated or mutated.

## External Gates

Accountable mapping and licence decisions remain external inputs. This track may
project current decisions but cannot manufacture or broaden them.

## Out of Scope

- New adjudication.
- New source rights decisions.
- Public product publication.

## Authoritative Inputs

- `docs/contracts/MEDALLION_ARCHITECTURE_CONTRACT.md` at contract commit `d67bbfac`.
- `data/derived/reviewed_source_bundles/` and current checksum-bound licence decisions.
- `data/derived/mapping_study/expansion_v9/` as the sealed mapping cycle.
