# Licence review queue

This generated queue is a review aid, not an approval record. Its row-level
`review_status` field remains neutral when regenerated; effective current-checksum
decisions are reported in the summary and batch files. Only rows with an effective
`pending` or `blocked` state require accountable action under
`docs/APPROVAL_POLICY.md` and `docs/REVIEW_DECISIONS.md`.

The checksums bind review to the exact candidate artefacts. Do not edit this generated
queue to simulate approval, and do not publish it as evidence that review occurred.
