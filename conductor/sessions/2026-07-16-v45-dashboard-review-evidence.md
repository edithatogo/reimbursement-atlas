# Session v45: dashboard review evidence retention

## Change

The Pages workflow now uploads the Playwright HTML report, route screenshots, performance metrics
and axe-core attachments for 30 days after the browser smoke job, including when that job fails.

## Boundary

This makes the automated evidence accessible to reviewers but does not convert screenshots or axe
results into human approval. Cross-platform visual review and accessibility sign-off remain open in
issue #188 and in the release-readiness handoff.
