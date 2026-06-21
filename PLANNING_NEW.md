# NexusResearch — Enterprise Cognitive Architecture & Implementation Ledger

This document serves as the master engineering design blueprint, data state ledger, and phased implementation lifecycle tracker for the NexusResearch multi-agent platform built natively on top of the **Google Agent Development Kit (ADK 2.0)**.

---

## 1. System Topology & Architectural Flows

NexusResearch implements a hybrid deployment model designed for local mac/windows. The entire compute layer (User Interface, FastAPI routing, and Google ADK 2.0 multi-agent graphs) executes natively within a local `uv` virtual workspace environment. This ensures sub-millisecond inter-agent communication, elimination of Docker virtualization overhead for LLM token processing, and instant developer hot-reloading. All stateful storage backends (Graph Database, Vector Engine, In-Memory Caches, and Audit Stores) are completely isolated inside production-grade Docker containers.

### 1.1 Macro-System Architecture Flowchart

```mermaid
graph TD
    %% Component Style Classes
    classDef frontend fill:#6c5ce7,stroke:#a29bfe,stroke-width:2px,color:#fff;
    classDef native fill:#0984e3,stroke:#74b9ff,stroke-width:2px,color:#fff;
    classDef workflow fill:#00b894,stroke:#55efc4,stroke-width:2px,color:#fff;
    classDef docker fill:#b2bec3,stroke:#dfe6e9,stroke-width:2px,color:#2d3436;
    classDef studio fill:#e17055,stroke:#fab1a0,stroke-width:2px,color:#fff;

    %% Presentation Layer (Native Host Workspace)
    subgraph Presentation_Layer ["Presentation Layer (Native Host Workspace)"]
        UI[Streamlit UI Dashboard<br/>frontend/app.py]:::frontend
    end

    %% Application Core Layer (Native Host Workspace)
    subgraph Application_Core ["Application Core Layer (Native Host Workspace)"]
        API[FastAPI Router Engine<br/>app/main.py]:::native
        Orchestrator[Master NexusOrchestrator<br/>backend/src/core/agents.py]:::native
        
        subgraph ADK_Workflows ["ADK 2.0 Graph Execution Loops"]
            IngestFlow[Asynchronous Ingestion Graph<br/>workflows/ingestion.py]:::workflow
            RuntimeFlow[Stateful Reasoning Graph<br/>workflows/reasoning.py]:::workflow
        end
        
        TraceExporter[ADK OpenTelemetry Exporter]:::native
    end

    %% Stateful Storage Layer (Docker Container Topology)
    subgraph Storage_Layer ["Stateful Storage Layer (Docker Container Topology)"]
        Chroma[(ChromaDB Container<br/>Port 8000)]:::docker
        Neo4j[(Neo4j APOC Cluster<br/>Ports 7474/7687)]:::docker
        Redis[(Redis Cache/Sessions<br/>Port 6379)]:::docker
        Postgres[(Postgres Telemetry Store<br/>Port 5432)]:::docker
    end

    %% Diagnostics & Observability
    subgraph Observability_Layer ["Observability Layer"]
        Studio[ADK Web Studio UI<br/>Port 4317 Tooling]:::studio
    end

    %% Interface Control Topologies
    UI <-->|Async WebSocket Stream<br/>& HTTP Multipart| API
    API <-->|Context State Injections| Orchestrator
    Orchestrator -->|Direct Memory Invocations| IngestFlow
    Orchestrator -->|Context Aggregations| RuntimeFlow

    %% Direct Host-to-Container Data Lines
    IngestFlow -->|HTTP API Collections| Chroma
    IngestFlow -->|Bolt Protocol Binary Writes| Neo4j
    RuntimeFlow -->|Vector Similarity Queries| Chroma
    RuntimeFlow -->|Analytical Cypher Trajectories| Neo4j
    API <-->|Token Caching & Session Boundaries| Redis
    
    %% Telemetry Stream Loopback
    IngestFlow & RuntimeFlow -.->|gRPC OTLP Frame Streams| TraceExporter
    TraceExporter -.->|Relay Local Intercepts| Postgres
    Postgres <-->|Query Metrics Logs| Studio

```

