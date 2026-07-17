# Session v158: SBOM control reconciliation

## Objective

Reconcile the generated repository-automation status with the actual SBOM implementation and add
regression coverage for the detector.

## Change

- Require both `data/derived/sbom/cyclonedx-python.json` and
  `data/derived/sbom/cyclonedx-dashboard.json` before reporting SBOM generation as implemented.
- Add `tests/unit/test_automation_controls.py` for incomplete and complete states.
- Regenerate the repository-automation artefacts and downstream release/public-product outputs.

## Evidence

- `pixi run python -m pytest tests/unit/test_automation_controls.py -q` passed.
- `pixi run repo-automation` reports 20 controls and zero warning/failure records.
- SBOM control status is `implemented` and maturity is `advanced`.

## Boundary

This corrects repository evidence only. It does not authorize release publication, OSF/Hugging
Face/Zenodo mutation, source licence approval, human research review or policy claims.
