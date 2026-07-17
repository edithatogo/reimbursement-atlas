# Handoff package export

The handoff package is produced outside the repository so raw local cache files and
machine-specific paths cannot be added to the public repository by accident. The exporter
creates four subjects from the current `HEAD`:

- a complete git bundle;
- a tracked-only source archive;
- a redacted manifest containing the commit, checksums and readiness booleans; and
- a SHA-256 checksum file.

Run it from a clean checkout after the final merge:

```bash
PYTHONPATH=src python scripts/export_handoff_bundle.py \
  --output-dir /Volumes/PortableSSD/GitHub \
  --prefix reimbursement-atlas-conductor-v59
```

The command verifies the bundle before writing the manifest. The manifest contains only
output basenames, never the caller's absolute path. Verify the checksum file from its output
directory before delivering the package:

```bash
cd /Volumes/PortableSSD/GitHub
shasum -a 256 -c reimbursement-atlas-conductor-v59.sha256
git -C /path/to/reimbursement-atlas-conductor bundle verify \
  /Volumes/PortableSSD/GitHub/reimbursement-atlas-conductor-v59.git.bundle
```

This package is a software and derived-artefact handoff, not evidence of licence approval,
human research review, OSF registration, Hugging Face publication or policy-claim readiness.
