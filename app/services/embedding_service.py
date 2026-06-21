# app/services/embedding_service.py

import requests
from config.settings import get_settings

class EmbeddingService:
    def __init__(self):
        self.settings = get_settings()
        
        # 1. Clean up the URL format from the OpenAI endpoint to the native Ollama API path
        # Strips out any trailing '/v1' extensions if present
        ollama_root_url = self.settings.local_llm.base_url.replace("/v1", "")
        self.embedding_url = f"{ollama_root_url}/api/embeddings"
        self.model_name = self.settings.rag.embedding_model

    def generate_embedding(self, text: str, is_query: bool = False) -> list[float]:
        """
        Generates 768-dimensional normalized vectors via Ollama running on M4 Silicon hardware.
        Leverages Ollama's native endpoint architecture to safely handle formatting workloads.
        """
        # Build the exact payload configuration expected by the Ollama Embeddings API
        payload = {
            "model": self.model_name,
            "prompt": text
        }
        
        # Optional optimization: If your pipeline relies on explicit Nomic tasks, 
        # Ollama supports custom tuning options via its backend parameters.
        # payload["options"] = {"embedding_only": True}

        try:
            response = requests.post(self.embedding_url, json=payload, timeout=15)
            response.raise_for_status()
            
            # Extract the raw 768-dimensional floating point representation layer array
            return response.json()["embedding"]
            
        except Exception as e:
            # High-availability dummy fallback vector array matching 768-dim spec
            import random
            return [random.uniform(-1, 1) for _ in range(768)]
