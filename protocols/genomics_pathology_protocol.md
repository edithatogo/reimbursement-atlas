# Protocol: genomics and pathology reimbursement architecture

## Background
Public reimbursement schedules are often treated as if they were directly comparable price lists. That assumption is rarely safe. A fee schedule entry can represent a professional service, facility component, laboratory payment amount, medicine reimbursement basis, hospital bundle, device listing, patient co-payment parameter, or a coverage signal with no price attached. The project therefore treats reimbursement comparison as an evidence architecture problem rather than a simple exchange-rate conversion problem. This protocol defines a reproducible approach for one policy question before any results are interpreted.

The protocol is deliberately conservative. It separates source acquisition from derived publication, distinguishes price from coverage, and requires human review before cross-system mappings are used as policy evidence. Raw source files, restricted descriptors, proprietary terminology releases, confidential net prices and local cache paths are excluded from public outputs unless a later licence review explicitly permits publication.

## Research question
How do public systems connect genomic/pathology test coverage, price and eligibility restrictions?

Secondary questions are: which sources are sufficiently machine-readable for reproducible analysis; which variables are observed directly rather than inferred; which mappings require clinical or health-economic adjudication; and which results should be presented as ranges, typologies or caveated qualitative findings rather than point estimates.

## Datasets
Primary datasets are: Australia MBS pathology/genomics items, US CMS CLFS and Medicare Coverage Database coverage records, NHS Genomic Test Directory, PBS only where medicines are linked to test eligibility, and selected comparator sources once validation gates pass.

Supporting metadata include the source registry, exact source-file table, source-download plans, source-content validation records, data-quality checks, research-question linkages, data dictionary and publication manifest. Additional datasets may be promoted only after a Conductor track, GitHub issue and data-governance review record exist. All source versions must be snapshotted with checksums and byte counts before derived rows are released.

## Inclusion and exclusion
Include records that have a clear public source, explicit jurisdiction, defined payment or coverage concept, effective date or version label where available, and enough metadata to classify the unit of comparison. Include metadata-only records when they clarify licence or acquisition status. Exclude records where the unit cannot be interpreted, where source licensing prevents even derived publication, or where a mapping would require proprietary descriptors that cannot be reviewed safely.

The unit of comparison for this question is test purpose, indication, specimen or method where available. Mappings are allowed only as candidate relationships until adjudicated. One-to-many and many-to-one mappings must be represented explicitly rather than collapsed into a false one-to-one equivalence.

## Analysis plan
First, regenerate source-download, validation, data-quality, data-dictionary, research-linkage and evidence-readiness artefacts. Second, ingest reviewed source files into derived-only records using registered parsers. Third, construct analysis baskets according to source-specific variables and exclusion rules. Fourth, generate deterministic candidate mappings using lexical, code-system and price/context evidence. Fifth, require human adjudication for any mapping used in the policy-facing analysis. Sixth, report summary metrics with explicit caveats for price concept, coverage status, bundling, patient exposure and missing net prices.

Sensitivity analyses will vary mapping confidence thresholds, price-concept inclusion, PPP/currency assumptions where relevant, bundled versus unbundled payment interpretation, and exclusion of sources with low machine-readability or restricted licence gates. Results will be versioned so that source updates can be compared with source-drift reports.

## Bias and limitations
Expected biases include survivorship of better-published systems, English-language source advantage, false lexical matches, hidden rebates, provider gap payments, local implementation differences, and absence of patient-level utilisation in early releases. Published fee amounts may not equal actual payments, allowed amounts, net prices, negotiated prices, patient costs or access. The analysis must avoid claiming causal access effects unless utilisation and implementation evidence are linked.

## Outputs
Planned outputs are coverage-price-restriction matrices, source-specific caveat tables, mapping review appendices and a public derived dataset suitable for Hugging Face and OSF appendices. Public outputs must pass the publication manifest, data-quality gate, public-data policy, evidence-readiness gate and source-drift gate. Dashboards should present caveats next to metrics rather than separating them into appendices only.

## OSF
The OSF component will contain this protocol, a generated data dictionary, source and licence caveats, analysis report, mapping appendix, sensitivity-analysis appendix and final paper/preprint materials when available. Registration status remains draft/planned until a human reviewer confirms that inclusion rules, source licences and mapping adjudication requirements are adequate for the research question.

## Estimands and outcomes
The primary descriptive estimand is the jurisdiction-specific proportion of adjudicated test-indication pairs with an explicit in-force coverage decision. Secondary outcomes are the proportion with a public schedule amount and the distribution of restriction classes. No cross-currency pooled price is permitted.

## Source versions and analysis window
Before outcome inspection, freeze retrieval time, effective-date window, source version, checksum and code commit. Superseded and overlapping decisions receive explicit status codes.

## Missing data and denominator rules
`not covered`, `not found`, `not yet effective`, `locally determined`, `not machine-readable` and `licence restricted` remain distinct. Undefined proportions are null, never zero.

## Mapping and comparability adjudication
Two independent qualified reviewers, blinded to price outcomes, classify analyte/gene, variant, indication, specimen, method, panel, setting and effective-date matches; a third resolves disagreements. Agreement is reported by relationship type.

## Uncertainty multiplicity and sensitivity analyses
The signed appendix must freeze interval methods, confirmatory families, correction method, minimum coverage and sensitivities before analysis.

## Negative controls and calibration
Parser and mapping performance are calibrated against hand-reviewed records. Longitudinal work requires prespecified unaffected tests or outcomes.

## Deviations amendments and human review
Every override and deviation receives a reason code. OSF registration requires signed methods, domain, licence and governance review; simulated review does not satisfy that gate.
