# Session v39: pinned OSF CLI local contract

## Scope

Verify the current upstream OSF CLI without reading credentials or mutating OSF.

## Evidence

- `go version`: Go 1.26.5.
- `go install github.com/edithatogo/osf-cli-go/cmd/osf@v1.0.0` produced CLI version `1.0.0`.
- `OSF_BIN=<pinned binary> pixi run osf-cli-contract` passed.
- The unrelated default `/opt/homebrew/bin/osf` reports `0.3.2` and fails the v1 contract, so it
  is not used for repository evidence.

## Boundary

The contract probe is unauthenticated and read-only. OSF discovery, upload, registration and
publication remain token-gated and fail-closed behind protocol, licence, methods and governance
review.
