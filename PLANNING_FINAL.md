# NexusResearch V2 — Enterprise Cognitive Architecture & Implementation Ledger

This document serves as the master engineering design blueprint, data state ledger, and phased implementation lifecycle tracker for the NexusResearch V2 multi-agent platform built natively on top of the **Google Agent Development Kit (ADK 2.0)**.

---

## 1. System Topology & Architectural Flows

NexusResearch V2 implements a high-performance hybrid deployment model. The entire compute layer—including the Streamlit UI, the FastAPI gateway, and the stateful multi-agent execution graphs powered by Google ADK 2.0—runs natively on the host machine using a `uv` virtual workspace. This eliminates virtualization overhead for LLM token streams and provides sub-millisecond inter-agent communication. 

All stateful storage engines and background analytical infrastructure run in completely isolated Docker containers.

### 1.1 Macro-System Architecture Flowchart

```mermaid
graph TD
    %% Component Style Classes
    classDef client fill:#2d3436,stroke:#dfe6e9,stroke-width:2px,color:#fff;
    classDef orchestrator fill:#0984e3,stroke:#74b9ff,stroke-width:2px,color:#fff;
    classDef control fill:#6c5ce7,stroke:#a29bfe,stroke-width:2px,color:#fff;
    classDef workflow fill:#00b894,stroke:#55efc4,stroke-width:2px,color:#fff;
    classDef agent fill:#e17055,stroke:#fab1a0,stroke-width:2px,color:#fff;
    classDef tool fill:#fdcb6e,stroke:#ffeaa7,stroke-width:2px,color:#2d3436;
    classDef storage fill:#b2bec3,stroke:#dfe6e9,stroke-width:2px,color:#2d3436;
    classDef compute fill:#d63031,stroke:#ff7675,stroke-width:2px,color:#fff;

    %% Presentation & Orchestration Layer
    UI[Streamlit UI Dashboard]:::client --> |Submits Payload Stream| API[FastAPI Delivery Gateway]:::orchestrator
    API --> Master[Master NexusOrchestrator]:::orchestrator
    Master --> |Inspects Structural Properties| Gate{Control Engine Routing Gate}:::control

    %% Intent Splitting & Short Circuits
    Gate --> |Payload = Local File Path Pointer| IngestFlow[ADK Ingestion Workflow]:::workflow
    Gate --> |Intent Match = CASUAL_CHITCHAT| DirectMLX[Direct Local Compute via MLX]:::compute
    Gate --> |Intent Match = RESEARCH_SEARCH| RuntimeFlow[ADK Chat Reasoning Workflow]:::workflow

    %% Ingestion Pipeline State Machine
    subgraph Ingestion_Pipeline ["Separate Ingestion Pipeline (Background Graph Construction)"]
        IngestFlow --> Parser[Parser Agent]:::agent
        Parser --> |Extract Layout Matrix| Chunker[Chunking Agent]:::agent
        Chunker --> |Generate Sliding Token Windows| Proposer[Entity Extraction Agent]:::agent
        Proposer --> |Mine Fact Triplet Candidates| Extractor[Relationship Extractor]:::agent
        Extractor --> |Format Directional Assertions| Validator[KG Validation Agent]:::agent
        Validator --> |Enforce Structural Quality| Indexer[Indexing Agent]:::agent
    end

    %% Runtime Multi-Agent Pipeline
    subgraph Reasoning_Pipeline ["Stateful Reasoning & Multi-Hop Query Execution Loop"]
        RuntimeFlow --> Guardrail[Governance/Guardrail Agent]:::agent
        Guardrail --> |Passes Safety Verification| Planner[Planner Agent]:::agent
        
        Planner --> |Complexity Signal Detected| Expander[Query Expander Agent]:::agent
        Planner --> |Heuristic Fast Path Match| Retrieval[Retrieval Agent]:::agent
        Expander --> Retrieval
        
        %% Protocol-Driven ADK Tool Registry Interface
        subgraph ADK_Tool_Registry ["MCP-Style Protocol Tool Registry"]
            Retrieval --> |Invoke Tool Execution| CTool[Chroma Vector Tool]:::tool
            Retrieval --> |Invoke Tool Execution| NTool[Neo4j Relational Tool]:::tool
            Retrieval --> |Invoke Tool Execution| WTool[Web Search Tool]:::tool
        end
        
        CTool & NTool & WTool --> |Stream Raw Extraction Blocks| Fusion[Knowledge Fusion Agent]:::agent
        
        %% Context Aggregation & Fallbacks
        Fusion --> |Reciprocal Rank Fusion & Deduplication| Reasoner[Reasoning Agent]:::agent
        Reasoner --> |Cross-Source Synthesized Context Pack| ModelGate{Complexity Model Router}:::control
    end

    %% Persistent Storage Topology
    Indexer --> |Cypher Transactional MERGE| Neo4j[(Neo4j Graph Database Cluster)]:::storage
    Indexer --> |Persistent Parquet / HNSW Tables| Chroma[(ChromaDB Vector Store Container)]:::storage
    
    Neo4j -.-> |Bolt Socket Data Fetch| NTool
    Chroma -.-> |HTTP Vector Extraction| CTool

    %% Inference Computation Targets
    ModelGate -- "Low Complexity (Context Nodes <= 5)" --> LocalMLX[MLX Local Engine: Qwen-2.5]:::compute
    ModelGate -- "High Complexity (Context Nodes > 5)" --> GeminiCloud[Gemini Cloud Engine: 2.5 Flash]:::compute

    DirectMLX & LocalMLX & GeminiCloud --> |Format Answers + Markdown Citations| UI

```

