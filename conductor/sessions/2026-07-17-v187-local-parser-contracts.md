# Session 2026-07-17: Local Parser Contracts

## Objective

Add a fail-closed local gate for source-specific parser contracts when ignored
MBS and PBS acquisition caches are available.

## Implemented

- Added `scripts/check_local_parser_contracts.py` and the `local-parser-contracts`
  Pixi task.
- Wired the gate into the quality task and repository automation workflows.
- Added synthetic tests for skipped caches and repeated PBS item codes.
- The report emits only redacted paths, checksums, counts and boolean checks.
- No network access, source mutation, licence approval, or publication state is
  changed by this gate.

## Evidence

The local ignored caches parse successfully. The PBS contract retains duplicate
item codes because denormalised rows may represent multiple presentations or
brands; the duplicate count is reported rather than treated as a uniqueness
requirement.

## Boundary

This is parser-contract evidence only. Human licence review, source review,
clinical/research review, and public publication gates remain external and are
not marked complete by this session.
