# Evidence-readiness matrix

The evidence-readiness matrix turns each protocolled research question into a generated release-review row. It combines protocol completeness, research-question linkages, data-quality blockers, source-content validation, mapping-resource coverage and output-plan coverage.

Generate it with:

```bash
PYTHONPATH=src reimbursement-atlas evidence-readiness
# or
PYTHONPATH=src python scripts/make_evidence_readiness.py
```

Outputs:

```text
data/derived/evidence_readiness/evidence_readiness.jsonl
data/derived/evidence_readiness/evidence_readiness.csv
data/derived/evidence_readiness/summary.json
```

Readiness stages:

| Stage | Meaning |
|---|---|
| `blocked` | A blocking data-quality or source-validation failure exists. |
| `design` | Protocol/source/mapping/output linkages are insufficient for prototype analysis. |
| `prototype_ready` | The research question has enough protocol and linkage structure to run on reviewed derived data. |
| `evidence_ready` | Protocol score, linkages and release gates are strong enough for preregistered policy analysis, once real reviewed-source bundles are present. |

The matrix is not a substitute for human review. It is a triage and release-gating artefact that helps decide which policy questions can move from design to prototype analysis.
