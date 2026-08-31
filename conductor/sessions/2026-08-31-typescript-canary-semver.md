# TypeScript canary peer-range correction

Follow-up to [#362](https://github.com/edithatogo/reimbursement-atlas/issues/362).
Prepared on isolated branch `codex/typescript-canary-semver`, based on committed
main `1f1285847e61e86c9ed5eaa987fc36a3c6508ba4`. Canonical main, the dashboard
worker and the parent's ignored `data/local` metadata report are not modified.

## Correction

The former substring helper admitted `5.*`, `>=7 <7` and `>=70`, and missed valid
ranges such as `>=6 <8` and exact `7.0.2`. It also recommended observed `7.0.2`
against `^7.2.0` without establishing candidate compatibility.

Range evaluation now belongs to npm: the existing fixed-argv, read-only `NpmView`
looks up `typescript@<complete-peer-range>` with field `version`. Exact versions
returned by that lookup are intersected with the independently observed
`typescript@7` versions. Only the intersection is recommended. The existing
candidate string field and report schema remain unchanged; successful reports
list only eligible candidates, not excluded candidates.

The local validator checks concrete stable numeric version strings only; it does
not parse semver ranges. Malformed metadata, prerelease/build-suffixed versions,
missing candidates and non-7 channel results fail closed as `unknown`. A valid
empty intersection is `blocked_peer`. Lookup errors retain existing non-upgrade
classification. `unknown` remains an external warning, not a repository release
blocker. No TypeScript upgrade, dependency install or new runtime dependency is
introduced. An unbounded `>=7` legitimately admits observed stable 7.x versions;
an artificial upper-bound requirement would itself be incorrect.

The additional request uses `npm view` without a shell or lifecycle scripts and
retains the existing per-request 60-second timeout. There are at most three
sequential lookups (up to 180 seconds total), versus the previous two.

## Validation

Run from the isolated worktree, using the canonical installed Python/Ruff tools:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  REIMBURSE_ATLAS_ROOT="$PWD" \
  /Volumes/PortableSSD/GitHub/med-billing/reimbursement-atlas-conductor/.pixi/envs/default/bin/python \
  -B -m pytest tests/unit/test_typescript_compatibility.py \
  tests/unit/test_typescript_compatibility_workflow_contract.py \
  tests/unit/test_governance_monitoring.py \
  tests/unit/test_dependency_automation_contract.py \
  -q -o addopts='' -p no:cacheprovider
/Volumes/PortableSSD/GitHub/med-billing/reimbursement-atlas-conductor/.pixi/envs/default/bin/ruff \
  check --no-fix --no-cache scripts/make_typescript_compatibility_report.py \
  tests/unit/test_typescript_compatibility.py
/Volumes/PortableSSD/GitHub/med-billing/reimbursement-atlas-conductor/.pixi/envs/default/bin/ruff \
  format --check --no-cache scripts/make_typescript_compatibility_report.py \
  tests/unit/test_typescript_compatibility.py
git diff --check
```

Initial results: 57 tests passed; Ruff lint and formatting passed; diff whitespace check
passed. Tests include full-range query arguments, wildcard/contradictory/bounded
ranges, exact candidate intersection, scalar/list metadata, invalid metadata,
lookup errors, fixed argv/timeout and non-release-blocking governance behavior.
Native subprocess-response tests explicitly cover empty stdout, empty version
lists, prerelease-only and mixed stable/prerelease results, build suffixes and
nonzero npm results even when stdout contains an otherwise eligible version.
Unit registry responses are injected fixtures.

## Authorized PR continuation

The parent authorized the three-file commit, normal push and PR linked to #362,
with native generated parity or hosted CI, but explicitly held merge until the
source/dashboard sequence settles. Use a non-closing issue reference: this fix
does not close the external watch or authorize adoption of TypeScript 7.

The native report CLI was run with the above Python environment and
`--output-dir data/local/canary-semver-20260831`. Both JSON and Markdown outputs
are confirmed ignored and excluded from the commit. Live metadata returned:

- Installed TypeScript: `6.0.3`.
- Checker: `@astrojs/check@0.9.10`.
- Peer range: `^5.0.0 || ^6.0.0`.
- Candidate: `7.0.2`.
- Status: `blocked_peer`; `upgrade_recommended: false`; `errors: []`.
- `network_io: true`; `mutation_performed: false` (metadata-only lookups;
  report output itself writes the two authorized ignored evidence files).

Hosted PR CI is the selected generated-parity check; no hosted success is claimed
at preparation time. No canonical generator, full local regeneration, workflow
dispatch, publication or merge was performed.

## PR 802 initial lexical input boundary (superseded)

Automated review identified that npm accepts package specs other than ranges.
The parent authorized a bounded lexical input allowlist, not a semantic parser:
at most 512 characters; ASCII digits, x/X, v/V, dots, wildcard, range operators,
ASCII whitespace and hyphens; at least one version digit or wildcard; no leading
hyphen. Rejected input is `unknown` and never reaches the third npm lookup.
Npm still evaluates accepted range semantics. This is deliberately not a claim
that the allowlist validates the full semver grammar.

Tests explicitly reject file/local paths, Git/HTTPS/tarball specs, npm aliases,
option-like inputs, ordinary dist-tags, empty/oversized/non-ASCII input and
alphabetic prerelease ranges. Prerelease selection is not needed for the stable
7.x canary; unsupported forms remain non-upgrade outcomes. Valid caret, OR,
bounded, hyphen, tilde, v-prefixed and x-range inputs retain npm evaluation.

The expanded four-module suite passes 80 tests. No new dependency, install,
release gate or owner approval is introduced. Merge remains held for the parent
and #362 remains an open external watch.

## Constrained stable-range token grammar

Erdos demonstrated that the character allowlist still accepted tag-like `x7`,
`xx`, `x-7` and `7-7`. It is replaced with a deliberately limited token grammar:

- One to three canonical numeric segments with no leading zeroes.
- Optional lowercase `v` only before numeric versions; no `vx` or uppercase `V`.
- Wildcard segments `x`, `X` or `*` only as a trailing suffix, never followed by
  a numeric segment.
- Explicit single comparator operators `<`, `<=`, `>`, `>=`, `=`, `~`, `^`;
  whitespace-separated comparator sets and nonempty `||` alternatives.
- Hyphen pairs require whitespace on both sides of the hyphen and bare version
  tokens at both ends; `7-7` is unsupported, not a prerelease or tag lookup.
- The 512-character ASCII bound remains. Numeric components must be below the
  JavaScript safe-integer maximum, reserving one increment for npm shorthand
  range expansion.

This checks supported token syntax, not comparator satisfaction or intersection.
Npm still owns those semantics. Unsupported syntax returns `unknown` without the
third lookup. Alphabetic prerelease ranges remain deliberately unsupported for
the stable 7.x canary; no dependency is added.

Validation: 114 targeted tests across the four documented modules. Regression
cases cover all four Erdos probes, leading zeroes, unknown alphabetic tokens,
misplaced wildcards, invalid operators/OR/hyphens, numeric bounds, `vx`, uppercase
`V`, and current `^5.0.0||^6.0.0` routing to npm. A development-only cross-check
of 1,050 accepted comparator/token combinations against the already installed
Node semver module found no invalid ranges after the numeric boundary correction.
That module is not imported or installed by the canary or its Python tests.

The reopened bot thread must remain unresolved until Erdos reviews this final
grammar. No merge is authorized; source/dashboard sequencing remains with parent.
