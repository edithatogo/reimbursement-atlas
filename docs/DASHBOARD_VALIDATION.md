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

The build performs `astro check` before `astro build`. It currently renders nine public route
families plus generated source and analysis detail routes:

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

The dashboard tables provide client-side text filtering, live result-count announcements, CSV
downloads, captions and stable section anchors. Wide tables remain inside keyboard-focusable,
locally scrollable containers rather than widening the page. Source and mapping pages link back to
generated provenance and review artefacts.

## Browser smoke gate

Playwright exercises every public route family plus representative source and analysis detail
routes in desktop and mobile Chromium, Firefox and WebKit profiles. It checks status codes, page
metadata, current-navigation state, captions, page-level horizontal overflow, console errors and
page-error events; runs axe-core accessibility checks; enforces a 5-second DOMContentLoaded and
8 MB transferred-resource budget; and captures bounded screenshot and performance artefacts:

```bash
cd apps/dashboard
npx playwright install chromium
npm run test:browser
```

The GitHub Pages workflow retains the Playwright HTML report, route screenshots, performance
metrics and axe-core attachments as `dashboard-review-evidence-<run-id>` for 30 days. Reviewers
should inspect that artifact on both desktop and mobile profiles and record the human visual and
accessibility decision in issue [#493](https://github.com/edithatogo/reimbursement-atlas/issues/493).
Public blocker/provenance parity is tracked in issue
[#501](https://github.com/edithatogo/reimbursement-atlas/issues/501).
Artifact availability is evidence for review, not approval by itself.

Pixel-diff baselines are intentionally not committed yet because the project currently validates
on macOS and Linux; cross-platform visual baselines require a dedicated browser-version policy
and human review. Pull requests now exercise Chromium desktop/mobile plus Firefox desktop and
WebKit desktop through the pinned `dashboard-browser.yml` workflow. The responsive smoke matrix
and axe-core checks are automated, but they do not substitute for approval of platform-specific
visual or accessibility baselines.
The suite also checks skip navigation, visible keyboard focus, filter result announcements, the
semantic graph alternative, representative detail pages, and bounded reflow at 640 px and 320 px
viewports (200% and 400% desktop-width equivalents). These are automated interaction and reflow
checks, not WCAG conformance or human assistive-technology approval.

## Cosmograph compatibility note

The current Cosmograph dependency chain imports `gl-bench`. Under the Astro 7 / Vite 8 / Rolldown build path, the browser field can resolve to a minified file without a default ESM export. The dashboard config aliases `gl-bench` to its ESM module file so the static build succeeds without patching vendored package files.

The WebGL canvas is treated as a visual overview. Every supported browser receives a semantic,
keyboard-operable alternative with node counts, a bounded node table and links to the complete
generated node and relationship CSVs. Firefox may use only that alternative where the headless
renderer is unavailable.

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

The accountable review record contract is [`schema/DashboardHumanReviewRecord.schema.json`](../schema/DashboardHumanReviewRecord.schema.json), with a copy-ready template in [`DASHBOARD_HUMAN_REVIEW_RECORD.md`](DASHBOARD_HUMAN_REVIEW_RECORD.md). It requires the deployed commit, reviewer, route/browser/OS/assistive-technology scope, provenance scope, findings and any remediation or waiver. An `approved_within_scope` record additionally requires a date-time, at least one durable evidence artifact, a non-empty bounded approval scope and completed provenance review. The schema rejects case variants of unscoped `WCAG compliant` or `WCAG conformant` claims.

When a completed record is placed at `data/derived/dashboard_review/human_review.json`, the `review-schemas` Pixi task validates it automatically. An absent record remains an explicit pending human-review state rather than a failed software gate.

The latest automated browser run is summarized in `data/derived/dashboard_review/automated_review_packet.json`. It binds the tested commit to the 36 retained route screenshots from nine route families across four browser/device projects. Screenshot binaries remain in the Playwright or GitHub Actions artifact; the committed packet retains their SHA-256 digests. This packet is an input to, not a substitute for, the accountable human review record.

After deployment, the Pages workflow runs a bounded live smoke check against the canonical
HTTPS URL. It retries for CDN propagation, then verifies the HTML references, favicon, status
manifest, graph CSVs and same-origin project routes all return HTTP 200:

```bash
uv run --all-extras python scripts/check_live_pages.py
```
