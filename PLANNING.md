# NexusResearch — Architecture, Lifecycle Planning & Scale Strategy

This document serves as the master engineering ledger, design blueprint, and scale strategy for the NexusResearch GraphRAG environment.

---

## 1. Architectural Strategy & Lifecycle Mechanics

NexusResearch handles multi-source research tasks by executing an optimized, multi-engine routing lifecycle. Rather than treating vector distances and structural networks as separate entities, the system treats them as complementary dimensions of a single semantic layer.

### 1.1 Intent Interception & Parallel Ingestion Mechanics
Before triggering database lookups, queries pass through the `ControlRouter` gate. If conversational chatter or a standard greeting is matched, the engine fast-paths the query straight to local compute. This protects network resources and locks out external API quota drain entirely.

For true informational queries, the system engages an asynchronous pipeline:

```text
                  [ Runtime User Query ]
                             │
                             ▼
              ┌─────────────────────────────┐
              │   ControlRouter Intercept   │
              └──────────────┬──────────────┘
                             │
            deterministic_route_check(query)
                             │
     ┌───────────────────────┼────────────────────────┐
     ▼                       ▼                        ▼
[ CASUAL_CHITCHAT ]   [ GRAPH_SEARCH ]         [ STANDARD_RAG ]
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

```

### 1.2 Core Integration Fields

* **Primary Semantic Field**: Managed via a self-contained ChromaDB engine. Text arrays are converted into **768-dimensional normalized floating-point coordinate boundaries** using the `nomic-embed-text-v1.5` transformer architecture.
* **Relational Field**: Handled via a multi-hop Neo4j Graph topology instance. Concepts are parsed dynamically via structured LLM schema prompts that ingest content and output explicit directional triplet matrices (`Source` $\rightarrow$ `Relation` $\rightarrow$ `Target`).

---

## 2. Modular Implementation Roadmap

### Phase 1: Local Control & Fast-Path Ingestion (Completed)

* Enforce strict Pydantic environment configurations to catch missing configuration fields early.
* Implement token match intercepts within `ControlRouter` to isolate basic conversational chit-chat from technical documentation.
* Configure `pypdf` extraction sequences to feed long-context materials through local GPU accelerated embeddings (`mps` framework).

### Phase 2: Entity Graph Enrichment Loop (Current Sprint)

* Transition from manual relational seeds to automated AI triplet mining.
* Upgrade `LLMService` to ingest page text windows and extract structured JSON entity profiles using cloud endpoints for high reasoning accuracy.
* Implement entity deduplication inside `GraphIngestor` via conditional Cypher `MERGE` statements to avoid concept fragmentation.

### Phase 3: Graph-Driven Vector Context Expansion (Upcoming)

* Update `HybridRetriever` to extract unique entity nodes from the initial Neo4j multi-hop query.
* Trigger an immediate secondary vector expansion inside ChromaDB using those graph entities as terms. This captures contextually relevant text fragments that sit below the raw semantic cosine similarity barrier of the initial user query.
* Implement context ranking boundaries to remove duplicate indices when primary and secondary retrieval sweeps overlap.

---

## 3. Scale Plan & Future Production Hardening

To migrate this architecture from a local MacBook Air environment to a high-availability enterprise production stack, the system will evolve across three main pillars:

### 3.1 Distributed Infrastructure Decoupling

```text
[ Streamlit UI App ] ──► [ Traefik / Envoy Load Balancer ]
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
┌──────────────────────┐               ┌──────────────────────┐
│  Agent Worker Pods   │               │  Agent Worker Pods   │
│   (FastAPI/ADK)      │               │   (FastAPI/ADK)      │
└──────────┬───────────┘               └──────────┬───────────┘
           │                                      │
           └──────────────────┬───────────────────┘
                              ▼
            ┌─────────────────┴─────────────────┐
            ▼                                   ▼
┌──────────────────────┐             ┌──────────────────────┐
│ Chroma Distributed   │             │  Neo4j Causal Cluster│
│   Cluster (K8s)      │             │  (3-Node RAFT Group) │
└──────────────────────┘             └──────────────────────┘

```

* **Storage Tier Migration**: Replace the single-file Chroma SQLite implementation with a distributed **Chroma Cluster orchestration** deployed on Kubernetes, decoupling write-heavy ingestion workers from read-only search operations.
* **Graph Cluster Resilience**: Transition the standalone Neo4j Docker container into a **Neo4j Causal Cluster** configured with a 3-node Core RAFT group. This setup isolates intensive transactional graph ingestion writes to a master node while distributing search load across secondary read replicas.

### 3.2 High-Throughput Ingestion Pipelines

* **Asynchronous Message Bus**: Replace synchronous ingestion scripts (`ingest_book.py`) with an event-driven worker pool powered by **Celery and Redis/RabbitMQ**. Large books will stream onto a message queue, allowing multiple worker processes to parse, embed, and index distinct page arrays in parallel.
* **Local Embedding Cluster**: Scale out local extraction by shifting the embedding layer from single-workstation MPS weights onto a dedicated microservice cluster running **vLLM or Hugging Face Text Embeddings Inference (TEI)** across unified, network-accessible data center GPUs.

### 3.3 Graph Compaction & Community Clustering

* **Hierarchical Levenshtein Consolidation**: To combat graph pollution (e.g., preventing `VECTOR_RAG`, `VECTOR_RAG_SYSTEM`, and `RAG_PIPELINE` from spawning as three isolated circles), the system will introduce a backend deduplication engine. This worker will compute Levenshtein distance metrics and semantic token proximity, automatically merging duplicate aliases into unified master nodes.
* **Graph Louvain Community Clustering**: Implement **Leiden/Louvain community detection algorithms** via the Neo4j Graph Data Science (GDS) library. The ingestion engine will periodically analyze density patterns to cluster closely related entities into higher-level "Topic Communities," allowing the agent to generate high-level global summaries of entire libraries rather than just pulling local page references.