### 1.2 Networking Topology Matrix

| Service Component | Environment | Internal Binding Address | Exposed Host Port | Transport Protocol | Primary Purpose |
| --- | --- | --- | --- | --- | --- |
| **Streamlit Interface** | Native Host Workspace | `127.0.0.1` | `8501` | HTTP / WebSocket | User dashboard rendering and file selection |
| **FastAPI Gateway** | Native Host Workspace | `0.0.0.0` | `8000` | HTTP / WebSocket | Unified network delivery and orchestration |
| **ChromaDB Core** | Docker Container | `0.0.0.0` | `8001` | HTTP REST | Semantic vector search storage |
| **Neo4j Graph Database** | Docker Container | `0.0.0.0` | `7474` (HTTP) / `7687` (Bolt) | HTTP / Bolt Binary | Relational knowledge graph persistence |
| **Redis Cache** | Docker Container | `0.0.0.0` | `6379` | TCP Telnet | Session state boundaries and prompt cache |
| **PostgreSQL DB** | Docker Container | `0.0.0.0` | `5432` | TCP SQL | Persistent ADK telemetry metric logs |
| **ADK Web Studio** | Native Loopback | `0.0.0.0` | `4317` | gRPC OpenTelemetry | Multi-agent execution graph visualization |

---

## 2. Standardized Enterprise Project Directory Structure

This layout groups related components together and abstracts external tools. The application core code uses the network gateway layer to interact with the frontend, and accesses storage infrastructure exclusively through an MCP-style tool registry.

