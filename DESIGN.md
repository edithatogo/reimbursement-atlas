# System Design

## Design principles

1. Policy questions first; data engineering serves analysis rather than raw collection.
2. Separate public schedule metadata from restricted/licensed source content.
3. Every imported row must carry provenance, version and parser metadata.
4. Crosswalks are hypotheses with confidence, not facts.
5. Published prices and effective payer costs are distinct variables.
6. The repository should be agent-readable through Conductor context files.

## High-level architecture

```mermaid
flowchart TD
    A[Public source registry] --> B[Ingestion adapters]
    B --> C[Raw landing zone]
    C --> D[Polars validation]
    D --> E[Arrow/Parquet snapshots]
    E --> F[DuckDB analytical marts]
    E --> G[LanceDB semantic index]
    H[Ontology adapters] --> I[Mapping workbench]
    F --> I
    G --> I
    I --> J[Analysis catalogue]
    J --> K[Policy outputs]
    J --> L[Astro dashboard]
    F --> L
    G --> L
    M[Conductor context] --> B
    M --> J
    M --> N[GitHub issues and projects]
```


## Live-source validation gate

```mermaid
flowchart TD
    A[Official public source page] --> B[Manual reviewed download]
    B --> C[Ignored local raw cache]
    C --> D[SourceSnapshotRecord: checksum and cache scope]
    D --> E{Licence gate}
    E -->|approved derived only| F[Source-specific parser]
    E -->|restricted| G[metadata only / local only]
    F --> H[ScheduleItemRecord or CoverageDecisionRecord]
    H --> I[Crosswalk candidates]
    I --> J[Human review queue]
    H --> K[Dashboard-safe CSV/JSONL]
    J --> K
    K --> L[Seed lake / dashboard / future HF dataset]
```

## Repository and context architecture

```mermaid
flowchart LR
    subgraph Repo[Repository]
        C[conductor/]
        D[docs/]
        S[src/]
        T[tests/]
        Data[data/seed/]
        Dash[apps/dashboard/]
        GH[.github/]
    end

    subgraph Conductor[Conductor context management]
        Brief[Project brief]
        Decisions[Decision log]
        Roadmap[Roadmap YAML]
        Sources[Source map]
        Analyses[Analysis map]
        Agents[Agent handoff cards]
    end

    C --> Brief
    C --> Decisions
    C --> Roadmap
    C --> Sources
    C --> Analyses
    C --> Agents
    Brief --> GH
    Roadmap --> GH
    Sources --> Data
    Analyses --> D
```

## Data model

```mermaid
erDiagram
    JURISDICTION ||--o{ SOURCE : hosts
    SOURCE ||--o{ SOURCE_VERSION : publishes
    SOURCE_VERSION ||--o{ SCHEDULE_ITEM : contains
    SCHEDULE_ITEM ||--o{ PRICE_COMPONENT : has
    SCHEDULE_ITEM ||--o{ RESTRICTION : may_have
    SCHEDULE_ITEM ||--o{ CONCEPT_MAPPING : maps_to
    ONTOLOGY_CONCEPT ||--o{ CONCEPT_MAPPING : supports
    ANALYSIS ||--o{ ANALYSIS_SOURCE : requires
    SOURCE ||--o{ ANALYSIS_SOURCE : supports
    ANALYSIS ||--o{ OUTPUT_ARTIFACT : produces

    JURISDICTION {
      string id
      string name
      string region
    }
    SOURCE {
      string id
      string jurisdiction_id
      string domain
      string access_tier
      boolean machine_readable
    }
    SOURCE_VERSION {
      string id
      string source_id
      date effective_from
      date retrieved_at
      string checksum
    }
    SCHEDULE_ITEM {
      string id
      string source_version_id
      string code
      string label
      string descriptor
    }
    PRICE_COMPONENT {
      string id
      string schedule_item_id
      string price_type
      decimal amount
      string currency
    }
    RESTRICTION {
      string id
      string schedule_item_id
      string text
      string criteria_json
    }
    CONCEPT_MAPPING {
      string id
      string local_code
      string ontology_id
      string concept_id
      float confidence
      string review_status
    }
```

## Mapping workflow

```mermaid
sequenceDiagram
    participant Agent as Research agent
    participant Registry as Source registry
    participant Parser as Parser adapter
    participant DuckDB as DuckDB mart
    participant Lance as LanceDB
    participant Review as Clinical/policy review
    participant Dashboard as Dashboard

    Agent->>Registry: Select first-wave source
    Registry->>Parser: Provide source URL, version rules, licence notes
    Parser->>Parser: Fetch or read local file
    Parser->>DuckDB: Write validated tabular snapshot
    Parser->>Lance: Embed descriptors/restrictions if licence allows
    DuckDB->>Review: Candidate crosswalks and anomalies
    Lance->>Review: Similarity explanations
    Review->>DuckDB: Approve/reject mapping hypotheses
    DuckDB->>Dashboard: Export graph/table data
    Lance->>Dashboard: Provide semantic search index
```

