# Casemix metadata handoff

- [Issue #880](https://github.com/edithatogo/reimbursement-atlas/issues/880)
- [Specification](spec.md)
- [Implementation plan](plan.md)
- [Metadata](metadata.json)
- [Validation evidence](validation.md)
- [Bounded operational admission receipt](operational_admission.json)
- [Receiving contract](../../../docs/CASEMIX_HANDOFF.md)

## Operational admission boundary

The operational receipt records only record counts, the exact handoff SHA-256 and
the producer commit observed during successful local metadata validation. It is
not a source-scope acceptance, a human rights decision or a publication approval.

The actual envelope and all eleven candidate payloads remain outside Git pending
acceptance of the new source scope. All eleven product candidates remain blocked;
this track adds no source content, source registry entries or public products.
