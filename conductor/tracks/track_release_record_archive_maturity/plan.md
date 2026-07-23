# Implementation plan

- [x] REL-01: Reconcile README, CITATION.cff, dashboard status and package identity. (Issue #487, subissue #499)
- [x] REL-01A: Add a structured human dashboard visual/accessibility/provenance review record contract. (Issue #487, subissue #501)
- [x] REL-02: Complete scoped visual/accessibility and provenance review evidence. The accountable
  owner approved the refreshed 64-test, 44-screenshot packet for the declared browser, route,
  automated accessibility and provenance scope. Manual VoiceOver and universal WCAG conformance
  remain explicitly outside scope. (Subissue #501, issue #493)
- [x] REL-02A: Bind accountable approval to both dashboard implementation and generated displayed
  data, recompute all readiness and blocker provenance assertions, and fail automation when either
  packet becomes stale. The post-transition browser run
  [30018170812](https://github.com/edithatogo/reimbursement-atlas/actions/runs/30018170812)
  passed 64/64 tests and produced the stable 44-screenshot packet. Any later OSF/readiness state
  transition requires a fresh bounded packet.
- [x] REL-03: Validate OSF/HF/GitHub identity, metadata and licence-boundary parity. (Subissue #503)
- [~] REL-04: Generate reproducible archive, wheel, sdist, SBOM, provenance, release manifest and
  machine-readable attestation receipts. The v2 inventory contract and exact-tag release download
  and receipt-verification path are implemented; signed final-release assets remain pending until
  upstream OSF registration evidence passes and the tag is published. (Subissue #505)
- [ ] REL-05: Run final release-readiness and publication boundary review; do not publish papers. (Subissue #507)
- [x] REL-06: Generate a deterministic Zenodo/DataCite draft manifest for software plus permitted
  derived data, with Apache-2.0 applied only to code and source-specific rights retained for data.
  (Issue #532)
- [x] REL-07: Validate creators/ORCIDs, concept/version relationships, OSF/GitHub/Hugging Face
  related identifiers, funding, temporal/spatial coverage and SHA-256 file inventory in sandbox
  and production-compatible payloads. (Issue #532)
- [x] REL-08: Add a dry-run-only preflight workflow; extend it to a token-gated deposition workflow
  that can create a draft,
  reserve a DOI after the file set is frozen, verify metadata parity, and publish only with an
  explicit environment approval. Exclude papers and preprints. (Issue #532)
- [x] REL-08A: Require the complete archive-publication gate before draft creation, DOI reservation
  or publication; retain a non-mutating plan mode, reject legacy or drifted inventories, and verify
  remote filename, size and checksum parity. (Issue #532)
- [x] REL-08B: Make tagged GitHub releases publish machine-readable attestation verification
  receipts, and require Zenodo transitions to download and re-verify the exact tag's complete
  release assets before credentials or remote mutation are used. (Issue #532)
- [ ] REL-09: Publish the versioned Zenodo record and verify DataCite DOI resolution only after
  mapping, dashboard, OSF registration, licence and release gates independently pass. (Issue #532)
- [x] REL-10: Add a daily read-only OSF registration monitor. Emit a redacted receipt and canonical
  snapshot when active/public, and maintain one bounded status comment on issue #532 without
  re-uploading files, modifying the registration or publishing papers. (Issue #532)
- [ ] REL-11: After the OSF registration is active and public, regenerate readiness and dashboard
  evidence, create the exact signed/attested GitHub release, and verify every release asset before
  any Zenodo credential is used. (Issue #532)
- [ ] REL-12: Deposit the verified release assets to one Zenodo concept record, verify remote
  filename/size/SHA-256 parity and DataCite metadata/DOI resolution, then record the concept DOI in
  the subsequent repository release. Papers and preprints remain excluded. (Issue #532)

## Validation

- `pixi run citation-validate`
- `pixi run dashboard-quality`
- `pixi run dashboard-routes`
- `pixi run release-readiness`
- `pixi run final-handoff`
- `pixi run public-data-policy`
