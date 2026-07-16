# v75 Dashboard provenance and quality closeout

## Scope

Close the dashboard provenance drill-down and automated experience-quality roadmap functions
after verifying that implementation and CI evidence are present.

## Local evidence

- Source and mapping provenance routes expose checksums, contracts, confidence and licence notes
  without exposing local absolute paths.
- Dashboard CI runs axe-core accessibility, page-size and performance budgets, route/deep-link
  checks, desktop/mobile Chromium smoke tests and retained visual evidence.
- The Astro build and browser matrix are green on the current main commit.

## Boundary

Both functions are implemented but remain review-gated. Human cross-platform visual review,
assistive-technology review and public deployment verification are not replaced by automated
checks. The GitHub Pages deployment function remains prototype until a canonical deployed URL is
verified.
