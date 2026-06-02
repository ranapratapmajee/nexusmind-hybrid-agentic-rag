# 🚀 NexusMind: Intelligent Hybrid LLM Orchestrator with RAG & Agentic Routing  
### *An AI system that thinks before it responds — intelligently routing, reasoning, and executing every query across LLMs, RAG, and tools.*

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red)
![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![Status](https://img.shields.io/badge/Status-Active-success)

---

## 🧠 What is NexusMind?

**NexusMind** is a production-grade, hybrid AI orchestration system that intelligently routes, optimizes, and executes user queries across local models, retrieval systems, tools, and cloud LLMs.

It is designed to go beyond traditional chatbots by introducing a decision-driven AI architecture that determines how each query should be solved before generating a response.

At its core, NexusMind powers **Nexa**, a smart AI assistant that behaves like a system-level orchestrator rather than a simple LLM wrapper.

---

## 🤖 Meet Nexa

**Nexa** Nexa is the user-facing AI chatbot powered by NexusMind.

Unlike traditional assistants, Nexa:

- Routes queries intelligently (local vs RAG vs tools vs cloud)
- Optimizes token usage and cost
- Uses memory-aware conversations
- Ensures structured, grounded responses

---

## 🧠 Core Philosophy

> **"Don’t send every query to a large model. Decide, optimize, and then execute."**

Every request is evaluated for:
- Complexity
- Intent
- Cost efficiency
- Context availability

---

## 🏗️ Architecture (Current + Future Vision)

### 🔷 CURRENT ARCHITECTURE (Implemented)

```text
User (Nexa UI - Streamlit)
        │
        ▼
┌────────────────────────────┐
│      FastAPI Server        │
│   (Streaming Gateway API)  │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────────────┐
│   Orchestrator (NexusMind Core)    │
│   - State Manager                  │
│   - Context Manager                │
│   - Session Memory Layer           │
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────┐
│     Router Agent           │
│ (Intent + Complexity + Cost)│
└───────┬─────────┬──────────┘
        │         │
        │         │
        ▼         ▼
┌────────────┐  ┌────────────────┐
│ Local LLM  │  │ RAG (ChromaDB) │
│ (Ollama)   │  │ Retrieval      │
└────────────┘  └────────────────┘
        │
        ▼
┌────────────────────────────┐
│ Tool System (Registry)     │
│ - Calculator               │
│ - Future tools             │
└────────────────────────────┘
        │
        ▼
┌────────────────────────────┐
│ Middleware Layer           │
│ - Token optimization       │
│ - Context trimming         │
│ - Logging / Guardrails     │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ Synthesis Agent            │
│ (Final Response Builder)   │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ Streamlit UI (Nexa)        │
└────────────────────────────┘
```

### 🔮 FUTURE ARCHITECTURE (Planned Evolution)

```text
                     ┌──────────────────────┐
                     │   Web Search Layer   │
                     │ (Free-first scraping)│
                     └──────────┬───────────┘
                                │
                 ┌──────────────▼────────────────┐
                 │ Multi-Agent Orchestration Hub │
                 │  - Planner Agent              │
                 │  - Critic Agent              │
                 │  - Tool Agent                │
                 │  - Memory Agent              │
                 └──────────────┬────────────────┘
                                │
        ┌───────────────────────┼────────────────────────┐
        ▼                       ▼                        ▼
┌──────────────┐     ┌─────────────────┐     ┌──────────────────┐
│ Local LLM     │     │ RAG Expansion   │     │ Web Scraping     │
│ (Fast tasks)  │     │ (Hybrid search) │     │ (Amazon/Flipkart)│
└──────────────┘     └─────────────────┘     └──────────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │ Cloud LLM Gateway    │
                    │ (Gemini / OpenAI)    │
                    │ ONLY fallback layer   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Critic / Validator   │
                    │ (Hallucination check)│
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Nexa UI (Streamlit)  │
                    └──────────────────────┘
```

---

## ⚙️ Tech Stack

### 🧠 LLM Layer

* Local: Ollama (`qwen2.5-coder:3b-instruct`)
* Embeddings: `nomic-embed-text`
* Cloud (optional fallback): Gemini / OpenAI

### 📚 RAG System

* ChromaDB (Dockerized)
* Semantic chunking + retrieval ranking

### 🌐 Backend

* FastAPI (async streaming API)

### 🧪 Frontend

* Streamlit (Nexa chat UI)

### ⚡ Infrastructure

* Docker (vector DB)
* uv (Python dependency manager)

---

## 📁 Project Structure

```text
nexusmind-hybrid-agentic-rag/
├── config/                # Central config loader (env + yaml)
├── frontend/              # Nexa UI (Streamlit)
├── src/
│   ├── core/              # Orchestrator + context manager
│   ├── agents/            # Router + synthesis agents
│   ├── rag/               # Retrieval system
│   ├── tools/             # Plugin tools
│   ├── database/          # ChromaDB integration
│   ├── memory/            # SQLite memory system
│   ├── pipeline/          # Ingestion + embedding pipeline
│   ├── api/               # FastAPI backend
│
├── data/                  # Input documents (PDFs, text)
├── docker-compose.yaml    # ChromaDB infra
├── run.sh                 # One-click startup
└── README.md
```

---

## 🔥 Key Features

### 🧠 Intelligent Routing Engine

* Chooses best execution path dynamically
* Avoids unnecessary LLM calls

### 🔀 Hybrid LLM Strategy

* Local-first architecture
* Cloud fallback only when required

### 📚 RAG Pipeline

* PDF ingestion
* Semantic retrieval via ChromaDB

### 🔌 Tool System

* Calculator (active)
* Web search (future: scraping-based)
* Extensible plugin architecture

### 🧠 Memory System

* Session-based SQLite memory

### ⚡ Streaming Responses

* Real-time response generation

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
uv sync
```

### 2. Start vector DB

```bash
docker-compose up -d
```

### 3. Run full system

```bash
./run.sh
```

---

## 🌐 Access

* 🖥️ UI → [http://localhost:8502](http://localhost:8502)
* ⚡ API → [http://localhost:9000](http://localhost:9000)

---

## 📥 Ingest Data

```bash
uv run src/pipeline/ingest.py
```

---

## ⚙️ Environment Variables

```env
ENVIRONMENT=development

CHROMA_HOST=127.0.0.1
CHROMA_PORT=8000
CHROMA_COLLECTION_NAME=nexusmind_knowledge

API_PORT=9000
STREAMLIT_PORT=8502

ROUTER_MODEL=qwen2.5-coder:3b-instruct
SYNTHESIS_MODEL=qwen2.5-coder:3b-instruct
EMBEDDING_MODEL=nomic-embed-text

MAX_TOKEN_BUDGET=4000
LLM_TEMPERATURE=0.0

GEMINI_API_KEY=
OPENAI_API_KEY=
```

---

## 🧠 What This Project Demonstrates

* Agentic AI system design
* Hybrid RAG architecture
* LLM routing strategies
* Cost-aware AI engineering
* Production-grade backend structure

---

## 🚀 Roadmap

### Phase 1 (Current)

* RAG pipeline
* Router + orchestrator
* Tool system (basic)

### Phase 2 (Next)

* Web search (free scraping-based)
* Better middleware optimization
* Context compression

### Phase 3 (Advanced)

* Multi-agent planner
* Autonomous task execution
* Smart tool chaining

### Phase 4 (Future Vision)

* E-commerce scraping (Amazon / Flipkart)
* Fully autonomous agent workflows
* Self-improving memory system
* Multimodal input support

---

## 🧠 Key Insight

> **NexusMind is the brain.
> Nexa is the voice.**

---

## 👨‍💻 Author

**Ranapratap Majee**
