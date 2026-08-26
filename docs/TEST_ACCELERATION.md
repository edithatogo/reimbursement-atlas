# Test acceleration

The release signal remains `pixi run coverage` plus the complete hosted quality, security, browser, mutation, rights, deterministic-generation and readiness gates. Selective profiles are local feedback only.

| Profile | Command | Boundary |
|---|---|---|
| Fast | `pixi run test-fast` | Excludes only registered `slow` tests; never release evidence. |
| Changed code | `pixi run -e test-acceleration test-changed` | Serial pytest-testmon; delete `.testmondata*` after dependency or inventory changes. |
| Benchmark | `pixi run -e test-acceleration test-benchmark` | Comparative evidence only; no brittle wall-clock assertions. |
| Coverage core trial | `pixi run coverage-sysmon` | Optional measurement; default coverage remains authoritative if plugins, branch coverage or concurrency are incompatible. |
| Mutation | `pixi run -e mutation mutation` | Existing bounded fail-closed/core-logic target set; ordinary tests remain the promotion gate. |

HTTP tests should continue using in-process transports. VCR.py is not adopted because recorded cassettes can retain credentials, restricted payloads, or unstable public responses. If a future replay-safe public endpoint cannot be tested in process, any cassette must be redacted and rights-reviewed before tracking.

Tests should use immutable fixtures and in-memory databases unless path, persistence, migration, recovery, or replay semantics are the behavior under test. Prefer explicit injectable clocks; Freezegun is not adopted because global time mutation can obscure asyncio and concurrency behavior.

`tests/benchmark` is excluded from ordinary discovery and currently contains one deterministic canonical-checksum microbenchmark. Benchmark reports are transient comparative diagnostics, not pass/fail performance claims.
