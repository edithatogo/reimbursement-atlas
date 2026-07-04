# ADR 0015: Locked dashboard build

## Status

Accepted.

## Context

The dashboard is intended to become a Hugging Face Space and GitHub-preview surface for the atlas. Previous versions scaffolded Astro and Cosmograph but had not completed a Node install or static build in the local runtime.

## Decision

Commit `apps/dashboard/package-lock.json`, use `npm ci` in CI, and require `npm run build` as the dashboard validation gate.

The Astro config aliases `gl-bench` to its ESM module entry to keep Cosmograph compatible with the Astro 7 / Vite 8 / Rolldown build path.

## Consequences

- Dashboard dependencies are reproducible.
- Node validation is no longer deferred to future work.
- CI and local validation use the same npm dependency graph.
- The Cosmograph workaround is explicit and localised to the dashboard config.
