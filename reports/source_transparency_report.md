# Bounded evidence report: rq_source_transparency

## Status and scope

This is a deterministic bounded evidence report, not a paper or preprint. The checksum-bound claim package is `approved_within_scope`. No manuscript submission or broad research-publication approval is implied.

## Research question

Which reimbursement systems publish data that are most reproducible, machine-readable and policy-complete?

## Evidence binding

- Claim package: `data/derived/research_claims/rq_source_transparency.json`
- Claim package SHA-256: `bdcea6fa2b9c2ba84f9f15dd5a2a306a9ffef8c8ca5eeeea92242163099ed5a2`
- Analysis status: `complete`
- Required reviewed sources: `1`
- Missing reviewed sources: `0`

## Prespecified methods

- source scorecard
- licence gate analysis
- format classification

The methods remain bounded to deterministic descriptive transformations of reviewed derived inputs. They do not estimate treatment effects, infer hidden prices, equate unlike payment concepts, or convert schedule inclusion into a coverage conclusion.

## Source scope

- `source_registry`

Each source is represented through its reviewed derived bundle, version and checksum. Missing observations are exclusions rather than zero values. Raw payloads, restricted descriptors and confidential commercial terms are not included in this report.

## Descriptive results

- `historical_versions_count`: `63`
- `input_path`: `data/seed/source_registry.jsonl`
- `input_sha256`: `4ee107f5f451d2e7149f534c8a2ba5b7a6ce22ec32d54fd13048561512c63ab8`
- `licence_notes_count`: `64`
- `machine_readable_count`: `41`
- `primary_url_count`: `64`
- `source_count`: `64`
- `utilisation_data_count`: `43`

## Supported claims

- The registry contains 64 source records; 41 are marked machine-readable.
- 63 records identify historical versions and every registry row includes licence notes and a primary URL.

## Excluded interpretations

- No causal effect is estimated.
- No cross-jurisdiction price equivalence is inferred.
- No coverage decision is inferred from the presence of a fee or price.
- No paper, preprint, causal, universal reimbursement, or unsupported policy claim is authorized.

## Planned non-manuscript outputs

- transparency scorecard
- dataset

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
