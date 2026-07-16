"""Validate the token-gated Hugging Face publication candidate bundle."""

from __future__ import annotations

from pathlib import Path

from reimburse_atlas.registry import project_root, repo_relative

REQUIRED_FILES = (
    "infra/huggingface/DATASET_CARD.md",
    "infra/huggingface/README.md",
    "infra/huggingface/SPACE_README.md",
    "data/derived/publication_manifest.json",
    "apps/dashboard/dist/index.html",
    "apps/dashboard/dist/status.json",
)
FORBIDDEN_MARKERS = ("data/raw_live", "/Users/", "/Volumes/", "HF_TOKEN=", "OSF_TOKEN=")
DATASET_CARD_MARKERS = (
    "license: other",
    "pretty_name:",
    "source-specific licensing",
    "does not grant apache-2.0 rights",
    "publish only manifest rows with confirmed redistribution permission",
)


def validate_bundle(root: Path) -> list[str]:
    """Return publication-bundle policy violations."""
    errors = [relative for relative in REQUIRED_FILES if not (root / relative).exists()]
    space_readme = root / "infra/huggingface/SPACE_README.md"
    if space_readme.exists():
        text = space_readme.read_text(encoding="utf-8").lower()
        for marker in ("sdk: static", "license: apache-2.0", "raw restricted source"):
            if marker not in text:
                errors.append(f"SPACE_README.md missing marker: {marker}")
    dataset_card = root / "infra/huggingface/DATASET_CARD.md"
    if dataset_card.exists():
        text = " ".join(dataset_card.read_text(encoding="utf-8").lower().split())
        for marker in DATASET_CARD_MARKERS:
            if marker not in text:
                errors.append(f"DATASET_CARD.md missing marker: {marker}")
    for path in (
        (root / "apps/dashboard/dist").rglob("*") if (root / "apps/dashboard/dist").exists() else ()
    ):
        if not path.is_file() or path.suffix.lower() not in {
            ".html",
            ".css",
            ".js",
            ".json",
            ".csv",
            ".svg",
            ".woff",
            ".woff2",
        }:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in FORBIDDEN_MARKERS:
            if marker in text:
                errors.append(f"{repo_relative(path)} contains forbidden marker: {marker}")
    return errors


def main() -> None:
    """Fail closed before any Hugging Face mutation."""
    errors = validate_bundle(project_root())
    if errors:
        raise SystemExit("Hugging Face bundle validation failed:\n- " + "\n- ".join(errors))
    print("Hugging Face bundle validation passed; publication remains token-gated.")


if __name__ == "__main__":
    main()
