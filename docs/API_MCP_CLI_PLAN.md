# CLI, API and MCP interface plan

The atlas should expose the same read-only core through three interfaces: CLI first, then local API, then MCP.

## CLI

Current CLI commands:

| Command | Purpose |
|---|---|
| `validate` | Validate seed registries and source references. |
| `sources` | Show registered sources, optionally filtered by domain. |
| `analyses` | Show planned policy analyses. |
| `score-sources` | Print source readiness scores. |
| `readiness` | Write source and analysis readiness CSV/JSONL. |
| `ingestion-plan` | Write parser/source-version task plans. |
| `acquisition-plan` | Write licence-gated acquisition and blocker tables. |
| `seed-lake` | Materialise seed registries into local JSONL/CSV lake layout. |
| `source-snapshots` | Write checksum/provenance records for committed synthetic fixtures. |
| `vertical-slice` | Parse local fixtures and write derived records. |
| `export-graph` | Generate graph nodes/edges for dashboard. |
| `snapshot` | Emit a concise Conductor handoff snapshot. |
| `export-schema` | Export Pydantic JSON schemas. |

## API

`src/reimburse_atlas/api.py` contains an optional read-only FastAPI factory. It is deliberately lightweight and imports FastAPI lazily.

Planned endpoints:

| Endpoint | Output |
|---|---|
| `/health` | Status check. |
| `/sources` | Source registry records. |
| `/analyses` | Analysis catalogue records. |
| `/readiness/sources` | Source readiness rows. |
| `/readiness/analyses` | Analysis readiness rows. |
| `/ingestion/first-wave` | First-wave ingestion tasks. |

Run locally after installing the API extra or Pixi API environment:

```bash
pixi run -e api api-dev
```

## MCP

The MCP surface should remain read-only until provenance and licence gates are mature. The initial tool manifest is in `mcp/tools.seed.json`, and `src/reimburse_atlas/mcp_server.py` provides a lazy optional server factory for the same read-only concepts.

Planned MCP tools:

```mermaid
flowchart TD
    A[MCP client] --> B[atlas.snapshot]
    A --> C[atlas.search_sources]
    A --> D[atlas.analysis_readiness]
    A --> E[atlas.ingestion_plan]
    A --> F[atlas.crosswalk_review_queue]
    B --> G[Seed registries]
    C --> G
    D --> H[Readiness outputs]
    E --> I[Ingestion plan]
    F --> J[Generated local review queue]
```

Run locally after installing the MCP extra or Pixi MCP environment:

```bash
pixi run -e mcp mcp-dev
```

No MCP tool should fetch live schedules, access restricted ontologies, or publish raw files until those operations are behind explicit user-supplied credentials and licence gates.
