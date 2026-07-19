# Licence Decision Matrix

This file is generated from `docs/LICENCE_DECISION_MATRIX.json`. It groups the
the current candidate artefact decisions into simple human decisions. It does
not grant approval. Exact file decisions remain checksum-bound in the generated
licence review queue.

| Group | Status | Simple decision | Recommended outcome | Historical catalogue records |
| --- | --- | --- | --- | ---: |
| Project code and documentation | `decided` | May project-owned code and documentation be distributed under Apache-2.0? | Yes, for material the project owns or is authorized to license. | 0 |
| Australian MBS | `pending_human_review` | May the specified derived MBS fields be redistributed under the applicable Commonwealth terms? | Publish only permitted derived fields with attribution; retain raw XML/TXT locally and review descriptor-only rows separately. | 0 |
| Australian PBS | `pending_human_review` | May the selected PBS schedule, item and fee fields be redistributed? | Publish reviewed derived schedule/list or payment values with PBS attribution; never publish raw responses, headers or credentials. | 1 |
| US CMS CLFS, PFS and ASP | `pending_human_review` | Which numeric CMS payment fields may be retained and published without redistributing restricted descriptors? | Permit only reviewed numeric/payment fields and permitted metadata; exclude CPT descriptors, restricted crosswalks and unsupported coverage or net-price claims. | 309 |
| NHS England genomic directories | `pending_human_review` | May transformed genomic-directory metadata be redistributed under NHS terms? | Publish only reviewed directory metadata and preserve provider attribution and version identifiers. | 6 |
| Generated research and governance artefacts | `pending_human_review` | May project-generated provenance, quality, protocol, dictionary and research-package artefacts be published? | Publish project-owned artefacts under Apache-2.0 or an explicitly recorded compatible metadata licence, while preserving embedded source restrictions. | 0 |

## Required evidence for every decision

Record the exact candidate path and SHA-256, source terms, attribution,
redistribution permission, restrictions, reviewer, review time and evidence URL.
Link the decision to the provider source, parser/transform version, excluded
fields and generated output checksum. Passing computational gates is not licence
approval, research approval or publication authorization.

## Transformation references

- `docs/SOURCE_PROVENANCE_AND_TRANSFORMATIONS.md` defines the source boundaries.
- `data/derived/processes/historical_source_transformation.bpmn` defines the fail-closed process.
- `data/derived/publication_manifest.json` binds candidate outputs to checksums.
- `data/derived/licence_review/licence_review_queue.jsonl` contains the exact review rows.
