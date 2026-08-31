# Compatible dashboard dependency refresh

## Scope and base

Local isolated branch `codex/dashboard-compatible-refresh`, based on fetched,
committed `origin/main` at `9e5d082ed93a50747bcd7c19182691eccf08281a` (#798).
The source-evidence branch/worktree and commit
`724e667a4234feea3969a460475feb8a865b1c99` remain preserved.
Its four owned files compare identically with integrated commit
`ab321dce33f25f5eddc993dd56ca0a14251fe20d` (`git diff --exit-code`
restricted to those four paths); the original worktree remains clean and preserved.

This is the compatible dashboard slice of
[#797](https://github.com/edithatogo/reimbursement-atlas/issues/797), not closure
of that issue or the dependency-refresh track. Parent integration follows #801.
No full regeneration, SBOM refresh, hosted evidence renewal, push or merge is
performed in this slice. Those integration obligations remain with the parent.

## Decisions and upstream evidence

Registry metadata and primary release sources checked on 31 August 2026:

| Package | Before | Selected | Compatibility evidence |
| --- | --- | --- | --- |
| Astro | 7.2.4 | 7.2.9 | Patch release; Node >=22.12.0 and npm >=9.6.5. |
| @cosmograph/react | 2.3.3 | 2.5.1 | Same major; core package pinned upstream to 2.5.1. React and React DOM peer range `>=16.8.0 || ^17 || ^18` admits installed stable 19.2.8 through its first clause. |
| js-yaml-orig alias | npm:js-yaml@5.3.0 | npm:js-yaml@5.4.1 | Both dashboard and local compatibility-wrapper dependency updated; ESM/CJS wrapper code and overrides retained. |
| PapaParse | 5.6.0 | 5.7.0 | Same major; remote download timeout addition does not change the dashboard's text-input usage. |
| TypeScript | 6.0.3 | 6.0.3 | Deliberately retained; checker peer range remains `^5.0.0 || ^6.0.0`. |

- [Astro 7.2.9 release](https://github.com/withastro/astro/releases/tag/astro%407.2.9): typing, route/manifest and escaping fixes. [Registry metadata](https://registry.npmjs.org/astro/7.2.9).
- [Cosmograph library releases](https://cosmograph.app/docs-lib/releases/): 2.4 introduces annotations/data preparation improvements; 2.5 introduces 3D support and link styling changes. No 3D mode or new application feature is enabled here. [React package metadata](https://registry.npmjs.org/@cosmograph%2freact/2.5.1).
- [js-yaml 5.4.1 changelog](https://github.com/nodeca/js-yaml/blob/5.4.1/CHANGELOG.md): 5.4.0 flags breaking low-level AST/style and sortKeys behavior, and formatting changes; 5.4.1 hardens merge limits. These are not ignored merely because this is a minor update. Wrapper tests cover load/dump and runtime resolution through Astro; static build exercises actual consumers. No raw AST manipulation is added. [Registry metadata](https://registry.npmjs.org/js-yaml/5.4.1).
- [PapaParse 5.7.0 release](https://github.com/mholt/PapaParse/releases/tag/5.7.0) and [registry metadata](https://registry.npmjs.org/papaparse/5.7.0).
- [Astro checker metadata](https://registry.npmjs.org/@astrojs%2fcheck/0.9.10) still excludes TypeScript 7. [#362](https://github.com/edithatogo/reimbursement-atlas/issues/362) remains monitored; Dependabot deferral and the compatibility canary are unchanged. This is a compatibility warning, not a new release gate.

`@astrojs/react` was already 6.0.4 on the base and remains unchanged. Its peer
contract admits React 19.2.8. No direct dependency major upgrades, forced resolution
or `--legacy-peer-deps` were used. Astro requires transitive `diff ^9.0.0`, so
diff 8 -> 9 is an upstream-required transitive change, not an elective major bump.
Lock changes also follow Astro compiler/sharp and Cosmograph rendering/UI dependency
changes. Existing security overrides remain unchanged.

## Focused verification

Environment: Node 26.8.1, npm 11.19.0, macOS arm64; this is local verification,
not hosted Linux/browser-matrix evidence.

Commands from `apps/dashboard`:

```sh
npm install --package-lock-only --ignore-scripts --no-audit --no-fund
npm ci --no-audit --no-fund
npm run test:dependencies
npm run build
npm audit --omit=dev --audit-level=high
npm ls astro @astrojs/check @astrojs/react @cosmograph/react js-yaml-orig papaparse typescript --depth=0
ASTRO_PREVIEW_BACKGROUND=1 CI=1 npm run test:browser -- --project=desktop-chromium --workers=1 --retries=0 --grep 'compatible Cosmograph|semantic graph alternative|searches rows beyond'
```

Commands from the repository root:

```sh
python -m pytest -q tests/unit/test_dependency_automation_contract.py tests/unit/test_typescript_compatibility.py tests/unit/test_typescript_compatibility_workflow_contract.py
python -m pytest -q tests/unit/test_dashboard_review_packet.py tests/unit/test_dashboard_owner_review_packet.py
git diff --check
```

- Clean npm installation completed. npm 11 reported unapproved install scripts for
  esbuild/fsevents; no broad approval was added, and the build ran successfully.
- Three Node dependency tests pass: exact compatible pins/lockfile and alias contract,
  ESM/CommonJS YAML load/dump plus Astro's resolved override, and PapaParse quoting,
  multiline values, string identifiers, malformed rows and real graph CSV assets.
- 51 Python tests pass across the five listed dependency, TypeScript and packet modules.
- `astro check`: zero errors, warnings or hints. Static build: 98 pages.
- Production audit: zero vulnerabilities. `npm ls` confirms selected direct versions.
- Three focused desktop Chromium tests pass: graph mount, semantic alternative and
  search beyond the compact initial table. This is not a full matrix run.

## Browser packet count contract

Playwright discovery lists 68 tests: eleven routes plus six behavioral tests in
each of the unchanged four projects. The added graph regression exercises Firefox's
intentional semantic fallback rather than skipping that project.

The generator now emits `dashboard-automated-review-v3`, requiring exactly 68
passing results and matching JUnit totals with zero failures, errors or skips.
The schema preserves historical v2/64 packets, but a v3 packet cannot pass with
64 results. Route/project coverage remains the complete 44-pair matrix, with 44
screenshots. Tests reject legacy counts in the current generator, skipped added
behavioral tests and cross-version count mismatches. Owner-packet tests read the
archived packet's count instead of assuming all historical evidence is current.
No generated packet or standing approval is rewritten. Existing dashboard scope
applies; no new owner approval is requested.

## Browser setup observations and residual risks

Astro detects this agent environment and backgrounds `preview`, initially causing
Playwright's foreground webServer process check to fail before browser tests.
The worktree-owned preview was stopped using `astro preview stop`. The scoped
`ASTRO_PREVIEW_BACKGROUND=1` setting follows the installed CLI's child-process
contract and keeps Playwright in charge of the foreground server. It is not a
committed application configuration change or permission bypass.

The first runnable browser attempt found only cached Chromium revision 1228,
whereas the existing locked Playwright requires revision 1234. Installed the
matching headless Chromium using `playwright install chromium --only-shell`;
this does not update the dependency lockfile or substitute an old browser.

Cosmograph's new visual defaults, 3D implementation and WebGL support need the
parent's full browser matrix before integration acceptance. The new canvas test
checks mounting and page errors, not pixel parity or exhaustive GPU behavior.
Firefox retains its existing semantic fallback. js-yaml's new formatting/AST
semantics remain an integration consideration for any future low-level consumers.
One focused run overlapping a rebuild failed the existing search test with zero
rows; a subsequent run against the completed build passed all three tests with
retries disabled. Build and browser execution should remain sequential.
No compatibility claim is made for TypeScript 7. Generated evidence is intentionally
stale relative to this local dependency patch until parent regeneration.
