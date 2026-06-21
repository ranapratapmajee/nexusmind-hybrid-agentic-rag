# NexusResearch 🤖

NexusResearch is a production-grade, local-first **Graph-Driven Hybrid Retrieval-Augmented Generation (GraphRAG)** AI Agent framework optimized for Apple Silicon hardware.

Instead of isolating context retrieval into standard isolated text matching, the system utilizes an asynchronous dual-engine matrix (ChromaDB for semantic vector coordinates + Neo4j for deterministic multi-hop knowledge connections). The architecture prioritizes a cost-efficient, low-latency execution flow, keeping computation completely local using MLX runtimes unless extreme structural complexity demands cloud reasoning fallbacks.

---

## 🏗️ System Architecture & Lifecycle Topology

The system splits execution into clear boundaries: **User Interface Layout**, **Deterministic Intent Routing Control**, **Asynchronous Dual-Core Retrieval**, and **Compute Layer Selection**. 

Below is the dynamic layout mapping your specific control and agent execution flow:

```text
       [ User Query Interface Stream (Streamlit UI) ]
                             │
                             ▼
               ┌───────────────────────────┐
               │    ControlRouter Gate     │
               └─────────────┬─────────────┘
                             │
            deterministic_route_check(query)
                             │
     ┌───────────────────────┼────────────────────────┐
     ▼                       ▼                        ▼
[ CASUAL_CHITCHAT ]   [ GRAPH_SEARCH ]         [ STANDARD_RAG / DYNAMIC ]
     │                       │                        │
     │                       ▼                        ▼
     │               Force Graph Context     Engage Parallel Fetches
     │                       │                        │
     ▼                       └───────────┬────────────┘
Bypass DB Layers                         │
     │                                   ▼
     │                      ┌──────────────────────────┐
     │                      │  asyncio.run(retriever)  │
     │                      └────────────┬─────────────┘
     │                                   │
     │                  ┌────────────────┴────────────────┐
     │                  ▼                                 ▼
     │          ┌────────────────┐                ┌────────────────┐
     │          │  ChromaDB TopK │                │   Neo4j Multi  │
     │          │  Vector Search │                │   Hop Cypher   │
     │          └───────┬────────┘                └───────┬────────┘
     │                  │                                 │
     │                  └────────────────┬────────────────┘
     │                                   ▼
     │                       [ Fused Context Block ]
     │                                   │
     │                        determine_compute_target()
     │                                   │
     │                         ┌─────────┴─────────┐
     │                         ▼                   ▼
     │                 [ Complexity LOW ]  [ Complexity HIGH ]
     │                         │                   │
     ▼                         ▼                   ▼
(MLX Local Engine)     (MLX Local Engine)  (Gemini Cloud Engine)
 [Qwen-2.5-Coder]       [Qwen-2.5-Coder]     [gemini-2.5-flash]
     │                         │                   │
     └─────────────────────────┼───────────────────┘
                               ▼
                    [ Synthesized UI Response ]

```

### The 4 Execution Phases:

1. **Control Routing Gate (`ControlRouter`)**: Intercepts queries instantly using lightweight token-matching. If a greeting or basic chitchat phrase is flagged, it returns `CASUAL_CHITCHAT` and forces an instant shortcut straight to local compilation, completely bypassing database read I/O operations.
2. **Parallel Retrieval Layer (`HybridRetriever`)**: If the query requires factual lookup, it spins up an asynchronous task envelope. ChromaDB computes vector distances via Apple Silicon GPU cores (`mps`), while Neo4j simultaneously scans entity relationships.
3. **Context Fusion Layer (`NexusResearchAgent`)**: Combines retrieved text strings and graph assertions into a structured workspace block, maintaining metadata attribution records.
4. **Compute Target Selection**: Inspects context token weights and graph connectivity dimensions. If structural complexity is low ($< 5$ linked graph nodes), it executes locally to preserve privacy and cloud API limits. If structural complexity is highly dense ($> 5$ linked graph nodes), it activates the premium cloud fallback model.

---

## 📁 Repository Directory Blueprint

This repository is organized into strict, decoupled domains separating infrastructure configuration, persistence storage, and programmatic logic layers:

