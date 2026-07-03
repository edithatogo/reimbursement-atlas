"""Export pydantic JSON schemas for documentation and downstream validation."""

from __future__ import annotations

from pathlib import Path

from reimburse_atlas.cli import export_schema

if __name__ == "__main__":
    export_schema(Path("schema"))
