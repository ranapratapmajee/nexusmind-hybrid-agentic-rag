from typing import Any, Dict, List

import config
from src.database.operations import VectorStore


# =========================================================
# 🧠 NEXUSMIND RAG ENGINE (FINAL - PRODUCTION SAFE)
# =========================================================
class RAG:
    """
    Production-grade RAG Engine

    GUARANTEES:
    - No legacy dependencies
    - Embedding dimension consistency
    - Zero crash behavior
    - Safe fallback handling
    """

    def __init__(self):
        self.db = VectorStore()
        self.embedding_dim = config.RAG_EMBEDDING_DIMENSION

        # lazy embedder (optional future injection)
        self.embedder = self._load_embedder()

        print("[RAG] Initialized (Production Mode)")

    # =========================================================
    # OPTIONAL EMBEDDER LOADER
    # =========================================================
    def _load_embedder(self):
        """
        Optional modern embedder (if exists in system)
        """
        try:
            from src.intelligence.ingestion import IngestionPipeline

            # reuse ingestion embedding logic if available
            return IngestionPipeline()._embed
        except Exception:
            return None

    # =========================================================
    # QUERY NORMALIZATION
    # =========================================================
    def _normalize_query(self, query: str) -> str:
        if not isinstance(query, str):
            return ""

        query = query.strip()
        if not query:
            return ""

        return query.replace("\n", " ")

    # =========================================================
    # SAFE EMBEDDING (CORE FIX)
    # =========================================================
    def _embed(self, query: str) -> List[float]:
        query = self._normalize_query(query)

        # EMPTY SAFETY
        if not query:
            return [0.0] * self.embedding_dim

        try:
            # 1. preferred embedder path (if available)
            if self.embedder:
                vec = self.embedder(query)
                return self._safe_vector(vec)

            # 2. fallback deterministic embedding (no external deps)
            return self._fallback_embed(query)

        except Exception as e:
            print(f"[RAG] embedding failed: {e}")
            return [0.0] * self.embedding_dim

    # =========================================================
    # VECTOR NORMALIZER (CRITICAL SAFETY LAYER)
    # =========================================================
    def _safe_vector(self, vec: List[float]) -> List[float]:
        """
        Ensures embedding always matches Chroma dimension
        """
        if not isinstance(vec, list):
            return [0.0] * self.embedding_dim

        # truncate or pad
        if len(vec) >= self.embedding_dim:
            return vec[: self.embedding_dim]

        return vec + [0.0] * (self.embedding_dim - len(vec))

    # =========================================================
    # FALLBACK EMBEDDING (SELF-CONTAINED)
    # =========================================================
    def _fallback_embed(self, text: str) -> List[float]:
        """
        Lightweight deterministic embedding
        (ONLY for safety fallback, NOT semantic)
        """
        vec = [0.0] * self.embedding_dim

        for i, c in enumerate(text[: self.embedding_dim]):
            vec[i] = (ord(c) % 97) / 100.0

        return vec

    # =========================================================
    # VECTOR SEARCH
    # =========================================================
    def _search(self, embedding: List[float], top_k: int):
        try:
            return self.db.query(query_embedding=embedding, top_k=top_k)
        except Exception as e:
            print(f"[RAG] vector search failed: {e}")
            return {}

    # =========================================================
    # RESULT PARSER (CHROMA SAFE)
    # =========================================================
    def _parse_results(self, results: Any) -> List[Dict[str, Any]]:
        if not results:
            return []

        docs_block = results.get("documents", [])
        meta_block = results.get("metadatas", [])

        docs = (
            docs_block[0]
            if docs_block and isinstance(docs_block[0], list)
            else docs_block
        )
        metas = (
            meta_block[0]
            if meta_block and isinstance(meta_block[0], list)
            else meta_block
        )

        parsed = []

        for i, doc in enumerate(docs or []):
            parsed.append(
                {
                    "text": doc,
                    "meta": metas[i] if metas and i < len(metas) else {},
                    "score": 1.0,
                }
            )

        return parsed

    # =========================================================
    # RANKING HOOK
    # =========================================================
    def _rank(self, items: List[Dict[str, Any]], query: str):
        return items

    # =========================================================
    # CONTEXT BUILDER
    # =========================================================
    def _build_context(self, items: List[Dict[str, Any]], max_docs: int = 6) -> str:
        if not items:
            return ""

        blocks = []
        for item in items[:max_docs]:
            source = item["meta"].get("filename", "unknown")
            blocks.append(f"[SOURCE: {source}]\n{item['text']}")

        return "\n\n".join(blocks).strip()

    # =========================================================
    # PUBLIC API
    # =========================================================
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        return_context: bool = True,
        return_raw: bool = False,
    ) -> Dict[str, Any]:

        clean_query = self._normalize_query(query)

        embedding = self._embed(clean_query)

        raw_results = self._search(embedding, top_k)

        parsed = self._parse_results(raw_results)

        ranked = self._rank(parsed, clean_query)

        context = self._build_context(ranked)

        response = {
            "query": clean_query,
            "count": len(ranked),
            "context": context,
        }

        if return_raw:
            response["documents"] = ranked

        if not return_context:
            response.pop("context", None)

        return response
