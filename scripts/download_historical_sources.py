"""Download historical source targets into the ignored local raw cache.

This command archives source payloads for reproducibility without publishing or
tracking them. The derived manifest records the exact URL, retrieval result,
bytes, checksum and review boundary for every target.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess  # nosec B404 - fixed curl argv; URL is HTTPS and host allowlisted
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

from reimburse_atlas.registry import project_root

OFFICIAL_HOSTS = {"www.mbsonline.gov.au"}
DEFAULT_SEED = Path("data/seed/historical_mbs_archive_targets.jsonl")
DEFAULT_RAW = Path("data/raw_live/historical_sources")
DEFAULT_OUTPUT = Path("data/derived/historical_sources")


def _load_targets(path: Path) -> list[dict[str, str]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _safe_filename(target: dict[str, str]) -> str:
    suffix = Path(target["file_name"]).suffix.lower() or ".bin"
    return f"{target['id']}{suffix}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download(url: str, destination: Path, *, force: bool) -> tuple[str, str]:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc not in OFFICIAL_HOSTS:
        return "blocked_untrusted_host", "URL is not an HTTPS URL on an allowed official host."
    if destination.exists() and not force:
        return "cached", "Existing local cache retained; use --force to replace it."
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "curl",
        "--fail",
        "--silent",
        "--show-error",
        "--location",
        "--proto",
        "=https",
        "--tlsv1.2",
        "--retry",
        "3",
        "--retry-delay",
        "2",
        "--retry-max-time",
        "45",
        "--connect-timeout",
        "20",
        "--max-time",
        "45",
        "--output",
        str(destination),
        url,
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)  # nosec B603
    except (OSError, subprocess.CalledProcessError) as exc:
        destination.unlink(missing_ok=True)
        detail = getattr(exc, "stderr", "") or str(exc)
        return "download_failed", detail.strip()[-500:]
    return "downloaded", "Retrieved into ignored local cache."


def write_manifest(rows: list[dict[str, object]], output_dir: Path) -> None:
    """Write checkpointed JSONL, CSV and summary evidence."""
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl = output_dir / "historical_source_downloads.jsonl"
    jsonl.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8"
    )
    fields = sorted({key for row in rows for key in row})
    with (output_dir / "historical_source_downloads.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row["status"])
        counts[status] = counts.get(status, 0) + 1
    (output_dir / "historical_source_downloads_summary.json").write_text(
        json.dumps(
            {
                "schema_version": "historical-source-downloads-v1",
                "generated_at": datetime.now(tz=UTC).isoformat(),
                "target_count": len(rows),
                "status_counts": counts,
                "raw_cache_policy": "ignored_local_only",
                "licence_policy": "download_does_not_grant_redistribution_rights",
                "transformation_process": (
                    "data/derived/processes/historical_source_transformation.bpmn"
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def process_target(
    target: dict[str, str], *, raw_dir: Path, force: bool, dry_run: bool
) -> dict[str, object]:
    """Retrieve one target and return its deterministic evidence row."""
    destination = raw_dir / _safe_filename(target)
    status, detail = (
        ("planned", "Dry run; no network request made.")
        if dry_run
        else _download(target["file_url"], destination, force=force)
    )
    row: dict[str, object] = {
        "id": target["id"],
        "source_id": target["source_id"],
        "source_version_id": target["source_version_id"],
        "archive_page": target["archive_page"],
        "source_url": target["file_url"],
        "file_name": target["file_name"],
        "file_kind": target["file_kind"],
        "cache_path": (
            str(destination.relative_to(project_root()))
            if destination.is_relative_to(project_root())
            else str(destination)
        ),
        "status": status,
        "detail": detail,
        "licence_gate": target["licence_gate"],
        "review_status": "pending_human_review",
        "citation_key": f"reimbursement_atlas:{target['source_version_id']}",
        "transformation_process": "data/derived/processes/historical_source_transformation.bpmn",
    }
    if destination.exists() and status in {"downloaded", "cached"}:
        row["byte_size"] = destination.stat().st_size
        row["checksum_sha256"] = _sha256(destination)
    else:
        row["byte_size"] = None
        row["checksum_sha256"] = None
    return row


def main() -> None:
    """Download or checkpoint the historical source archive inventory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=Path, default=project_root() / DEFAULT_SEED)
    parser.add_argument("--raw-dir", type=Path, default=project_root() / DEFAULT_RAW)
    parser.add_argument("--output-dir", type=Path, default=project_root() / DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=int, default=0, help="Only process the first N targets.")
    parser.add_argument("--force", action="store_true", help="Replace existing local payloads.")
    parser.add_argument("--dry-run", action="store_true", help="Write a planned manifest only.")
    parser.add_argument("--workers", type=int, default=4, help="Concurrent downloads (default: 4).")
    parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="Retry only targets marked download_failed in the checkpoint.",
    )
    args = parser.parse_args()
    targets = _load_targets(args.seed)
    existing_rows: dict[str, dict[str, object]] = {}
    failed_ids: set[str] = set()
    if args.retry_failed:
        checkpoint = args.output_dir / "historical_source_downloads.jsonl"
        if checkpoint.exists():
            checkpoint_rows = [
                json.loads(line)
                for line in checkpoint.read_text(encoding="utf-8").splitlines()
                if line
            ]
            existing_rows = {str(row["id"]): row for row in checkpoint_rows}
            failed_ids = {
                str(row["id"]) for row in checkpoint_rows if row.get("status") == "download_failed"
            }
        targets = [
            target
            for target in targets
            if target["id"] in failed_ids or str(target["id"]) not in existing_rows
        ]
    if args.limit:
        targets = targets[: args.limit]
    target_ids = {target["id"] for target in targets}
    rows: list[dict[str, object]] = [
        row for row_id, row in existing_rows.items() if row_id not in target_ids
    ]
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {
            executor.submit(
                process_target,
                target,
                raw_dir=args.raw_dir,
                force=args.force,
                dry_run=args.dry_run,
            ): target
            for target in targets
        }
        for index, future in enumerate(as_completed(futures), start=1):
            rows.append(future.result())
            if index % 10 == 0 or index == len(futures):
                rows.sort(key=lambda row: str(row["id"]))
                # Periodic checkpoints balance resumability with concurrent I/O cost.
                write_manifest(rows, args.output_dir)
    write_manifest(rows, args.output_dir)
    print(json.dumps({"target_count": len(rows), "output_dir": str(args.output_dir)}))


if __name__ == "__main__":
    main()
