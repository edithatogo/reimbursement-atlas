# Policy demonstrators

Generated from local fixture sources only. Missing fixture coverage is listed in the brief caveats.

- Brief count: 3
- Source count: 5

## Genomics and pathology coverage and price comparison

- Demonstrator: `genomics_pathology`
- Sources compared: ['au_mbs', 'au_pbs', 'us_cms_asp', 'us_cms_clfs', 'us_cms_pfs']
- Item count: 2
- Metric summary: Compared genomics items across 5 sources; 2 items found, 100.0% with a public schedule amount. No pooled payment statistic is calculated across unharmonised sources.
- Caveats:
  - Genomics domain labels may differ across jurisdictions.
  - Only items explicitly tagged 'genomics' or containing 'genomic' are compared.
  - This is a parser/rendering fixture, not a cross-jurisdiction price comparison.
  - Pooled prices require harmonised currency year, price concept, component, bundle and unit.
  - Missing fixture coverage for: uk_genomic_test_directory, us_cms_mcd.

## Cognitive versus procedural fee relativities

- Demonstrator: `cognitive_procedural_index`
- Sources compared: ['au_mbs', 'au_pbs', 'us_cms_asp', 'us_cms_clfs', 'us_cms_pfs']
- Item count: 2
- Metric summary: Cognitive items identified: 0; procedural items identified: 2. No relativity is calculated without matched, within-jurisdiction baskets.
- Caveats:
  - Keyword-based cognitive/procedural classification is a prototype heuristic.
  - No case-mix or complexity adjustment applied.
  - This fixture does not measure incentives, value, provider income or actual payment.
  - A result requires both classes and prespecified matching, component and minimum-sample rules.
  - Missing fixture coverage for: ca_on_ohip.

## Medicine public schedule-amount missingness

- Demonstrator: `medicine_public_amount_missingness`
- Sources compared: ['au_mbs', 'au_pbs', 'us_cms_asp', 'us_cms_clfs', 'us_cms_pfs']
- Item count: 4
- Metric summary: Medicine items across 5 sources; 4 items, 4 with public price, public schedule amount missingness 0.0.
- Caveats:
  - This metric measures field missingness, not price opacity or transparency.
  - List prices may overstate net reimbursement.
  - No confidential discount or bundled-payment adjustment applied.
  - Missing fixture coverage for: nz_pharmac.
