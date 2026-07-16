# Mutation testing

Mutation testing is configured through `mutmut`, but it is intentionally a nightly or manually triggered gate rather than a fast pull-request blocker.

## Current configuration

`pyproject.toml` points mutmut at `src/reimburse_atlas` and uses the unit-test subset for mutation runs. Pytest now has `pythonpath = ["src"]`, which makes mutmut import mutated source code rather than an installed wheel/site-package copy.

## Local command

```bash
pixi run mutation
```

The repository-owned runner uses an 80-minute default budget, starts mutmut in
its own process group, and returns exit code `124` after terminating the group.
Pass `--timeout-seconds` to the script for a shorter local smoke run. The
workflow also has a job-level timeout and concurrency cancellation, so a
scheduled run cannot occupy a runner indefinitely.

The v7 validation attempt confirmed that mutmut can now:

- generate mutants;
- collect coverage/statistics;
- run clean tests;
- run the forced-fail test;
- start evaluating mutants.

The complete run is large for this repository state: the first configured pass generated 3,673 mutants across 45 files. It was therefore left as a nightly gate instead of forcing a full completion inside the current interactive runtime.

## Interpreting early results

Early v7 mutation output showed both killed and surviving mutants, which is useful: the test suite is wired to the mutation engine, and the surviving mutants should become a prioritised test-hardening backlog.

## Recommended next hardening

1. Create a narrower `mutation-smoke` profile for high-value modules such as parsers, source-quality scoring, publication manifests and local-source bundling.
2. Export mutmut CI/CD stats from the nightly job.
3. Convert surviving mutants into generated GitHub issues once the first real-source validation bundle lands.
4. Keep `mutmut run` scheduled weekly until parser contracts stabilise; then consider gating on a minimum mutation score.
