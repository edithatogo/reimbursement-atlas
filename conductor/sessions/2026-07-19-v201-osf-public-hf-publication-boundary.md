# v201 OSF visibility and Hugging Face publication boundary

Date: 2026-07-19

## Completed

- Authenticated OSF project `q8cnx` was changed from private to public through the
  OSF project visibility control.
- Public OSF API readback confirmed `public: true`.
- OSF remains empty: zero files, no registration and no papers were uploaded.
- Hugging Face dataset `edithatogo/reimbursement-atlas` was read back as
  `license: other`, which remains the correct source-specific data boundary.
- The Hugging Face Space was read back as `license: mit`, `sdk: gradio`, with only
  `.gitattributes`, `README.md` and the Gradio `app.py` scaffold present.
- The local Hugging Face bundle validator passed.

## Deferred deliberately

The Space metadata was not partially changed to `license: apache-2.0` and
`sdk: static`. Those fields describe the static dashboard deployment, and changing
them without deploying the validated bundle would create an inconsistent public
destination. Full Space reconciliation and dataset publication remain behind the
existing licence, research, evidence, policy and explicit publication gates.
Papers, OSF registration and research publication were not submitted.

## Evidence

- OSF API: `https://api.osf.io/v2/nodes/q8cnx/`, read back with `public: true`.
- Hugging Face readback: `hf spaces card edithatogo/reimbursement-atlas` and
  authenticated Hub API inspection.
- `PYTHONPATH=src uv run --all-extras python scripts/check_huggingface_bundle.py`
  passed.
- `PYTHONPATH=src uv run --all-extras python scripts/check_huggingface_publication_gates.py`
  failed closed on research/evidence/policy readiness, protocol OSF readiness and
  source licence review. No remote Hugging Face mutation was attempted.
