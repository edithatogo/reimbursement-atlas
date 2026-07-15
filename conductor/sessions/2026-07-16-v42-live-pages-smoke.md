# v42 Post-deployment Pages smoke gate

## Scope

Convert the manual public-site verification from v41 into a recurring deployment gate.

## Changes

- Added `scripts/check_live_pages.py` with bounded retries for GitHub Pages/CDN propagation.
- The probe requires HTTPS, validates the `/reimbursement-atlas/` project prefix, checks same-origin
  HTML references, and fetches the favicon, status manifest and graph CSVs.
- Added unit tests for healthy project-prefixed references and root-relative reference rejection.
- Added a `live-smoke` job after `deploy` in `.github/workflows/pages.yml`, using Python 3.14 and
  SHA-pinned actions.
- Regenerated repository automation, release-readiness, data-dictionary, seed-lake and research
  package descriptors.

## Evidence

- PR #204 required contexts passed and merged as `a8065eb`.
- Main Pages run `29442862134` passed `build`, `deploy` and `live-smoke`.
- Local live probe passed against `https://edithatogo.github.io/reimbursement-atlas/`.
- Focused unit tests passed; Bandit, Ruff and basedpyright passed.

## Remaining

Human cross-platform visual/accessibility review, source licensing, OSF registration and public
HF/Zenodo publication remain fail-closed external gates.
