# Public Product, Citation and Dashboard Maturity

## Objective

Turn the generated reimbursement-atlas metadata surface into a current, citable and accessible
public product without implying that software readiness equals evidence or publication readiness.

## Scope

- Validate and improve `CITATION.cff` for the Apache-2.0 software repository.
- Update the README with current product status, citation guidance and underlying-data licensing
  boundaries.
- Publish a deterministic machine-readable status manifest with separate software, evidence and
  publication dimensions.
- Add dashboard executive status cards, accessible search/filter controls, stable section anchors,
  downloadable generated artefacts and provenance links.
- Add CI/build coverage for citation metadata, status generation and the static dashboard.
- Provide manual, gated deployment paths for GitHub Pages and Hugging Face Spaces without placing
  tokens or unreviewed source payloads in the repository.

## Non-goals

- Do not publish raw MBS, PBS, CMS, CPT or other licence-gated source payloads.
- Do not mark OSF, Hugging Face or Zenodo publication complete without credentials, licence review,
  protocol review and explicit publication approval.
- Do not describe fixture-backed policy demonstrators as evidence-ready findings.

## Acceptance Criteria

1. `CITATION.cff` contains valid required software citation metadata and its repository URL.
2. `pixi run citation-validate` fails closed for malformed or incomplete citation metadata.
3. README documents the current public product, Apache-2.0 software licence and separate source-data
   licensing.
4. `apps/dashboard/public/status.json` is generated from current tracked readiness summaries and
   distinguishes software, evidence and publication states.
5. Dashboard index presents the three readiness dimensions and an explicit no-overclaiming notice.
6. Dashboard tables provide accessible search controls, downloads and stable deep-link anchors.
7. Source and mapping pages expose provenance/review paths without exposing restricted payloads.
8. Dashboard build, Python tests, lint, type checks and public-data policy gates pass locally.
9. Unavailable deployment, DOI and human-review gates remain visible as gated, not successful.

## Cross-references

- Parent issue: `Public product, citation and dashboard maturity`
- Generated child issues: `.github/generated-issues/102-*.md` through `.github/generated-issues/112-*.md`
- Output plans: `out_citation_cff`, `out_public_dashboard`, `out_public_status_manifest`,
  `out_zenodo_release_doi`
