# Specification

- Run the complete coverage suite with four locked `pytest-xdist` workers.
- Cancel obsolete runs for heavy pull-request workflows.
- Keep the required four-project browser matrix independent from the deployment smoke gate.
- Do not lower coverage, security, deterministic-generation, or evidence thresholds.
