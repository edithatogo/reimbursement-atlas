"""Create the reviewed derived CMS HCPCS Level II bundle."""

from reimburse_atlas.hcpcs_level_ii import build_hcpcs_level_ii_bundle
from reimburse_atlas.registry import project_root


def main() -> None:
    """Build the current ignored-raw HCPCS Level II derived bundle."""
    root = project_root()
    bundle = build_hcpcs_level_ii_bundle(
        root / "data/raw_live/us_cms_hcpcs_level_ii/july-2026-alpha-numeric-hcpcs-file.zip",
        root / "data/derived/reviewed_source_bundles",
    )
    print(bundle.relative_to(root))


if __name__ == "__main__":
    main()
