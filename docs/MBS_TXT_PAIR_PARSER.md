# MBS TXT pair parser

Date: 2026-07-04

MBS Online currently exposes item-map and item-descriptor TXT files in addition to XML release pages. The repo now includes a parser for this two-file pattern.

## Parser

```python
from reimburse_atlas.parsers import parse_mbs_txt_pair

records = parse_mbs_txt_pair(
    item_map_path="data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT",
    descriptor_path="data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT",
)
```

CLI:

```bash
PYTHONPATH=src reimbursement-atlas parse-mbs-txt-pair \
  data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT \
  data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT \
  --output-dir data/derived/reviewed_sources
```

## Supported local validation formats

The parser is intentionally defensive during early validation. It accepts:

- headered pipe-delimited TXT;
- headered tab-delimited TXT;
- headered comma/semicolon-delimited text;
- a simple whitespace fallback where the first token is the MBS item number.

The output is `ScheduleItemRecord`. Raw MBS files remain local-only until reuse and attribution terms are reviewed.

## Test fixture

Synthetic fixtures live under `tests/fixtures/mbs_txt/` and prove that item-map prices can be joined to descriptors while descriptor-only rows remain explicit.
## Reviewed bundle command

For reviewed live-source validation, prefer the pair-bundle command because it snapshots both raw files and redacts local paths in bundle metadata:

```bash
PYTHONPATH=src reimbursement-atlas reviewed-mbs-txt-pair-bundle \
  data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT \
  data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT \
  --output-dir data/derived/reviewed_source_bundles
```

