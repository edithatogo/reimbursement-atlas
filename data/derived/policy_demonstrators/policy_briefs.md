# Policy demonstrators

Generated from local fixture sources only. Missing fixture coverage is listed in the brief caveats.

- Brief count: 3
- Source count: 6

## Genomics and pathology coverage and price comparison

- Demonstrator: `genomics_pathology`
- Sources compared: ['au_mbs', 'au_pbs', 'uk_genomic_test_directory', 'us_cms_asp', 'us_cms_clfs', 'us_cms_pfs']
- Item count: 4
- Metric summary: Compared genomics items across 6 sources; 4 items found, 50.0% priced, median payment 999.75.
- Caveats:
  - Genomics domain labels may differ across jurisdictions.
  - Only items explicitly tagged 'genomics' or containing 'genomic' are compared.
  - No currency normalisation or PPP adjustment applied.
  - Missing fixture coverage for: us_cms_mcd.

## Cognitive versus procedural fee relativities

- Demonstrator: `cognitive_procedural_index`
- Sources compared: ['au_mbs', 'au_pbs', 'uk_genomic_test_directory', 'us_cms_asp', 'us_cms_clfs', 'us_cms_pfs']
- Item count: 2
- Metric summary: Cognitive items: 0 (median N/A), Procedural items: 2 (median 443.575), Ratio (proc/cog): N/A.
- Caveats:
  - Keyword-based cognitive/procedural classification is a prototype heuristic.
  - No case-mix or complexity adjustment applied.
  - Currency and purchasing-power differences are not normalised.
  - Missing fixture coverage for: ca_on_ohip.

## Medicine price-opacity scorecard

- Demonstrator: `medicine_opacity_index`
- Sources compared: ['au_mbs', 'au_pbs', 'uk_genomic_test_directory', 'us_cms_asp', 'us_cms_clfs', 'us_cms_pfs']
- Item count: 4
- Metric summary: Medicine items across 6 sources; 4 items, 4 with public price, opacity index 0.0 (lower = more transparent).
- Caveats:
  - Medicine price opacity reflects only public schedule amounts, not rebates.
  - List prices may overstate net reimbursement.
  - No confidential discount or bundled-payment adjustment applied.
  - Missing fixture coverage for: nz_pharmac.
