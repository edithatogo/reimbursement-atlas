# Casemix receiving contract

The Casemix intake validates metadata and immutable references. Successful intake
records `admitted_metadata_only`; it does not change source registries, confirm
provider authority, authorize source redistribution, or promote an artifact.

## Interface

```bash
PYTHONPATH=src python scripts/validate_casemix_handoff.py handoff.json --output admission.json
```

The CLI exits zero for a valid envelope, even when all candidate promotions remain
blocked. Invalid input exits nonzero and emits a generic rejection without echoing
possibly restricted content. The optional admission file contains counts, source
release/commit identity and the SHA-256 of the exact bytes validated. Input is read
once for validation and hashing. No source payload is fetched or transferred.

The Python interface is `CasemixHandoff.model_validate(payload)`,
`load_casemix_handoff(path)` or `admit_casemix_handoff(path)` in
`reimburse_atlas.casemix_handoff`.

## Envelope

Unknown fields and duplicate JSON keys are rejected, including within nested records.

| Field | Contract |
| --- | --- |
| `schema_version` | Exactly `casemix-atlas-handoff-v1` |
| `source_release_id` | Lowercase metadata token using letters, digits, `_`, `.`, `:`, `-` |
| `source_commit` | Full 40-character lowercase hexadecimal Git commit |
| `generated_at` | ISO date/time |
| `sources` | Nonempty list of `{source_id, provider_urls}`; each URL list is nonempty |
| `source_index` | Nonempty list of existing `BronzeSourceIndexRecord` rows |
| `acquisition_receipts` | Existing `BronzeAcquisitionReceipt` rows; default empty |
| `evidence` | Existing `BronzeEvidenceRecord` rows; default empty |
| `artifacts` | Existing `MedallionArtifactRecord` candidates/blocked rows; default empty |
| `promotion_decisions` | Existing `MedallionPromotionDecision` blocked/rejected rows; default empty |

The existing medallion model definitions remain authoritative for required nested
fields and enums. `source_id` and `source_version_id` use their existing lowercase
underscore identifier contract. Event, acquisition, evidence, artifact, contract,
decision, gate and reason identifiers are lowercase metadata tokens.

Every nested `notes` field must contain exactly:

> Metadata-only handoff; no source payload included.

Every promotion decision `scope_notes` field must contain exactly:

> Metadata intake only; no public promotion authorized.

This fixed wording closes free-text channels for native descriptors, excerpts or
local paths. Native code lists, labels, mappings, source payload fields, embedded
human decisions and arbitrary extensions are outside this envelope.

## Bronze relationships

The `sources` set must match the B0 source IDs. Each authoritative B0 locator and
B1 provider locator must appear in its source's `provider_urls`. Public HTTP(S)
URLs with credentials, secret query parameters, local hostnames or private IP
addresses are rejected. URL membership verifies internal consistency; the adapter
does not independently establish publisher authority or a licence grant.

B0 source/version pairs, B1 event and acquisition IDs, and B2 evidence/acquisition
IDs must be unique. B1 must refer to a B0 source/version and preserve its rights
state. An acquired B1 event must have payload SHA-256, byte size and
`evidence_disposition=rights_constrained_reference`; retained-byte transfer is
rejected. B0 `acquisition_status=acquired` must be supported by an acquired B1 row
in the same envelope. A catalogue-only handoff remains unacquired.

Every B2 row must use:

- `evidence_kind=rights_constrained_reference`;
- `immutable_locator=urn:sha256:<payload_sha256>`;
- an acquired B1 `acquisition_id` with exactly matching source, source version,
  payload hash, size, provider URL and rights state.

An `admission_state` carried by B1 is source evidence, not a publication decision.
Quarantined acquired references can be represented without releasing their bytes.

## Candidate lineage and promotion

Every candidate artifact has one blocked/rejected promotion decision, matched by
`subject_id=artifact_id`. Candidate input IDs and checksums are paired in order;
length mismatches, duplicate inputs, missing predecessors and hash mismatches fail.
Silver inputs resolve to B1 acquired references or B2 evidence, Gold inputs resolve
to Silver artifacts, and Platinum inputs resolve to Gold artifacts. A decision's
source layer must match its inputs; its target layer and input checksums must match
the candidate. Artifact paths must remain repository-relative and cannot reference
machine paths, raw/private caches, traversal or encoded-path forms.

This initial adapter accepts `candidate`/`blocked` artifacts and
`blocked`/`rejected` decisions only. A claimed `approved` decision or
`approved_within_scope` artifact is rejected even if all supplied gate IDs claim to
have passed. The envelope has no place for a self-attested human decision. An
actual reviewed promotion must go through the existing receiving repository's
checksum-bound licence queue/ledger and other required scientific/product gates.
The adapter does not override an existing decision; it does not process promotions.

## Authority and standing scope

`docs/APPROVAL_POLICY.md` and `data/licence_review/README.md` continue to govern
source-derived publication. The existing 19-path standing metadata scope does not
cover this new source-product scope. No whitelist, source licence or human decision
is created by this code or by a passing validation receipt. A grouped material-scope
review can be prepared separately against concrete candidate checksums.

The adapter validates the envelope's references, not the actual bytes of absent
candidate artifacts or immutable source objects. Hash and byte-size equality here
means the claims agree across records; independent retrieval/fixity verification
remains the upstream evidence obligation. This distinction is explicit in the
admission receipt.
