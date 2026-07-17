# Reimbursement Atlas: methods and evidence architecture

**Status:** methods scaffold, not submitted and not publication-ready

## Abstract

Reimbursement Atlas is a licence-aware, reproducible software and data
architecture for comparing public reimbursement schedules, coverage decisions,
restrictions and price concepts across jurisdictions. This manuscript records
the planned methods before any policy-facing result is promoted. It does not
present clinical, economic or equity conclusions. Those conclusions require
reviewed source bundles, source-specific licence decisions, qualified domain
review, mapping adjudication and an approved research protocol.

## Scope and research questions

The project represents reimbursement records as evidence-bearing observations,
not as interchangeable prices. The initial research questions cover genomics
and pathology coverage-price-restriction linkage, cognitive and procedural
relativities, medicine price opacity, local versus national coverage discretion,
and source transparency. Their protocols and report templates are the source of
truth in [`protocols/`](../protocols/) and [`reports/`](../reports/).

## Evidence and licensing boundary

Raw live source files remain local and ignored. Public derived artefacts may be
committed only after source-content validation, source-contract validation,
licence review and the public-data policy gate. A source registry entry is not
evidence that redistribution is permitted. Restricted descriptors, credentials,
confidential prices and local absolute paths are excluded from this manuscript
and from release archives.

## Unit of analysis and estimands

The primary unit is an adjudicated test-indication or service-context pair
within a jurisdiction, source version and effective-date window. Coverage
status, restriction class and public schedule amount are separate variables.
The descriptive estimands are the proportion of assessable pairs with an
explicit in-force coverage decision, the proportion with an observable public
schedule amount, and the distribution of restriction classes. Undefined
denominators remain null; absence of a public record is not treated as a denial.
No cross-currency pooled price is permitted.

## Acquisition and transformation

Acquisition is performed through the hardened source-download plan. Each
reviewed source snapshot records its retrieval time, effective period, checksum,
byte count, source URL and licence decision. Registered parsers preserve source
wording and hierarchy before producing typed, derived rows. Validation outputs,
data dictionaries, source-drift reports and research linkages are regenerated
from the same seed records as the dashboard and handoff package.

## Mapping and adjudication

Automated lexical, code-system and context matching produces candidate mappings
only. Two qualified reviewers independently assess purpose, population,
specimen, method, panel scope and temporal overlap without price-derived
ranking. A third reviewer resolves disagreements. Reviewer qualification,
conflicts, disagreement fields and adjudication rationale are recorded. The
mapping workbench must retain one-to-many and many-to-one relationships rather
than forcing false equivalence.

## Analysis and sensitivity plan

Analysis is stratified by jurisdiction, source version, test or service family,
coverage concept and restriction class before synthesis. Prespecified
sensitivities vary strict versus broad purpose matching, panel-to-single-test
links, overlapping effective windows, local implementation notes, bundled versus
unbundled payment concepts and exclusion of low-machine-readability sources.
Parser and mapping performance are calibrated against hand-reviewed records.

## Reproducibility and publication gates

The release candidate must pass the source-content and source-contract gates,
data-quality and evidence-readiness checks, public-data policy, data-package
metadata validation, dashboard build, deterministic regeneration, and final
handoff generation. OSF registration, Hugging Face publication, Zenodo DOI
creation and any policy claim remain fail-closed until accountable human
methods, domain, governance and licence review is recorded. This scaffold is
therefore suitable for review and later preregistration preparation, not for
submission or publication by itself.

## Planned materials

- Protocols and question-specific reports in [`protocols/`](../protocols/) and [`reports/`](../reports/).
- Typed source, mapping, evidence-readiness and publication-manifest records.
- Derived-only Frictionless and RO-Crate metadata with checksums and provenance.
- A static dashboard that presents readiness and caveats alongside metrics.
- A versioned release bundle only after all applicable external gates pass.

## Review record

Reviewers should use [`docs/RESEARCH_PROTOCOL_REVIEW_CHECKLIST.md`](../docs/RESEARCH_PROTOCOL_REVIEW_CHECKLIST.md)
and record decisions in Conductor and the linked generated GitHub issue. No
simulated or automated review substitutes for accountable human approval.
