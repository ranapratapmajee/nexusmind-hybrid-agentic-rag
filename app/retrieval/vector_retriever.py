# app/retrieval/vector_retriever.py

from typing import List, Dict, Any
from app.services.chroma_service import ChromaService

class VectorRetriever:
    def __init__(self, chroma_service: ChromaService):
        """
        Initialized with ChromaService.
        EmbeddingService is no longer needed here as Chroma handles text search natively.
        """
        self.chroma = chroma_service

    def retrieve_context(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Performs a native semantic search directly using the raw text query."""
        # Query Chroma using the raw text. Chroma's underlying Ollama hook will automate vectorization.
        raw_results = self.chroma.query_similarity_by_text(
            query_text=query,
            top_k=top_k
        )
        
        formatted_chunks = []
        if raw_results and raw_results.get("documents") and raw_results["documents"]:
            documents = raw_results["documents"][0]
            metadatas = raw_results["metadatas"][0]
            ids = raw_results["ids"][0]
            
            for idx in range(len(documents)):
                formatted_chunks.append({
                    "id": ids[idx],
                    "text": documents[idx],
                    "metadata": metadatas[idx]
                })
        return formatted_chunks
