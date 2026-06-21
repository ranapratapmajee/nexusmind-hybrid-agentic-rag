# app/services/chroma_service.py

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from config.settings import get_settings

class ChromaService:
    def __init__(self):
        self.settings = get_settings()
        
        # 1. Initialize HTTP client connecting directly to your persistent docker instance
        self.client = chromadb.HttpClient(
            host=self.settings.chroma.host,
            port=self.settings.chroma.port,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # 2. Configure native Ollama Embedding tracking 
        # Using the base URL to map directly to Ollama's local engine endpoint
        # We strip the trailing '/v1' from the base URL since the native embedding hook appends its own paths
        ollama_root_url = self.settings.local_llm.base_url.replace("/v1", "")
        self.embedding_function = OllamaEmbeddingFunction(
            url=f"{ollama_root_url}/api/embeddings",
            model_name=self.settings.rag.embedding_model
        )
        
        # 3. Establish or grab the primary collection target bound to the embedding engine
        self.collection = self.client.get_or_create_collection(
            name=self.settings.chroma.collection_name,
            embedding_function=self.embedding_function
        )

    def add_chunks(self, ids: list[str], documents: list[str], metadatas: list[dict], embeddings: list[list[float]] = None):
        """Indexes raw text segments into storage. Automatically computes embeddings via Ollama if none are provided."""
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings  # Optional: If None, Chroma automatically calls Ollama using nomic-embed-text
        )

    def query_similarity_by_vector(self, query_vector: list[float], top_k: int = 5) -> dict:
        """Runs a precise distance search using a pre-computed vector footprint."""
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k
        )
        return results

    def query_similarity_by_text(self, query_text: str, top_k: int = 5) -> dict:
        """
        Runs a precise semantic search using raw text.
        Automatically calls Ollama to embed the query string behind the scenes.
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k
        )
        return results
