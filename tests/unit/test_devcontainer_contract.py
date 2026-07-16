"""Contract tests for the reproducible development container."""

from __future__ import annotations

import json
from pathlib import Path


def test_devcontainer_uses_pinned_official_pixi_image(repo_root: Path) -> None:
    """Codespaces must use a pinned Pixi image and the project environment."""
    config = json.loads((repo_root / ".devcontainer" / "devcontainer.json").read_text())

    assert config["image"] == "ghcr.io/prefix-dev/pixi:0.72.2"
    assert config["postCreateCommand"] == "pixi install"
    assert config["forwardPorts"] == [4321, 8000]
    assert config["remoteUser"] == "root"