## Analysis pipeline

```mermaid
flowchart TD
    Q[Policy question] --> B[Define service/drug/test basket]
    B --> M[Map codes and restrictions]
    M --> V[Validate with domain reviewer]
    V --> P[Normalize price variables]
    P --> X[PPP/currency/context adjustment]
    X --> A[Run analysis]
    A --> U[Uncertainty and caveat layer]
    U --> O[Policy output]
    O --> R[Reusable dataset and dashboard]
```

## Dashboard design

```mermaid
flowchart LR
    Seed[Seed CSV graph] --> Astro[Astro 7 app]
    Duck[DuckDB extracts] --> Astro
    Lance[LanceDB search API later] --> Astro
    Astro --> Cosmo[Cosmograph graph]
    Astro --> Tables[Source and analysis tables]
    Astro --> Maps[Future geospatial views]
    Astro --> Cards[Policy insight cards]
```

## Storage design

| Layer | Default | Purpose |
|---|---|---|
| Raw landing | local ignored `data/raw/` and `data/raw_live/` | User-supplied and live-downloaded source files. |
| Seed | tracked `data/seed/` | Permissive registry and graph design data. |
| Processed | local ignored `data/processed/` | Arrow/Parquet snapshots from parsers. |
| Analytical | DuckDB | Joins, marts, reproducible analyses. |
| Semantic | LanceDB | Embeddings of descriptors, restrictions and coverage text when allowed. |
| Public dataset | Hugging Face datasets | Only permissive derived/metadata data. |
| Dashboard | Hugging Face Spaces | Public seed and analysis outputs. |

## First-wave implementation slices

1. Validate seed registries and JSON schemas.
2. Build source-quality scoring.
3. Implement MBS XML parser.
4. Implement CMS PFS and CLFS parsers.
5. Implement PBS CSV/API parser.
6. Implement NHS genomic directory parser.
7. Build mapping model and human-review tables.
8. Add local-source snapshot and parse CLI commands.
9. Render seed graph, source-status table and review queue in dashboard.
10. Add LanceDB semantic search over permitted descriptors.
11. Convert Conductor roadmap into GitHub issues.

## Key design risks

| Risk | Mitigation |
|---|---|
| False comparability | Bundle taxonomy, vignettes, confidence scores and explicit caveats. |
| Licence breach | Licence gate, local-only restricted cache, no proprietary descriptor mirroring. |
| Over-engineering | Thin vertical slices and ADRs for every major stack addition. |
| Ontology complexity | Start with metadata-only ontology registry and one high-value pathway: genomics/pathology. |
| Effective price opacity | Model transparency and published-price variables separately. |
| Agent drift | Conductor context files are mandatory reading before implementation. |

## v5 reviewed-source bundle and publication flow

```mermaid
flowchart TD
    A[Manual official-source download] --> B[Ignored local raw path]
    B --> C[reviewed-source-bundle CLI]
    C --> D[SourceSnapshotRecord]
    C --> E[Parser contract]
    E --> F[Derived rows only]
    D --> G[Validation report]
    F --> G
    G --> H[Bundle-local publication manifest]
    F --> I[Seed lake candidate]
    H --> J{Publication review}
    J -->|approved metadata/derived| K[GitHub release / Hugging Face dataset]
    J -->|blocked| L[Local only]
```

## Analysis recipe graph

```mermaid
flowchart LR
    A[Analysis catalogue] --> R[Analysis recipes]
    R --> I[Required input tables]
    R --> Q[Quality gates]
    R --> O[Output tables]
    I --> P[Policy signal matrix]
    Q --> P
    P --> D[Dashboard-safe artefacts]
    P --> H[Future HF dataset]
```

## v8 exact source-file layer

```mermaid
flowchart TD
    A[SourceRecord] --> B[SourceVersionRecord]
    B --> C[SourceFileRecord]
    C --> D{Acquisition mode}
    D -->|manual_download| E[data/raw_live ignored]
    D -->|api_rate_limited| F[rate-limited API request]
    D -->|licence_clickthrough_manual| G[human licence review]
    E --> H[Parser]
    F --> H
    G --> H
    H --> I[Derived contract rows]
    I --> J[Publication manifest]
    C --> K[Dashboard source-file table]
```

```mermaid
flowchart LR
    Q[External quality gate] --> R{Outcome}
    R --> P[passed]
    R --> F[failed]
    R --> B[blocked_network]
    R --> M[missing_tool]
    R --> T[timed_out]
    B --> N[Do not claim pass; retry in network-capable CI]
```
