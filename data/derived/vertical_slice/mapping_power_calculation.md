# Mapping Calibration Power Calculation

This generated report replaces an informal sample-size estimate. It uses
explicit normal-approximation formulas and is planning guidance, not evidence
of mapping performance.

## Current fixture

The current fixture has **4 cases**: 2 positive cases and 2 negative controls.
It remains a smoke test only.

## Assumptions

- Positive and negative calibration cases are sampled separately and treated as independent.
- Each case has one adjudicated reference outcome and one evaluated mapping outcome.
- The confidence-interval calculations use a two-sided 95% normal approximation.
- Power calculations use a one-sided alpha=0.05 test with 80% power.
- No clustering, spectrum bias, class imbalance, verification bias or missing adjudications is modelled.
- The synthetic four-case fixture is a smoke test and is not used to estimate the target metric.

## Calculation

For confidence-interval planning, the implementation uses `n = z^2 p(1-p) / d^2`.
For one-sided power planning, it uses the standard normal approximation combining
the null and alternative variances. Both formulas are implemented in
`scripts/make_mapping_power_calculation.py` and covered by unit tests.

| Expected metric | CI half-width | Cases per class |
| ---: | ---: | ---: |
| 90% | +/-5% | 139 |
| 90% | +/-3% | 385 |
| 80% | +/-5% | 246 |
| 50% | +/-5% | 385 |

| Null metric | Alternative metric | Alpha | Power | Cases per class |
| ---: | ---: | ---: | ---: | ---: |
| 80% | 90% | 5% | 80% | 83 |
| 90% | 95% | 5% | 80% | 184 |

## Recommended design

- Development set: **300 positive + 300 negative = 600 cases**.
- Independent holdout: **75 positive + 75 negative = 150 cases**.
- Total including holdout: **750 cases**.
- Rationale: 300 development cases per class gives approximately +/-3.4 points at an expected 90% metric and +/-4.5 points at an expected 80% metric; the holdout is additional.

Cases should be stratified across MBS, PBS, CMS, genomics, procedures, medicines,
devices and ambiguous mappings. Near-duplicate cases do not provide independent
information.

## Limitations

- The normal approximation is planning guidance, not an exact binomial power calculation.
- The design must be re-estimated if the estimand, acceptable null, prevalence, clustering or adjudication protocol changes.
- Cases must be stratified across sources and mapping difficulty; duplicating near-identical cases does not increase effective sample size.
