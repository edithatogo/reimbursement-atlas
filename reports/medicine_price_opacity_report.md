# Bounded evidence report: rq_medicine_opacity

## Status and scope

This is a deterministic bounded evidence report, not a paper or preprint. The checksum-bound claim package is `approved_within_scope`. No manuscript submission or broad research-publication approval is implied.

## Research question

How opaque are medicine reimbursement prices across public systems?

## Evidence binding

- Claim package: `data/derived/research_claims/rq_medicine_opacity.json`
- Claim package SHA-256: `0e3e4a7e78167e463ea5627712bfa1d4ed477634d663a039712aba218f661791`
- Analysis status: `complete`
- Required reviewed sources: `3`
- Missing reviewed sources: `0`

## Prespecified methods

- price concept taxonomy
- rebate caveat scoring
- restriction extraction

The methods remain bounded to deterministic descriptive transformations of reviewed derived inputs. They do not estimate treatment effects, infer hidden prices, equate unlike payment concepts, or convert schedule inclusion into a coverage conclusion.

## Source scope

- `au_pbs`
- `us_cms_asp`
- `nz_pharmac`

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

- opacity scorecard
- policy report

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
