---
license: other
pretty_name: Reimbursement Atlas Derived Medallion Dataset
configs:
  - config_name: catalogue_b0
    data_files: data/medallion/catalogue_b0/data.jsonl
  - config_name: acquisition_b1
    data_files: data/medallion/acquisition_b1/data.jsonl
  - config_name: evidence_b2
    data_files: data/medallion/evidence_b2/data.jsonl
  - config_name: silver
    data_files: data/medallion/silver/data.jsonl
  - config_name: gold
    data_files: data/medallion/gold/data.jsonl
  - config_name: platinum
    data_files: data/medallion/platinum/data.jsonl
  - config_name: lineage
    data_files: data/medallion/lineage/data.jsonl
  - config_name: promotion_decisions
    data_files: data/medallion/promotion_decisions/data.jsonl
tags:
  - health-economics
  - reimbursement
  - public-policy
  - cms
  - mbs
  - pbs
---

# Reimbursement Atlas Derived Medallion Dataset

This dataset publishes checksum-bound, licence-safe derived metadata from the
Reimbursement Atlas medallion architecture. Configurations keep catalogue B0,
acquisition B1, immutable evidence B2, source-faithful Silver, reviewed Gold,
explicitly promoted Platinum, field lineage and promotion decisions separate.

Presence in `catalogue_b0` does not prove acquisition. Presence in
`acquisition_b1` does not prove immutable evidence admission. A downstream
record does not imply that an upstream gate passed unless the checksum-bound
promotion decision says so.

The repository code and documentation are Apache-2.0. Dataset rows retain
source-specific licensing and attribution requirements; this card does not
grant Apache-2.0 rights to underlying MBS, PBS, CMS, ontology, or other
third-party data. Publish only manifest rows with confirmed redistribution
permission.

No configuration contains ignored raw source payloads, restricted descriptors,
credentials or local absolute paths. Gold and Platinum records retain their
bounded permitted scope and prohibited claims. Hugging Face is a distribution
destination, not the acquisition origin or evidentiary source of truth.
