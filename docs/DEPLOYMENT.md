# Deployment

## GitHub

- Main repository for source code, design docs, issues, projects and CI.
- Releases should attach generated schema and public seed data.
- Use signed, tagged releases once implementation matures.

## Hugging Face dataset

- Store only permissive seed metadata and derived outputs.
- Include dataset card, licence, attribution and provenance.
- Do not upload raw restricted ontologies or proprietary descriptors.

## Hugging Face Space

- Static Astro dashboard first.
- Later optional API-backed dashboard.
- Use data files from approved public dataset or release assets.

## Local development

Pixi is the primary environment manager. uv is used for builds and Python package workflows. Raw data stays local and ignored.
