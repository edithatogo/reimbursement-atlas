# v127 dashboard canary compatibility recheck

## Scope

Reassess the remaining dashboard dependency drift and TypeScript 7 compatibility follow-up using
current npm registry metadata and the repository's existing validation contract.

## Evidence

- Astro current: `7.1.0`.
- `@cosmograph/react` current: `2.3.3`.
- `@astrojs/check` current: `0.9.9`.
- `@astrojs/check@0.9.9` peer dependency: `typescript: ^5.0.0 || ^6.0.0`.
- TypeScript latest: `7.0.2`.
- The repository remains pinned to TypeScript `6.0.3`, which passes the dashboard checks.

## Decision

Close issue #360 as resolved and keep issue #362 blocked. Do not use a peer override or
`--legacy-peer-deps` to claim TypeScript 7 compatibility before the checker contract changes.
