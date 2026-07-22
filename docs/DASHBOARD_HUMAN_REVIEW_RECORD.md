# Dashboard Human Review Record

This template records accountable visual, accessibility, and provenance review. It is not
completed by automated browser or axe checks, and it must not claim universal WCAG conformance.

Copy the JSON shape below into a review record only after inspecting the deployed commit and
retained browser evidence artifact. Validate it against
`schema/DashboardHumanReviewRecord.schema.json`.

```json
{
  "schema_version": "dashboard-human-review-v1",
  "status": "pending",
  "commit": "<deployed-commit>",
  "reviewer": "<accountable-reviewer>",
  "reviewed_at": null,
  "scope": {
    "routes": [],
    "browsers": [],
    "operating_systems": [],
    "assistive_technology": [],
    "provenance": false
  },
  "findings": [],
  "evidence_artifacts": [],
  "remediation_or_waiver": null,
  "approval_scope": null
}
```

Required review coverage is documented in [`DASHBOARD_VALIDATION.md`](DASHBOARD_VALIDATION.md):
visual layout, keyboard operation, screen-reader semantics, responsive states, provenance
traceability, source/version/checksum links, and confirmation that software readiness is not
evidence or publication readiness.
