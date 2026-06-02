from typing import Any, Dict, List

from removed_files.pipeline.embedder import Embedder
from src.database.operations import VectorStore


# =========================================================
# 🧠 NEXUSMIND RAG ENGINE (FINAL)
# =========================================================
class RAG:
    """
    Unified Retrieval-Augmented Generation Engine

    Responsibilities:
    - Embedding generation
    - Vector retrieval
    - Result normalization
    - Lightweight ranking (MVP)
    - Context formatting for LLM

    No orchestration logic here.
    """

    def __init__(self):
        self.db = VectorStore()
        self.embedder = Embedder()

        print("[RAG] Initialized (Production Mode)")

    # =========================================================
    # NORMALIZATION
    # =========================================================
    def _normalize_query(self, query: str) -> str:
        return query.strip().replace("\n", " ")

    # =========================================================
    # EMBEDDING
    # =========================================================
    def _embed(self, query: str):
        return self.embedder.embed(query)

    # =========================================================
    # VECTOR SEARCH
    # =========================================================
    def _search(self, embedding: List[float], top_k: int):
        return self.db.query(query_embedding=embedding, top_k=top_k)

    # =========================================================
    # SAFE RESULT PARSING (ROBUST AGAINST CHROMA SHAPES)
    # =========================================================
    def _parse_results(self, results: Any) -> List[Dict[str, Any]]:
        if not results:
            return []

        docs_block = results.get("documents", [])
        meta_block = results.get("metadatas", [])

        # Chroma nested format safety
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

        parsed: List[Dict[str, Any]] = []

        for i, doc in enumerate(docs or []):
            parsed.append(
                {
                    "text": doc,
                    "meta": metas[i] if metas and i < len(metas) else {},
                    "score": 1.0,  # placeholder for reranker
                }
            )

        return parsed

    # =========================================================
    # LIGHTWEIGHT RANKING (HOOK FOR FUTURE LLM RERANKER)
    # =========================================================
    def _rank(self, items: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        # Future upgrade:
        # - cross-encoder reranker
        # - LLM scoring
        # - semantic relevance boost

        return items

    # =========================================================
    # CONTEXT BUILDER (LLM READY FORMAT)
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
    # PUBLIC API (ORCHESTRATOR USE ONLY)
    # =========================================================
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        return_context: bool = True,
        return_raw: bool = False,
    ) -> Dict[str, Any]:

        # 1. Normalize query
        query = self._normalize_query(query)

        # 2. Embed
        embedding = self._embed(query)

        # 3. Vector search
        raw_results = self._search(embedding, top_k)

        # 4. Parse results safely
        parsed = self._parse_results(raw_results)

        # 5. Rank (future-ready hook)
        ranked = self._rank(parsed, query)

        # 6. Build context string
        context = self._build_context(ranked)

        # 7. Return unified contract
        response = {
            "query": query,
            "count": len(ranked),
            "context": context,
        }

        # Optional raw output for debugging / advanced agents
        if return_raw:
            response["documents"] = ranked

        if not return_context:
            response.pop("context", None)

        return response
