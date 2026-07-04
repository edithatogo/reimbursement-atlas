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

The build performs `astro check` before `astro build`. It currently renders six static routes:

- `/`
- `/sources/`
- `/analyses/`
- `/crosswalks/`
- `/ontologies/`
- `/readiness/`

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
