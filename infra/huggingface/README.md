# Hugging Face deployment

## Dataset

The dataset is an explicit medallion distribution with separate
`catalogue_b0`, `acquisition_b1`, `evidence_b2`, `silver`, `gold`, `platinum`,
`lineage`, and `promotion_decisions` configurations. The generated federation
manifest links those configurations to the GitHub control plane and immutable
release record.

It must not contain restricted ontology dumps, proprietary descriptors, raw scraped content with unclear rights, or confidential prices.

The publisher stages only allow-listed generated records. It must not contain
restricted ontology dumps, proprietary descriptors, raw scraped content with
unclear rights, confidential prices, credentials or local paths.

## Space

The dashboard is deployed as a static Astro Platinum product. Its displayed
readiness and provenance values come from generated repository evidence.
