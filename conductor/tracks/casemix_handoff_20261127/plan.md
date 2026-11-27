# Implementation plan

- [x] CMH-01 Define a reference-only envelope using existing medallion models. (AC: 1, 2)
- [x] CMH-02 Validate provenance and candidate promotion boundaries. (AC: 2, 3)
- [x] CMH-03 Add a read-only receiving CLI and document the input contract. (AC: 1, 3)
- [x] CMH-04 Complete focused tests, lint and type checks. (AC: 4)
- [ ] CMH-05 Run repository/hosted quality gates and independent review before merge. (AC: 4)

Source-rights and scientific/publication reviews remain separate external gates.

Focused validation: Python 3.14, 39 tests passed (34 intake tests and five existing medallion contract tests); strict type checking passed with the isolated environment. Entire-repository Ruff lint/format, compilation, seed consistency, public-data policy and native CLI validation passed. The native data-quality report passed all 43 checks. Track, graph, Project, seed-lake and dashboard projections were regenerated. Eight of 17 quick-profile command equivalents were executed; this is not a complete quick-profile run. Full repository and hosted merge gates remain pending. See [validation.md](./validation.md) for executed commands and remaining gates.
