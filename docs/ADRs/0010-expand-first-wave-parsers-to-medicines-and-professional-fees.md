# ADR 0010: Expand first-wave parsers to medicines and professional fees

Date: 2026-07-03

## Status

Accepted.

## Context

The original executable slice covered MBS, CMS CLFS and the NHS genomic test directory. That is strong for genomics/pathology, but too narrow for the broader CMS versus MBS/PBS comparison.

## Decision

Add fixture-backed parser contracts for:

- PBS API/CSV-style item rows;
- CMS ASP payment-limit files;
- CMS PFS fee/RVU-derived rows.

## Consequences

The vertical slice now demonstrates services, laboratory/genomics, medicines, professional fees and coverage-directory records. It remains synthetic but better represents the planned policy architecture.
