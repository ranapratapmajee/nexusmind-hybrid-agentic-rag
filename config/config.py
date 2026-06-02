import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

# =========================================================
# LOAD ENV
# =========================================================
load_dotenv()

# =========================================================
# LOAD YAML (SAFE)
# =========================================================
CONFIG_PATH = Path(__file__).parent / "config.yaml"

if not CONFIG_PATH.exists():
    raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")

with open(CONFIG_PATH, "r") as f:
    y = yaml.safe_load(f) or {}

# =========================================================
# ENVIRONMENT
# =========================================================
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# =========================================================
# DATABASE
# =========================================================
CHROMA_HOST = os.getenv("CHROMA_HOST", "127.0.0.1")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "nexusmind_knowledge")

# =========================================================
# PORTS
# =========================================================
API_PORT = int(os.getenv("API_PORT", y.get("system", {}).get("api_port", 9000)))
UI_PORT = int(os.getenv("UI_PORT", y.get("system", {}).get("ui_port", 8502)))

# =========================================================
# MODELS
# =========================================================
ROUTER_MODEL = os.getenv("ROUTER_MODEL", "llama3")
SYNTHESIS_MODEL = os.getenv("SYNTHESIS_MODEL", "llama3")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

# =========================================================
# EMBEDDING CONFIG (NEW - IMPORTANT FIX)
# =========================================================

RAG_EMBEDDING_PROVIDER = y.get("rag", {}).get("embedding", {}).get("provider", "ollama")
RAG_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", y["embedding"]["model"])
RAG_EMBEDDING_DIMENSION = int(
    os.getenv("EMBEDDING_DIMENSION", y["embedding"]["dimension"])
)

# =========================================================
# API KEYS
# =========================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# =========================================================
# LLM CONFIG
# =========================================================
TEMPERATURE = float(
    os.getenv("LLM_TEMPERATURE", y.get("llm", {}).get("temperature", 0.0))
)

MAX_TOKENS = int(
    os.getenv("MAX_TOKEN_BUDGET", y.get("llm", {}).get("max_tokens", 2048))
)

# =========================================================
# YAML CONFIG (SAFE ACCESS)
# =========================================================
APP_NAME = y.get("app", {}).get("name", "NexusMind")
APP_VERSION = y.get("app", {}).get("version", "1.0.0")
ASSISTANT_NAME = y.get("app", {}).get("assistant", "Nexa")

RAG_TOP_K = y.get("rag", {}).get("top_k", 5)
CHUNK_SIZE = y.get("rag", {}).get("chunk_size", 300)
CHUNK_OVERLAP = y.get("rag", {}).get("chunk_overlap", 50)

MAX_MESSAGES = y.get("memory", {}).get("max_messages", 50)

ENABLE_CALCULATOR = y.get("tools", {}).get("calculator", True)
ENABLE_WEB_SEARCH = y.get("tools", {}).get("web_search", True)
