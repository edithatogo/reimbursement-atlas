# Development container

The repository includes a Codespaces/devcontainer definition at
`.devcontainer/devcontainer.json`. It uses the official Pixi container image pinned to
Pixi `0.72.2`, then runs `pixi install` so the project environment is resolved from the
tracked `pyproject.toml` and lock metadata.

The container exposes the Astro dashboard on port `4321` and the optional read-only API on
port `8000`. No host credentials, OSF tokens, PBS keys or raw source directories are mounted
or copied into the container. Add secrets through the Codespaces secret store only when a
specific token-gated workflow is being run, and keep live source payloads in the ignored
`data/raw_live/` path.

The container is a reproducible development surface, not evidence that live acquisition,
licence review, OSF registration or public publication gates have passed. Run the same Pixi
quality tasks used by CI before creating a pull request.
