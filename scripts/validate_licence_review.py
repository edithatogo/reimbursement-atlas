"""Validate the checksum-bound licence review queue and human decisions."""

from reimburse_atlas.licence_review_validation import validate_licence_review_queue
from reimburse_atlas.registry import project_root


def main() -> None:
    """Exit non-zero when queue integrity or recorded decisions are invalid."""
    root = project_root()
    queue_path = root / "data" / "derived" / "licence_review" / "licence_review_queue.jsonl"
    decisions_path = root / "data" / "licence_review" / "decisions.jsonl"
    errors = validate_licence_review_queue(
        queue_path,
        root=root,
        decisions_path=decisions_path,
    )
    if errors:
        raise SystemExit("Licence review validation failed:\n- " + "\n- ".join(errors))
    decision_count = (
        sum(1 for line in decisions_path.read_text(encoding="utf-8").splitlines() if line.strip())
        if decisions_path.exists()
        else 0
    )
    print(f"Licence review validation passed: queue={queue_path} decisions={decision_count}")


if __name__ == "__main__":
    main()
