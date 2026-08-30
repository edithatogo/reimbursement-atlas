# PBS Raw Redistribution Permission

## Active decision (2026-08-31)

The accountable owner stated: "I have permission for raw pbs redistribution",
then directed the project to record and apply it without requiring them to supply
or apply terms. Raw PBS redistribution is allowed on this owner attestation.
No further per-file or checksum approval is required.

The machine-readable record is `data/licence_review/pbs_raw_permission.json`.
Its basis is `owner_attestation`, not a publisher document independently verified
by the project. No grantor identity, open licence, expiry or new terms are invented.
This decision supersedes the permission request below, which is retained as history
and must not be sent as a new permission request or treated as an owner blocker.

Scope includes raw PBS schedule PDFs, machine-readable schedule packages,
historical editions and source-identified archive variants, not MBS, CMS or other
sources. Preserve original bytes, copyright notices, attribution, disclaimers,
edition identity, retrieval provenance and checksums. Code remains Apache-2.0;
PBS payloads are not relicensed under Apache-2.0.

Generators now report `allowed_owner_attested_permission` independently from
acquisition and publication. They remain metadata-only: external raw archive
transfer requires a manifest and checksum readback before claiming publication.
Raw payloads remain outside the software Git repository. Missing December 1987
RPBS bytes and early XML/schema recovery remain source gaps, not approval gaps.
Papers and preprints remain excluded.

## Historical position before the owner attestation

The project has locally preserved 1,048 of 1,049 official historical PBS publication PDFs and all
655 discovered machine-readable historical packages. The files remain ignored and unpublished.
The PBS copyright page permits limited personal/reference reproduction and otherwise reserves
rights, so public availability on the source website is not treated as permission to redistribute
the corpus.

## Superseded permission request (not sent)

Send the following to the Department of Health, Disability and Ageing copyright or PBS publication
contact through an official channel:

> Reimbursement Atlas is an open, non-commercial research-data infrastructure project that has
> preserved historical Pharmaceutical Benefits Scheme publication PDFs and machine-readable
> schedule packages from official PBS URLs. We seek written permission to redistribute unchanged
> copies of these files through GitHub Releases, Hugging Face and Zenodo/Internet Archive for
> provenance, citation, reproducibility and long-term preservation. Each file would retain its
> original filename, source URL, retrieval date, checksum, Commonwealth attribution, copyright
> notice and PBS historical-accuracy disclaimer. The project would not apply Apache-2.0 to the PBS
> files, imply Departmental endorsement, alter the source files, or claim structured field parity
> across editions. Please confirm whether an existing open licence applies, or grant permission
> covering public copying, communication, preservation and redistribution of the unchanged corpus.

The request should also ask the Department to repair or supply the official December 1987 RPBS PDF
currently listed at
`https://www.pbs.gov.au/publication/schedule/1951-2002/1987-12-01-RPBS-Schedule.PDF?variant=3`,
which returns HTTP 403.

## Missing early structured releases

The [2026-08-30 revalidation](HISTORICAL_SOURCE_BOUNDARIES.md) narrows the
machine-readable gap: official legacy documentation describes G2B XML from
December 2006, but discovered downloads start in April 2007. Add this to the
same publisher request rather than requesting another owner approval:

> Please also provide the December 2006 and January-March 2007 G2B XML schedule
> releases, if retained, together with the schema/DTD, XSL stylesheets, version
> identifiers and amendment history applicable to each release. The legacy
> schema-archive link currently returns 404. Please distinguish release-specific
> schema versions from later retrospective descriptions, and confirm whether
> any releases or accompanying schemas were never publicly distributed or are
> no longer retained. A catalogue or preservation reference would also help.

This remains an unsent request. Do not infer permission or source availability
from preparing it. Publication destinations and permitted acts must still be
confirmed by the responding authority.

## Superseded receipt proposal (not required from the owner)

Before raw publication, record:

- the official responding authority and contact channel;
- the exact scope, destinations and permitted acts;
- attribution and disclaimer wording;
- any exclusions, expiry, revocation or downstream-use conditions;
- a checksum or immutable reference to the permission record;
- a source-specific licence identifier distinct from Apache-2.0.

The owner attestation above replaces this proposed receipt requirement. The project
does not require the owner to supply a document or record terms before allowing PBS
raw redistribution. The missing-source recovery request remains useful and unsent.
