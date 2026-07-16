# Session v93: OSF CLI v1 contract refresh

## Objective

Verify whether an upstream `osf-cli-go` release newer than the repository pin exists and
refresh the local contract evidence without performing OSF mutations.

## Evidence

- Upstream latest release: `v1.0.0`.
- Installed `github.com/edithatogo/osf-cli-go/cmd/osf@v1.0.0` into an ignored temporary bin.
- `pixi run osf-cli-contract` passed: `OSF CLI contract passed: osf 1.0.0`.
- No token values were read or logged; no OSF node, component, file or registration changed.

## Boundary

This verifies the pinned CLI toolchain only. Protocol approval, source licence decisions,
evidence readiness, human research review and OSF publication authorization remain separate
fail-closed gates.
