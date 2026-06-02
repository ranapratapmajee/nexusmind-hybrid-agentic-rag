import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

# =========================================================
# LOAD ENV
# =========================================================
load_dotenv()

# =========================================================
# LOAD YAML
# =========================================================
CONFIG_PATH = Path(__file__).parent / "config.yaml"

with open(CONFIG_PATH, "r") as f:
    y = yaml.safe_load(f)

# =========================================================
# ENV (SECRETS / OVERRIDES)
# =========================================================
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# DATABASE
CHROMA_HOST = os.getenv("CHROMA_HOST", "127.0.0.1")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "nexusmind_knowledge")

# PORTS
API_PORT = int(os.getenv("API_PORT", y["system"]["api_port"]))
UI_PORT = int(os.getenv("UI_PORT", y["system"]["ui_port"]))

# MODELS
ROUTER_MODEL = os.getenv("ROUTER_MODEL", "llama3")
SYNTHESIS_MODEL = os.getenv("SYNTHESIS_MODEL", "llama3")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

# API KEYS
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# LLM CONFIG
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", y["llm"]["temperature"]))
MAX_TOKENS = int(os.getenv("MAX_TOKEN_BUDGET", y["llm"]["max_tokens"]))

# =========================================================
# YAML CONFIG
# =========================================================
APP_NAME = y["app"]["name"]
APP_VERSION = y["app"]["version"]
ASSISTANT_NAME = y["app"].get("assistant", "Nexa")

RAG_TOP_K = y["rag"]["top_k"]
CHUNK_SIZE = y["rag"]["chunk_size"]
CHUNK_OVERLAP = y["rag"]["chunk_overlap"]

MAX_MESSAGES = y["memory"]["max_messages"]

ENABLE_CALCULATOR = y["tools"]["calculator"]
ENABLE_WEB_SEARCH = y["tools"]["web_search"]