### 1.2 Networking Topology Matrix

| Service Component | Environment | Internal Binding Address | Exposed Host Port | Transport Protocol | Primary Purpose |
| --- | --- | --- | --- | --- | --- |
| **Streamlit Interface** | Native macOS | `127.0.0.1` | `8501` | HTTP / WebSocket | Client rendering and file uploads |
| **FastAPI Gateway** | Native macOS | `0.0.0.0` | `8000` | HTTP / WebSocket | Stream orchestration and routing |
| **ChromaDB Core** | Docker Container | `0.0.0.0` | `8001` | HTTP REST | Vector space indexing and retrieval |
| **Neo4j Graph Database** | Docker Container | `0.0.0.0` | `7474` (HTTP) / `7687` (Bolt) | HTTP / Bolt Binary | Topological knowledge graphs |
| **Redis Cache** | Docker Container | `0.0.0.0` | `6379` | TCP Telnet | Session lockfiles and token caching |
| **PostgreSQL DB** | Docker Container | `0.0.0.0` | `5432` | TCP SQL | Persistent ADK telemetry execution ledger |
| **ADK Web Studio** | Native / Loopback | `0.0.0.0` | `4317` | gRPC OpenTelemetry | Multi-agent execution step debugging |

---

## 2. Standardized Enterprise Project Directory Structure

```text
nexusmind-platform/
├── docker-compose.yaml          # Infrastructure definition for Neo4j, ChromaDB, Redis, and Postgres
├── pyproject.toml               # Root uv workspace anchor declaring members = ["frontend", "backend"]
├── uv.lock                      # Universal deterministic package environment state lockfile
├── run.sh                       # Local orchestration runtime automation and sanity bootloader script
├── .env                         # Consolidated credential store (GOOGLE_API_KEY, NEO4J_PASSWORD, etc.)
├── PLANNING.md                  # Comprehensive platform technical architectural ledger (This Document)
|
├── config/
│   ├── config.yaml              # System network parameters, port assignments, and models configuration
│   └── settings.py              # Strict environment evaluation layer enforced by Pydantic
│
├── storage/                     # Isolated Local Directory Mounts for Containers (Git Ignored)
│   ├── chroma_data/             # SQLite databases and raw HNSW vector segment tables
│   ├── neo4j_data/              # Database block stores, relational constraints, and txn journals
│   ├── pg_data/                 # Relational relational definitions tracking ADK system executions
│   └── redis_data/              # Periodic RDB state tracking snap snapshots
│
├── frontend/                    # TIER 1: Presentation Layer Workspace
|.  ├── ui/
│   └── app.py                   # Pure interface logic; contains no AI imports or client configurations
│
└── app/                     # TIER 2 & 3: Unified Network Gateway & ADK Cognitive Engine
        ├── main.py              # System entry point; initializes FastAPI application and binds ADK tracing
        │
        ├── api/                 # Network Transport & Router Subsystem
        │   ├── __init__.py
        │   ├── dependencies.py  # Shared security context extractors, Redis brokers, and client instances
        │   └── routes/
        │       ├── chat.py      # Binds WebSocket loops to the ADK context-amplified reasoning graph
        │       └── ingest.py    # Multi-part binary file data collection streaming targets
        │
        ├── core/                # The Cognitive Domain Layer (Google ADK 2.0 Brain)
        │   ├── __init__.py
        │   ├── agents.py        # Complete definitions mapping all individual structural adk.Agent properties
        │   ├── prompts.py       # Centrally configured system instruction templates and schema layout rules
        │   └── workflows/       # Stateful Multi-Agent Execution State Flow Machines
        │       ├── ingestion.py # Background asynchronous multi-stage knowledge graph construction graph
        │       └── reasoning.py # High-fidelity multi-hop context retrieval and synthesis engine graph
        │
        ├── infrastructure/      # Database Persistence Subsystem Managers
        │   ├── __init__.py
        │   ├── chroma_client.py # HTTP client wrapping similarity space collections and embeddings
        │   └── neo4j_driver.py  # Session context managers managing transaction-safe Cypher blocks
        │
        └── tools/               # Pure Executable Injections (Strictly type-hinted and docstring-documented)
            ├── __init__.py
            ├── vector_tools.py  # Vector lookups and dense metadata coordinate aggregators
            ├── graph_tools.py   # Explicit multi-hop path visualizers and Cypher trajectory scrapers
            └── file_tools.py    # Document layout segment parsers and chunk extraction layers

```

