# Session v123: stack-canary dashboard updates

## Scope

Use the current-channel stack canary to identify and safely adopt compatible dashboard
dependency updates without weakening the reproducible `npm ci` or type-checking contract.

## Evidence

- Manual Stack Canary run: `29526345487`.
- Canary workflow passed Pixi, Python 3.14, external quality, dashboard dependency detection,
  dashboard build and Mojo smoke.
- Canary drift issue: [#360](https://github.com/edithatogo/reimbursement-atlas/issues/360).
- Adopted `@cosmograph/react` `2.3.3` and Astro `7.1.0` in `apps/dashboard/package.json` and
  `apps/dashboard/package-lock.json`.
- Retained TypeScript `6.0.3`; `@astrojs/check` `0.9.9` declares a TypeScript `^5.0.0 || ^6.0.0`
  peer range, so TypeScript `7.0.2` was not forced with a legacy peer override.
- Local `npm ci --ignore-scripts`, `npm run build`, and `npm audit --omit=dev --audit-level=moderate`
  passed. Astro check reported zero errors, warnings and hints; the static build produced 94 pages.

## Conductor linkage

The TypeScript 7 follow-up is recorded in `HARNESS-021` as a blocked compatibility item. It must
be re-tested with a normal clean install and the full dashboard/browser gates after the Astro
checker supports TypeScript 7.

## Safety boundary

No runtime peer override, raw source payload, secret, publication mutation or evidence-readiness
claim was introduced. The stack-canary issue remains a dependency observation, not a release
approval.
