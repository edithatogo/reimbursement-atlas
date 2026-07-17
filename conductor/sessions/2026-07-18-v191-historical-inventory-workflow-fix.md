# Conductor Session: v191 Historical Inventory Workflow Fix

Date: 2026-07-18

## Scope

Repair and verify the metadata-only historical MBS archive inventory refresh.

## Finding

The first manual refresh run `29589169920` failed before inventory generation because the
workflow did not expose the repository `src` directory on `PYTHONPATH`; the script could not
import `reimburse_atlas.registry`.

## Implementation

- Added `PYTHONPATH: src` to the historical inventory job environment.
- Added a unit contract test that prevents removal of the workflow import path.
- Regenerated workflow-derived automation, licence-review, research-package and seed-lake
  artefacts so deterministic CI remains clean.

## Verification

- PR #445 passed the protected browser, Python 3.14, security, dashboard, readiness,
  deterministic-regeneration and generated-artifact checks.
- Merged commit: `12cb345d400f97e5b5545e0224384e38a9d8c590`.
- Post-merge inventory run `29589791609` passed and discovered 343 historical targets across
  32 archive pages with no inventory drift.
- The inventory remains metadata-only: 0 downloadable targets, 343 manual-review targets,
  and no raw historical payloads were downloaded or committed.

## Boundary

Historical acquisition, parsing and publication remain gated on source-specific licence review;
the successful inventory refresh is not licence approval.
