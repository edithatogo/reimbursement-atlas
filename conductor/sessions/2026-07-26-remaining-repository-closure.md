# Remaining repository-owned closure

Date: 2026-07-26

## Scope

- Reconciled merged `main` after PR #588.
- Resolved the legacy MBS XML adapter decision without changing live-source,
  licence, evidence or publication gates.
- Dispatched read-only OSF registration, Zenodo, TypeScript compatibility and
  GitHub security monitors against merged `main`.

## MBS XML decision

`MbsXmlFixtureAdapter` remains synthetic, fixture-only compatibility
infrastructure. Its output is bound to `synthetic_fixture` provenance and cannot
be promoted as reviewed evidence. The reviewed-source `parse_mbs_xml` path is
separate and remains the current-release XML route. Historical/full-map MBS
coverage continues to use checksum-bound TXT pairs.

This decision does not approve raw payload publication and does not alter the
source-specific licence ledger.

## Remaining boundaries

- Four research claim packages remain partial pending their specified reviewed
  counterpart sources.
- Read-only run `30181343265` confirmed OSF registration `gqk4z` is active,
  public and immutable. The submitted approval freeze is now reconstructed from
  `data/osf_review/registration_decision.json`; it is never inferred from the
  latest mutable draft.
- The current protocol, manifest and source cutoff drift from the immutable
  submitted freeze. This is reported as fingerprint drift rather than a pending
  registration or permission to overwrite the record.
- Zenodo/DataCite deposition and the exact signed release remain downstream of
  the independent evidence and registration gates.
- Papers and preprints remain excluded.
