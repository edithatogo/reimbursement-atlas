# ADR 0026: Mojo-first kernels with Python 3.14 orchestration target

Status: accepted

## Decision
Use Mojo for performance-critical kernels and target Python 3.14 for orchestration, typing, packaging and CI. Maintain Python 3.13 as a temporary sandbox compatibility fallback only where 3.14 cannot be installed.

## Consequences
- Mojo kernels need parity tests against Python reference implementations.
- CI should run Python 3.14 as the release target.
- The current sandbox inability to install Python 3.14 is recorded as a runtime gate, not ignored.