```text
nexusmind-platform/
├── docker-compose.yaml          # Infrastructure configurations (Neo4j APOC, ChromaDB, Redis, Postgres)
├── pyproject.toml               # Universal master uv project pinning workspace specifications
├── uv.lock                      # Enforced deterministic package environment lockfile
├── run.sh                       # Automation boot script (Brings up containers, FastAPI, and Streamlit)
├── .env                         # Master credential store (API keys, connection strings, system flags)
├── PLANNING.md                  # Comprehensive architectural blueprints and milestones (This Document)
├── README.md                    # Technical developer onboarding manual
│
├── config/                      # Environment Mapping & Application Parameters
│   ├── config.yaml              # Threshold settings, model mappings, and structural margins
│   └── settings.py              # Configuration schemas enforced by Pydantic V2 settings
│
├── data/                        # Local File System Volumes
│   ├── input/                   # Dedicated drop-zone for text analysis files and source PDFs
│   └── output/                  # Storage target for generated research reports and system logs
│
├── storage/                     # Isolated Container Data Mount Points (Ignored by Git)
│   ├── chroma_data/             # SQLite coordination maps and HNSW index spaces
│   ├── neo4j_data/              # Relational records blocks and server transaction journals
│   ├── pg_data/                 # Event relational blocks tracking ADK run telemetry
│   └── redis_data/              # In-memory database dump snapshot records
│
├── frontend/                    # TIER 1: Lean Presentation Layer
│   ├── ui/                      # Presentation components (views, layouts, rendering blocks)
│   └── app.py                   # Pure interface logic; speaks to backend via network endpoints only
│
└── backend/                     # TIER 2 & 3: Network Delivery & ADK Cognitive Intellect
    ├── main.py                  # API initialization script; hooks up OpenTelemetry tracing
    │
    ├── api/                     # Network Transport Layer
    │   ├── __init__.py
    │   ├── dependencies.py      # Resource injection modules (Redis connections, DB handles)
    │   └── routes/
    │       ├── chat.py          # WebSocket loops streaming real-time multi-agent responses
    │       ├── health.py        # System health checks and status diagnostics
    │       └── ingest.py        # Endpoints handling multipart file uploads
    │
    ├── infrastructure/          # Low-Level Driver Abstractions (Used only by Tools)
    │   ├── __init__.py
    │   ├── chroma_service.py    # Native HTTP configuration client wrapper for vector space collections
    │   ├── neo4j_service.py     # Thread-safe connection session management wrapper for Bolt connections
    │   └── pg_logger.py         # Relational schema tracking layer logging execution costs
    │
    ├── mcp/                     # Protocol-Driven Tool Registry (Infinite Capability Expansion)
    │   ├── __init__.py          # Bundles tools into standard exports for ADK agents
    │   ├── chroma_tools.py      # Type-hinted vector retrieval and entry insertion tools
    │   ├── neo4j_tools.py       # Analytical graph navigation and transaction execution tools
    │   └── web_tools.py         # Web query tools hooking into public search tools (e.g., DDG)
    │
    └── cognitive/               # Unified Multi-Agent Engine Core
        ├── __init__.py
        ├── agents.py            # Instantiates adk.Agent profiles with associated prompts and tools
        ├── prompts.py           # Completely isolated raw system instruction prompt variables
        ├── flow_ingest.py       # Asynchronous background graph construction workflow
        └── flow_runtime.py      # Stateful context-amplified multi-hop reasoning workflow

```

---

## 3. Deep Component Lifecycle Specifications

### 3.1 Structural Intent Routing Logic (`backend/backend/api/routes/`)

Operating before execution shifts to a token-heavy agent workflow, the API routing gateway runs quick, stateless evaluation rules on the user prompt to identify the correct processing path.

* **`FILE_UPLOAD`**: Triggered when a multipart boundary hits `/api/ingest`. The file payload is saved to `data/input/`, and the system spins up an isolated background worker thread to execute the `Asynchronous Ingestion Graph` without blocking the main event loop.
* **`CASUAL_CHITCHAT`**: Identifies standard greeting strings, conversational idioms, or brief questions. It bypasses database lookups and expensive cloud LLMs entirely, routing the request directly to an execution model running locally on the host device via MLX to keep network latency low.
* **`RESEARCH_SEARCH`**: The standard default path for complex information lookups. It sets up unique session transaction containers across the cache layers and activates the core `Stateful Reasoning Graph`.

### 3.2 The Governance & Guardrail Shield (`backend/backend/cognitive/`)

The **Governance/Guardrail Agent** is positioned directly at the `START` entry point of the reasoning workflow, acting as an automated safety check. It runs strict evaluation logic before passing data to downstream planners:

* **Prompt Injection Safeguards:** Scans incoming payloads for typical pattern bypass tricks, character escapes, or system override overrides.
* **PII Masking Filter:** Checks for matching structural entities like social security numbers, private emails, and phone configurations, dynamically replacing sensitive identifiers with encrypted placeholder tokens.
* **Workflow Short-Circuiting:** If a prompt fails safety checks, the agent updates the ADK execution state to a closed status, skips the planning and retrieval agents entirely, and routes directly to the finalization block to deliver a standard refusal message.