---

## 3. Deep Component Lifecycle Specifications

### 3.1 Structural Intent Routing Logic (`backend/src/api/routes/`)

Operating before any token-heavy multi-agent reasoning graphs are initialized, the API router executes stateless analysis parameters on incoming payloads to ensure minimal processing latency.

```mermaid
graph LR
    UserQuery[Incoming Payload Stream] --> Router{Intent Classifier Engine}
    
    Router -->|Match: String matches File Path Pointer| Ingest[Trigger Asynchronous Ingestion Graph]
    Router -->|Match: Conversational Bounds / Greeting| Local[Direct Route to Apple Local Compute via MLX]
    Router -->|Match: Multi-Hop Analytical Query| Runtime[Trigger Stateful Reasoning Graph Loop]

```

* **`FILE_UPLOAD`**: When a file transaction endpoint is hit via `/api/ingest`, the gateway bypasses runtime reasoning graphs, caches the raw document layout to disk, and spins up a native independent background processing task bound to the `Asynchronous Ingestion Graph`.
* **`CASUAL_CHITCHAT`**: Evaluates strings using regex patterns and token constraints. If a query contains only standard conversational greetings ("hello", "who are you", "thanks"), it routes directly to a local, small footprint LLM running on device via MLX. This strategy preserves database connections and keeps cloud compute token overhead at zero.
* **`RESEARCH_SEARCH`**: The standard operational default profile for multi-hop lookups. Initializes complete transactional session contexts across the persistence layer and boots the ADK Reasoning execution engine.

### 3.2 The Ingestion Pipeline (Stateful Graph Construction Step Trace)

The processing path for binary documents transforms raw, unformatted prose into deeply linked knowledge clusters without structural gaps:

```text
[START]
   │
   ▼
[Parser Agent] ──────────────> Extract layout typography matrix and structural document maps.
   │
   ▼
[Chunking Agent] ────────────> Slices data matrices into continuous 500-token sliding windows.
   │
   ▼
[Entity Extraction Agent] ───> Scans sliding window spans to isolate key data concepts.
   │
   ▼
[Relationship Extractor] ────> Maps directional link assertions (Source -> VERB -> Target).
   │
   ▼
[KG Validation Agent] ───────> Cleans unclosed JSON arguments and verifies formatting profiles.
   │
   ▼
[Indexing Agent] ────────────> Writes dense text windows to ChromaDB and paths to Neo4j.
   │
   ▼
 [END]

```

1. **Parser Agent (`parser_agent_py`)**: Extracts embedded structural headers, page indexes, and text configurations from incoming binaries.
2. **Chunking Agent (`chunking_agent_py`)**: Applies structural token sliding boundaries. It uses standard text chunks of 500 tokens wrapped with a trailing 10% step-back overlap margin to maintain cross-window readability.
3. **Entity Extraction Agent (`entity_extractor_py`)**: Extracts specific system vocabulary markers, tracking properties, and category types from text spans.
4. **Relationship Extractor (`relationship_extractor_py`)**: Links entity references into clear assertions, outputting clean arrays of structural facts (`Source` $\rightarrow$ `VERB` $\rightarrow$ `Target`).
5. **KG Validation Agent (`validation_agent_py`)**: Functions as a data quality gate. It verifies incoming graph changes, handles broken array properties, and fixes invalid JSON formatting before any database writes occur.
6. **Indexing Agent (`indexer_agent_py`)**: Receives the clean, structured facts array. It writes dense semantic chunks to ChromaDB and relational updates to Neo4j using transaction-safe Cypher queries to keep data organized and deduplicated:
```cypher
MERGE (s:Entity {name: $source_name})
SET s.type = $source_type, s.updated_at = timestamp()
MERGE (t:Entity {name: $target_name})
SET t.type = $target_type, t.updated_at = timestamp()
MERGE (s)-[r:RELATION {type: $rel_type}]->(t)
SET r.weight = coalesce(r.weight, 0) + 1

```



