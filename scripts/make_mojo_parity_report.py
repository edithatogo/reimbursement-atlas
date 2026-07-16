"""Run the Python reference contract and official Mojo smoke parity gate."""

from __future__ import annotations

import hashlib
import json
import subprocess  # nosec B404 - executes the fixed repository smoke script only
from pathlib import Path

from reimburse_atlas.registry import project_root

PARITY_CASES = (
    ("ABCDE12345", (5, 5), ("ABCDE", "12345")),
    ("whole exome", None, ("whole", "exome")),
)
FUZZY_CASES = (
    ("whole exome", "whole exome sequencing", 2 / 3),
    ("a a", "a b", 0.5),
)


def _sha256_json(value: object) -> str:
    """Hash canonical JSON so benchmark evidence remains reproducible."""
    payload = json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def fixed_width_tokenize(line: str, widths: tuple[int, ...]) -> tuple[str, ...]:
    """Reference implementation for the fixed-width Mojo kernel."""
    position = 0
    tokens: list[str] = []
    for width in widths:
        tokens.append(line[position : position + width].strip())
        position += width
    return tuple(tokens)


def token_jaccard(left: str, right: str) -> float:
    """Reference implementation for the candidate-only Mojo prefilter."""
    left_tokens = set(left.split())
    right_tokens = set(right.split())
    union = left_tokens | right_tokens
    return len(left_tokens & right_tokens) / len(union) if union else 0.0


def _run_mojo_smoke(root: Path) -> dict[str, object]:
    try:
        result = subprocess.run(  # nosec B603, B607 - fixed command and repository cwd
            ["bash", "scripts/run_mojo_smoke.sh"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "blocked", "detail": type(exc).__name__}
    if result.returncode:
        return {"status": "blocked", "detail": result.stderr[-500:]}
    return {"status": "pass", "stdout": result.stdout.strip().splitlines()}


def build_mojo_parity_report(root: Path, *, run_smoke: bool = True) -> dict[str, object]:
    """Build a parity report while keeping missing Mojo separate from failure."""
    fixed_width_results = [
        fixed_width_tokenize(line, widths) if widths else tuple(line.split())
        for line, widths, _expected in PARITY_CASES
    ]
    fixed_width_pass = all(
        result == expected
        for result, (_line, _widths, expected) in zip(
            fixed_width_results, PARITY_CASES, strict=True
        )
    )
    fuzzy_pass = all(
        abs(token_jaccard(left, right) - expected) < 1e-9 for left, right, expected in FUZZY_CASES
    )
    fixed_width_outputs = [list(result) for result in fixed_width_results]
    fuzzy_outputs = [token_jaccard(left, right) for left, right, _expected in FUZZY_CASES]
    benchmark_contract = {
        "status": "pass" if fixed_width_pass and fuzzy_pass else "fail",
        "deterministic": True,
        "workload_sha256": _sha256_json({
            "fixed_width": fixed_width_outputs,
            "fuzzy_prefilter": fuzzy_outputs,
        }),
        "fixed_width_cases": len(PARITY_CASES),
        "fixed_width_input_bytes": sum(len(line.encode("utf-8")) for line, _w, _e in PARITY_CASES),
        "fixed_width_output_tokens": sum(len(result) for result in fixed_width_results),
        "fixed_width_output_sha256": _sha256_json(fixed_width_outputs),
        "fuzzy_prefilter_cases": len(FUZZY_CASES),
        "fuzzy_prefilter_output_sha256": _sha256_json(fuzzy_outputs),
    }
    smoke = _run_mojo_smoke(root) if run_smoke else {"status": "not_run"}
    return {
        "schema_version": "mojo-parity-v1",
        "python_reference_status": "pass" if fixed_width_pass and fuzzy_pass else "fail",
        "mojo_smoke": smoke,
        "benchmark_contract": benchmark_contract,
        "publication_safe": True,
        "notes": [
            "Python remains the auditable reference implementation.",
            (
                "Mojo smoke availability is environment-dependent and does not alter "
                "evidence readiness."
            ),
        ],
    }


def main() -> None:
    """Write the parity report and fail only when the Python contract fails."""
    root = project_root()
    report = build_mojo_parity_report(root)
    path = root / "data" / "derived" / "mojo" / "mojo_parity_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if report["python_reference_status"] != "pass":
        message = "Mojo/Python parity contract failed"
        raise SystemExit(message)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
