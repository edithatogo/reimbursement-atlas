# ADR 0027: OSF/Hugging Face publication split

Status: accepted

## Decision
Use OSF for research protocols, detailed reports and preprints; use Hugging Face Datasets for licence-safe derived data; use Hugging Face Spaces for the public dashboard.

## Consequences
- Research questions must link to protocol and report paths.
- Raw or restricted source files are excluded from public publication targets.
- Release workflows are token-gated and dry-run safe until release-readiness gates pass.
