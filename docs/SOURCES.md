# Public source registry

This file maps possible public billing schedules, reimbursement lists, hospital tariffs, drug schedules, coverage-decision sources and contextual datasets.

The registry is seeded in:

- `data/seed/source_registry.jsonl`
- `data/seed/source_registry.csv`
- `data/seed/source_versions.jsonl`
- `data/seed/source_versions.csv`

Current design inventory: **60 source families**. This is an inventory of research-usable public sources, not a claim that every source is immediately comparable or permissively redistributable.

## Access tiers

| Tier | Meaning |
|---|---|
| `tier_1` | Bulk or mostly machine-readable public source; good for reproducible ingestion. |
| `tier_2` | Public but messy: PDF, HTML, translation, manual cleaning or fragmented metadata. |
| `tier_3` | Public fragments, major subnational variation, access applications, or poor reproducibility. |

## Seed source families

| id | jurisdiction | schedule | domain | access_tier | format | machine_readable | historical_versions | utilisation_data |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| au_mbs | Australia | Medicare Benefits Schedule | medical_services | tier_1 | XML/CSV/HTML | True | True | True |
| au_pbs | Australia | Pharmaceutical Benefits Schedule | medicines | tier_1 | API/CSV | True | True | True |
| au_ihacpa_nep | Australia | IHACPA National Efficient Price / NWAU | hospital | tier_1 | PDF/XLSX | True | True | True |
| au_msac | Australia | MSAC Public Summary Documents | coverage_decisions | tier_2 | HTML/PDF | False | True | False |
| au_pbac | Australia | PBAC Public Summary Documents | coverage_decisions | tier_2 | HTML/PDF | False | True | False |
| us_cms_pfs | United States | Physician Fee Schedule | medical_services | tier_1 | ZIP/CSV/RVUDB | True | True | True |
| us_cms_clfs | United States | Clinical Laboratory Fee Schedule | laboratory | tier_1 | ZIP/CSV | True | True | True |
| us_cms_opps | United States | Outpatient Prospective Payment System | hospital_outpatient | tier_1 | ZIP/CSV | True | True | True |
| us_cms_ipps | United States | Inpatient Prospective Payment System | hospital_inpatient | tier_1 | ZIP/CSV/PDF | True | True | True |
| us_cms_asp | United States | Average Sales Price Drug Pricing Files | medicines | tier_1 | ZIP/CSV/PDF | True | True | True |
| us_cms_mcd | United States | Medicare Coverage Database | coverage_decisions | tier_1 | HTML/API-like search | True | True | False |
| us_medicaid_state_fees | United States | State Fee-for-Service Schedules | medical_services | tier_3 | PDF/HTML/CSV varies | False | True | True |
| uk_nhs_payment_scheme | England | NHS Payment Scheme / national prices | hospital | tier_1 | XLSX/PDF | True | True | True |
| uk_nhs_drug_tariff | England | Drug Tariff | medicines | tier_2 | PDF/HTML/XML fragments | False | True | True |
| uk_genomic_test_directory | England | National Genomic Test Directory | genomics | tier_1 | XLSX/PDF | True | True | False |
| ca_on_ohip | Canada - Ontario | Schedule of Benefits | medical_services | tier_2 | PDF | False | True | True |
| ca_bc_msp | Canada - British Columbia | Medical Services Commission Payment Schedule | medical_services | tier_2 | PDF/HTML | False | True | True |
| ca_ab_somb | Canada - Alberta | Schedule of Medical Benefits | medical_services | tier_2 | PDF | False | True | True |
| nz_pharmac | New Zealand | Pharmaceutical Schedule | medicines_devices | tier_1 | HTML/CSV/API-like downloads | True | True | True |
| de_ebm | Germany | Einheitlicher Bewertungsmaßstab | medical_services | tier_2 | HTML/PDF/ZIP | False | True | True |
| de_gdrg | Germany | G-DRG catalogues | hospital | tier_1 | XLSX/PDF | True | True | True |
| fr_ccam | France | CCAM/NGAP tariffs | medical_services | tier_2 | HTML/CSV/XML varies | False | True | True |
| fr_lpp | France | Liste des Produits et Prestations | devices | tier_2 | CSV/HTML | True | True | True |
| fr_haspub | France | HAS decisions and evaluations | coverage_decisions | tier_2 | HTML/PDF | False | True | False |
| nl_nza_dbc | Netherlands | DBC care products and tariffs | hospital_specialist | tier_1 | XLSX/CSV/PDF | True | True | True |
| be_inami | Belgium | NomenSoft nomenclature | medical_services | tier_1 | Web/CSV-like exports | True | True | True |
| jp_mhlw_fee | Japan | National medical fee schedule | medical_services | tier_2 | PDF/XLSX | False | True | True |
| jp_nhi_drug_prices | Japan | NHI Drug Price Standard | medicines | tier_2 | PDF/XLSX | False | True | True |
| tw_nhi_services | Taiwan | Medical service payment standards | medical_services | tier_1 | Open data CSV | True | True | True |
| kr_hira | South Korea | Fee schedules and claims data references | medical_services | tier_3 | Portal/API/PDF varies | False | True | True |
| ch_tarmed_tardoc | Switzerland | TARMED/TARDOC outpatient tariffs | medical_services | tier_2 | PDF/XML varies | False | True | True |
| ch_swissdrg | Switzerland | SwissDRG catalogues | hospital | tier_1 | XLSX/PDF | True | True | True |
| ch_specialities_list | Switzerland | Specialities List | medicines | tier_1 | Web/CSV-like | True | True | True |
| dk_drg | Denmark | DRG tariffs and cost weights | hospital | tier_1 | XLSX/PDF | True | True | True |
| no_helfo_tariffs | Norway | Tariffs for reimbursement claims | medical_services | tier_2 | PDF/Excel | True | True | True |
| se_tlv | Sweden | Medicine price and subsidy database | medicines | tier_1 | Web/CSV-like | True | True | True |
| se_norddrg | Sweden | NordDRG weights | hospital | tier_1 | XLSX/PDF | True | True | True |
| sg_fee_benchmarks | Singapore | Hospital bills and fee benchmarks | price_benchmarks | tier_2 | Web/CSV-like | True | True | False |
| oecd_health_stats | Multi-country | Health statistics and expenditure indicators | contextual | tier_1 | API/CSV | True | True | True |
| who_gho | Multi-country | Global Health Observatory | contextual | tier_1 | API/CSV | True | True | True |
| us_cms_asc | United States | Ambulatory Surgical Center Payment System | hospital_outpatient | tier_1 | ZIP/CSV/PDF | True | True | False |
| us_cms_dmepos | United States | DMEPOS Fee Schedule | devices_equipment | tier_1 | ZIP/CSV/PDF | True | True | False |
| us_cms_snf | United States | Skilled Nursing Facility Prospective Payment System | post_acute | tier_1 | ZIP/CSV/PDF | True | True | True |
| us_cms_home_health | United States | Home Health Prospective Payment System | community_care | tier_1 | ZIP/CSV/PDF | True | True | True |
| us_cms_partd_puf | United States | Part D Prescriber and Drug Spending Public Use Files | medicines | tier_2 | CSV/API | True | True | True |
| au_aihw_mbs_pbs_stats | Australia | MBS and PBS utilisation and expenditure statistics | utilisation | tier_1 | CSV/XLSX/HTML | True | True | True |
| uk_nice_guidance | England | NICE technology appraisal and diagnostics guidance | coverage_decisions | tier_2 | HTML/PDF/API | False | True | False |
| uk_nhs_reference_costs | England | NHS reference costs / patient-level costing outputs | costs | tier_2 | CSV/XLSX | True | True | True |
| ca_qc_ramq | Canada - Quebec | Physician remuneration agreements and tariffs | medical_services | tier_2 | PDF/HTML | False | True | False |
| ca_ciihi_cmg | Canada | Case Mix Groups and resource intensity weights | hospital | tier_2 | PDF/XLSX | False | True | True |
| ie_hse_reimbursement | Ireland | Reimbursement lists and community drug schemes | medicines | tier_2 | XLSX/PDF/HTML | True | True | False |
| fi_kela_reimbursements | Finland | Medicine reimbursement and price data | medicines | tier_2 | HTML/CSV/API | True | True | False |
| es_bifimed | Spain | BIFIMED medicine financing and price information | medicines | tier_2 | HTML/search | False | True | False |
| it_aifa_reimbursement | Italy | AIFA reimbursed medicines and pricing decisions | medicines | tier_2 | HTML/CSV/PDF | False | True | False |
| br_sigtap | Brazil | SIGTAP procedures, medicines and OPM table | medical_services | tier_1 | DAT/CSV/HTML | True | True | True |
| za_upfs | South Africa | Uniform Patient Fee Schedule | medical_services | tier_2 | PDF/XLSX | False | True | False |
| in_abpmjay_hbp | India | Health Benefit Packages and rates | hospital | tier_2 | PDF/XLSX/HTML | False | True | True |
| is_hta_catalogue | Israel | National Health Basket and technology updates | coverage_decisions | tier_2 | HTML/PDF | False | True | False |
| mx_imss_costs | Mexico | Published medical service unit costs and tariffs | medical_services | tier_3 | PDF/HTML | False | True | False |
| us_cms_hospice | United States | Hospice Payment System | palliative_end_of_life | tier_1 | PDF/ZIP/CSV | True | True | True |

## First-wave sources

1. `au_mbs`
2. `au_pbs`
3. `au_ihacpa_nep`
4. `us_cms_pfs`
5. `us_cms_clfs`
6. `us_cms_asp`
7. `us_cms_mcd`
8. `uk_nhs_payment_scheme`
9. `uk_nhs_drug_tariff`
10. `uk_genomic_test_directory`
11. `ca_on_ohip`
12. `nz_pharmac`
13. `de_ebm`
14. `de_gdrg`
15. `jp_mhlw_fee`
16. `tw_nhi_services`
17. `us_cms_partd_puf`
18. `au_aihw_mbs_pbs_stats`

## Source scoring fields to add next

- licence status: permissive, attribution-required, restricted, unknown;
- live URL check status;
- parser readiness;
- provenance completeness;
- price variable clarity;
- restriction extractability;
- utilisation linkage;
- ontology linkability;
- effective-price opacity;
- clinical-review priority.

## Working source-selection principle

Use `tier_1` sources for automated ingestion, `tier_2` sources for policy-context extraction and manually validated baskets, and `tier_3` sources only when the policy insight is important enough to justify bespoke cleaning.
