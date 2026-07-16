"""Run mutation testing with a portable timeout and graceful cancellation."""

from __future__ import annotations

import argparse
import os
import signal
import subprocess  # nosec B404 - executes the fixed repository mutation command
import sys
from collections.abc import Sequence

DEFAULT_TIMEOUT_SECONDS = 80 * 60


def run_bounded(command: Sequence[str], timeout_seconds: int) -> int:
    """Run ``command`` and terminate its process group when the budget expires."""
    process = subprocess.Popen(  # nosec B603 - shell execution is disabled and argv is controlled
        list(command),
        start_new_session=(os.name != "nt"),
    )
    try:
        return process.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        if os.name != "nt":
            os.killpg(process.pid, signal.SIGTERM)
        else:
            process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            if os.name != "nt":
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            process.wait()
        print(
            f"Mutation command exceeded timeout of {timeout_seconds}s and was terminated.",
            file=sys.stderr,
        )
        return 124


def main(argv: Sequence[str] | None = None) -> int:
    """Parse the timeout and run the repository mutation command."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Maximum runtime before the mutation process group is terminated.",
    )
    args = parser.parse_args(argv)
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive")
    return run_bounded(
        ("mutmut", "run", "--paths-to-mutate", "src/reimburse_atlas", "--max-children", "2"),
        args.timeout_seconds,
    )


if __name__ == "__main__":
    raise SystemExit(main())