### 3.3 The Knowledge Fusion Engine (`backend/src/tools/vector_tools.py`)

To prevent information overlap when retrieving data from multiple systems, the platform applies a mathematical **Reciprocal Rank Fusion (RRF)** algorithm layer within the retrieval tools. When parallel threads query ChromaDB and Neo4j, the individual results are unified through an algorithmic ranking function:

$$\text{RRF Score}(d \in D) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

Where $M$ represents the array of storage engines (Chroma proximity distances and Neo4j topological degree counts), $r_m(d)$ represents the precise item ordinal index position returned by database channel $m$, and $k$ represents a smoothing safety constant (defaulting to $60$).

```text
Raw Vector Results Matrix  ───┐
                               ├──> [Knowledge Fusion Agent] ──> Normalized Context Array
Raw Graph Relational Array ───┘         (RRF Scoring Filter)

```

The output list is sorted by final calculated relevance scores, dropping duplicate text snippets and filtering out information collisions before formatting the text payload for the reasoning model.

---

## 4. Master Configuration Manifest Files

### 4.1 Master Workspace Workspace Core Configuration (`pyproject.toml`)

```toml

[project]
name = "nexusmind-platform"
version = "2.0.0"
description = "Enterprise Hybrid Local-Compute Multi-Agent Platform"
requires-python = ">=3.11"
dependencies = [
    "google-agent-development-kit>=2.0.0",
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.28.0",
    "chromadb>=0.4.24",
    "neo4j>=5.18.0",
    "redis>=5.0.3",
    "pydantic-settings>=2.2.1",
    "pydantic>=2.6.4",
    "httpx>=0.27.0",
    "websockets>=12.0",
    "opentelemetry-api>=1.23.0",
    "opentelemetry-sdk>=1.23.0",
    "opentelemetry-exporter-otlp>=1.23.0",
    "streamlit>=1.32.0",
    "httpx>=0.27.0",
    "websockets>=12.0"
]

```

### 4.2 Dockerized Persistent Storage Infrastructure Subsystem (`docker-compose.yaml`)

```yaml
version: '3.8'

services:
  chromadb:
    image: chromadb/chroma:0.4.24
    container_name: nexus-vector-chroma
    ports:
      - "8001:8000"
    environment:
      - CHROMA_SERVER_AUTH_PROVIDER=None
      - PERSIST_DIRECTORY=/chroma/data
    volumes:
      - ./storage/chroma_data:/chroma/data
    restart: unless-stopped

  neo4j:
    image: neo4j:5.18.0-community
    container_name: nexus-graph-neo4j
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/MustChangePassword2026!
      - NEO4J_PLUGINS=["apoc"]
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*
      - NEO4J_dbms_security_procedures_allowlist=apoc.*
    volumes:
      - ./storage/neo4j_data:/data
    restart: unless-stopped

  redis:
    image: redis:7.2-alpine
    container_name: nexus-cache-redis
    ports:
      - "6379:6379"
    volumes:
      - ./storage/redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    container_name: nexus-audit-postgres
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=nexus_admin
      - POSTGRES_PASSWORD=SecureAuditPassword2026!
      - POSTGRES_DB=nexus_telemetry
    volumes:
      - ./storage/pg_data:/var/lib/postgresql/data
    restart: unless-stopped

```

### 4.5 Runtime Environment Configuration Declarations (`.env`)

```env
# Global System Directives
ENVIRONMENT=development
LOG_LEVEL=INFO

# Third Party LLM Provision Coordinates
GOOGLE_API_KEY=AIzaSyYourDecoupledGoogleADKKeyHere_2026

# Docker Container local port matching endpoints
CHROMA_API_URL=http://localhost:8001
NEO4J_BOLT_URL=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=MustChangePassword2026!
REDIS_URL=redis://localhost:6379/0
POSTGRES_DSN=postgresql+psycopg2://nexus_admin:SecureAuditPassword2026@localhost:5432/nexus_telemetry

# ADK Telemetry Flag tracking configurations
ADK_ENABLE_OBSERVABILITY=true
ADK_TRACE_HOST=0.0.0.0
ADK_TRACE_PORT=4317

```

