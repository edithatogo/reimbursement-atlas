"""Attempt optional non-core toolchain checks without hiding environmental blockers."""

from __future__ import annotations

from reimburse_atlas.registry import project_root
from reimburse_atlas.toolchain import run_external_quality_gate, write_external_quality_gate_records


def main() -> None:
    """Run optional install/probe commands and record their outcomes."""
    root = project_root()
    records = [
        run_external_quality_gate(
            gate_id="mojo_uv_tool_probe",
            command=("uv", "tool", "run", "--from", "mojo-compiler", "mojo", "--version"),
            cwd=root,
            timeout_seconds=240,
        ),
        run_external_quality_gate(
            gate_id="official_pixi_on_path",
            command=("bash", "-lc", "pixi --version"),
            cwd=root,
            timeout_seconds=30,
        ),
        run_external_quality_gate(
            gate_id="official_pixi_installer_reachable",
            command=("bash", "-lc", "curl -I -fsSL https://pixi.sh/install.sh >/dev/null"),
            cwd=root,
            timeout_seconds=60,
        ),
    ]
    json_path, csv_path = write_external_quality_gate_records(
        records,
        json_path=root / "data" / "derived" / "optional_toolchain_installs.json",
        csv_path=root / "data" / "derived" / "optional_toolchain_installs.csv",
    )
    print(f"Wrote {json_path} and {csv_path}")
    for record in records:
        print(f"{record.id}: {record.outcome}")


if __name__ == "__main__":
    main()
