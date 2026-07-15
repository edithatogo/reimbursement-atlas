"""Generate the artifact-level licence review queue."""

from reimburse_atlas.licence_review import build_and_write_licence_review_queue


def main() -> None:
    """Write the current fail-closed licence review queue."""
    paths = build_and_write_licence_review_queue()
    print("Wrote licence review queue: " + ", ".join(str(path) for path in paths))


if __name__ == "__main__":
    main()
