# Specification

- Register `slow` and provide an opt-in fast profile that excludes it.
- Provide an opt-in serial pytest-testmon profile; never use its local database as release evidence.
- Provide a bounded pytest-benchmark profile without wall-clock assertions.
- Retain the existing bounded mutation runner and complete full suite in authoritative CI.
- Permit `coverage.py`'s `sysmon` core only as a measured optional profile.
- Do not record HTTP credentials, restricted payloads, or raw source bytes.
- Prefer in-process transports, immutable fixtures, in-memory databases, and injectable clocks.
