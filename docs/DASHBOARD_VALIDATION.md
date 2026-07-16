# Dashboard validation

The dashboard is now a build-tested Astro 7 static application rather than a placeholder scaffold.

## Reproducible install

The dashboard has a committed npm lockfile:

```bash
cd apps/dashboard
npm ci
```

CI should use `npm ci`, not `npm install`, so that the Hugging Face Space and GitHub preview build use the same dependency graph that was validated locally.

## Build gate

```bash
cd apps/dashboard
npm run build
```

The build performs `astro check` before `astro build`. It currently renders nine static routes:

- `/`
- `/sources/`
- `/analyses/`
- `/crosswalks/`
- `/ontologies/`
- `/readiness/`
- `/automation/`
- `/roadmap/`
- `/demonstrators/`

The public status contract is generated separately and is available at
`apps/dashboard/public/status.json`. It distinguishes software release readiness from evidence
and external publication readiness. The deterministic quality gate checks that every generated
HTML page has a language, title, viewport, heading and bounded page size:

```bash
pixi run dashboard-status
cd apps/dashboard && npm run build
cd ../.. && pixi run dashboard-quality
```

The dashboard tables provide client-side text filtering, CSV downloads and stable section anchors.
Source and mapping pages link back to generated provenance and review artefacts.

## Browser smoke gate

Playwright exercises every public route in desktop and mobile Chromium profiles, checks status
codes, page metadata, console errors and page-error events, runs axe-core accessibility checks,
enforces a 5-second DOMContentLoaded and 8 MB transferred-resource budget, and captures bounded
screenshot and performance artefacts for CI diagnostics:

```bash
cd apps/dashboard
npx playwright install chromium
npm run test:browser
```

The GitHub Pages workflow retains the Playwright HTML report, route screenshots, performance
metrics and axe-core attachments as `dashboard-review-evidence-<run-id>` for 30 days. Reviewers
should inspect that artifact on both desktop and mobile profiles and record the human visual and
accessibility decision in issue [#188](https://github.com/edithatogo/reimbursement-atlas/issues/188).
Artifact availability is evidence for review, not approval by itself.

Pixel-diff baselines are intentionally not committed yet because the project currently validates
on macOS and Linux; cross-platform visual baselines require a dedicated browser-version policy
and human review. The responsive smoke matrix and axe-core checks are automated, but they do not
substitute for approval of platform-specific visual or accessibility baselines.
The suite also checks that the first public table's search control is keyboard-focusable and
filters rows when used from the keyboard. This is interaction evidence, not WCAG conformance or
human assistive-technology approval.

## Cosmograph compatibility note

The current Cosmograph dependency chain imports `gl-bench`. Under the Astro 7 / Vite 8 / Rolldown build path, the browser field can resolve to a minified file without a default ESM export. The dashboard config aliases `gl-bench` to its ESM module file so the static build succeeds without patching vendored package files.

## Dashboard-safe data contract

The dashboard only reads copied CSV artefacts from `apps/dashboard/public/data`. These are generated metadata or synthetic vertical-slice outputs. They must not contain raw MBS/PBS/CMS/NHS source dumps, CPT descriptors, restricted ontology payloads, UMLS/RxNorm distributions, DSM-5 text, confidential rebates or special-pricing arrangements.

The smoke tests now require key dashboard data files and the package lock to exist:

```bash
uv run pytest tests/smoke/test_dashboard_assets.py -q
```

## Security check

```bash
cd apps/dashboard
npm audit --omit=dev --audit-level=moderate
```

The current local run found zero vulnerabilities for production dependencies.

## GitHub Pages project-site contract

The public deployment is a project site at
`https://edithatogo.github.io/reimbursement-atlas/`, not a root site. Local builds keep
the root base for development; the Pages workflow sets `PUBLIC_DEPLOY_TARGET=github-pages`
so Astro emits the `/reimbursement-atlas/` prefix. Navigation, CSV downloads, status JSON and
the client-side graph loader all derive URLs from Astro's `BASE_URL`.

The Pages workflow also runs this fail-closed artifact check before upload:

```bash
PUBLIC_DEPLOY_TARGET=github-pages npm run build
cd ../..
uv run --all-extras python scripts/check_dashboard_pages_assets.py
```

This prevents root-relative `/_astro/` or `/data/` references from reaching the public site.

After deployment, the Pages workflow runs a bounded live smoke check against the canonical
HTTPS URL. It retries for CDN propagation, then verifies the HTML references, favicon, status
manifest, graph CSVs and same-origin project routes all return HTTP 200:

```bash
uv run --all-extras python scripts/check_live_pages.py
```
