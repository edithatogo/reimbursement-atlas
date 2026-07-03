# Analysis catalogue

The project should avoid simple country-A-pays-more-than-country-B comparisons unless the payment bundle is carefully normalised. The best analyses treat schedules as policy instruments.

Seed analysis definitions are stored in:

- `data/seed/analysis_catalogue.jsonl`
- `data/seed/analysis_catalogue.csv`

Current design inventory: **25 policy analyses**.

## Seed analyses

| id | title | difficulty | stage | policy_insight | primary_output |
| --- | --- | --- | --- | --- | --- |
| cognitive_vs_procedural_ratio | Cognitive versus procedural reward index | medium | design | Identifies whether schedules structurally privilege procedures over diagnostic reasoning, chronic care, counselling and coordination. | Jurisdiction-level index and service-pair basket table. |
| genomics_coverage_price_diffusion | Genomics coverage, price and diffusion atlas | medium | design | Shows whether public coverage produces actual uptake and whether restrictions create bottlenecks. | Genomic test graph, coverage chronology and utilisation panel. |
| published_vs_effective_price_opacity | Published versus effective price opacity score | medium | design | Highlights hidden rebates, confidential deeds, out-of-pocket gaps and negotiated plan/hospital prices. | Opacity index and evidence table. |
| coverage_decision_architecture | Coverage decision architecture comparison | low | design | Clarifies institutional design choices: national vs local discretion, explicit HTA, evidence thresholds and appeals. | Process maps and decision taxonomy. |
| patient_cost_exposure | Patient cost exposure and gap risk | high | design | Shows whether public reimbursement actually protects patients from out-of-pocket exposure. | Cost exposure profiles and simulated patient vignettes. |
| local_discretion_postcode_lottery | Local discretion and postcode-lottery index | medium | design | Distinguishes responsiveness from inequity: local coverage can speed innovation or create access variation. | Variation dashboard and maps. |
| hospital_professional_unbundling | Hospital-professional unbundling map | high | design | Shows whether apparent cross-country price differences are driven by bundling rather than generosity. | Bundle decomposition schema and exemplar procedures. |
| innovation_time_to_reimbursement | Time from evidence/approval to reimbursement | medium | design | Reveals whether systems trade speed for certainty, price discipline or evidentiary rigor. | Timeline dataset and survival models. |
| substitution_and_volume_control | Substitution and volume-control evaluation | medium | design | Helps distinguish productive innovation from additive low-value growth. | Utilisation panels and substitution networks. |
| medicine_access_restriction_text | Medicine restriction-text strictness index | medium | design | Turns opaque listing text into auditable access constraints. | Restriction ontology and strictness score. |
| ontology_maturity_score | Ontology and mapping maturity score | low | design | Identifies data infrastructure gaps that limit comparative policy analysis. | Maturity matrix and mapping backlog. |
| schedule_transparency_benchmark | Schedule transparency benchmark | low | design | Creates a policy transparency index across public reimbursement systems. | Transparency leaderboard and reproducible registry. |
| ai_diagnostics_reimbursement_readiness | AI diagnostics reimbursement readiness | high | design | Anticipates policy gaps before AI diagnostics diffuse. | Readiness framework and case studies. |
| equity_weighting_and_rural_loadings | Equity weighting and rurality adjustments | medium | design | Shows where reimbursement corrects or compounds geographic access inequity. | Equity adjustment catalogue. |
| price_revision_velocity | Price revision velocity and indexation discipline | medium | design | Identifies whether schedules actively manage inflation, technology maturity and budget pressure or allow legacy relativities to persist. | Versioned price-change panel and revision-timing dashboard. |
| local_vs_national_discretion | Local versus national coverage discretion map | medium | design | Distinguishes responsive local adaptation from postcode-lottery risk and maps where national schedules still hide local access rules. | Coverage-discretion taxonomy and jurisdiction heatmap. |
| rare_disease_reimbursement_pathways | Rare disease and ultra-orphan reimbursement pathways | high | design | Shows whether systems rely on HTA flexibility, managed entry, exceptional funding, local discretion or delayed access. | Rare-disease pathway typology and case-study matrix. |
| device_and_prosthesis_visibility | Device and prosthesis price visibility comparison | high | design | Reveals where device policy is transparent enough for price comparison versus obscured by procurement and episode bundling. | Device visibility index and exemplar device basket. |
| telehealth_payment_architecture | Telehealth payment architecture and parity rules | medium | design | Shows whether virtual care is treated as equivalent care, a lower-cost substitute, or a tightly restricted exception. | Telehealth rule matrix and fee-parity ratio table. |
| primary_care_longitudinal_incentives | Primary-care longitudinal incentive architecture | medium | design | Indicates whether public payment systems encourage episodic visits or longitudinal population management. | Primary-care incentive typology and matched service basket. |
| hospital_outpatient_carveout | Hospital outpatient carve-out and bundling comparison | high | design | Shows how bundling choices shape incentives for sites of care, device use and diagnostic ordering. | Bundling boundary map and cross-setting payment comparison. |
| terminology_coverage_completeness | Terminology coverage and ontology-dependency audit | low | prototype | Makes explicit where licensing or terminology access can block otherwise public reimbursement analysis. | Analysis-by-ontology dependency matrix and licence-risk register. |
| coverage_to_utilisation_lag | Coverage-to-utilisation lag after listing | medium | design | Separates nominal access from realised access and highlights implementation bottlenecks. | Event-study panel and diffusion-lag estimates. |
| global_public_schedule_access_index | Global public schedule access and reproducibility index | low | prototype | Ranks where comparative reimbursement research is easiest, most reproducible and most licence-constrained. | Open reimbursement data maturity leaderboard. |
| medicine_substitution_and_price_ladders | Medicine substitution, reference pricing and price ladder analysis | high | design | Identifies where public policy accelerates price convergence and where published prices remain opaque. | Therapeutic-class price ladder and policy mechanism map. |

## Recommended first policy paper

**Working title:** What do public reimbursement schedules reward? A comparative atlas of genomics, specialist care and high-cost medicines across Australia, US Medicare and selected OECD systems.

## Analysis design patterns

### Basket analysis

Select clinically meaningful service/drug/test baskets and compare:

- code and descriptor;
- eligibility/restriction;
- professional versus facility components;
- price type;
- patient cost exposure;
- utilisation;
- evidence/coverage history;
- confidence in crosswalk.

### Event-study analysis

Use listing or coverage decision date as the intervention and evaluate:

- utilisation growth;
- substitution away from older items;
- total volume expansion;
- provider/geographic diffusion;
- patient cost exposure changes.

### Transparency analysis

Score each schedule on:

- access;
- machine readability;
- historical availability;
- provenance;
- licence clarity;
- restriction visibility;
- effective-price opacity.

### Graph analysis

Represent sources, items, restrictions, ontologies and analyses as graph objects:

- jurisdictions publish sources;
- sources contain schedule versions;
- versions contain items;
- items map to concepts;
- concepts support analysis baskets;
- analyses generate outputs.

## Output formats

- Markdown policy briefs.
- DuckDB analytical marts.
- Parquet/Arrow datasets.
- Cosmograph graph CSV.
- Static dashboard pages.
- Future API/MCP responses.
