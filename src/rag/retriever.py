from typing import Any, Dict, List

from src.database.operations import VectorStore
from src.pipeline.embedder import Embedder


class Retriever:
    def __init__(self):
        self.db = VectorStore()
        self.embedder = Embedder()

    # ----------------------------
    # Normalize query (important for embedding stability)
    # ----------------------------
    def _normalize_query(self, query: str) -> str:
        return query.strip().replace("\n", " ")

    # ----------------------------
    # Core retrieval
    # ----------------------------
    def retrieve(
        self, query: str, top_k: int = 5, include_metadata: bool = True
    ) -> Dict[str, Any]:

        query = self._normalize_query(query)

        # 1. Embed query
        query_embedding = self.embedder.embed(query)

        # 2. Query vector DB
        results = self.db.query(query_embedding=query_embedding, top_k=top_k)

        # 3. Handle empty results safely
        if not results or not results.get("documents"):
            return {"query": query, "documents": [], "metadatas": [], "count": 0}

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]

        # 4. Format clean output
        formatted_docs: List[str] = []
        formatted_meta: List[Dict[str, Any]] = []

        for i, doc in enumerate(docs):
            formatted_docs.append(doc)

            if include_metadata and metas:
                formatted_meta.append(metas[i])

        return {
            "query": query,
            "documents": formatted_docs,
            "metadatas": formatted_meta,
            "count": len(formatted_docs),
        }
