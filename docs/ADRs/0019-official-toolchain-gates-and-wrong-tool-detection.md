# ADR 0019: Official toolchain gates and wrong-tool detection

## Status

Accepted.

## Context

Some optional tools are distributed through non-PyPI channels or have same-named packages that are not
the intended executable. Pixi is the key example: the official Prefix.dev package manager is a single
executable distributed through official installers and GitHub release assets, while a PyPI package named
`pixi` can place a different command on PATH.

## Decision

External quality gates must distinguish:

- `passed`;
- `failed`;
- `blocked_network`;
- `missing_tool`;
- `timed_out`;
- `wrong_tool`.

Mojo is probed through `uv tool run --from mojo-compiler mojo --version`. Pixi must be treated as official
only when the actual Prefix.dev executable is installed.

## Consequences

The repo can honestly record that Mojo is available while Pixi remains blocked by network/DNS or absent.
A same-named wrong executable will not silently satisfy CI or handoff checks.
