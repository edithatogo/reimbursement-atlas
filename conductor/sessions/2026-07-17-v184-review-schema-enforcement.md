# v184 Review schema enforcement

## Scope

Added an approval-neutral JSON Schema validator for the optional human licence and mapping
decision files. The `review-schemas` Pixi task now runs in QA and deterministic CI, while empty
decision files remain valid and fail closed.

## Evidence

- `pixi run review-schemas` passed with `licence_review=0, mapping_review=0`.
- Unit tests cover empty review files and rejection of out-of-range mapping confidence.
- The generated backlog issue is `.github/generated-issues/179-enforce-human-mapping-and-licence-decision-schemas-in-ci.md`.

## Boundary

No human decisions were created. Mapping, licence, evidence, research and publication gates
remain unchanged and require the appropriate human or external approval.
