import hashlib
from typing import Any, Dict, List

import config
from src.database.operations import VectorStore


# =========================================================
# 🧠 RAG ENGINE (CLEAN EVENTBUS VERSION)
# =========================================================
class RAG:
    """
    Production-grade retrieval engine

    ROLE:
    - Retrieve relevant documents
    - Return structured raw results
    - NO formatting / NO context building
    """

    def __init__(self):
        self.db = VectorStore()
        self.embedding_dim = config.RAG_EMBEDDING_DIMENSION

        print("[RAG] Initialized (EventBus-safe)")

    # =========================================================
    # QUERY NORMALIZATION
    # =========================================================
    def _normalize_query(self, query: str) -> str:
        if not isinstance(query, str):
            return ""
        return query.strip().replace("\n", " ")

    # =========================================================
    # EMBEDDING (STABLE FALLBACK ONLY)
    # =========================================================
    def _embed(self, query: str) -> List[float]:
        query = self._normalize_query(query)

        if not query:
            return [0.0] * self.embedding_dim

        return self._fallback_embed(query)

    # =========================================================
    # FALLBACK EMBEDDING
    # =========================================================
    def _fallback_embed(self, text: str) -> List[float]:
        vec = [0.0] * self.embedding_dim

        h = hashlib.md5(text.encode("utf-8")).hexdigest()

        for i in range(min(self.embedding_dim, len(h))):
            vec[i] = int(h[i], 16) / 15.0

        for i, c in enumerate(text[: self.embedding_dim]):
            vec[i] = (vec[i] + (ord(c) % 97) / 100.0) / 2

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
    # PARSE RESULTS (CLEAN STRUCTURE ONLY)
    # =========================================================
    def _parse_results(self, results: Any) -> List[Dict[str, Any]]:
        if not results:
            return []

        docs_block = results.get("documents", [])
        meta_block = results.get("metadatas", [])

        docs = docs_block[0] if isinstance(docs_block, list) and docs_block else []
        metas = meta_block[0] if isinstance(meta_block, list) and meta_block else []

        parsed = []

        for i, doc in enumerate(docs or []):
            meta = metas[i] if i < len(metas) else {}

            parsed.append(
                {
                    "text": doc,
                    "meta": meta if isinstance(meta, dict) else {},
                }
            )

        return parsed

    # =========================================================
    # RANKING HOOK (FUTURE ML READY)
    # =========================================================
    def _rank(self, items: List[Dict[str, Any]], query: str):
        return items

    # =========================================================
    # PUBLIC API (PURE RETRIEVAL)
    # =========================================================
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        return_raw: bool = False,
    ) -> Dict[str, Any]:

        clean_query = self._normalize_query(query)
        embedding = self._embed(clean_query)

        raw_results = self._search(embedding, top_k)
        parsed = self._parse_results(raw_results)
        ranked = self._rank(parsed, clean_query)

        response = {
            "query": clean_query,
            "count": len(ranked),
            "documents": ranked,
        }

        if return_raw:
            response["raw"] = raw_results

        return response
