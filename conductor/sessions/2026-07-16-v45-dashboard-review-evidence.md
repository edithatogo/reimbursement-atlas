# Session v45: dashboard review evidence retention

## Change

The Pages workflow now uploads the Playwright HTML report, route screenshots, performance metrics
and axe-core attachments from the configured `apps/playwright-report` and `apps/test-results`
output paths for 30 days after the browser smoke job, including when that job fails.

## Boundary

This makes the automated evidence accessible to reviewers but does not convert screenshots or axe
results into human approval. Cross-platform visual review and accessibility sign-off remain open in
issue #188 and in the release-readiness handoff.

## Verification

Pages run `29445732834` passed build, deployment and live smoke. The artifact
`dashboard-review-evidence-29445732834` was downloaded and verified to contain the HTML report and
18 PNG route screenshots across the desktop and mobile projects.
