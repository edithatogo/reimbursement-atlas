# Bounded evidence report: rq_local_national_coverage

## Status and scope

This is a deterministic bounded evidence report, not a paper or preprint. The checksum-bound claim package is `approved_within_scope`. No manuscript submission or broad research-publication approval is implied.

## Research question

Do local coverage systems create greater access variation than national reimbursement systems?

## Evidence binding

- Claim package: `data/derived/research_claims/rq_local_national_coverage.json`
- Claim package SHA-256: `1173436f4de00273c24738a321341a2192bb37b3c6fae44c60834d480bc4af83`
- Analysis status: `complete`
- Required reviewed sources: `3`
- Missing reviewed sources: `0`

## Prespecified methods

- national-local comparison
- MAC geography taxonomy
- equity caveats

The methods remain bounded to deterministic descriptive transformations of reviewed derived inputs. They do not estimate treatment effects, infer hidden prices, equate unlike payment concepts, or convert schedule inclusion into a coverage conclusion.

## Source scope

- `us_cms_mcd`
- `au_mbs`
- `uk_nhs_payment_scheme`

Each source is represented through its reviewed derived bundle, version and checksum. Missing observations are exclusions rather than zero values. Raw payloads, restricted descriptors and confidential commercial terms are not included in this report.

## Descriptive results

- `missing_source_count`: `0`
- `required_source_count`: `3`
- `reviewed_source_count`: `3`

## Supported claims

- 3 of 3 protocol-required sources have checksum-bound reviewed derived bundles.

## Excluded interpretations

- No causal effect is estimated.
- No cross-jurisdiction price equivalence is inferred.
- No coverage decision is inferred from the presence of a fee or price.
- No paper, preprint, causal, universal reimbursement, or unsupported policy claim is authorized.

## Planned non-manuscript outputs

- coverage discretion map
- report

These output names describe bounded repository artefacts only. They do not authorize external submission, peer-reviewed publication, system rankings, clinical recommendations or policy decisions.

## Audit checklist

- Confirm the claim-package path and SHA-256 before using any result.
- Confirm all required sources remain checksum-bound and approved within scope.
- Preserve source-specific licence, attribution and excluded-field rules.
- Keep denominators, missingness and jurisdictional differences explicit.
- Do not generalize beyond the supported claims listed above.
- Treat any changed input or package checksum as a new review state.

## Reproducibility

Regenerate with `pixi run research-claim-packages`. Inputs are reviewed derived bundles; raw payloads and restricted descriptors are excluded.
The generation step is deterministic and performs no network mutation. Review decisions remain external checksum-bound records, so regeneration can recognize an existing approval without embedding or manufacturing approval inside the claim package itself.
