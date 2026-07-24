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
| `evidence_ready` | The protocol/linkage threshold passes and a current checksum-bound claim package records reviewed-derived inputs, validated analysis and scoped accountable approval. |

Scores alone cannot produce `evidence_ready`. Optional decisions are validated
against `data/research_claims/decision.schema.json`; missing, malformed, stale,
pending or rejected decisions cap the question at `prototype_ready`. Fixture
policy briefs are interface demonstrations and are not claim packages.

Generate bounded package candidates before the matrix:

```bash
pixi run research-claim-packages
pixi run evidence-readiness
```

The five JSON packages under `data/derived/research_claims/` bind reviewed
source bundles, mapping holdout evidence, denominators, exclusions and
unsupported claims. Generation never grants approval. A partial package records
the exact missing protocol-required sources and remains ineligible for an
evidence claim.

The matrix is not a substitute for human review. It is a triage and release-gating artefact that helps decide which policy questions can move from design to prototype analysis.
