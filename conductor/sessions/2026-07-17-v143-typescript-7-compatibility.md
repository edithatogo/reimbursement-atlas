# Session v143: TypeScript 7 compatibility

Date: 2026-07-17
Track: `track_harness_engineering`
Related issue: #362

## Evidence

- npm stable TypeScript: `7.0.2`
- npm next TypeScript: `7.1.0-dev.20260715.1`
- Pinned checker: `@astrojs/check@0.9.9`
- Checker peer contract: `typescript: ^5.0.0 || ^6.0.0`
- TypeScript 7 install probe: `ERESOLVE` before `astro check`
- Current supported dashboard compiler: TypeScript `6.0.3`

## Decision

Do not use `--legacy-peer-deps`, force-install TypeScript 7, or weaken lockfile reproducibility. Keep
the compatibility issue open until `@astrojs/check` publishes TypeScript 7 peer support.

## Adoption gate

After checker support is published, rerun `npm ci`, `npm run check`, `npm run build` and the browser
matrix before changing the pinned TypeScript version.