### 3.3 The Ingestion Pipeline (Asynchronous Graph Construction)

When raw text data enters the ingestion flow, it passes sequentially through an isolated multi-stage pipeline designed to parse layout features and index records cleanly:

1. **Parser Agent (`parser_agent_py`)**: Reads unformatted files from storage directories, extracting text blocks alongside structural page numbers, titles, and layout properties.
2. **Chunking Agent (`chunking_agent_py`)**: Partitions text segments into sliding token windows of 500 tokens, maintaining a trailing 10% overlap margin to preserve semantic flow across adjacent text blocks.
3. **Entity Extraction Agent (`entity_extractor_py`)**: Processes individual text windows to isolate key domain names, systems, categories, and descriptive tags.
4. **Relationship Extractor (`relationship_extractor_py`)**: Explores connection paths across extracted concepts, rendering factual claims as structured data arrays (`Source` $\rightarrow$ `VERB` $\rightarrow$ `Target`).
5. **KG Validation Agent (`validation_agent_py`)**: Inspects the extracted data streams to fix typical formatting issues, unclosed json elements, or orphaned references.
6. **Indexing Agent (`indexer_agent_py`)**: Writes dense text windows to ChromaDB and commits relational patterns to Neo4j using transaction-safe Cypher queries to keep data organized and deduplicated:
```cypher
MERGE (s:Entity {name: $source_name})
SET s.type = $source_type, s.updated_at = timestamp()
MERGE (t:Entity {name: $target_name})
SET t.type = $target_type, t.updated_at = timestamp()
MERGE (s)-[r:RELATION {type: $rel_type}]->(t)
SET r.weight = coalesce(r.weight, 0) + 1

```



### 3.4 The Knowledge Fusion Engine (`backend/backend/mcp/`)

To resolve information overlaps and balance data from multiple systems, the platform applies an algorithmic **Reciprocal Rank Fusion (RRF)** scoring matrix layer within the tool layer. When the `Retrieval Agent` queries vector store segments, relational graphs, and public web sources in parallel, the combined result streams are unified using a standardized ranking formula:

$$\text{RRF Score}(d \in D) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

Where $M$ represents the set of storage engines (Chroma proximity distances, Neo4j connection counts, and Web Search metrics), $r_m(d)$ represents the item's ordinal index position within a specific database query result stream, and $k$ represents a smoothing safety constant (defaulting to $60$).

The output list is sorted by final calculated relevance scores, dropping duplicate text snippets and filtering out information collisions before formatting the text payload for the reasoning model.

---

## 4. Master Configuration Manifest Files

### 4.1 Unified Project Virtual Environment Profile (`pyproject.toml`)

```toml
[project]
name = "nexusmind-platform"
version = "2.0.0"
description = "Enterprise Hybrid Local-Compute Multi-Agent Platform Built on Google ADK 2.0"
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
    "streamlit>=1.32.0"
]

[tool.uv]
managed = true

```

### 4.2 Dockerized Infrastructure Subsystem (`docker-compose.yaml`)

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

### 4.3 Runtime Environment Variables Credentials Layout (`.env`)

```env
# Global Execution Directives
ENVIRONMENT=development
LOG_LEVEL=INFO

# Central LLM Platform Token Keys
GOOGLE_API_KEY=AIzaSyYourDecoupledGoogleADKKeyHere_2026

# Storage Subsystem Connection Parameters
CHROMA_API_URL=http://localhost:8001
NEO4J_BOLT_URL=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=MustChangePassword2026!
REDIS_URL=redis://localhost:6379/0
POSTGRES_DSN=postgresql+psycopg2://nexus_admin:SecureAuditPassword2026@localhost:5432/nexus_telemetry

# OpenTelemetry Visual Diagnostic Tracing Parameters
ADK_ENABLE_OBSERVABILITY=true
ADK_TRACE_HOST=0.0.0.0
ADK_TRACE_PORT=4317

```

