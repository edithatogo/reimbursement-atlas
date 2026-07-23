# Specification

## Overview

Complete the OSF registration created from the public Reimbursement Atlas project.
The record must describe the research questions, protocol scope, source
cutoff, provenance, transformations, licensing boundaries, analysis outputs and
publication exclusions before any registration submission.

## Requirements

- Complete OSF title, description, contributor, licence, subject and tag metadata.
- Link the protocol packet, data dictionary, manifests, RO-Crate and transformation documentation.
- Freeze the source cutoff and manifest digest before registration submission.
- Record the OSF draft and eventual registration identifiers without storing tokens.
- Keep paper, preprint and manuscript publication out of scope.

## Acceptance criteria

- [x] OSF registration metadata is complete and internally consistent.
- [x] Protocol sections identify all five research questions and their outputs.
- [x] Source cutoff, manifest digest and licence boundaries are frozen and verified.
- [x] OSF validation passes and submission has explicit accountable approval.
- [ ] Repository outputs record the OSF draft/registration state and URL.

## External gates

- OSF account access and draft editing.
- Accountable reviewer approval of protocol contents.
- Explicit approval before submitting or making the registration public.

## Out of scope

- Paper, preprint or manuscript submission.
- Public release of raw source payloads or restricted descriptors.

## Authoritative inputs

- `data/derived/osf/registration_review_packet.md`
- `data/derived/osf/registration_freeze.json`
- `docs/RESEARCH_PROTOCOL_REVIEW_CHECKLIST.md`
- `docs/SOURCE_PROVENANCE_AND_TRANSFORMATIONS.md`
