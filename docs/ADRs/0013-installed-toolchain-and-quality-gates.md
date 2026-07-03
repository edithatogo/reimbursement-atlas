# ADR 0013: Installed Python toolchain and strict quality gates

## Status

Accepted.

## Context

Earlier repository passes scaffolded Ruff, basedpyright, Hypothesis, mutmut, Scalene, Bandit, pip-audit and uv build tasks. v6 installed the core Python toolchain locally and used it to harden the library.

## Decision

Use `uv` as the fastest local bootstrap path and keep Pixi as the primary multi-environment workflow. The Python core must pass:

- Ruff lint;
- Ruff format check;
- basedpyright strict type check;
- pytest coverage gate at >90%;
- Bandit source scan;
- compileall;
- uv source and wheel build.

## Consequences

- The repository now has executable quality gates rather than aspirational CI hooks.
- The Ruff profile remains strict but has pragmatic ignores for scripts, tests, preview-rule conflicts and scaffold-heavy early design files.
- Coverage is enforced over the core library while optional interface shells remain smoke-tested and explicitly excluded from the denominator.