---

## 5. Granular, Phased Implementation Schedule

### Phase 1: Environment Assembly & Local Cluster Instantiations

* [ ] Execute system initialization command sequences via `uv init --workspace`. Create empty project scopes matching `frontend/` and `backend/` folders.
* [ ] Populated the target directory with files matching structural layout manifests for `pyproject.toml`, `pyproject.toml` configurations, and local system environments `.env`.
* [ ] Verify matching file infrastructure by executing command loop structures targeting data generation tracks:
```bash
mkdir -p storage/chroma_data storage/neo4j_data storage/pg_data storage/redis_data

```


* [ ] Run `docker compose up -d` to spin up the container infrastructure. Verify port accessibility using terminal validation tooling:
```bash
nc -zvw3 localhost 7687 && nc -zvw3 localhost 8001

```



### Phase 2: Native ADK 2.0 Functional Tooling & Core Agents Pool

* [ ] Build low-level infrastructure singletons within `backend/src/infrastructure/` ensuring thread-safe pool management wrappers for Bolt driver interfaces.
* [ ] Draft explicit type-hinted functional definitions inside `backend/src/tools/` using docstrings to let the ADK engine interpret them automatically:
```python
def query_vector_space(query_text: str, limit: int = 5) -> list[str]:
    """Queries the local containerized vector collection for proximity semantic search records."""
    ...

```


* [ ] Inject strict system configuration prompts within `backend/src/core/prompts.py`, isolating variable behaviors from the code logic.
* [ ] Scaffold agent references inside `backend/src/core/agents.py`, explicitly defining required tools and engine backings for each agent.

### Phase 3: Ingestion Graph Construction State Machine

* [ ] Map out the state graph flow configuration within `backend/src/core/workflows/ingestion.py` using `adk.Workflow`.
* [ ] Programmatically link operational nodes across the sequential extraction path: `START` $\rightarrow$ `Parser` $\rightarrow$ `Chunker` $\rightarrow$ `Proposer` $\rightarrow$ `Extractor` $\rightarrow$ `Validator` $\rightarrow$ `Indexer` $\rightarrow$ `END`.
* [ ] Verify the indexing process by uploading a raw document file and inspecting the Neo4j relational graph browser at `http://localhost:7474` to confirm nodes are deduplicating correctly via `MERGE` patterns.

### Phase 4: Runtime Retrieval, Knowledge Fusion, & Complexity Routing

* [ ] Build the stateful conversational tracking engine in `backend/src/core/workflows/reasoning.py`.
* [ ] Code the mathematical Reciprocal Rank Fusion matrix array handler inside the context integration logic to merge graph outputs and vector text windows smoothly.
* [ ] Build the complexity model router to check graph trajectory weights, ensuring requests scale from low-latency local execution up to deep cloud processing fallback paths.

### Phase 5: Streamlit Interface Integration & Master Session Testing

* [ ] Build out the FastAPI application endpoints inside `backend/src/main.py` using asynchronous streaming blocks.
* [ ] Code the Streamlit presentation interface layout inside `frontend/app.py` using network endpoints (`httpx` and `websockets`) to display outputs without importing core database drivers.
* [ ] Run the environment initialization tracking script `run.sh`, spin up the standalone **ADK Web Studio** framework, and evaluate system stability across multi-stage chat history loops.

---

## 6. Technical Constraints & Code-Level Guardrails

* **Zero-Footprint UI Rule**: `frontend/app.py` must never import `google.adk`, `chromadb`, or `neo4j`. Any change to UI views must pass through the FastAPI gateway network layer.
* **Deduplicated Storage Updates**: Every update to the Neo4j knowledge base must run via transaction-controlled Cypher `MERGE` scripts. Do not use direct `CREATE` statements to prevent duplicate relational patterns.
* **Strict Asynchronous Data Streaming**: Long-running data lookups and heavy agent loops must use asynchronous methods to prevent blocking the WebSocket execution path during runtime conversation tasks.