---

## 5. Granular, Phased Implementation Schedule

### Phase 1: Environment Assembly & Local Cluster Instantiations

* [ ] Initialize the workspace virtual layout using the dependency tracking tool: `uv init`.
* [ ] Generate the core configuration modules, mapping environment credentials to explicit Pydantic verification models inside `config/settings.py`.
* [ ] Setup host system mount points for local file processing and persistent storage logs:
```bash
mkdir -p storage/chroma_data storage/neo4j_data storage/pg_data storage/redis_data data/input data/output

```


* [ ] Boot up containerized services via `docker compose up -d` and run quick terminal integration checks to ensure all networking sockets are active.

### Phase 2: Native ADK 2.0 Functional Tooling & Core Agents Pool

* [ ] Code the baseline connection wrappers within `backend/src/infrastructure/` to handle background thread connection pooling for the graph database driver.
* [ ] Build out type-hinted functional components within the `backend/src/mcp/` folder, adding granular docstrings so the ADK runtime engine can analyze tool details automatically.
* [ ] Create the central multi-agent system layout inside `backend/src/cognitive/agents.py`, linking individual agent personas directly to their corresponding tool selections.

### Phase 3: Ingestion Graph Construction State Machine

* [ ] Build out the asynchronous pipeline graph logic within `backend/src/cognitive/flow_ingest.py` using `adk.Workflow`.
* [ ] Connect operational steps sequentially across the processing path: `START` $\rightarrow$ `Parser` $\rightarrow$ `Chunker` $\rightarrow$ `Proposer` $\rightarrow$ `Extractor` $\rightarrow$ `Validator` $\rightarrow$ `Indexer` $\rightarrow$ `END`.
* [ ] Test the pipeline end-to-end by uploading a mock PDF file to confirm text blocks map correctly to Chroma vector segments and create clean, deduplicated relations in the Neo4j graph viewer.

### Phase 4: Runtime Retrieval, Knowledge Fusion, & Complexity Routing

* [ ] Setup the runtime multi-agent conversation tracking logic within `backend/src/cognitive/flow_runtime.py`.
* [ ] Integrate the **Governance/Guardrail Agent** into the entry point of the reasoning workflow to act as an automated safety filter.
* [ ] Add the Reciprocal Rank Fusion matrix sorting algorithm within the retrieval tool layers to combine multi-source inputs into optimized context strings.
* [ ] Build out complexity routing checks to evaluate graph connections, dynamically balancing execution between low-latency local processing and comprehensive cloud LLM tasks.

### Phase 5: Streamlit Interface Integration & Master Session Testing

* [ ] Mount API routing layers within `backend/src/main.py` using asynchronous streaming loops.
* [ ] Code the presentation dashboard within `frontend/app.py` using simple network interaction libraries (`httpx` and `websockets`), keeping UI operations completely detached from internal core database frameworks.
* [ ] Launch the workspace orchestration initialization script `run.sh`, run live tracing checks inside **ADK Web Studio**, and verify thread management across long multi-turn agent conversations.

---

## 6. Technical Constraints & Code-Level Guardrails

* **The Infinite Scalability Contract:** All new capabilities, tools, or third-party service connections must be placed inside the `backend/src/mcp/` directory as structured python functions with explicit typing and docstrings. To add a capability to any agent, simply pass the function reference directly into the agent's `tools=[]` initialization array. No modifications should be made to core workflow loop files.
* **Zero-Footprint UI Boundary Rule:** The `frontend/app.py` file must never import `google.adk`, `chromadb`, or `neo4j`. Any adjustments to presentation parameters must pass exclusively through network interactions managed by the FastAPI delivery gateway.
* **Deduplicated Graph Commits:** Every single transactional update targeting the knowledge graph database must pass through strict Cypher `MERGE` statements. The use of standard `CREATE` command blocks is completely forbidden to prevent data duplication over time.
* **Strict Asynchronous Operations:** All long-running disk operations, remote API calls, and complex multi-agent calculation loops must use asynchronous methods to prevent blocking the WebSocket communication thread during user interactions.