# v41 GitHub Pages base-path fix

## Scope

The public GitHub Pages site loaded HTML but emitted root-relative Astro assets, causing
JavaScript and hydration requests to return 404 at the domain root. The same issue affected
client-side graph CSV fetches and dashboard navigation when hosted below `/reimbursement-atlas/`.

## Changes

- Added conditional Astro `site` and `base` configuration for `PUBLIC_DEPLOY_TARGET=github-pages`.
- Converted navigation, provenance links, CSV downloads, status JSON and graph data fetches to
  use Astro `BASE_URL`.
- Added `scripts/check_dashboard_pages_assets.py` and wired it into the Pages workflow.
- Documented the local-root versus GitHub-project-site contract in `docs/DASHBOARD_VALIDATION.md`.

## Validation

- Local `npm run build`: passed.
- Pages-targeted `PUBLIC_DEPLOY_TARGET=github-pages npm run build`: passed with zero Astro
  diagnostics.
- `uv run --all-extras python scripts/check_dashboard_pages_assets.py`: passed.

## Remaining

After merge, recheck the deployed URL in a browser for zero console errors and successful graph
CSV loading. Human cross-platform visual and accessibility review remains a separate gate.
