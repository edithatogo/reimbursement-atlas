# Ontology and terminology strategy

## Seed ontology registry

| id | name | domain | licence_risk | mapping_use |
| --- | --- | --- | --- | --- |
| loinc | LOINC | laboratory_clinical_observations | medium | Genomics/pathology and lab observation crosswalks. |
| rxnorm | RxNorm | medicines | medium | NDC/ingredient/brand/clinical drug mapping; PBS and Part B drug harmonisation. |
| umls | UMLS Metathesaurus | cross_terminology | high | Terminology bridge across ICD, CPT, SNOMED CT, RxNorm, MeSH and others where licensed. |
| icd10 | ICD-10 / ICD-10-CM / ICD-10-AM | diagnoses | medium | Eligibility, indication, case-mix and hospital episode mapping. |
| icd11 | ICD-11 | diagnoses | medium | Modern diagnosis concept spine and international classification reference. |
| atc | WHO ATC/DDD | medicines | medium | International medicine class comparisons. |
| snomed_ct | SNOMED CT | clinical_terms | high | Clinical indication and procedure semantic mapping. |
| hpo | Human Phenotype Ontology | phenotypes | low_medium | Genomic indication and rare disease phenotype matching. |
| omim | OMIM | genetics_disease | high | Gene-disease validity and rare disease labels. |
| orpha | ORPHAnet / ORDO | rare_disease | medium | Rare disease and indication grouping. |
| hgnc | HGNC | genes | low | Gene symbols and stable identifiers. |
| read_codes | Read Codes / CTV3 | primary_care_terms | high_or_deprecated | Historical UK primary-care mapping. |
| dsm5 | DSM-5 | psychiatric_diagnoses | high | Mental health indication comparisons. |
| mesh | MeSH | biomedical_indexing | low_medium | Evidence literature indexing and concept enrichment. |

## Core rule

Ontologies are connectors, not assumptions. A mapping should record:

- source code;
- target ontology;
- target concept id;
- target label if licence permits;
- mapper;
- method;
- confidence;
- review status;
- date;
- version of ontology;
- licence notes.

## Priority ontology pathways

### Genomics and pathology

- LOINC for lab observations/tests where appropriate.
- HPO for phenotypic eligibility.
- HGNC for gene identifiers.
- OMIM/ORDO as local licensed/reference-only rare disease resources.
- ICD-10/ICD-11 for diagnosis indications.
- UMLS only as local licensed bridge.

### Medicines

- RxNorm/RxNav for US-centric medication concepts.
- ATC/DDD for international therapeutic class comparisons.
- PBS/AMT mapping where available and licensed.
- NDC/HCPCS J-code mapping for US Part B medicines where possible.

### Hospital and procedures

- ICD-10 variants for diagnosis and indication.
- CPT/HCPCS where licensed.
- MBS item taxonomy.
- DRG/APC groupers as source-specific payment artefacts rather than universal clinical concepts.

## Licence gates

Never commit:

- UMLS source files;
- CPT long descriptors;
- DSM-5 text;
- proprietary SNOMED CT release files unless the repository is private and licence-covered;
- OMIM data files;
- confidential payer/manufacturer pricing files.

## RxNav-in-a-Box stance

The repository should support a local RxNav-in-a-Box deployment through configuration, but not require it. The default implementation can use:

1. remote RxNav API for low-volume development;
2. user-supplied local RxNav-in-a-Box endpoint for higher-volume or offline workflows;
3. cached derived identifiers where redistribution is allowed.

## Mapping confidence scale

| Score | Meaning |
|---:|---|
| 1 | String similarity only; no review. |
| 2 | Ontology-assisted candidate; unreviewed. |
| 3 | Programmatic mapping with supporting source. |
| 4 | Human-reviewed mapping. |
| 5 | Human-reviewed and validated in at least one analysis. |

## v5 local-only terminology seeds

`tests/fixtures/ontology_concepts_fixture.csv` and generated `data/seed/ontology_concepts.*` are synthetic workflow seeds. They are not redistributed ontology dumps.

The seed concepts exercise the future mapping workflow for LOINC-like laboratory observations, HPO-like phenotypes, ATC/RxNorm-like medicines, ICD-like diagnoses and HGNC-like genes. Restricted or account-gated terminology resources remain local-only and should be mapped through reviewed adapters rather than committed to the repo.
