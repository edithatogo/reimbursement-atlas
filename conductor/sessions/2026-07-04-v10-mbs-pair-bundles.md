# Session: v10 MBS pair bundles and redacted reviewed-source metadata

## Summary

Added a dedicated derived-only bundle workflow for the two-file MBS TXT source pattern and hardened reviewed-source bundles so local raw paths are redacted from bundle snapshot outputs.

## Changes

- Added `build_mbs_txt_pair_bundle` and `MbsTxtPairBundleResult`.
- Added CLI command `reviewed-mbs-txt-pair-bundle`.
- Updated manual acquisition pack parse guidance to prefer the MBS pair bundle command.
- Redacted `local_path` in reviewed-source bundle snapshot exports.
- Added pair-bundle tests and path-redaction tests.
- Added documentation and ADR 0021.

## Validation intent

Use synthetic MBS TXT fixtures to prove that the pair workflow snapshots both files, joins descriptors, emits derived schedule rows, reports descriptor-only rows, and does not copy raw source files into the bundle.

## Next step

Run the command against manually downloaded July 2026 MBS TXT files in `data/raw_live/au_mbs/`, then inspect the validation report and derived row counts before any public publication decision.
