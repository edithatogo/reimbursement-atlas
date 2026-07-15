# Session v37: dashboard performance budget

## Scope

Advance issue #188 without treating automated checks as human visual approval.

## Changes

- Added Playwright budgets for every public route in desktop and mobile Chromium:
  - DOMContentLoaded at or below 5 seconds;
  - transferred resources at or below 8 MB.
- Attached machine-readable performance metrics to each browser test result.
- Updated the dashboard validation contract and Conductor plan.

## Evidence

- `npm run test:browser` remains the executable route, accessibility, performance and browser
  smoke gate.
- Cross-platform pixel baselines and human accessibility sign-off remain blocked review items.
