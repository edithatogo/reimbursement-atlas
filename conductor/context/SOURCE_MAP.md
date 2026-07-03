# Source map

This is a Conductor-readable summary of the seed source registry. The canonical machine-readable source is `data/seed/source_registry.jsonl`.

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
