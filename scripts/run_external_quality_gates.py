"""Run external toolchain gates and record pass/fail/blocked status."""

from __future__ import annotations

from reimburse_atlas.registry import project_root
from reimburse_atlas.toolchain import run_external_quality_gate, write_external_quality_gate_records


def main() -> None:
    """Run network/toolchain-sensitive gates with honest classification."""
    root = project_root()
    records = [
        run_external_quality_gate(
            gate_id="pip_audit_strict",
            command=(
                "bash",
                "-lc",
                (
                    "tmpdir=$(mktemp -d) && "
                    "reqfile=$(mktemp) && "
                    "uv run --all-extras python -m pip freeze "
                    '| grep -vE "^(-e )?git\\+https://github.com/edithatogo/reimbursement-atlas\\.git|'
                    '^(reimbursement-atlas|reimbursement_atlas)(==| @ )|git\\+file:" '
                    '| grep -v " @ file://" '
                    '> "$reqfile" && '
                    'uv run --all-extras python -m venv "$tmpdir" && '
                    '"$tmpdir/bin/python" -m pip install --upgrade pip '
                    "> /dev/null && "
                    '"$tmpdir/bin/python" -m pip install pip-audit -q && '
                    '"$tmpdir/bin/python" -m pip install -r "$reqfile" '
                    "> /dev/null && "
                    '"$tmpdir/bin/pip-audit" --strict -r "$reqfile"; '
                    'status=$?; rm -rf "$tmpdir" "$reqfile"; exit $status'
                ),
            ),
            cwd=root,
            timeout_seconds=180,
        ),
        run_external_quality_gate(
            gate_id="npm_audit_dashboard",
            command=("npm", "audit", "--omit=dev", "--audit-level=moderate"),
            cwd=root / "apps" / "dashboard",
            timeout_seconds=120,
        ),
        run_external_quality_gate(
            gate_id="pixi_available",
            command=("bash", "-lc", "pixi --version"),
            cwd=root,
            timeout_seconds=30,
        ),
        run_external_quality_gate(
            gate_id="pixi_installer_reachable",
            command=("bash", "-lc", "curl -I -fsSL https://pixi.sh/install.sh >/dev/null"),
            cwd=root,
            timeout_seconds=60,
        ),
        run_external_quality_gate(
            gate_id="zizmor_workflow_security",
            command=("uv", "tool", "run", "zizmor", "--min-severity", "medium", ".github"),
            cwd=root,
            timeout_seconds=180,
        ),
        run_external_quality_gate(
            gate_id="repo_automation_matrix",
            command=("uv", "run", "python", "scripts/make_repo_automation_matrix.py"),
            cwd=root,
            timeout_seconds=120,
        ),
        run_external_quality_gate(
            gate_id="mojo_available_uv_tool",
            command=("uv", "tool", "run", "--from", "mojo-compiler", "mojo", "--version"),
            cwd=root,
            timeout_seconds=240,
        ),
    ]
    json_path, csv_path = write_external_quality_gate_records(
        records,
        json_path=root / "data" / "derived" / "external_quality_gates.json",
        csv_path=root / "data" / "derived" / "external_quality_gates.csv",
    )
    print(f"Wrote {json_path} and {csv_path}")
    for record in records:
        print(f"{record.id}: {record.outcome}")


if __name__ == "__main__":
    main()
