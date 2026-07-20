# Specification

## Overview

Make historical and live source handling academically reproducible while retaining
raw payloads only in ignored local storage. Each source version must have an
identity, retrieval evidence, checksum, licence boundary, transformation lineage,
citation metadata and publication status.

## Requirements

- Catalogue historical MBS/PBS/CMS/NHS targets and acquisition attempts.
- Bind raw local cache references to checksums without committing raw payloads.
- Describe retrieval, parsing, normalisation, validation and packaging as BPMN 2.0-compatible process steps.
- Separate source licence, derived-field permission and public-release decisions.
- Make source cutoff and transformation manifests reproducible from a clean checkout.

## Acceptance criteria

- [ ] Every target has URL, retrieval timestamp, version, checksum, citation and licence state.
- [ ] Every derived output links to source versions and transformation steps.
- [ ] Restricted descriptors and raw payloads are excluded by policy gates.
- [ ] Historical failures, missing releases and metadata-only targets remain visible.
- [ ] Rebuilds produce deterministic manifests and package metadata.

## Authoritative inputs

- `docs/SOURCE_PROVENANCE_AND_TRANSFORMATIONS.md`
- `docs/SOURCE_FIELD_LICENCE_MATRIX.md`
- `docs/LIVE_SOURCE_VALIDATION_PLAYBOOK.md`
- `data/derived/historical_sources/`
- `data/derived/source_validation/`
- `data/derived/source_contracts/`
