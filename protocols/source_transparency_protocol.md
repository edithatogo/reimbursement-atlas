# Protocol: source transparency atlas

## Background
Public reimbursement schedules are often treated as if they were directly comparable price lists. That assumption is rarely safe. A fee schedule entry can represent a professional service, facility component, laboratory payment amount, medicine reimbursement basis, hospital bundle, device listing, patient co-payment parameter, or a coverage signal with no price attached. The project therefore treats reimbursement comparison as an evidence architecture problem rather than a simple exchange-rate conversion problem. This protocol defines a reproducible approach for one policy question before any results are interpreted.

The protocol is deliberately conservative. It separates source acquisition from derived publication, distinguishes price from coverage, and requires human review before cross-system mappings are used as policy evidence. Raw source files, restricted descriptors, proprietary terminology releases, confidential net prices and local cache paths are excluded from public outputs unless a later licence review explicitly permits publication.

## Research question
Which reimbursement systems publish data that are most reproducible, machine-readable and policy-complete?

Secondary questions are: which sources are sufficiently machine-readable for reproducible analysis; which variables are observed directly rather than inferred; which mappings require clinical or health-economic adjudication; and which results should be presented as ranges, typologies or caveated qualitative findings rather than point estimates.

## Datasets
Primary datasets are: All registered source families, exact source-file records, source-status observations, download attempts, source validation, publication manifest and data dictionary outputs.

Supporting metadata include the source registry, exact source-file table, source-download plans, source-content validation records, data-quality checks, research-question linkages, data dictionary and publication manifest. Additional datasets may be promoted only after a Conductor track, GitHub issue and data-governance review record exist. All source versions must be snapshotted with checksums and byte counts before derived rows are released.

## Inclusion and exclusion
Include records that have a clear public source, explicit jurisdiction, defined payment or coverage concept, effective date or version label where available, and enough metadata to classify the unit of comparison. Include metadata-only records when they clarify licence or acquisition status. Exclude records where the unit cannot be interpreted, where source licensing prevents even derived publication, or where a mapping would require proprietary descriptors that cannot be reviewed safely.

The unit of comparison for this question is source family, exact file or endpoint, acquisition mode, format, refresh cadence, licensing and historical availability. Mappings are allowed only as candidate relationships until adjudicated. One-to-many and many-to-one mappings must be represented explicitly rather than collapsed into a false one-to-one equivalence.

## Analysis plan
First, regenerate source-download, validation, data-quality, data-dictionary, research-linkage and evidence-readiness artefacts. Second, ingest reviewed source files into derived-only records using registered parsers. Third, construct analysis baskets according to source-specific variables and exclusion rules. Fourth, generate deterministic candidate mappings using lexical, code-system and price/context evidence. Fifth, require human adjudication for any mapping used in the policy-facing analysis. Sixth, report summary metrics with explicit caveats for price concept, coverage status, bundling, patient exposure and missing net prices.

Sensitivity analyses will vary mapping confidence thresholds, price-concept inclusion, PPP/currency assumptions where relevant, bundled versus unbundled payment interpretation, and exclusion of sources with low machine-readability or restricted licence gates. Results will be versioned so that source updates can be compared with source-drift reports.

## Bias and limitations
Expected biases include survivorship of better-published systems, English-language source advantage, false lexical matches, hidden rebates, provider gap payments, local implementation differences, and absence of patient-level utilisation in early releases. Published fee amounts may not equal actual payments, allowed amounts, net prices, negotiated prices, patient costs or access. The analysis must avoid claiming causal access effects unless utilisation and implementation evidence are linked.

## Outputs
Planned outputs are transparency scorecard, reproducibility tiers, source onboarding priorities and a reusable source-assessment dataset. Public outputs must pass the publication manifest, data-quality gate, public-data policy, evidence-readiness gate and source-drift gate. Dashboards should present caveats next to metrics rather than separating them into appendices only.

## OSF
The OSF component will contain this protocol, a generated data dictionary, source and licence caveats, analysis report, mapping appendix, sensitivity-analysis appendix and final paper/preprint materials when available. Registration status remains draft/planned until a human reviewer confirms that inclusion rules, source licences and mapping adjudication requirements are adequate for the research question.

## Estimands and outcomes
Primary outcomes are domain-level proportions of eligible registered sources meeting frozen evidence-backed criteria. System transparency is separate from repository parser/onboarding maturity. Unstable ranks are prohibited; tiers may be used.

## Source versions and analysis window
Freeze the source universe, assessment date/window, URL, redirect chain, retrieval evidence hash and code commit before scoring.

## Missing data and denominator rules
Unavailable, inaccessible, authentication-gated, licence-restricted, non-machine-readable, not assessed and not applicable are distinct. Report numerator, denominator and unassessable count.

## Mapping and comparability adjudication
Every rubric domain has response options, evidence requirements and aggregation rules. Two independent reviewers rate subjective fields and a third resolves disagreement.

## Uncertainty multiplicity and sensitivity analyses
Freeze weight, unassessable-source and multiplicity sensitivities. Report confidence or stability ranges with comparisons.

## Negative controls and calibration
Calibrate automated accessibility/readability checks against manual assessment and known transient-failure cases; retain immutable evidence hashes.

## Deviations amendments and human review
Version rubric changes, reratings and overrides. Signed methods, source-domain, licence and governance review is required; simulated review is advisory only.

## Operational prespecification details
The unit of analysis is one registered source family and one exact file, endpoint or release artefact assessed at a frozen date. A source family is not scored from reputation or a landing page alone. Evidence must identify the actual acquisition route, response or file format, version or effective date, refresh cadence, licensing statement, historical availability, documentation, checksum and validation outcome. Redirects and authentication gates are recorded because a nominally public page may not provide a reproducible payload.

The rubric records domain responses as `pass`, `partial`, `fail`, `not_assessed`, `not_applicable` or `blocked`, with an evidence pointer and assessment timestamp. Automated checks may establish format, checksum and accessibility observations; they cannot determine whether a licence permits reuse or whether a field is policy-complete. Two reviewers independently rate subjective domains including documentation sufficiency, historical reproducibility, licensing clarity and semantic completeness. A third reviewer resolves disagreements by domain, retaining both original ratings and the final reason.

The denominator for each domain excludes only `not_applicable` sources and reports all other states, including blocked and not assessed. A transient network failure is not converted into a source failure without a retry record. A source can be machine-readable but still fail reproducibility because versioning, licence or provenance evidence is absent. Tiers summarize observed evidence and are not a league table of source quality or institutional performance.

The sensitivity matrix includes domain-weighted versus unweighted summaries, blocked sources included versus excluded, current-only versus historical availability, strict versus permissive licence evidence, and treatment of transient retrieval failures. Source drift is evaluated against the prior digest and rubric version. Any rubric or source-universe change is an amendment requiring a new digest, regenerated artefacts and explicit reviewer acknowledgement before comparisons are interpreted.
Assessment results are versioned by source digest, rubric digest and reviewer decision, allowing a changed web page to be distinguished from a changed scoring rule.

## Pre-registration review checklist
Complete `docs/RESEARCH_PROTOCOL_REVIEW_CHECKLIST.md` for `rq_source_transparency`.
The protocol remains draft/planned until an accountable human reviewer records a
decision and all external source and licence gates are resolved.
