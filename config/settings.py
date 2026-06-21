# config/settings.py

from __future__ import annotations

import os
import re
import tomllib
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field

# ============================================================
# Path Resolution Setup
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"

ENV_VAR_PATTERN = re.compile(r"\$\{(\w+)\}")

# ============================================================
# Environment Validation & Interpolation Workers
# ============================================================

def get_project_version() -> str:
    try:
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)
        return data.get("project", {}).get("version", "0.1.0")
    except Exception:
        return "0.1.0"


def load_dotenv_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.split("#")[0].strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


def interpolate_env_vars(raw_text: str) -> str:
    def replacer(match):
        var_name = match.group(1)
        return os.getenv(var_name, "")
    return ENV_VAR_PATTERN.sub(replacer, raw_text)

# ============================================================
# Data Model Structure Setup (Pydantic Validation Sections)
# ============================================================

class AppSection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str
    bot_name: str
    description: str
    version: str = Field(default_factory=get_project_version)


class ChromaSection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    host: str
    port: int
    collection_name: str


class Neo4jSection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    uri: str
    username: str
    password: str
    database: str


class LocalLLMSection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    base_url: str
    model: str


class GeminiSection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    api_key_env: str
    model: str


class ResearchSection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    top_k_vector_results: int
    top_k_graph_results: int
    max_web_results: int


class RagSection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    chunk_size: int
    chunk_overlap: int
    embedding_model: str


class PathsSection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    data_dir: str


class LoggingSection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    level: str = "INFO"

# ============================================================
# Orchestration Factory Settings
# ============================================================

class Settings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    app: AppSection
    chroma: ChromaSection
    neo4j: Neo4jSection
    local_llm: LocalLLMSection
    gemini: GeminiSection
    research: ResearchSection
    rag: RagSection
    paths: PathsSection
    logging: LoggingSection

    @classmethod
    def load(cls) -> Settings:
        load_dotenv_file(PROJECT_ROOT / ".env")
        config_path = DEFAULT_CONFIG_PATH
        
        if not config_path.exists():
            raise FileNotFoundError(f"Missing config configuration blueprint at: {config_path}")

        raw_yaml = config_path.read_text(encoding="utf-8")
        interpolated_yaml = interpolate_env_vars(raw_yaml)
        data = yaml.safe_load(interpolated_yaml) or {}

        return cls.model_validate(data)

    @property
    def version(self) -> str:
        return self.app.version

    @property
    def data_dir(self) -> Path:
        return Path(self.paths.data_dir).resolve()

    @property
    def gemini_api_key(self) -> str:
        return os.getenv(self.gemini.api_key_env, "")

# ============================================================
# System Singleton Hook Entrypoint
# ============================================================

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.load()