```text
.
├── PLANNING.md              # Long-term milestones and active sprint tracker
├── README.md                # System documentation, architecture maps, and launch gates
├── run.sh                   # Unified master startup script (Docker check + Streamlit)
├── ingest_book.py           # Automated AI-powered text to graph extraction script
├── test.py                  # Sandbox integration test validation cradle script
├── docker-compose.yaml      # Multi-container cluster layout mapping (Neo4j & ChromaDB)
├── pyproject.toml           # Modern package blueprint properties declaration
├── uv.lock                  # Lockfile enforcing exact deterministic library builds
├── config/
│   ├── config.yaml          # System network parameters, port assignments, and models configuration
│   └── settings.py          # Strict environment evaluation layer enforced by Pydantic
├── data/                    # Local storage drop-zone for text documents and target PDF books
├── storage/                 # Data persistence directories mounted out of Docker engines
│   ├── chroma/              # SQLite indices and raw coordinate binaries
│   └── neo4j/               # Relational data blocks, authorization paths, and transaction logs
└── app/                     # Framework source code domain
    ├── main.py              # Central application initialization connection injector
    ├── prompts.py           # Global directory for system rules and instructions
    ├── agents/
    │   └── research_agent.py # Context orchestration loop coordinator
    ├── control/
    │   └── router.py        # Intent interpreter and compute cost optimizer router
    ├── ingestion/
    │   ├── chunker.py       # Text window sliding partition manager
    │   ├── pdf_loader.py    # PyPDF extraction extraction driver
    │   ├── vector_ingestor.py # Chroma DB chunk storage manager
    │   └── graph_ingestor.py  # Neo4j APOC Cypher transaction manager
    ├── retrieval/
    │   ├── vector_retriever.py # Chroma top-k vector extraction interface
    │   ├── graph_retriever.py  # Cypher graph link explorer
    │   └── hybrid_retriever.py # Asynchronous retrieval fusion coordinator
    ├── services/
    │   ├── chroma_service.py   # Low-level vector socket manager
    │   ├── neo4j_service.py    # Active transactional bolt connection driver
    │   ├── embedding_service.py # Native Hugging Face sentence-transformers embedding manager
    │   └── llm_service.py      # Dual-endpoint generation client adapter (MLX & Gemini)
    └── ui/
        └── streamlit_app.py    # Interface presentation application dashboard

```

---

## ⚡ Quick Start Protocol

### 1. Launch Infrastructure Stack

Ensure your Docker runtime configuration environment is active (Colima/Docker Desktop), then bring up your background engine containers from the root workspace folder:

```bash
docker compose up -d

```

### 2. Configure Environment Parameters

Create a `.env` file at the root of the repository to feed your access configurations securely:

```ini
GEMINI_API_KEY=AIzaSy...YourSecretKey
NEO4J_PASSWORD=********

```

### 3. Grant Executive Launcher Permissions

Configure permission controls to make the startup automation script operational:

```bash
chmod +x run.sh

```

### 4. Execute the Unified Launch Routine

Execute the main launcher script. This wrapper script verifies database states, sets log suppression filters, patches the Streamlit file-watcher tracking bug, and brings up your interface workspace instantly:

```bash
./run.sh

```

---

## 📚 Dynamic Knowledge Graph Ingestion Workflow

To ingest deep reference documentation (like the pre-loaded **Abhinav Kimothi GraphRAG Guide** inside `/data`), run the automated structural extractor:

```bash
uv run ingest_book.py

```

### What happens under the hood:

1. **Semantic Vector Indexing**: The file is parsed into pages and vectorized locally on your MacBook's hardware GPU (`mps` acceleration) using `nomic-embed-text-v1.5` at **768 dimensions**, then stored in ChromaDB.
2. **AI Triplet Mining Loop**: The text windows pass through a cloud processing step where core concepts are converted into clean structured tracking entities (e.g., `CHROMA_DB` $\rightarrow$ `STORES` $\rightarrow$ `VECTOR_EMBEDDINGS`) and written to your Neo4j container.

---

## 🔍 Visualizing the Knowledge Graph

To view, trace, and explore your generated entity-relationship network visually:

1. Open your browser and navigate to the Neo4j Dashboard interface at **`http://localhost:7474`**.
2. Connect using the credentials configured in your system configuration parameters:
* **Connection URL**: `bolt://localhost:7687`
* **Username**: `neo4j`
* **Password**: `********`


3. Enter this query in the workspace terminal command bar to view the visual graph web:

```cypher
MATCH (source:Entity)-[relationship]->(target:Entity) 
RETURN source, relationship, target 
LIMIT 150;


MATCH (n)
OPTIONAL MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 300


```

*Tip: Click the `Entity` label badge at the top of the result panel and change the display property label setting to **`name`** to show human-readable text labels on your screen circles!*


---
